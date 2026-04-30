# Changelog

All notable changes to this project should be documented in this file.

## [0.1.19] - 2026-05-01
- Fixed the Flatpak release build to retry transient `flatpak-builder` download failures. The failing GitHub Actions job died while fetching the `libdbusmenu` source tarball from `archive.ubuntu.com` with `SSL connection timeout`, before any compile step started.
- Added a retry loop to `scripts/build-flatpak.sh` so temporary network failures while downloading Flatpak sources no longer fail the release on the first attempt.

## [0.1.18] - 2026-05-01
- Removed the unused transparent placeholder icon (`network-speed-indicator-empty.svg`) entirely. The AppIndicator is now constructed with an empty icon name, so the GNOME `appindicator` extension does not allocate an icon slot to the left of the label. The speed text now sits flush in the panel and the popup menu naturally centers under the narrower indicator.
- Cleaned up all build paths (`install.sh`, `scripts/build-deb.sh`, `snap/snapcraft.yaml`, the Flatpak manifest) and Python constants (`ICON_NAME`, `PROJECT_ICON_DIR`, `ICON_DIR`) that referenced the removed asset.

## [0.1.17] - 2026-05-01
- Removed the Snap Store listing sync step (`scripts/sync-snap-store-listing.sh`) and the workflow step that ran it. The Dashboard API call kept failing in CI with `HTTP 401: Expired macaroon` because the discharge macaroon in `STORE_LOGIN` only lives ~24 h and the snapcraft upload path does not refresh it. Snap Store category and screenshots are now maintained directly via the Snap Store web dashboard, which is the supported workflow.
- Removed the `pymacaroons` install step from the release pipeline since it was only used by the deleted listing-sync script.
- Shrunk the placeholder indicator icon (`network-speed-indicator-empty.svg`) to a true 1x1 SVG so any AppIndicator renderer that respects the source icon aspect ratio collapses the icon slot. The visible left-side gap is the AppIndicator icon slot reserved by the GNOME `appindicator` extension; it cannot be eliminated entirely without replacing the renderer, but this minimizes it on extensions that scale by source dimensions.

## [0.1.16] - 2026-05-01
- Tightened the panel indicator's left padding by shrinking the transparent placeholder icon (`network-speed-indicator-empty.svg`) from 16x16 to 1x16. AyatanaAppIndicator no longer reserves a full icon slot on the left of the speed text, so the label sits flush in the GNOME top bar and the popup menu re-centers under the narrower indicator automatically.

## [0.1.15] - 2026-05-01
- Re-released `0.1.14` payload (snap launcher fix + autostart fix) after a transient apt mirror failure caused the previous amd64 build to fail mid-release.
- Replaced `snapcore/action-build@v1` with a direct `snapcraft pack --destructive-mode` step in the release workflow. The GitHub runner's Ubuntu 24.04 image already matches the snap's `core24` base, so building destructively skips the LXD VM bootstrap and shaves several minutes off each architecture.
- Added a 3-attempt retry loop around the snap build so transient apt mirror outages are recovered automatically instead of failing the whole release.

## [0.1.14] - 2026-05-01
- Fixed Snap launcher to also locate the Python interpreter inside the gnome-46-2404 content snap (`$SNAP/gnome-platform/usr/bin/python3*`) so the app actually starts on systems where the gnome extension prunes Python from the snap itself.
- Fixed Snap login autostart by actually generating the `linux-network-speed-indicator-autostart.desktop` file referenced by `apps.<name>.autostart` so snapd installs the autostart entry on first run.
- Trimmed the GitHub Actions `validate` job to just project validation, tests, and release archive builds; the Snap and Flatpak bundles are now built only in the release path, cutting CI time on every push and pull request.
- Marked the Snap Store listing sync step as non-fatal so an expired macaroon discharge no longer fails the release pipeline; the snap upload + tag + GitHub release still complete and a warning is surfaced in the job log.

## [0.1.13] - 2026-04-30
- Fixed Snap packaging to include the `network_speed_indicator_core.py` runtime module so installed Snap builds start correctly.
- Fixed Snap login autostart so the app writes a matching per-user desktop entry into `$SNAP_USER_DATA/.config/autostart` and uses `/snap/bin/linux-network-speed-indicator` when launched from Snap.
- Added regression coverage for Snap packaging and autostart metadata to catch these release regressions before publish.

## [0.1.12] - 2026-04-29
- Added explicit Snap `platforms` for `amd64` and `arm64` so the package can be built and published for both mainstream architectures.
- Updated the GitHub Actions release pipeline to build Snap artifacts per architecture, publish them only after both builds succeed, and keep the release/tag/listing finalization as a single gated step.

## [0.1.11] - 2026-04-29
- Fixed Flatpak dependency archive URLs so Flatpak Builder recognizes the pinned Ayatana source archives reliably in CI and release builds.
- Consolidated validation and publishing into a single GitHub Actions pipeline so release only runs after validation succeeds and only when `VERSION` changes on `main`.

## [0.1.10] - 2026-04-29
- Extracted the core network speed parsing, formatting, and config normalization logic into a GTK-free module with automated unit coverage.
- Added shared project validation for local use, CI, and release automation, and expanded CI to exercise the Snap, release-archive, and Flatpak build paths before release.
- Improved runtime diagnostics for config loading, autostart writes, and repeated update failures, and hardened Flatpak dependency sources to use reproducible archive URLs recognized by Flatpak Builder.

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
