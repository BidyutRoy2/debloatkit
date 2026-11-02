# Contributing

## Package-database entries (most welcome!)

See `docs/package-database.md` for the format. Include the exact package
name, device model + OS version, what the app does, and what broke (or
didn't) when disabled manually. `safe` needs a clear reason core functions
can't be affected.

## Code

- Python 3.9+, zero dependencies — keep it that way.
- Run `python -m unittest discover -s tests -t .` before opening a PR.
- New behavior needs a test (see `tests/` — a fake ADB runner is provided).
- Never add a flag that bypasses the never-touch list.

## Release checklist

1. Bump `__version__` and `pyproject.toml`.
2. Update CHANGELOG.md.
3. Run the full test suite.
