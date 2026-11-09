# NetWatch

Ping monitoring, device discovery, port checks, SQLite storage, a live
dashboard, and Telegram alerts. Built for exactly your situation: no home
router of your own, just campus wifi, a phone hotspot, and PdaNet at
different times. A "network profile" system lets you switch between them
with one command instead of hand-editing IPs every time you move.

## First-time setup (do this once)

1. Install Python 3 if you don't have it, then:
   ```
   pip install flask
   ```
   On Raspberry Pi OS, if that fails: `sudo apt install python3-flask`

2. Unzip this project somewhere, e.g. `~/netwatch`, and `cd` into it.

## Every time you change networks

NetWatch ships with three profiles in `profiles/`: `campus`, `hotspot`,
`pdanet`. Each one just holds a gateway IP, a subnet, and a target list -
nothing else changes.

1. Connect to the network as normal (join campus wifi, or turn on your
   phone's hotspot, or start PdaNet).
2. Find your gateway IP:
   - Linux/Pi/Mac: `ip route | grep default`
   - Windows: `ipconfig` → look for "Default Gateway"
3. The first time you use a profile, open `profiles/<name>.py` and paste
   that gateway IP into `GATEWAY` (and `LAN_SUBNET` if you know it - it's
   only used as a note to yourself, not required for the scan to work).
   You only need to do this once per network; it won't change again unless
   the network itself changes its addressing.
4. Tell NetWatch which profile to use:
   ```
   python switch_network.py campus
   ```
   or `hotspot` or `pdanet`. Run with no argument to check which one is
   currently active.

## Run it

1. Terminal 1:
   ```
   python monitor.py
   ```
2. Terminal 2:
   ```
   python app.py
   ```
3. Open http://localhost:5000 in a browser. The page header shows which
   profile is active, so you always know what you're looking at.
   - From another device on the same network (e.g. your phone on the same
     hotspot as the Pi): `http://<pi-ip>:5000`

`python monitor.py --once` runs a single round of everything immediately,
useful for testing without waiting for the loop.

## Controlled simulation scenarios

Run an offline scenario to exercise NetWatch's recording and alert paths without probing a real network. Simulation records are labelled in SQLite and in the dashboard; simulated alerts never send Telegram messages.

```powershell
py simulate.py NORMAL
py simulate.py HIGH_LATENCY
py simulate.py PACKET_LOSS
py simulate.py HOST_DOWN
py simulate.py UNKNOWN_DEVICE
py simulate.py PORT_CHANGE
```

Each scenario writes to its own `netwatch_simulation_<scenario>.db` by default, separate from live `netwatch.db`. For example, view the high-latency run:

```powershell
$env:NETWATCH_DB_PATH = "$PWD/netwatch_simulation_high_latency.db"
py app.py
```

These scenarios verify software responses; they are not real network measurements or Raspberry Pi field results. `PORT_CHANGE` seeds an open-port baseline and submits a closed state. `UNKNOWN_DEVICE` submits a synthetic MAC address. For live unknown-device alerts, add trusted MAC addresses to `KNOWN_DEVICE_MACS` in the active network profile. Until that list is populated, every discovered MAC is treated as unregistered.

## What to expect differently per network

- **Campus wifi**: internet targets (Google DNS, Cloudflare DNS) work
  normally. Device discovery will likely show very few devices even though
  many people are connected - most campus wifi enforces **client
  isolation**, which blocks devices on the same wifi from seeing each
  other, for security. This is the network's policy, not a fault in your
  code. Mention this in your report's limitations section rather than
  spending time trying to "fix" it.
- **Phone hotspot / PdaNet**: this is your own private network, so you're
  the only device on it (plus whatever you connect) and device discovery
  will show exactly what's there - no isolation issue.
- **IP addresses change every time you switch networks.** This is normal
  and expected; it's exactly why the profile system above exists, and why
  Tailscale (below) is worth setting up if you want one fixed address that
  works no matter which of the three networks you're on.

## What each file does

- `config.py` - every setting you're likely to change
- `db.py` - all SQLite reads/writes, one schema shared by monitor and app
- `monitor.py` - the background agent: ping, device scan (via `arp`), port
  checks, and alert logic
- `app.py` + `templates/index.html` - the Flask dashboard
- `test_scenarios.py` - scripted tests for your evaluation chapter
- `simulate.py` - labelled, offline abnormal-condition scenarios

## Telegram setup (10 minutes)

1. In Telegram, message **@BotFather**, send `/newbot`, follow the prompts,
   copy the token.
2. Open a chat with your new bot and send it any message.
3. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser.
   Find `"chat":{"id":123456789` - that number is your chat id.
4. Set both as environment variables before running the monitor:
   - Linux/Pi/Mac: `export NETWATCH_BOT_TOKEN="..."` and
     `export NETWATCH_CHAT_ID="..."`
   - Windows PowerShell: `$env:NETWATCH_BOT_TOKEN="..."` and
     `$env:NETWATCH_CHAT_ID="..."`

## Device discovery

Uses `arp -a` (Windows) / `arp -an` (Linux/Pi/Mac) to list devices that have
recently talked to this machine on the LAN. This needs no special
privileges, unlike `nmap -sn`, which generally needs sudo for a full sweep.
Trade-off worth a line in your report: `arp` only shows devices this
machine has already exchanged packets with. If the list looks short the
first time, ping the subnet broadcast address once (or just wait - normal
traffic fills the ARP cache within a minute or two) and rescan.

## Port checks

A plain TCP connect to each `(address, port)` pair in `WATCHED_PORTS`,
2-second timeout. Open/closed states are stored; changes are alerted after an
initial baseline exists. Configure only services on networks you administer.

## Tailscale (remote access without port forwarding)

1. Install Tailscale on the Pi and on your laptop/phone:
   https://tailscale.com/download
2. `sudo tailscale up` on the Pi, sign in, same account on your other device.
3. Both devices now have a `100.x.x.x` Tailscale IP. Visit
   `http://<pi-tailscale-ip>:5000` from anywhere, no router config needed.
4. Worth noting in your report: Tailscale is a WireGuard mesh VPN, so traffic
   to your dashboard is encrypted end to end even over the public internet.

## Evaluation scenarios

`python test_scenarios.py` records Scenario A (baseline checks) and Scenario C
(cached-neighbor discovery). Scenario B is an interactive controlled loss and
recovery test. Choose a reachable test device you administer; do not disrupt a
gateway, public host, or another user's device. Run it with a configured local
target name:
```
python -c "import test_scenarios as t; t.scenario_b_induced_fault('YOUR_TEST_HOST')"
```
Temporarily disconnect the authorized test device or stop its network
connection, then restore it when prompted. The script persists readings and
alerts. Measure detection and recovery separately from Telegram delivery.

Report two numbers separately:
- **Detection time**: what the script measures (time from fault to NetWatch
  marking the host down).
- **Alert delivery time**: time until the Telegram message actually appears
  on your phone, timed by hand for a few runs. `telegram_delay_ms` in the
  `alerts` table is only the time for Telegram's API to accept the message,
  not the time it takes to reach your phone - say this explicitly if you
  quote both figures, so they aren't confused.

## Known limitations (worth a paragraph in your report)

- If the internet itself is down, a Telegram alert can't be delivered until
  it comes back - alerts are saved to SQLite regardless, but Telegram
  delivery is best-effort.
- Device discovery via `arp` only sees devices that have communicated
  recently; it is not an active network sweep.
- Port checks confirm TCP connectivity, not that the service behind the
  port is actually healthy.
