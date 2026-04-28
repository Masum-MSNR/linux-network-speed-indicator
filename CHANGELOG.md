# Changelog

All notable changes to this project should be documented in this file.

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
