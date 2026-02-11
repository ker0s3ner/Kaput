"""Utility functions and helpers"""

import re
import logging
from datetime import datetime
import ipaddress
from colorama import Fore, Style


class Logger:
    """Simple logging utility"""
    
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logging configuration"""
        handler = logging.FileHandler(f"logs/{self.name}.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def info(self, msg):
        """Log info message"""
        self.logger.info(msg)
    
    def error(self, msg):
        """Log error message"""
        self.logger.error(msg)
    
    def warning(self, msg):
        """Log warning message"""
        self.logger.warning(msg)


class NetworkUtils:
    """Network-related utilities"""
    
    @staticmethod
    def is_valid_ip(ip):
        """Validate IP address"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_domain(domain):
        """Validate domain name"""
        pattern = r'^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$'
        return re.match(pattern, domain, re.IGNORECASE) is not None
    
    @staticmethod
    def parse_port_range(port_spec):
        """Parse port specification (e.g., '1-1000', '80,443,8080')"""
        ports = []
        
        for part in port_spec.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                ports.extend(range(int(start), int(end) + 1))
            else:
                ports.append(int(part))
        
        return list(set(ports))  # Remove duplicates
    
    @staticmethod
    def get_common_ports():
        """Return dictionary of common ports and services"""
        return {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            445: 'SMB',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            5900: 'VNC',
            8080: 'HTTP-Proxy',
            8443: 'HTTPS-Alt',
            27017: 'MongoDB',
            6379: 'Redis'
        }


class ColorPrinter:
    """Utility for colored terminal output"""
    
    @staticmethod
    def success(msg):
        """Print success message"""
        print(f"{Fore.GREEN}[+] {msg}{Style.RESET_ALL}")
    
    @staticmethod
    def error(msg):
        """Print error message"""
        print(f"{Fore.RED}[-] {msg}{Style.RESET_ALL}")
    
    @staticmethod
    def warning(msg):
        """Print warning message"""
        print(f"{Fore.YELLOW}[!] {msg}{Style.RESET_ALL}")
    
    @staticmethod
    def info(msg):
        """Print info message"""
        print(f"{Fore.CYAN}[*] {msg}{Style.RESET_ALL}")
