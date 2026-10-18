# PenTest Terminal v2.0

A comprehensive, modular penetration testing framework designed for terminal-based security assessments. Provides an interactive CLI for network reconnaissance, port scanning, service detection, vulnerability research, and exploitation.

## 🎯 Overview

PenTest Terminal is a complete security testing platform with 18 categories and 75+ tools for:
- Network reconnaissance and enumeration
- Port scanning and service detection
- Vulnerability scanning and exploit database
- Web application testing
- OSINT and social media searching
- Payload generation and post-exploitation
- Brute force and cryptographic operations
- Fuzzing and network tools

## ✨ Features

| Category | Tools |
|----------|-------|
| **Reconnaissance** | WHOIS, DNS, Reverse DNS, GeoIP, Email Intelligence |
| **Scanning** | Port Scan, Service Detect, UDP Scan, Stealth Scan |
| **Enumeration** | Host Discovery, SMB, SNMP, Share Enumeration |
| **Exploitation** | Exploit DB, Metasploit Search, Vulnerability Matcher, Payload Generator |
| **Payloads** | Reverse Shell, Web Shell, Meterpreter, Custom Payload |
| **Post-Exploit** | Privilege Escalation, Persistence, Data Exfiltration, Cover Tracks |
| **Network Tools** | Network Mapper, Packet Sniffer, ARP Spoofing, Network Jammer |
| **Web Tools** | SQL Injection, XSS, LFI/RFI, Web Crawler |
| **OSINT** | Email Finder, Social Media Search, Domain Scraper, Metadata Extractor |
| **Vulnerability Scanner** | CVE Scanner, Weakness Finder, Configuration Audit, Compliance Check |
| **DDOS Tools** | HTTP Flood, DNS Flood, SYN Flood, UDP Flood |
| **Brute Force** | SSH, FTP, Web Form, Hash Crack |
| **Crypto** | Hash Generator, Encryption/Decryption, Encoding |
| **Fuzzing** | Protocol Fuzzer, Web Fuzzer, Binary Fuzzer, Custom Fuzzer |
| **Settings** | Target Config, Wordlists, Network Iface, Proxy |
| **Clear** | Clear screen |
| **Help** | Help system |

## 🚀 Quick Start

### Installation

```bash
cd /home/ligma/Work/Hacking
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the Application

```bash
python3 pentest_terminal.py
```

### Basic Workflow

1. Launch app → See main menu with 18 categories
2. Navigate grid with arrow keys (↑↓←→)
3. Press ENTER to enter submenu
4. Select tool from submenu
5. Execute tool or view placeholder
6. Press ESC to return to main menu
7. Press 'q' to quit anytime

## 📦 Installation & Dependencies

### Python Dependencies

```
colorama>=0.4.4
dnspython>=2.2.0
python-whois>=0.7.3
prompt_toolkit>=3.0.0
requests>=2.28.0
beautifulsoup4>=4.11.0
scapy>=2.4.5
paramiko>=2.11.0
cryptography>=3.4.8
```

### Python Version

- **Required**: Python 3.7+
- **Tested**: Python 3.14.2 (venv configured)

## 📁 Project Structure

```
pentest_terminal/
├── pentest_terminal.py       # Main application (completely redesigned v2.0)
├── requirements.txt          # Python dependencies (updated v2.0)
├── TERMINAL_README.md        # Comprehensive documentation
├── MENU_VISUAL_GUIDE.md      # Visual menu guide
├── UPDATE_SUMMARY.md         # This file - upgrade summary
├── config.conf               # Configuration file
├── .gitignore               # Git ignore patterns
├── modules/                 # Core modules package
│   ├── __init__.py
│   ├── utils.py             # Utilities & helpers
│   ├── scanner.py           # Port scanning module
│   ├── recon.py             # Reconnaissance module
│   ├── exploit.py           # Exploit database module
│   └── data/
│       └── exploits.json    # Searchable exploit database
└── .venv/                   (Virtual environment)
```

## 🎮 Navigation

### Main Menu

The main menu features a 3-column grid layout with 18 categories. Navigate using:

- **↑** - Move up (grid rows)
- **↓** - Move down (grid rows)
- **←** - Move left (grid columns)
- **→** - Move right (grid columns)
- **ENTER** - Select option / Enter submenu
- **ESC** - Go back to main menu
- **q** - Quit application

### Submenus

Each main category has a submenu with 4-5 specialized tools. ESC returns to main menu from anywhere.

## 🛠️ Available Tools

### Core Features (Ready ✅)

- **Port Scanning** - Multi-threaded TCP/UDP scanning
- **Service Detection** - Banner grabbing and service identification
- **DNS Enumeration** - A, MX, NS, TXT, CNAME, SOA record lookup
- **WHOIS Lookup** - Domain registration information
- **Host Discovery** - Ping-based active host detection
- **Exploit Database** - Searchable CVE/vulnerability database
- **Service Enumeration** - Common service banner grabbing

### Placeholder Features (🔄 Coming Soon)

All advanced features are marked as "Coming Soon" and can be easily implemented by:
1. Adding to submenu in `MenuNavigator._init_submenus()`
2. Creating handler in `PentestTerminal` class
3. Adding to handlers dict in `handle_selection()`
4. Implementing functionality or using `_show_placeholder()`

## 📚 Documentation

- **TERMINAL_README.md** - Comprehensive documentation
- **MENU_VISUAL_GUIDE.md** - Visual menu layout and examples
- **UPDATE_SUMMARY.md** - upgrade history and changes
- **PROJECT_SUMMARY.md** - Project technical details

## 🔧 Customization

### Add New Tool

1. Add to submenu in `MenuNavigator._init_submenus()`
2. Create handler in `PentestTerminal` class
3. Add to handlers dict in `handle_selection()`
4. Implement functionality or use `_show_placeholder()`

### Modify Menu Layout

- Change `cols = 3` in `MenuNavigator.__init__()` for different grid sizes
- Edit `menu_items` list to reorder or rename categories
- Customize colors in the code (search for `Fore.` constants)

### Customize Colors

```python
# Current color scheme
Fore.RED    # Branding, warnings
Fore.GREEN  # Success
Fore.CYAN   # Selection, tools
Fore.YELLOW # Prompts, info
```

## 📊 Version History

- **v2.0** (Feb 2026) - Complete redesign with grid menu, 18 categories, 75+ tools, ESC support
- **v1.0** (Earlier) - Basic command interface with 9 tools

## ⚠️ Legal & Ethical

**⚠️ For authorized security testing only.** This tool is designed for authorized penetration testing and security research.

- Always obtain written permission before testing any systems you do not own
- Unauthorized access is illegal in most jurisdictions
- Document all testing activities
- Maintain detailed logs (automatically created)
- Follow responsible disclosure practices

## 🎉 Status

**Version**: v2.0  
**Status**: ✅ Ready to Use  
**Last Updated**: February 9, 2026  
**Total Lines of Code**: 900+  
**Categories**: 18  
**Tools**: 75+  

🎉 **Enjoy your new PenTest Terminal!**

## 📄 License & Disclaimer

This project is provided **as-is** for educational and authorized security testing purposes.

**⚠️ DISCLAIMER**: Unauthorized access to computer systems is illegal. Users are solely responsible for ensuring their use of this tool complies with all applicable laws and regulations. The authors assume no liability for misuse.

---

*For questions, issues, or feature requests, check the documentation files or review the code comments.*