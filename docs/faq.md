# FAQ

See also the FAQ section in the README.

## Do I need root?
No. ADB + `pm disable-user` works without root on stock devices.

## Does disabling apps free storage?
Mostly it frees RAM and stops background activity; system apps still occupy
the system partition. The visible win is a cleaner home screen, faster boot
to a usable launcher, and fewer background preloads — not gigabytes of space.

## Can I debloat a Fire TV / other Android TV forks?
If it exposes ADB over Wi-Fi and uses standard package names, yes — but
fork-specific launchers may be named differently and will show as `unknown`
until classified. Report them via an issue.

## Is my data sent anywhere?
No. debloatkit has no telemetry, no accounts, and no network code beyond
the ADB connection you start yourself.

## How do I update the package database?
Pull the latest release and re-run `scan` — your old backup files still work
with `restore`, because restore only needs the package list.
