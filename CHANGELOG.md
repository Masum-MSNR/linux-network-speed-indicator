# Changelog

All notable changes to this project should be documented in this file.

## [0.1.9] - 2026-04-29
- Fixed the Snap launcher to start the app through the staged Python runtime, with a fallback for versioned `python3.x` interpreter paths inside the snap.
- Switched the Snap desktop file to the packaged `meta/gui` icon path and simplified the Snap contact metadata to satisfy store validation more reliably.
- Delayed release tag creation until after the Snap build and store publish steps succeed so failed runs do not leave orphaned version tags behind.

## [0.1.8] - 2026-04-29
- Fixed Snap packaging so the app launches from the installed script path instead of a missing `usr/bin/python3` entry.
- Fixed the Snap desktop launcher to use an explicit in-snap icon path and added Snap contact/icon metadata for store validation.

## [0.1.7] - 2026-04-29
- Added Snap packaging with `snap/snapcraft.yaml`, a local `scripts/build-snap.sh` helper, and Snap-aware asset lookup in the app runtime.
- Updated release automation and documentation so versioned GitHub releases now attach a `.snap` artifact alongside the existing `.deb`, `.flatpak`, `.zip`, and `.tar.gz` assets.
- Added automatic Snap Store publishing to the `stable` channel from the release workflow.

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
