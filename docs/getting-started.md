# Getting started

## 1. Install ADB (platform-tools)

- **macOS:** `brew install android-platform-tools`
- **Windows:** download platform-tools from developer.android.com, unzip, add to PATH
- **Linux (Debian/Ubuntu):** `sudo apt install android-tools-adb`
- Verify: `adb version`

## 2. Enable wireless debugging on the device

**Google TV / Android TV:**
Settings → System → About → click "Build" 7 times (Developer options appear),
then Settings → System → Developer options → enable **Wireless debugging**
(or **USB debugging** on older versions).

**Phone/tablet:** Settings → About phone → tap "Build number" 7 times,
then Developer options → **Wireless debugging**.

Note the device IP: Settings → Network → your Wi-Fi network → IP address.

## 3. Install debloatkit

```bash
pip install debloatkit
# or, without installing: python -m debloatkit scan --host <IP>
```

## 4. Scan, review, apply, restore

```bash
debloatkit scan --host 192.168.1.50 --report report.html
debloatkit apply --host 192.168.1.50 --backup backup.json --yes
debloatkit restore --host 192.168.1.50 --backup backup.json --yes
```

If `adb connect` fails, make sure the phone/PC and TV are on the same Wi-Fi
network and that you accepted the "Allow wireless debugging?" prompt on the TV.
