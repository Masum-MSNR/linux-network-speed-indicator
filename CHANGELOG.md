# Changelog

All notable changes to this project should be documented in this file.

## [Unreleased]
- Added Snap packaging with `snap/snapcraft.yaml`, a local `scripts/build-snap.sh` helper, and Snap-aware asset lookup in the app runtime.
- Updated release automation and documentation so the next versioned GitHub release can attach a `.snap` artifact alongside the existing `.deb`, `.flatpak`, `.zip`, and `.tar.gz` assets.

## [0.1.6] - 2026-04-29
- Fixed Flatpak CI builds by forcing the Ayatana CMake modules to install their libraries under `/app/lib` instead of `/app/lib64`.
- Unblocked dependency discovery for `libayatana-indicator` and the GitHub-hosted `.flatpak` release pipeline.

## [0.1.5] - 2026-04-29
- Fixed GitHub Actions Flatpak dependency installation by using the user-scoped Flathub remote with host `flatpak-builder`.
- Unblocked GitHub release publishing for the `.flatpak` bundle.

## [0.1.4] - 2026-04-29
- Fixed the Flatpak build so the bundled Ayatana and libdbusmenu stack now builds successfully.
- Added a GitHub release `.flatpak` bundle alongside the existing `.deb`, `.zip`, and `.tar.gz` assets.
- Updated the release workflow and README download instructions for the new Flatpak artifact.

## [0.1.3] - 2026-04-29
- Added the final real application screenshots to the README.
- Replaced generated AppStream screenshot assets with the final approved images.
- Removed the obsolete screenshot generator script and reference image workflow.

## [0.1.2] - 2026-04-29
- Fixed the autostart override generator so the in-app toggle no longer writes a broken desktop entry.
- Added AppStream metadata and a themed launcher icon for Linux software center readiness.
- Improved package installation paths and local install cleanup for launcher, icon, and metainfo assets.
- Reworked the README for clearer installation guidance, Linux search visibility, and MIT license messaging.

## [0.1.1] - 2026-04-29
- Changed GitHub release automation to publish only when `VERSION` changes on `main`.
- Added automatic tag creation from the `VERSION` file during the release workflow.

## [0.1.0] - 2026-04-29
- First GitHub-ready release of the Linux Network Speed Indicator project.
- Added user-local install and uninstall scripts.
- Added GitHub Actions CI and release packaging workflow support.
- Added persistent settings for units, display mode, refresh interval, and autostart.
