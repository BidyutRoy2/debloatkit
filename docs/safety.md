# Safety model

debloatkit is designed so the worst case is "an app you wanted is disabled",
never "the device won't boot". The layers, in order:

1. **Never-touch list (code-enforced).** `debloatkit/packages.py` defines
   `NEVER_TOUCH`. `plan()` never puts these in the action list, and `apply`
   re-checks every package at apply time. There is no flag to override this.
2. **Disable, don't uninstall.** System apps are disabled via
   `pm disable-user --user 0`, which Android can always reverse. Nothing is
   deleted from the system partition.
3. **Mandatory backup.** `apply` requires `--backup`. The file records the
   device, profile, and exact package list.
4. **Dry-run default.** Without `--yes`, `apply` and `restore` only print
   what they would do.
5. **Unknown packages are never touched.** If a package isn't classified,
   it appears in the report as `unknown` and nothing happens to it.
6. **Same-network only.** debloatkit connects to an IP you type, on your own
   Wi-Fi. It never scans networks or guesses addresses.

## What to do if something feels wrong

1. Run `restore` with your backup file.
2. If ADB is unreachable, reboot the TV and try again.
3. Last resort: factory reset from the TV's Settings or recovery menu —
   this restores all preloaded apps.

## What debloatkit will never do

- Uninstall system packages, modify the system partition, or require root.
- Touch the launcher, System UI, Play services, Bluetooth, or Wi-Fi stacks.
- Send data anywhere: there is no network code except the ADB connection
  you initiate, and no telemetry of any kind.
