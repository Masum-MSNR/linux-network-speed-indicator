# Linux Network Speed Indicator

Linux Network Speed Indicator is a simple top-bar and tray speed meter for Ubuntu GNOME and other Linux desktops that support AppIndicator or StatusNotifier items.

Users should install the `.deb` release.

## Supported Linux Desktops

- Ubuntu GNOME 24.04 and newer
- Ubuntu 26.04 GNOME
- Debian GNOME
- Other Linux desktops with AppIndicator or StatusNotifier support

Important note:

- GNOME needs an AppIndicator host in the top bar.
- Ubuntu already includes this by default through the Ubuntu AppIndicators extension.

## Download and Install

1. Open the GitHub Releases page.
2. Download the latest `.deb` file.
3. Install it with:

```bash
sudo apt install ./linux-network-speed-indicator_<version>_all.deb
```

Why this command:

- it installs the app
- it installs required dependencies automatically
- it works better than `dpkg -i` for normal users

## After Install

- the app appears in the top bar or tray area
- it starts automatically on login
- click the indicator to change units, display mode, refresh rate, or autostart

## Remove

```bash
sudo apt remove linux-network-speed-indicator
```

## What It Shows

- `↓` download speed
- `↑` upload speed
- `⇅` total speed

Units available from the menu:

- automatic `KB/MB/GB`
- fixed `KB/s`
- fixed `MB/s`
- fixed `GB/s`

## For Maintainers

Project, version-control, release, and packaging notes are in [MAINTAINING.md](MAINTAINING.md).
