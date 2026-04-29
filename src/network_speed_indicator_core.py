from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


DEFAULT_CONFIG = {
    'unit_mode': 'auto',
    'display_mode': 'split',
    'refresh_interval': 1,
}

UNIT_OPTIONS = (
    ('auto', 'Automatic (KB/MB/GB)'),
    ('kb', 'Always KB/s'),
    ('mb', 'Always MB/s'),
    ('gb', 'Always GB/s'),
)

DISPLAY_OPTIONS = (
    ('split', 'Download + Upload'),
    ('total', 'Total only'),
    ('download', 'Download only'),
    ('upload', 'Upload only'),
)

REFRESH_OPTIONS = (
    (1, 'Every 1 second'),
    (2, 'Every 2 seconds'),
    (5, 'Every 5 seconds'),
)

FORCED_UNITS = {
    'kb': (1024.0, 'KB/s'),
    'mb': (1024.0 * 1024.0, 'MB/s'),
    'gb': (1024.0 * 1024.0 * 1024.0, 'GB/s'),
}

VALID_UNIT_MODES = {value for value, _label in UNIT_OPTIONS}
VALID_DISPLAY_MODES = {value for value, _label in DISPLAY_OPTIONS}
VALID_REFRESH_INTERVALS = {value for value, _label in REFRESH_OPTIONS}

IGNORED_IFACE_PATTERNS = (
    re.compile(r'^lo$'),
    re.compile(r'^br[0-9]+$'),
    re.compile(r'^br-[A-Za-z0-9]+$'),
    re.compile(r'^tun[0-9]+$'),
    re.compile(r'^tap[0-9]+$'),
    re.compile(r'^veth[A-Za-z0-9]+$'),
    re.compile(r'^virbr[0-9]+$'),
    re.compile(r'^docker0$'),
    re.compile(r'^proton[0-9]+$'),
)


def should_ignore_interface(name: str) -> bool:
    return any(pattern.match(name) for pattern in IGNORED_IFACE_PATTERNS)


def parse_proc_net_dev_lines(lines: Iterable[str]) -> tuple[int, int]:
    download_total = 0
    upload_total = 0

    for line in lines:
        if ':' not in line:
            continue

        iface, raw_values = line.split(':', 1)
        iface = iface.strip()
        if should_ignore_interface(iface):
            continue

        values = raw_values.split()
        if len(values) < 16:
            continue

        download_total += int(values[0])
        upload_total += int(values[8])

    return download_total, upload_total


def read_bytes(proc_net_dev_path: str | Path = '/proc/net/dev') -> tuple[int, int]:
    proc_net_dev_path = Path(proc_net_dev_path)

    with proc_net_dev_path.open('r', encoding='utf-8') as proc_net_dev:
        next(proc_net_dev, None)
        next(proc_net_dev, None)
        return parse_proc_net_dev_lines(proc_net_dev)


def normalize_config(raw_config: object) -> dict[str, object]:
    config = DEFAULT_CONFIG.copy()
    if not isinstance(raw_config, dict):
        return config

    unit_mode = raw_config.get('unit_mode')
    if unit_mode == 'bytes':
        unit_mode = 'kb'
    if unit_mode in VALID_UNIT_MODES:
        config['unit_mode'] = unit_mode

    display_mode = raw_config.get('display_mode')
    if display_mode in VALID_DISPLAY_MODES:
        config['display_mode'] = display_mode

    refresh_interval = raw_config.get('refresh_interval')
    if type(refresh_interval) is int and refresh_interval in VALID_REFRESH_INTERVALS:
        config['refresh_interval'] = refresh_interval

    return config


def format_number(value: float, unit_label: str) -> str:
    if value >= 100:
        return f'{value:.0f} {unit_label}'
    if value >= 10:
        return f'{value:.1f} {unit_label}'
    return f'{value:.2f} {unit_label}'


def format_rate(rate_bytes_per_second: float, unit_mode: str) -> str:
    if unit_mode != 'auto':
        factor, unit_label = FORCED_UNITS[unit_mode]
        value = max(rate_bytes_per_second, 0.0) / factor
        return format_number(value, unit_label)

    units = ('KB/s', 'MB/s', 'GB/s', 'TB/s')
    value = max(rate_bytes_per_second, 0.0) / 1024.0
    unit_index = 0

    while value >= 1024.0 and unit_index < len(units) - 1:
        value /= 1024.0
        unit_index += 1

    return format_number(value, units[unit_index])


def build_indicator_label(
    download_rate: float,
    upload_rate: float,
    unit_mode: str,
    display_mode: str,
) -> str:
    if display_mode == 'split':
        return (
            f'↓ {format_rate(download_rate, unit_mode)}  '
            f'↑ {format_rate(upload_rate, unit_mode)}'
        )

    if display_mode == 'total':
        return f'⇅ {format_rate(download_rate + upload_rate, unit_mode)}'

    if display_mode == 'download':
        return f'↓ {format_rate(download_rate, unit_mode)}'

    return f'↑ {format_rate(upload_rate, unit_mode)}'