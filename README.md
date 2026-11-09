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
2-second timeout. True/false open, logged every round, alerts if a port
that should be open isn't.

## Tailscale (remote access without port forwarding)

1. Install Tailscale on the Pi and on your laptop/phone:
   https://tailscale.com/download
2. `sudo tailscale up` on the Pi, sign in, same account on your other device.
3. Both devices now have a `100.x.x.x` Tailscale IP. Visit
   `http://<pi-tailscale-ip>:5000` from anywhere, no router config needed.
4. Worth noting in your report: Tailscale is a WireGuard mesh VPN, so traffic
   to your dashboard is encrypted end to end even over the public internet.

## Evaluation scenarios

`python test_scenarios.py` runs Scenario A (normal conditions, checks every
target reads up with acceptable loss) and Scenario C (device discovery).
Scenario B (induced fault) is interactive - it waits for you to break a
host's connectivity, then times how long NetWatch takes to detect it. Run it
with:
```
python -c "import test_scenarios as t; t.scenario_b_induced_fault()"
```
Ways to induce a fault: unplug a device, block it with
`sudo iptables -A OUTPUT -d <ip> -j DROP` (undo with `-D` instead of `-A`),
or add traffic shaping for packet loss:
`sudo tc qdisc add dev eth0 root netem loss 30%` (undo:
`sudo tc qdisc del dev eth0 root`).

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
