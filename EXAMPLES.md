# PenTest Terminal - Usage Examples

## Example 1: Basic Port Scan

```bash
$ python3 pentest_terminal.py

[PenTest]> set_target 192.168.1.100
[+] Target set to: 192.168.1.100

[PenTest:192.168.1.100]> port_scan 1-1000
[*] Starting port scan on 192.168.1.100:1-1000...
[*] Scanning 1000 ports on 192.168.1.100
    Progress: 1000/1000

[+] Open ports found:
    22/tcp - open (SSH)
    80/tcp - open (HTTP)
    443/tcp - open (HTTPS)
    3306/tcp - open (MySQL)

[PenTest:192.168.1.100]> exit
[+] Goodbye!
```

## Example 2: Service Enumeration

```bash
[PenTest]> set_target webserver.example.com
[+] Target set to: webserver.example.com

[PenTest:webserver.example.com]> service_enum webserver.example.com 80,443,8080
[*] Enumerating services on webserver.example.com...

[+] Service Enumeration Results:
    Port 80: HTTP - Apache/2.4.41 (Ubuntu)
    Port 443: HTTPS - nginx/1.18.0
    Port 8080: HTTP-Proxy - Custom App Server v1.2
```

## Example 3: DNS Enumeration

```bash
[PenTest]> dns_enum example.com
[*] Performing DNS enumeration on example.com (A)...

[+] DNS Records Found:
    93.184.216.34

[PenTest]> dns_enum example.com -t MX
[*] Performing DNS enumeration on example.com (MX)...

[+] DNS Records Found:
    10 aspmx.l.google.com.
    20 alt1.aspmx.l.google.com.
```

## Example 4: Host Discovery

```bash
[PenTest]> host_discovery 192.168.1.0/24
[*] Scanning network: 192.168.1.0/24...

[+] Active hosts found:
    192.168.1.1
    192.168.1.10
    192.168.1.50
    192.168.1.100
    192.168.1.200
```

## Example 5: Exploit Search

```bash
[PenTest]> searchsploit Apache
[*] Searching exploit database for: Apache...

[+] Exploits Found:
    [CVE-2013-6438] Apache 2.4.1 - Mod_dav Denial of Service

[PenTest]> searchsploit OpenSSH
[*] Searching exploit database for: OpenSSH...

[+] Exploits Found:
    [CVE-2012-0814] OpenSSH 5.x - Information Disclosure
```

## Example 6: Complete Assessment Workflow

```bash
[PenTest]> set_target target.company.com
[+] Target set to: target.company.com

# Step 1: DNS Enumeration
[PenTest:target.company.com]> dns_enum target.company.com
[+] DNS Records Found:
    192.168.1.50

# Step 2: Port Scanning
[PenTest:target.company.com]> port_scan 1-1000 -t 100
[+] Open ports found:
    22/tcp - open (SSH)
    80/tcp - open (HTTP)
    443/tcp - open (HTTPS)
    3306/tcp - open (MySQL)

# Step 3: Service Detection
[PenTest:target.company.com]> service_enum target.company.com 22,80,443,3306
[+] Service Enumeration Results:
    Port 22: SSH - OpenSSH 5.3p1 Debian 3ubuntu7
    Port 80: HTTP - Apache/2.2.9 (Debian)
    Port 443: HTTPS - Apache/2.2.9 (Debian)
    Port 3306: MySQL - MySQL 5.1.37

# Step 4: Vulnerability Research
[PenTest:target.company.com]> searchsploit OpenSSH 5.3
[+] Exploits Found:
    [CVE-2012-0814] OpenSSH 5.x - Information Disclosure
    [CVE-2008-5161] OpenSSH 5.x - Buffer overflow

[PenTest:target.company.com]> searchsploit Apache 2.2
[+] Exploits Found:
    [CVE-2010-0433] Apache 2.2.x - Security bypass

[PenTest:target.company.com]> searchsploit MySQL 5.1
[+] Exploits Found:
    [CVE-2010-0733] MySQL 5.1.x - Buffer Overflow
```

## Example 7: WHOIS Lookup

```bash
[PenTest]> whois example.com
[*] Performing WHOIS lookup on example.com...

[+] WHOIS Information:
    Domain: example.com
    Registrar: VeriSign Global Registry Services
    Created: 1995-08-14
    Expires: 2028-08-13
    Name Servers: ['a.iana-servers.net', 'b.iana-servers.net']
```

## Example 8: Scanning Multiple Ports

```bash
[PenTest]> set_target server.local
[+] Target set to: server.local

# Common web service ports
[PenTest:server.local]> port_scan 80,443,8080,8443
[+] Open ports found:
    80/tcp - open (HTTP)
    8080/tcp - open (HTTP-Proxy)

# Database server ports
[PenTest:server.local]> port_scan 3306,5432,27017,6379
[+] Open ports found:
    3306/tcp - open (MySQL)
    5432/tcp - open (PostgreSQL)

# Full range with threads
[PenTest:server.local]> port_scan 1-65535 -t 200
[*] Scanning 65535 ports on server.local
[+] Open ports found:
    22/tcp - open (SSH)
    80/tcp - open (HTTP)
    443/tcp - open (HTTPS)
```

## Command Syntax Reference

### Basic Syntax
```
[PenTest]> <command> <arguments> [options]
```

### Port Range Formats
- **Individual ports**: `80,443,8080`
- **Port range**: `1-1000`
- **Mixed**: `80,443,1000-1010`

### Threading Options
```
port_scan <range> -t <number>
-t 20    # Fewer threads (conservative, less network impact)
-t 100   # Balanced
-t 200   # Aggressive (more threads, faster but higher load)
```

### DNS Record Types
```
dns_enum <domain> -t <TYPE>
-t A       # IPv4 address
-t AAAA    # IPv6 address
-t MX      # Mail exchange
-t NS      # Name server
-t TXT     # Text record
-t CNAME   # Canonical name
-t SOA     # Start of authority
```

## Tips for Effective Pentesting

1. **Start Broad, Then Deep**: Do a quick scan of common ports first, then expand
   ```
   port_scan 80,443,22,3306
   port_scan 1-10000 -t 100
   ```

2. **Combine Reconnaissance Tools**: Use DNS enumeration with port scanning
   ```
   dns_enum target.com
   port_scan 1-1000
   service_enum target.com 22,80,443
   ```

3. **Cross-Reference with Exploit Database**: Search for vulnerabilities in identified services
   ```
   searchsploit Apache
   searchsploit OpenSSH
   ```

4. **Document Your Findings**: All operations are logged to `logs/` directory

5. **Respect Rate Limits**: Adjust threads based on target network capacity

## Legal & Ethical Guidelines

⚠️ **Remember**: This tool is for authorized security testing only
- Always obtain written authorization before testing
- Never scan or test systems you don't own
- Follow local and international laws
- Document all findings professionally
- Share results only with authorized parties

Stay ethical, stay legal! 🔒
