import unittest
from pathlib import Path


class SnapPackagingTests(unittest.TestCase):
    def test_snap_installs_all_python_runtime_modules(self) -> None:
        snapcraft_path = Path(__file__).resolve().parents[1] / 'snap' / 'snapcraft.yaml'
        snapcraft_text = snapcraft_path.read_text(encoding='utf-8')

        self.assertIn(
            'src/network_speed_indicator.py',
            snapcraft_text,
        )
        self.assertIn(
            'src/network_speed_indicator_core.py',
            snapcraft_text,
        )
        self.assertIn(
            '"$CRAFT_PART_INSTALL/bin/network_speed_indicator_core.py"',
            snapcraft_text,
        )

    def test_snap_declares_login_autostart_desktop_entry(self) -> None:
        snapcraft_path = Path(__file__).resolve().parents[1] / 'snap' / 'snapcraft.yaml'
        snapcraft_text = snapcraft_path.read_text(encoding='utf-8')

        self.assertIn(
            'autostart: linux-network-speed-indicator-autostart.desktop',
            snapcraft_text,
        )

    def test_autostart_template_uses_packaged_command_path(self) -> None:
        autostart_template_path = (
            Path(__file__).resolve().parents[1]
            / 'assets'
            / 'autostart'
            / 'linux-network-speed-indicator.desktop.in'
        )
        autostart_template_text = autostart_template_path.read_text(encoding='utf-8')

        self.assertIn('Exec=__EXEC_PATH__', autostart_template_text)
        self.assertIn('TryExec=__EXEC_PATH__', autostart_template_text)


if __name__ == '__main__':
    unittest.main()