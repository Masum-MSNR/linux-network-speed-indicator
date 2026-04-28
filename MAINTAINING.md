# Maintaining Linux Network Speed Indicator

## Repository Layout

```text
linux-network-speed-indicator/
├── assets/
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
4. Create a tag like `v0.1.0`
5. Push branch and tags

Example:

```bash
git add .
git commit -m "Release v0.1.0"
git tag v0.1.0
git push origin main --tags
```

## GitHub Actions

- `ci.yml` validates Python, shell scripts, JSON, and Debian package creation.
- `release.yml` builds `.deb`, `.zip`, and `.tar.gz` artifacts and publishes them on version tags.

## Semantic Versioning

- `MAJOR`: breaking changes
- `MINOR`: new features
- `PATCH`: fixes and small improvements

Current version is stored in `VERSION`.