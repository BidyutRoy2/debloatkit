# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-11-02

### Added
- `scan`, `apply`, `restore`, `inventory`, `profiles` CLI commands
- Curated package database with safe / caution / never / unknown levels
- Code-enforced never-touch list (launcher, System UI, Play services, Wi-Fi, Bluetooth)
- Mandatory backup file before any change; one-command restore
- Markdown + dark-mode-aware HTML reports
- Profiles: tv-minimal, tv-balanced, phone-minimal, aggressive
- Interactive HTML preview demo (`preview/index.html`)
- 14 unit tests (fake ADB runner, no device needed)
