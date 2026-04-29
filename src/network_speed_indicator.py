#!/usr/bin/python3

import fcntl
import json
import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')

from gi.repository import AyatanaAppIndicator3 as AppIndicator3
from gi.repository import GLib
from gi.repository import Gtk

if __package__:
    from .network_speed_indicator_core import (
        DEFAULT_CONFIG,
        DISPLAY_OPTIONS,
        REFRESH_OPTIONS,
        UNIT_OPTIONS,
        VALID_DISPLAY_MODES,
        VALID_REFRESH_INTERVALS,
        VALID_UNIT_MODES,
        build_indicator_label,
        normalize_config,
        read_bytes,
    )
else:
    from network_speed_indicator_core import (
        DEFAULT_CONFIG,
        DISPLAY_OPTIONS,
        REFRESH_OPTIONS,
        UNIT_OPTIONS,
        VALID_DISPLAY_MODES,
        VALID_REFRESH_INTERVALS,
        VALID_UNIT_MODES,
        build_indicator_label,
        normalize_config,
        read_bytes,
    )


APP_ID = 'linux-network-speed-indicator'
APP_TITLE = 'Linux Network Speed Indicator'
SCRIPT_PATH = Path(__file__).resolve()
IS_FLATPAK = Path('/.flatpak-info').exists() or 'FLATPAK_ID' in os.environ
IS_SNAP = 'SNAP' in os.environ
IS_SANDBOXED = IS_FLATPAK or IS_SNAP
DATA_HOME = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local' / 'share')))
USER_SHARE_DIR = DATA_HOME / APP_ID
FLATPAK_SHARE_DIR = Path('/app/share') / APP_ID
SNAP_ROOT = Path(os.environ['SNAP']) if IS_SNAP else None
SNAP_SHARE_DIR = SNAP_ROOT / 'usr' / 'share' / APP_ID if SNAP_ROOT else None
SYSTEM_SHARE_DIR = Path('/usr/share') / APP_ID
STATE_HOME = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local' / 'state')))
STATE_DIR = STATE_HOME / APP_ID
CONFIG_HOME = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config')))
CONFIG_DIR = CONFIG_HOME / APP_ID
CONFIG_PATH = CONFIG_DIR / 'config.json'
AUTOSTART_PATH = CONFIG_HOME / 'autostart' / f'{APP_ID}.desktop'
SYSTEM_AUTOSTART_PATH = Path('/etc/xdg/autostart') / f'{APP_ID}.desktop'
LOCK_PATH = Path(os.environ.get('XDG_RUNTIME_DIR', '/tmp')) / f'{APP_ID}.lock'
LOG_PATH = STATE_DIR / f'{APP_ID}.log'
ICON_NAME = 'network-speed-indicator-empty'
APP_ICON_NAME = 'linux-network-speed-indicator'
AUTOSTART_SUPPORTED = not IS_SANDBOXED

PROJECT_ROOT = next(
    (
        parent
        for parent in SCRIPT_PATH.parents
        if (parent / 'VERSION').exists() and (parent / 'src').exists()
    ),
    None,
)
PROJECT_ICON_DIR = PROJECT_ROOT / 'assets' / 'icons' if PROJECT_ROOT else None
PROJECT_DEFAULT_CONFIG_PATH = (
    PROJECT_ROOT / 'config' / 'default-config.json' if PROJECT_ROOT else None
)



def first_existing_path(*candidates: Path | None) -> Path | None:
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    return None


def configure_logging() -> logging.Logger:
    logger = logging.getLogger(APP_ID)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            LOG_PATH,
            maxBytes=256 * 1024,
            backupCount=3,
            encoding='utf-8',
        )
    except OSError:
        logger.warning('Failed to initialize log file at %s.', LOG_PATH)
        return logger

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


LOGGER = configure_logging()


ICON_DIR = first_existing_path(
    USER_SHARE_DIR / 'icons',
    FLATPAK_SHARE_DIR / 'icons',
    SNAP_SHARE_DIR / 'icons',
    SYSTEM_SHARE_DIR / 'icons',
    PROJECT_ICON_DIR,
)
DEFAULT_CONFIG_SOURCE = first_existing_path(
    USER_SHARE_DIR / 'default-config.json',
    FLATPAK_SHARE_DIR / 'default-config.json',
    SNAP_SHARE_DIR / 'default-config.json',
    SYSTEM_SHARE_DIR / 'default-config.json',
    PROJECT_DEFAULT_CONFIG_PATH,
)


def render_autostart(enabled: bool) -> str:
    exec_path = SCRIPT_PATH
    return f"""[Desktop Entry]
Type=Application
Version=1.0
Name=Linux Network Speed Indicator
Comment=Show live download and upload speeds in the top bar
Exec={exec_path}
TryExec={exec_path}
Terminal=false
X-GNOME-Autostart-enabled={str(enabled).lower()}
X-GNOME-Autostart-Delay=3
OnlyShowIn=GNOME;Unity;
StartupNotify=false
Icon={APP_ICON_NAME}
Categories=Network;Utility;
"""


