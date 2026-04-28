# Maintaining Linux Network Speed Indicator

## Repository Layout

```text
linux-network-speed-indicator/
├── assets/
│   ├── applications/
│   ├── autostart/
│   ├── icons/
│   └── metainfo/
├── config/
├── scripts/
├── src/
├── .github/workflows/
├── install.sh
├── uninstall.sh
├── README.md
├── MAINTAINING.md
├── CHANGELOG.md
├── LICENSE
└── VERSION
```

## Local Development

- Keep source changes inside the repository.
- Do not edit installed copies under `~/.local/bin` or `/usr/bin` directly.
- Reinstall from the repo after changes.

## Local User Install

```bash
chmod +x install.sh
./install.sh
```

## Debian Package Build

```bash
chmod +x scripts/build-deb.sh
./scripts/build-deb.sh
```

This creates:

- `dist/linux-network-speed-indicator_<version>_all.deb`

The Debian package also installs:

- a launcher in `/usr/share/applications/`
- an AppStream file in `/usr/share/metainfo/`
- a themed app icon in `/usr/share/icons/hicolor/scalable/apps/`

## Full Release Build

```bash
chmod +x scripts/build-release.sh
./scripts/build-release.sh
```

This creates:

- `dist/linux-network-speed-indicator_<version>_all.deb`
- `dist/linux-network-speed-indicator-<version>.tar.gz`
- `dist/linux-network-speed-indicator-<version>.zip`

## Version Control Flow

Recommended release flow:

1. Update `VERSION`
2. Update `CHANGELOG.md`
3. Commit changes
4. Push `main`

Example:

```bash
git add .
git commit -m "Release v0.1.1"
git push origin main
```

GitHub Actions creates the matching `v<version>` tag and publishes the release automatically.

## GitHub Actions

- `ci.yml` validates Python, shell scripts, JSON, and Debian package creation.
- `release.yml` runs only when `VERSION` changes on `main`, creates the matching Git tag, then publishes `.deb`, `.zip`, and `.tar.gz` artifacts.

## Linux Store Readiness

- `assets/metainfo/linux-network-speed-indicator.metainfo.xml` provides AppStream metadata.
- The package installs a hicolor launcher icon and desktop entry for software center indexing.
- This improves compatibility with GNOME Software, KDE Discover, Ubuntu App Center, and other AppStream-based Linux stores.
- Publishing into those stores still requires a compatible repository or additional package formats such as Flatpak, Snap, COPR, or AUR.

## Semantic Versioning

- `MAJOR`: breaking changes
- `MINOR`: new features
- `PATCH`: fixes and small improvements

Current version is stored in `VERSION`.