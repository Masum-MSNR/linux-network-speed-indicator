import tempfile
import textwrap
import unittest
from pathlib import Path

from src.network_speed_indicator_core import (
    DEFAULT_CONFIG,
    build_indicator_label,
    format_rate,
    normalize_config,
    read_bytes,
    should_ignore_interface,
)


class NormalizeConfigTests(unittest.TestCase):
    def test_invalid_config_uses_defaults(self) -> None:
        self.assertEqual(normalize_config('invalid'), DEFAULT_CONFIG)

    def test_normalize_config_filters_invalid_values(self) -> None:
        raw_config = {
            'unit_mode': 'bytes',
            'display_mode': 'download',
            'refresh_interval': True,
        }

        self.assertEqual(
            normalize_config(raw_config),
            {
                'unit_mode': 'kb',
                'display_mode': 'download',
                'refresh_interval': DEFAULT_CONFIG['refresh_interval'],
            },
        )


class InterfaceFilterTests(unittest.TestCase):
    def test_virtual_interfaces_are_ignored(self) -> None:
        self.assertTrue(should_ignore_interface('docker0'))
        self.assertTrue(should_ignore_interface('virbr0'))
        self.assertFalse(should_ignore_interface('eth0'))


class ProcNetDevTests(unittest.TestCase):
    def test_read_bytes_aggregates_non_ignored_interfaces(self) -> None:
        proc_net_dev = textwrap.dedent(
            """\
            Inter-|   Receive                                                |  Transmit
             face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
                lo: 100 0 0 0 0 0 0 0 200 0 0 0 0 0 0 0
              eth0: 2048 0 0 0 0 0 0 0 1024 0 0 0 0 0 0 0
           docker0: 4096 0 0 0 0 0 0 0 2048 0 0 0 0 0 0 0
            wlp2s0: 1024 0 0 0 0 0 0 0 512 0 0 0 0 0 0 0
            """
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            proc_net_dev_path = Path(temp_dir) / 'proc_net_dev'
            proc_net_dev_path.write_text(proc_net_dev, encoding='utf-8')

            self.assertEqual(read_bytes(proc_net_dev_path), (3072, 1536))


class FormattingTests(unittest.TestCase):
    def test_format_rate_uses_expected_units(self) -> None:
        self.assertEqual(format_rate(1024, 'auto'), '1.00 KB/s')
        self.assertEqual(format_rate(10 * 1024 * 1024, 'mb'), '10.0 MB/s')
        self.assertEqual(format_rate(-1, 'kb'), '0.00 KB/s')

    def test_build_indicator_label_respects_display_mode(self) -> None:
        self.assertEqual(
            build_indicator_label(2048, 1024, 'auto', 'split'),
            '↓ 2.00 KB/s  ↑ 1.00 KB/s',
        )
        self.assertEqual(
            build_indicator_label(2048, 1024, 'auto', 'total'),
            '⇅ 3.00 KB/s',
        )


if __name__ == '__main__':
    unittest.main()