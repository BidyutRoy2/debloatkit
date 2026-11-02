# Security Policy

## Reporting

If debloatkit ever disables something it shouldn't, or a command could
affect a device beyond the documented `pm disable-user` / `pm enable`
calls, open an issue with the label `security` — or, if it involves a
bypass of the never-touch list, open a private security advisory instead.

## Scope notes

- debloatkit runs ADB commands you initiate against an IP you type. It
  never scans networks, never guesses addresses, and never phones home.
- ADB over Wi-Fi trusts your local network. Only run debloatkit on Wi-Fi
  networks you trust, and disable wireless debugging when you're done.
- Supported versions: the latest release only; package-database fixes are
  backported when they change a risk level.
