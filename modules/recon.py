"""Network reconnaissance modules"""

import socket
import subprocess
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from .utils import NetworkUtils, ColorPrinter


class NetworkRecon:
    """Network reconnaissance tools"""
    
    @staticmethod
    def discover_hosts(network):
        """Discover active hosts in a network using ping
        
        Args:
            network: Network in CIDR notation (e.g., 192.168.1.0/24)
        
        Returns:
            List of active IP addresses
        """
        active_hosts = []
        
        try:
            # Parse network
            import ipaddress
            network_obj = ipaddress.ip_network(network, strict=False)
            
            for ip in network_obj.hosts():
                if NetworkRecon._ping_host(str(ip)):
                    active_hosts.append(str(ip))
            
        except Exception as e:
            ColorPrinter.error(f"Error discovering hosts: {str(e)}")
        
        return active_hosts
    
    @staticmethod
    def _ping_host(ip):
        """Ping a single host"""
        try:
            # Use ping command
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def whois_lookup(domain):
        """Perform WHOIS lookup
        
        Args:
            domain: Domain name
        
        Returns:
            Dictionary of WHOIS information
        """
        try:
            import whois
            info = whois.whois(domain)
            
            return {
                'Domain': info.domain,
                'Registrar': getattr(info, 'registrar', 'N/A'),
                'Created': getattr(info, 'creation_date', 'N/A'),
                'Expires': getattr(info, 'expiration_date', 'N/A'),
                'Name Servers': getattr(info, 'name_servers', 'N/A'),
            }
        except Exception as e:
            ColorPrinter.warning(f"WHOIS lookup failed: {str(e)}")
            return None


class DNSEnum:
    """DNS enumeration tools"""
    
    @staticmethod
    def enumerate(domain, record_type='A'):
        """Enumerate DNS records
        
        Args:
            domain: Domain name
            record_type: DNS record type (A, MX, NS, TXT, CNAME, SOA)
        
        Returns:
            List of DNS records
        """
        try:
            import dns.resolver
            
            results = []
            answers = dns.resolver.resolve(domain, record_type)
            
            for rdata in answers:
                results.append(str(rdata))
            
            return results
        
        except Exception as e:
            ColorPrinter.warning(f"DNS enumeration failed: {str(e)}")
            return []
    
    @staticmethod
    def reverse_dns_lookup(ip):
        """Reverse DNS lookup
        
        Args:
            ip: IP address
        
        Returns:
            Hostname associated with IP
        """
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except socket.herror:
            return "Unknown"
