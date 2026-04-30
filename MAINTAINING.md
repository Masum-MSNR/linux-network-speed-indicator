# Maintaining Linux Network Speed Indicator

## Repository Layout

```text
linux-network-speed-indicator/
├── assets/
│   ├── applications/
│   ├── autostart/
│   ├── icons/
│   ├── metainfo/
│   └── screenshots/
├── snap/
├── io.github.MasumMSNR.LinuxNetworkSpeedIndicator.yaml
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

## Flatpak Build

```bash
chmod +x scripts/build-flatpak.sh
./scripts/build-flatpak.sh
```

This creates:

- `dist/io.github.MasumMSNR.LinuxNetworkSpeedIndicator.flatpak`
- `dist/flatpak-build/`
- `dist/flatpak-repo/`

The Flatpak manifest lives at `io.github.MasumMSNR.LinuxNetworkSpeedIndicator.yaml`.

## Snap Build

```bash
chmod +x scripts/build-snap.sh
./scripts/build-snap.sh
```

This creates:

- `dist/linux-network-speed-indicator_<version>_<arch>.snap`

Install the local Snap with:

```bash
sudo snap install --dangerous dist/linux-network-speed-indicator_<version>_<arch>.snap
```

If needed, connect the network observation interface once after install:

```bash
sudo snap connect linux-network-speed-indicator:network-observe
```

The Snapcraft project file lives at `snap/snapcraft.yaml`.

AppStream screenshot assets are generated with:

```bash
cp /path/to/indicator-only-screenshot.png assets/screenshots/overview.png
cp /path/to/menu-open-screenshot.png assets/screenshots/menu.png
```

The AppStream screenshots are committed directly in `assets/screenshots/`.
When the UI changes, replace those two files with new real screenshots instead of regenerating them from a script.

Flatpak-specific behavior:

- the app now probes `/app/share/linux-network-speed-indicator/` for bundled icons and default config
- Flatpak builds disable the autostart toggle because sandboxed autostart files do not affect the host desktop session
- the manifest uses `--share=network` so `/proc/net/dev` reflects host traffic instead of only sandbox traffic
- the tray icon only requests `org.kde.StatusNotifierWatcher` on the session bus

Snap-specific behavior:

- the app now probes `$SNAP/usr/share/linux-network-speed-indicator/` for bundled icons and default config
- Snap builds declare the autostart desktop filename through `apps.linux-network-speed-indicator.autostart`
- the app writes the matching desktop entry into `$SNAP_USER_DATA/.config/autostart` on first run, and the in-app toggle can update that entry afterward
- the Snap uses strict confinement and requests `network-observe` for `/proc/net/dev` access
- Snap Store screenshots and the Snap Store category are separate store-listing metadata maintained directly through the Snap Store web dashboard at https://snapcraft.io/linux-network-speed-indicator/listing

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

- `scripts/validate-project.sh` is the shared validation entrypoint for local checks and the pipeline workflow; it runs Python compilation, unit tests, shell syntax checks, JSON validation, and AppStream validation when available.
- `ci.yml` is now the single pipeline workflow: it always validates and builds on pushes to `main` plus pull requests, and it only runs the release job after validation succeeds on a push to `main` where `VERSION` changed.
- The release path in `ci.yml` now builds Snap artifacts for both `amd64` and `arm64` on native GitHub-hosted runners, and only publishes them to the Snap Store after both architecture builds succeed.
- The final release job inside `ci.yml` installs Snapcraft plus `pymacaroons`, publishes the built Snap artifacts, syncs the Snap Store screenshots/category, then creates the matching Git tag and publishes `.deb`, `.flatpak`, `.snap`, `.zip`, and `.tar.gz` artifacts.

## Linux Store Readiness

- `assets/metainfo/linux-network-speed-indicator.metainfo.xml` provides AppStream metadata.
- `assets/screenshots/` contains the AppStream screenshot assets referenced by the metainfo file.
- The package installs a hicolor launcher icon and desktop entry for software center indexing.
- This improves compatibility with GNOME Software, KDE Discover, Ubuntu App Center, and other AppStream-based Linux stores.
- `io.github.MasumMSNR.LinuxNetworkSpeedIndicator.yaml` adds a repo-local Flatpak packaging path for Flathub-style builds.
- `snap/snapcraft.yaml` adds a repo-local Snap packaging path for GitHub-hosted `.snap` builds and Snap Store publication.
- Snap Store screenshots and the Snap Store category are managed separately in the Snap Store listing or Dashboard API.
- The intended Snap Store category for this app is `Utilities`, and the listing screenshots should use `assets/screenshots/overview.png` and `assets/screenshots/menu.png`.
- Publishing into those stores still requires a compatible repository or additional package formats such as COPR or AUR.
- Flathub submission may still need review-driven metadata cleanup after the repo screenshots are in place.

## Semantic Versioning

- `MAJOR`: breaking changes
- `MINOR`: new features
- `PATCH`: fixes and small improvements

Current version is stored in `VERSION`.