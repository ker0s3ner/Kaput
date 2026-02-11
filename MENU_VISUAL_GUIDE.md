# PENTEST TERMINAL v2.0 - Visual Guide

## Main Menu Layout

```
    /\_/\
   ( o.o )
    > ^ <
   /|   |\
  (_|   |_)

╔═══════════════════════════════════════════════════════════════════╗
║              PENTEST TERMINAL v2.0 - All-In-One Tools             ║
║          Metasploit + Nmap + OSINT + Exploitation Combined        ║
╚═══════════════════════════════════════════════════════════════════╝

[✓] Reconnaissance    [ ] Scanning           [ ] Enumeration
[ ] Exploitation      [ ] Payloads           [ ] Post-Exploit
[ ] Network Tools     [ ] Web Tools          [ ] OSINT
[ ] Vulnerability Sc  [ ] DDOS Tools         [ ] Brute Force
[ ] Crypto Tools      [ ] Fuzzing            [ ] Settings
[ ] Clear             [ ] Help               [ ] Exit

↑↓←→ Navigate | Enter: Select | 'q': Quit
Target: 192.168.1.100
```

## Submenu Layout (Example: Reconnaissance)

```
╔═══════════════════════════════════════════════════════════════════╗
║                         Reconnaissance                             ║
╚═══════════════════════════════════════════════════════════════════╝

[✓] WHOIS Lookup
[ ] DNS Enumeration
[ ] Reverse DNS
[ ] GeoIP Lookup
[ ] Back

↑↓ Navigate | Enter: Select | ESC: Back to Main Menu
Target: example.com
```

## Navigation Examples

### Example 1: Access Port Scanning Tool
```
Step 1: Main Menu
Current: [✓] Reconnaissance (top-left)

Step 2: Navigate to Scanning (press RIGHT ARROW twice)
Current: [✓] Scanning

Step 3: Press ENTER to enter submenu
Displays Scanning submenu

Step 4: Navigate to "Port Scan" (press DOWN ARROW)
Current: [✓] Port Scan

Step 5: Press ENTER to execute
Opens Port Scan tool
```

### Example 2: Access DDOS Tools
```
Step 1: Main Menu
Current: [✓] Reconnaissance

Step 2: Navigate to DDOS Tools (RIGHT ARROW 2x, DOWN ARROW 3x)
Current: [✓] DDOS Tools

Step 3: Press ENTER
Displays DDOS submenu

Step 4: Select desired tool
- [ ] HTTP Flood
- [✓] DNS Flood (selected)
- [ ] SYN Flood
- [ ] UDP Flood
- [ ] Back

Step 5: Press ENTER to execute
```

## Feature Highlights

### 1. Smart Grid Navigation
```
[✓]      [ ]      [ ]
  ↓
[ ]      [ ]      [ ]
  ↓
[ ]      [ ]      [ ]
```
- Use ↑↓ to move vertically through rows
- Use ←→ to move horizontally through columns
- Current selection always highlighted with [✓]

### 2. Submenu System
```
Main Menu (3-column grid)
    ↓ (press ENTER)
Submenu (single column list)
    ↓ (select tool)
Tool Execution
    ↓ (press ESC)
Back to Main Menu
```

### 3. Escape to Go Back
- At any submenu: Press ESC → Returns to main menu
- At main menu: ESC has no effect (use 'q' to quit)
- Always have a "Back" option at bottom of submenu

## Menu Structure

