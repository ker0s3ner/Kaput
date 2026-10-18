# Kaput

Kaput is an experimental, menu-driven Python toolkit for security research
and authorized assessment. It brings together reconnaissance,
network scanning, enumeration, web testing, OSINT, fuzzing, cryptography, and
other utilities in one terminal application.

The project is a collection of modules at different stages of development. Some
features perform real network or local operations; others are demonstrations,
stubs, or incomplete integrations. Treat results as unverified and review the
relevant implementation before relying on a tool.

## Requirements

- Python 3.9 or newer
- A POSIX terminal (Linux or macOS) for the interactive menu
- The Python packages listed in [`requirements.txt`](./requirements.txt)

Some operations require network access. Packet capture and certain network
features may require additional operating-system permissions or tools.

## Installation

From the repository directory, create and activate a virtual environment, then
install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run

```bash
python pentest_terminal.py
```

The application opens an interactive menu. Use the arrow keys to move through
the menu, press Enter to select an item, and press `q` to quit. In a submenu,
use `Esc` to return to the main menu. Set a target from **Settings** before
using tools that depend on the saved target.

The application stores its target and preferences in `settings.json` beside
the application code and writes its log to `logs/pentest_terminal.log`.
These files are created at runtime and are not required in advance.

## What is included

The current main menu contains these sections:

| Section | Examples of functionality in the repository |
| --- | --- |
| Reconnaissance | Combined lookup, WHOIS, DNS and reverse DNS lookups, GeoIP, and contact or profile searches |
| Scanning | TCP and UDP port checks, service detection, host discovery, and enumeration |
| Exploitation | Exploit reference data, vulnerability matching, and device/payload demonstrations |
| Network Tools | Network mapping, packet capture, HTTP parameter checks, and network utilities |
| Brute Force | SSH, FTP, web-form, and hash-cracking modules |
| Crypto Tools | Hash generation, text encryption/decryption, and encoding |
| Post-Exploit | Experimental post-exploitation demonstrations |
| Fuzzing | Web, protocol, and custom fuzzing modules |
| Settings | Target, wordlist, network interface, proxy, and optional AI model settings |
| Clear, Help, Exit | Screen clearing, in-app navigation help, and application exit |

Other code is available as modules even if it is not exposed as a dedicated
menu item. The repository includes code for HTTP tools, vulnerability and
configuration checks, service enumeration, device utilities, and OSINT
platform data. The local AI integration uses an Ollama server on the same
machine; Ollama is optional and is not installed by `requirements.txt`.

### Implementation status

The menu is not a guarantee that every item performs the action its label
suggests. Some handlers are functional integrations, while others return
placeholder output or simulate behavior. For example, the SYN-style scan is
explicitly simulated; some payload and post-exploitation screens report
success without carrying out the described operation. Check the relevant
handler and module before using a result or assuming an action occurred.

There is no automated test suite in the repository at this time.

## Repository layout

```text
.
├── pentest_terminal.py       # Interactive application and menu handlers
├── sploiter.py               # Alternate/older application entry point
├── patch_handlers.py         # Source-editing utility
├── config.conf               # Example settings; not loaded by the main app
├── requirements.txt          # Python dependencies
├── modules/
│   ├── bruteforce.py
│   ├── crypto_tools.py
│   ├── device_tools.py
│   ├── enumeration.py
│   ├── exploit.py
│   ├── fuzzer.py
│   ├── http_tools.py
│   ├── intel.py
│   ├── local_ai.py
│   ├── network_tools.py
│   ├── osint.py
│   ├── platforms.py
│   ├── recon.py
│   ├── scanner.py
│   ├── utils.py
│   ├── vuln_scanner.py
│   └── data/
│       └── exploits.json    # Local exploit-reference data
└── logs/                     # Runtime logs
```

## Responsible use

Use this software only on systems, networks, accounts, and data that you own
or are explicitly authorized to assess. Some modules can send traffic, attempt
authentication, capture packets, or interact with third-party services. Obtain
permission, define an approved scope, and comply with applicable laws and
service terms before running them. Do not treat this project as a substitute
for a reviewed security tool or a professional assessment.
