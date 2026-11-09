# NetWatch project audit and baseline plan

Audit date: 10 November 2026
Project title in the corrected proposal: End User Network Monitoring System for Small Scale Network

## 1. Materials reviewed

| Material | Audit use and current status |
|---|---|
| `netwatch_v3/netwatch/` | Current source snapshot; read the README, Python modules, profile settings, and dashboard template. No database, Git metadata, evidence folder, deployment guide, or test-result log was present in this folder. |
| `FYP FORMAT (old).pdf` | UiTM format guide dated 2015. Useful as a provisional reference only; it cannot establish the current required format. |
| `MuhammadZailan_FullReport (fyp format new).pdf` | Completed example with five chapter-style content and implementation/testing sections. It is an example, not an official template; its system and claims must not be copied. |
| `CSP600_FinalProposal_Naqish_Corrected_NetWatch.docx` | Corrected proposal. Contains the current title, objectives, scope, two scenarios, intended indicators, and proposed evaluation metrics. It remains a proposal, so proposed behavior is not evidence of implementation. |
| `FYP_Naqish_Ch1_3_Corrected_FINAL.pdf` | Related FYP1 report located in Downloads and reviewed as supplemental project history. It has Chapters 1–3 and the same project title, but its Scenario A is a distance variation; the corrected proposal now describes Scenario A as baseline monitoring. |
| `A_Raspberry_Pi-Based_Framework_for_Network_Securit.pdf` | Anchor paper located in Downloads and reviewed. Published 31 December 2025 in *PLATFORM: A Journal of Science & Technology*, Volume 8, Number 2, pages 11 onward; DOI 10.61762/pjstvol8iss2art002. |
| Pasted project handover | Treated as the user's requested mission and workflow. Its embedded claims about earlier tests and features were checked against this source snapshot rather than assumed true. |

No separate supervisor feedback file or current official report template was in the named materials. The project handover describes supervisor requirements, but those descriptions are not a written supervisor record.

## 2. Academic baseline and conflicts

### Current proposal baseline

The corrected proposal defines the project as a Raspberry Pi-based web monitoring and alert system for a small LAN. Its three objectives are to:

1. Collect latency, packet loss, host availability, connected device count, and selected open-port status using a Raspberry Pi monitoring agent.
2. Display those indicators and alert history in a web dashboard.
3. Evaluate monitoring accuracy, dashboard update time, Telegram alert delivery time, false-alert observations, and user usability feedback.

Its Scenario A is baseline monitoring and dashboard validation. Scenario B introduces controlled abnormal conditions and checks database recording, dashboard updates, and Telegram notifications. The proposal also discusses remote dashboard access through a private VPN.

### Anchor paper findings relevant to NetWatch

The paper describes a Raspberry Pi 400 and TP-Link AC1200 isolated LAN; a Node-RED dashboard; Nmap host/port discovery; ping-based host health and latency; ifstat bandwidth monitoring; and SYN flood, TCP port scan, and honeypot scenarios. It uses Agile SDLC and reports resource-constrained monitoring. These are the paper's methods, not NetWatch's current methods.

NetWatch can adapt the paper's small-LAN topology, periodic reachability and latency measurements, dashboard validation, and controlled scenario-based evaluation. The paper's attack simulations should not be described as NetWatch tests unless the approved project scope is explicitly changed. A controlled host outage, packet-loss condition, or threshold crossing is a closer fit to NetWatch's current monitoring objectives. Differences in hardware (Pi 3 Model B+ vs Pi 400), framework (Flask vs Node-RED), and test scenarios must be stated in the final report.

### Format conflict

The supplied format PDF is explicitly marked old and contains 2015 guidance. It specifies English, at least 50 pages excluding appendices, Times New Roman 12 point body text, bold 14 point headings, 3 cm top / 4 cm left / 2.5 cm right / 2 cm bottom margins, 1.5 line spacing, a 250–300 word abstract, five main chapters, front matter, APA-style references, and optional appendices. The example follows a newer-looking five-chapter structure but is not a normative document. Obtain the current UiTM template or written supervisor confirmation before final formatting.

The old FYP1 report's Scenario A (varying Raspberry Pi/router distance) differs from the corrected proposal's baseline Scenario A. The corrected proposal is newer and should be the working baseline pending supervisor confirmation.

## 3. Current software audit

### Present in source

- Flask dashboard with `/` and `/api/status` routes.
- A separate polling monitor for ping, TCP connect checks, ARP-table parsing, SQLite writes, and threshold alerts.
- Three network profiles (`campus`, `hotspot`, `pdanet`) with target lists.
- SQLite tables: `readings`, `alerts`, `device_scans`, and `port_checks`.
- Threshold alerts for host-down, high latency, packet loss, and expected-open ports that are closed.
- Optional Telegram send path controlled by environment variables.
- A one-page dashboard template and a script named `test_scenarios.py`.

### Missing or unverified against the proposal/handover