def load_default_config() -> dict[str, object]:
    if not DEFAULT_CONFIG_SOURCE:
        return DEFAULT_CONFIG.copy()

    try:
        with DEFAULT_CONFIG_SOURCE.open('r', encoding='utf-8') as config_file:
            raw_config = json.load(config_file)
    except (OSError, json.JSONDecodeError) as error:
        LOGGER.warning('Failed to load default config from %s: %s', DEFAULT_CONFIG_SOURCE, error)
        return DEFAULT_CONFIG.copy()

    return normalize_config(raw_config)


def load_config() -> dict[str, object]:
    try:
        with CONFIG_PATH.open('r', encoding='utf-8') as config_file:
            raw_config = json.load(config_file)
    except FileNotFoundError:
        return load_default_config()
    except (OSError, json.JSONDecodeError) as error:
        LOGGER.warning('Failed to load user config from %s: %s', CONFIG_PATH, error)
        return load_default_config()

    return normalize_config(raw_config)


def save_config(config: dict[str, object]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open('w', encoding='utf-8') as config_file:
        json.dump(config, config_file, indent=2, sort_keys=True)
        config_file.write('\n')


def write_autostart_file(enabled: bool) -> None:
    if not AUTOSTART_SUPPORTED:
        return

    AUTOSTART_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUTOSTART_PATH.write_text(render_autostart(enabled), encoding='utf-8')


def is_autostart_enabled() -> bool:
    if not AUTOSTART_SUPPORTED:
        return False

    try:
        content = AUTOSTART_PATH.read_text(encoding='utf-8')
    except FileNotFoundError:
        try:
            content = SYSTEM_AUTOSTART_PATH.read_text(encoding='utf-8')
        except (FileNotFoundError, OSError):
            return False
    except OSError:
        return True

    for line in content.splitlines():
        if line.startswith('X-GNOME-Autostart-enabled='):
            return line.partition('=')[2].strip().lower() == 'true'

    return True


def acquire_single_instance_lock():
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock_handle = LOCK_PATH.open('w', encoding='utf-8')

    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_handle.close()
        return None

    lock_handle.write(f'{os.getpid()}\n')
    lock_handle.flush()
    return lock_handle


class NetworkSpeedIndicator:
    def __init__(self, lock_handle) -> None:
        self._lock_handle = lock_handle
        self.config = load_config()
        self.autostart_enabled = is_autostart_enabled()
        self._update_id = 0
        self._last_error_signature: tuple[str, str] | None = None
        self._last_label: str | None = None
        self._split_label_guide = '↓ 9999.9 TB/s  ↑ 9999.9 TB/s'
        self._single_label_guides = {
            'download': '↓ 9999.9 TB/s',
            'upload': '↑ 9999.9 TB/s',
            'total': '⇅ 9999.9 TB/s',
        }
        indicator_icon = ICON_NAME if ICON_DIR else 'network-transmit-receive-symbolic'

        self.indicator = AppIndicator3.Indicator.new(
            APP_ID,
            indicator_icon,
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES,
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_title(APP_TITLE)
        if ICON_DIR and ICON_DIR.exists():
            self.indicator.set_icon_theme_path(str(ICON_DIR))
            self.indicator.set_icon_full(indicator_icon, APP_TITLE)
        else:
            self.indicator.set_icon_full(indicator_icon, APP_TITLE)

        self.indicator.set_label('↓ --  ↑ --', self._split_label_guide)
        self.indicator.set_menu(self._build_menu())

        self.previous_download, self.previous_upload = read_bytes()
        self.previous_time = time.monotonic()

        self._restart_timer()
        self.update_label()

    def _append_radio_submenu(
        self,
        menu: Gtk.Menu,
        title: str,
        options,
        current_value,
        callback,
    ) -> None:
        menu_item = Gtk.MenuItem(label=title)
        submenu = Gtk.Menu()
        group_item = None

        for value, label in options:
            if group_item is None:
                radio_item = Gtk.RadioMenuItem.new_with_label(None, label)
                group_item = radio_item
            else:
                radio_item = Gtk.RadioMenuItem.new_with_label_from_widget(group_item, label)

            radio_item.set_active(value == current_value)
            radio_item.connect('toggled', callback, value)
            radio_item.show()
            submenu.append(radio_item)

        menu_item.set_submenu(submenu)
        menu_item.show()
        menu.append(menu_item)

    def _restart_timer(self) -> None:
        if self._update_id:
            GLib.source_remove(self._update_id)
            self._update_id = 0

        interval = int(self.config['refresh_interval'])
        self._update_id = GLib.timeout_add_seconds(interval, self.update_label)

    def _get_label_guide(self) -> str:
        display_mode = self.config['display_mode']
        if display_mode == 'split':
            return self._split_label_guide

        return self._single_label_guides[display_mode]

    def _build_menu(self) -> Gtk.Menu:
        menu = Gtk.Menu()

        self._append_radio_submenu(
            menu,
            'Units',
            UNIT_OPTIONS,
            self.config['unit_mode'],
            self._on_unit_mode_changed,
        )
        self._append_radio_submenu(
            menu,
            'Display',
            DISPLAY_OPTIONS,
            self.config['display_mode'],
            self._on_display_mode_changed,
        )
        self._append_radio_submenu(
            menu,
            'Refresh Rate',
            REFRESH_OPTIONS,
            self.config['refresh_interval'],
            self._on_refresh_interval_changed,
        )

        if AUTOSTART_SUPPORTED:
            start_on_login_item = Gtk.CheckMenuItem(label='Start on Login')
            start_on_login_item.set_active(self.autostart_enabled)
            start_on_login_item.connect('toggled', self._on_autostart_toggled)
        else:
            start_on_login_item = Gtk.MenuItem(
                label='Start on Login (not available in sandboxed packages)'
            )
            start_on_login_item.set_sensitive(False)
        start_on_login_item.show()
        menu.append(start_on_login_item)

        separator = Gtk.SeparatorMenuItem()
        separator.show()
        menu.append(separator)

        quit_item = Gtk.MenuItem(label='Quit Speed Meter')
        quit_item.connect('activate', self._quit)
        quit_item.show()
        menu.append(quit_item)

        return menu

    def _on_unit_mode_changed(self, item: Gtk.RadioMenuItem, unit_mode: str) -> None:
        if not item.get_active() or self.config['unit_mode'] == unit_mode:
            return

        self.config['unit_mode'] = unit_mode
        save_config(self.config)
        self.update_label()

    def _on_display_mode_changed(self, item: Gtk.RadioMenuItem, display_mode: str) -> None:
        if not item.get_active() or self.config['display_mode'] == display_mode:
            return

        self.config['display_mode'] = display_mode
        save_config(self.config)
        self.update_label()

    def _on_refresh_interval_changed(self, item: Gtk.RadioMenuItem, refresh_interval: int) -> None:
        if not item.get_active() or self.config['refresh_interval'] == refresh_interval:
            return

        self.config['refresh_interval'] = refresh_interval
        save_config(self.config)
        self._restart_timer()
        self.update_label()

    def _on_autostart_toggled(self, item: Gtk.CheckMenuItem) -> None:
        enabled = item.get_active()
        if self.autostart_enabled == enabled:
            return

        try:
            write_autostart_file(enabled)
        except OSError:
            LOGGER.exception('Failed to update autostart entry at %s.', AUTOSTART_PATH)
            item.handler_block_by_func(self._on_autostart_toggled)
            item.set_active(self.autostart_enabled)
            item.handler_unblock_by_func(self._on_autostart_toggled)
            return

        self.autostart_enabled = enabled

    def _quit(self, _item: Gtk.MenuItem) -> None:
        if self._update_id:
            GLib.source_remove(self._update_id)
            self._update_id = 0
        Gtk.main_quit()

    def update_label(self) -> bool:
        try:
            current_download, current_upload = read_bytes()
            current_time = time.monotonic()
            elapsed = max(current_time - self.previous_time, 1e-6)

            download_rate = (current_download - self.previous_download) / elapsed
            upload_rate = (current_upload - self.previous_upload) / elapsed

            self.previous_download = current_download
            self.previous_upload = current_upload
            self.previous_time = current_time

            unit_mode = self.config['unit_mode']
            display_mode = self.config['display_mode']
            label = build_indicator_label(download_rate, upload_rate, unit_mode, display_mode)
            if self._last_label != label:
                self.indicator.set_label(label, self._get_label_guide())
                self._last_label = label

            if self._last_error_signature is not None:
                LOGGER.info('Recovered from previous runtime update error.')
                self._last_error_signature = None
        except Exception as error:  # pragma: no cover
            error_signature = (type(error).__name__, str(error))
            if self._last_error_signature != error_signature:
                LOGGER.exception('Failed to update network speed indicator.')
                self._last_error_signature = error_signature

            error_label = '↓ err  ↑ err'
            if self._last_label != error_label:
                self.indicator.set_label(error_label, self._split_label_guide)
                self._last_label = error_label

        return True


def main() -> None:
    lock_handle = acquire_single_instance_lock()
    if lock_handle is None:
        LOGGER.info('Another %s instance is already running.', APP_ID)
        return

    if AUTOSTART_SUPPORTED and not AUTOSTART_PATH.exists() and not SYSTEM_AUTOSTART_PATH.exists():
        try:
            write_autostart_file(True)
        except OSError:
            LOGGER.exception('Failed to initialize autostart entry at %s.', AUTOSTART_PATH)

    try:
        NetworkSpeedIndicator(lock_handle)
    except Exception:  # pragma: no cover
        LOGGER.exception('Application startup failed.')
        raise

    Gtk.main()


if __name__ == '__main__':
    main()
