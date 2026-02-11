# PenTest Terminal - Quick Start Guide

## Installation & Setup

### 1. Install Dependencies
```bash
cd /home/ligma/Work/Hacking
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python3 pentest_terminal.py
```

## First Steps

### Step 1: Set Your Target
```
[PenTest]> set_target 192.168.1.1
```

### Step 2: Scan Common Ports
```
[PenTest:192.168.1.1]> port_scan 80,443,22,23,25,3306,5432
```

### Step 3: Get Service Information
```
[PenTest:192.168.1.1]> service_enum 192.168.1.1 80,443,22
```

### Step 4: Search for Known Exploits
```
[PenTest:192.168.1.1]> searchsploit Apache
[PenTest:192.168.1.1]> searchsploit OpenSSH
```

### Step 5: DNS Enumeration (for domains)
```
[PenTest]> dns_enum example.com
[PenTest]> dns_enum example.com -t MX
```

## Common Workflows

### Web Server Assessment
```
[PenTest]> set_target example.com
[PenTest:example.com]> port_scan 80,443,8080,8443
[PenTest:example.com]> service_enum example.com 80,443
[PenTest:example.com]> searchsploit Apache
[PenTest:example.com]> searchsploit Nginx
```

### Network Reconnaissance
```
[PenTest]> host_discovery 192.168.1.0/24
[PenTest]> set_target 192.168.1.50
[PenTest:192.168.1.50]> port_scan 1-1000 -t 100
```

### Full System Assessment
```
[PenTest]> set_target 192.168.1.100
[PenTest:192.168.1.100]> port_scan 1-1000
[PenTest:192.168.1.100]> service_enum 192.168.1.100 21,22,25,53,80,110,143,389,443,445,3306,3389
[PenTest:192.168.1.100]> searchsploit OpenSSH
[PenTest:192.168.1.100]> searchsploit Samba
```

## Tips & Tricks

### Fast Port Scanning
Use fewer ports for quick scans:
```
[PenTest]> set_target target.com
[PenTest:target.com]> port_scan 80,443,8080
```

### Thorough Port Scanning
For comprehensive scans with multiple threads:
```
[PenTest]> port_scan 1-65535 -t 200
```

### DNS Record Types
- **A**: IPv4 address records
- **AAAA**: IPv6 address records
- **MX**: Mail exchange records
- **NS**: Name server records
- **TXT**: Text records (SPF, DKIM, etc.)
- **CNAME**: Canonical name records
- **SOA**: Start of authority records

Example:
```
[PenTest]> dns_enum example.com -t MX
[PenTest]> dns_enum example.com -t NS
```

## Troubleshooting

### "No module named 'colorama'"
```bash
pip install colorama
```

### "No module named 'dns'"
```bash
pip install dnspython
```

### Port scan hangs
- Try reducing the port range
- Increase timeout in config.conf
- Reduce number of threads: `port_scan 1-1000 -t 20`

### DNS resolution fails
- Verify domain name is correct
- Check internet connectivity
- Try with explicit DNS server (future feature)

## Features Overview

- ✅ Port scanning with multi-threading
- ✅ Service detection & banner grabbing
- ✅ DNS enumeration (A, MX, NS, TXT, CNAME, SOA)
- ✅ Host discovery via ping
- ✅ WHOIS lookups
- ✅ Searchable exploit database
- ✅ Colored terminal output
- ✅ Comprehensive logging
- ✅ Input validation

## Legal Notice

This tool is for **authorized security testing only**. Ensure you have written permission before testing any systems. Unauthorized access is illegal.

## Next Steps

1. Explore the `modules/` directory to understand the architecture
2. Add custom exploits to `modules/data/exploits.json`
3. Extend with new modules following the existing pattern
4. Configure settings in `config.conf`
5. Check logs in the `logs/` directory

Happy hunting! 🎯