- No six claimed simulation modes, simulated-data labeling, or simulation-to-alert workflow.
- No unknown-device detection or registered-device baseline.
- No explicit port-change detection; current logic checks only configured ports and alerts when one is closed.
- ARP parsing reads the local neighbor cache; it does not actively discover all devices on a subnet. The profiles' subnet field is not used by the scan.
- Device scans store snapshots, but the code does not compare snapshots to find newly appeared devices.
- No `monitoring_cycles` table or earlier named `devices`, `measurements`, `host_status`, and `port_status` tables in this database schema. No pre-existing database file was present to inspect or migrate.
- No authentication is visible in the Flask app, which binds to `0.0.0.0`. Remote use must stay behind an appropriately restricted private network; do not expose this dashboard via public port forwarding without an access-control design.
- The monitor's alert-active state is held only in memory and resets on restart.
- `test_scenarios.py` is a manual live-network script, not a unit/integration test suite. Its Scenario B times a direct ping loop; it does not exercise the regular monitor cycle, call alert logic, persist the fault result, or measure Telegram delivery.
- The repository contains no actual test-results log, screenshots, deployment evidence, or report Chapters 4 and 5.

### Checks performed

- Parsed all project Python files with Python's AST parser: syntax parsing succeeded for each file.
- The bundled Python runtime does not have Flask installed. This says nothing about other Python environments on the user's machine or Raspberry Pi.
- `test_scenarios.py` ran from an isolated source copy on the Windows development host. The configured campus gateway `10.0.0.1` failed; Google DNS replied at 61 ms / 0% loss; Cloudflare DNS replied at 93 ms / 0% loss; ARP parsing returned one neighbor. This was one live run, not Pi evidence.
- `monitor.py --once` then ran in the same isolated copy with Telegram disabled. The campus gateway failure, two DNS responses, and one ARP neighbor were written to SQLite; a `host_down` alert row persisted. No ports were checked because the campus profile has none configured.
- Isolated Flask/SQLite checks passed for `/`, `/api/status`, database writes/reads, and latency history using a temporary database.
- A mocked host-down/recovery check passed: the alert and resolution were stored; no network or Telegram call was made.
- Development-host runtime behavior is verified for one polling cycle and the isolated dashboard/database/alert checks only. Raspberry Pi deployment and sustained monitoring remain unverified.

## 4. Gap analysis

| Area | Current evidence | Gap / next evidence needed |
|---|---|---|
| Academic requirements | Corrected proposal; old UiTM guide; example report | Current official template, final supervisor instructions, confirmation of final scope and Scenario A/B. |
| Software | Small Flask/SQLite monitor snapshot | Runtime verification; testable modules; unknown-device/port-change behavior or proposal scope adjustment; better test coverage. |
| Hardware | Proposal and handover specify Pi 3 Model B+ | Confirm actual Pi, OS, SD card/network access, and deployment availability; no hardware evidence is present. |
| Monitoring methodology | Ping/ARP/TCP-connect code | Define targets, sample counts/durations, thresholds, ground-truth comparison, false-alert method, update-time measurement, and controlled conditions. |
| Alerts | Telegram API path exists in code | Safe configuration and end-to-end delivery evidence; current script does not measure phone delivery. |
| Database | Four-table schema in code | Create a safe test database, verify persistence/restart behavior and retention; decide whether schema changes are needed. |
| Report | FYP1 Chapters 1–3 and corrected proposal | Align/revise Chapters 1–3; write implementation/results/conclusion only after verified evidence; apply current template. |
| Evidence | None found in project tree | Capture genuine dashboard, database, test logs, Pi deployment, and alert evidence when runs occur. |
| Risks | Campus/hotspot/PdaNet profiles in README | Client isolation, changing IPs, ARP-cache limits, ICMP/network restrictions, no dashboard authentication, Telegram outage, and unconfirmed Pi availability. |

## 5. Completion plan, ordered by dependency

1. **Close the audit and confirm the baseline:** obtain the current UiTM template and latest supervisor feedback; map the corrected proposal and old report; settle Scenario A/B and exact evaluation metrics.
2. **Establish a reproducible software environment:** install only project dependencies in an isolated environment; inspect the actual dashboard and database behavior; run safe, clearly scoped tests; preserve any existing data.
3. **Repair only demonstrated gaps:** prioritize correctness of data parsing, persistence, detection behavior, alert state, and automated tests. Avoid adding attack detection, machine learning, or other out-of-scope features.
4. **Deploy to the approved Pi 3 Model B+:** configure the network profile and service startup, keep dashboard access private, and capture genuine deployment evidence.
5. **Execute the two scenarios:** collect baseline readings and controlled fault results; compare against a reference tool; record detection and dashboard update times separately from Telegram delivery; report limitations.
6. **Complete the report alongside verified results:** revise Chapters 1–3; write Chapters 4–5; complete front matter, references, appendices, figures/tables, and formatting from the confirmed official template.
7. **Prepare review/demo materials:** repeatable demo sequence, concise architecture/method explanation, test evidence index, known limitations, and questions requiring supervisor confirmation.

## 6. Immediate blockers and next action

Write access to the supplied source folder was granted for this turn. The requested `PROJECT_STATUS.md`, `DEVELOPMENT_LOG.md`, `TEST_PLAN.md`, `TEST_RESULTS.md`, `DEPLOYMENT_GUIDE.md`, `SYSTEM_ARCHITECTURE.md`, `REPORT_PROGRESS.md`, and `KNOWN_LIMITATIONS.md` were created in the project folder; the existing README was preserved. The anchor paper was found locally; no external contact was made.

## 7. Updates after the initial audit

The `test_scenarios.py` Scenario B was not run because it requires a manually induced real fault. Do not count it as passed.

