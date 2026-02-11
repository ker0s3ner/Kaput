# PENTEST TERMINAL v2.0 - All-In-One Security Testing Platform

## Overview
The Pentest Terminal has been completely redesigned to be an all-in-one comprehensive security testing platform combining the functionality of Metasploit, Nmap, OSINT tools, and DDOS utilities into a single unified dashboard.

## New Features

### 1. **Grid-Based Menu System**
- Navigate using arrow keys (↑↓←→) for intuitive 3-column grid layout
- Current selection highlighted with checkmark `[✓]`
- Unselected options shown as `[ ]`
- Much more visually appealing and organized

### 2. **ASCII Cat Logo**
- Cool ASCII cat mascot at the top of the main menu
- Adds visual appeal to the interface

### 3. **Submenu System**
- Press Enter on a category to see available tools
- Each category has 4+ specialized tools
- Press ESC to return to main menu (new feature!)

### 4. **18 Major Tool Categories**

#### **Reconnaissance** (OSINT & Information Gathering)
- WHOIS Lookup
- DNS Enumeration
- Reverse DNS Lookup
- GeoIP Lookup

#### **Scanning** (Port & Service Discovery)
- Port Scan (all TCP/UDP variations)
- Service Detection
- UDP Scan
- Stealth Scan

#### **Enumeration** (Service Enumeration)
- Host Discovery
- SMB Enumeration
- SNMP Enumeration
- Share Enumeration

#### **Exploitation** (Exploit Management)
- Exploit Database Search
- Metasploit Integration
- Vulnerability Matcher
- Payload Generator

#### **Payloads** (Payload Generation)
- Reverse Shell Generator
- Web Shell Generator
- Meterpreter Payload
- Custom Payload Builder

#### **Post-Exploit** (Post-Exploitation)
- Privilege Escalation
- Persistence Mechanisms
- Data Exfiltration
- Cover Tracks

#### **Network Tools** (Network Attacks)
- Network Mapper (enhanced nmap)
- Packet Sniffer
- Network Jammer
- ARP Spoofing

#### **Web Tools** (Web Application Testing)
- SQL Injection Tester
- XSS Detector
- LFI/RFI Scanner
- Web Crawler

#### **OSINT** (Open Source Intelligence)
- Email Finder
- Social Media Search
- Domain Scraper
- Metadata Extractor

#### **Vulnerability Scanner** (Vuln Detection)
- CVE Scanner
- Weakness Finder
- Configuration Audit
- Compliance Check

#### **DDOS Tools** (Network Testing)
- HTTP Flood
- DNS Flood
- SYN Flood
- UDP Flood

#### **Brute Force** (Dictionary Attacks)
- SSH Brute Force
- FTP Brute Force
- Web Form Attack
- Hash Cracker

#### **Crypto Tools** (Cryptography)
- Hash Generator
- Hash Cracker
- Encryption Tool
- Decryption Tool

#### **Fuzzing** (Fuzz Testing)
- Protocol Fuzzer
- Web Fuzzer
- Binary Fuzzer
- Custom Fuzzer

#### **Settings** (Configuration)
- Set Target (IP/Domain)
- Configure Wordlists
- Network Interface Selection
- Proxy Settings

## Navigation Controls

| Key | Action |
|-----|--------|
| ↑ | Move up (grid: rows) |
| ↓ | Move down (grid: rows) |
| ← | Move left (grid: columns) |
| → | Move right (grid: columns) |
| Enter | Select option/Enter submenu |
| ESC | Go back to main menu |
| 'q' | Quit application |

## Usage

### Running the Tool
```bash
python3 pentest_terminal.py
```

### Basic Workflow
1. Launch the application
2. Use arrow keys to navigate the 3-column grid menu
3. Press Enter to select a category (enters submenu)
4. Navigate the submenu with ↑↓ keys
5. Press Enter to select a tool
6. Tool will execute (either interactive or placeholder)
7. Press ESC or complete tool to return to main menu
8. Press 'q' at any time to quit

### Example: Running Port Scan
1. Launch `python3 pentest_terminal.py`
2. Navigate to "Scanning" (right arrow)
3. Press Enter to enter Scanning submenu
4. Navigate to "Port Scan" (down arrow)
5. Press Enter to execute
6. Enter target IP and port range
7. Press ESC to return to main menu

## Features Roadmap

### Currently Implemented
- ✅ Menu system with grid layout
- ✅ Submenu navigation
- ✅ Target setting
- ✅ Basic port scanning
- ✅ DNS enumeration
- ✅ WHOIS lookup
- ✅ Host discovery
- ✅ Service enumeration
- ✅ Exploit database search

### Planned (Placeholders Ready)
- 🔲 Metasploit integration
- 🔲 Advanced vulnerability scanning
- 🔲 DDOS simulation tools
- 🔲 Web application testing suite
- 🔲 Payload generation engine
- 🔲 Hash cracking tools
- 🔲 Network sniffing
- 🔲 OSINT automation
- 🔲 Much more...

## System Requirements
- Python 3.7+
- Linux/Unix terminal (tested on Bash/Zsh)
- Root/sudo access for some features
- 500MB+ free space

## Dependencies
```
colorama>=0.4.4
dnspython>=2.2.0
python-whois>=0.7.3
```

Install with:
```bash
pip install -r requirements.txt
```

## Disclaimer

⚠️ **IMPORTANT**: This tool is designed for authorized security testing and penetration testing on systems you own or have explicit written permission to test. 

**Unauthorized access to computer systems is illegal.** By using this tool, you agree to:
- Only test systems you own
- Have written authorization before testing third-party systems
- Follow all applicable laws and regulations
- Use this tool responsibly and ethically

The developers assume no liability for misuse or damage caused by this tool.

## Architecture

```
pentest_terminal.py
├── MenuNavigator: Grid-based menu navigation
│   ├── Main menu (3-column grid)
│   ├── 15 submenus with specialized tools
│   └── Escape key handling
│
└── PentestTerminal: Tool execution engine
    ├── Reconnaissance tools
    ├── Scanning tools
    ├── Enumeration tools
    ├── Exploitation tools
    ├── Network tools
    ├── Web testing tools
    ├── OSINT tools
    └── Many more...
```

## Color Scheme
- 🔴 Red: Branding, important info
- 🟢 Green: Success messages
- 🔵 Cyan: Menu selection, tool names
- 🟡 Yellow: Warnings, user prompts

## Contributing

To add new tools:
1. Add submenu item in `MenuNavigator._init_submenus()`
2. Create handler method in `PentestTerminal`
3. Add handler to `handle_selection()` method
4. Implement or create placeholder

## Future Enhancements
- Database support for scan results
- Multi-threaded scanning
- Result export (JSON, HTML, CSV)
- Advanced filtering and searching
- Custom tool plugins
- Wordlist management
- Session saving/loading
- Automated reporting

---

**Version**: 2.0  
**Last Updated**: February 2026  
**Status**: Actively Developed