```
PENTEST TERMINAL v2.0
│
├─ Reconnaissance (4 tools)
│  ├─ WHOIS Lookup
│  ├─ DNS Enumeration
│  ├─ Reverse DNS
│  └─ GeoIP Lookup
│
├─ Scanning (4 tools)
│  ├─ Port Scan
│  ├─ Service Detection
│  ├─ UDP Scan
│  └─ Stealth Scan
│
├─ Enumeration (4 tools)
│  ├─ Host Discovery
│  ├─ SMB Enumeration
│  ├─ SNMP Enumeration
│  └─ Share Enumeration
│
├─ Exploitation (4 tools)
│  ├─ Exploit Database
│  ├─ Metasploit Search
│  ├─ Vulnerability Matcher
│  └─ Payload Generator
│
├─ Payloads (4 tools)
│  ├─ Reverse Shell
│  ├─ Web Shell
│  ├─ Meterpreter
│  └─ Custom Payload
│
├─ Post-Exploit (4 tools)
│  ├─ Privilege Escalation
│  ├─ Persistence
│  ├─ Data Exfiltration
│  └─ Cover Tracks
│
├─ Network Tools (4 tools)
│  ├─ Network Mapper
│  ├─ Packet Sniffer
│  ├─ Network Jammer
│  └─ ARP Spoofing
│
├─ Web Tools (4 tools)
│  ├─ SQL Injection Tester
│  ├─ XSS Detector
│  ├─ LFI/RFI Scanner
│  └─ Web Crawler
│
├─ OSINT (4 tools)
│  ├─ Email Finder
│  ├─ Social Media Search
│  ├─ Domain Scraper
│  └─ Metadata Extractor
│
├─ Vulnerability Scanner (4 tools)
│  ├─ CVE Scanner
│  ├─ Weakness Finder
│  ├─ Configuration Audit
│  └─ Compliance Check
│
├─ DDOS Tools (4 tools)
│  ├─ HTTP Flood
│  ├─ DNS Flood
│  ├─ SYN Flood
│  └─ UDP Flood
│
├─ Brute Force (4 tools)
│  ├─ SSH Brute Force
│  ├─ FTP Brute Force
│  ├─ Web Form Attack
│  └─ Hash Cracker
│
├─ Crypto Tools (4 tools)
│  ├─ Hash Generator
│  ├─ Hash Cracker
│  ├─ Encryption Tool
│  └─ Decryption Tool
│
├─ Fuzzing (4 tools)
│  ├─ Protocol Fuzzer
│  ├─ Web Fuzzer
│  ├─ Binary Fuzzer
│  └─ Custom Fuzzer
│
├─ Settings (4 options)
│  ├─ Set Target
│  ├─ Configure Wordlists
│  ├─ Network Interface
│  └─ Proxy Settings
│
├─ Clear (Clear screen)
├─ Help (Help information)
└─ Exit (Quit application)
```

## Keyboard Reference

| Key | Action | Context |
|-----|--------|---------|
| ↑ | Move up | Grid: up row; List: previous item |
| ↓ | Move down | Grid: down row; List: next item |
| ← | Move left | Grid only: previous column |
| → | Move right | Grid only: next column |
| Enter | Select/Enter | Main menu: enter submenu; Submenu: execute tool |
| ESC | Back | Submenu: return to main menu |
| q | Quit | Anywhere: exit application |

## Color Legend

🔴 **Red (Fore.RED)**: Branding, box borders, warnings
🟢 **Green (Fore.GREEN)**: Success messages, completion
🔵 **Cyan (Fore.CYAN)**: Selected items, tool names
🟡 **Yellow (Fore.YELLOW)**: User prompts, information

## Tips & Tricks

1. **Quick Navigation**: Use arrow keys smoothly to navigate the grid
2. **Submenu Selection**: Remember current category when in submenu for context
3. **Target Persistence**: Once set, target remains until changed
4. **Help System**: Press 'q' on main menu and select "Help" for detailed info
5. **Fast Exit**: Press 'q' anytime to exit (no confirmation needed)

## Future Enhancements

- [ ] Mouse support for menu navigation
- [ ] Configuration file for persistent settings
- [ ] Custom theme support
- [ ] Search functionality across tools
- [ ] Favorite tools pinning
- [ ] Recent tools history
- [ ] Multi-target support
- [ ] Result caching and history

---

**Last Updated**: February 2026
**Version**: 2.0
