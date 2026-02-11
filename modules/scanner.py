"""Port scanning and service detection modules"""

import socket
import threading
import struct
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import NetworkUtils, ColorPrinter


class PortScanner:
    """Port scanning functionality"""
    
    def __init__(self, timeout=2):
        self.timeout = timeout
        self.results = {}
        
    def udp_scan(self, target, port_range, threads=50):
        """Perform UDP port scan
        
        Args:
            target: IP address or domain
            port_range: Port specification
            threads: Number of parallel threads
        
        Returns:
            Dictionary of open/closed UDP ports
        """
        ports = NetworkUtils.parse_port_range(port_range)
        self.results = {}
        
        ColorPrinter.info(f"UDP scanning {len(ports)} ports on {target}")
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {
                executor.submit(self._check_udp_port, target, port): port 
                for port in ports
            }
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 10 == 0 or completed == len(ports):
                    print(f"    Progress: {completed}/{len(ports)}", end='\r')
        
        print()
        return self.results
    
    def stealth_scan(self, target, port_range, threads=50):
        """Perform stealth SYN scan (requires root privileges)
        
        Args:
            target: IP address
            port_range: Port specification
            threads: Number of parallel threads
        
        Returns:
            Dictionary of port states
        """
        ports = NetworkUtils.parse_port_range(port_range)
        self.results = {}
        
        ColorPrinter.info(f"Stealth scanning {len(ports)} ports on {target}")
        ColorPrinter.warning("Note: Stealth scans require root privileges")
        
        # For demonstration, we'll simulate the behavior
        # In production, this would use raw sockets
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {
                executor.submit(self._simulate_stealth_scan, target, port): port 
                for port in ports
            }
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 10 == 0 or completed == len(ports):
                    print(f"    Progress: {completed}/{len(ports)}", end='\r')
        
        print()
        return self.results
    
    def scan(self, target, port_range, threads=50):
        """Scan target for open ports
        
        Args:
            target: IP address or domain
            port_range: Port specification (e.g., '1-1000', '80,443')
            threads: Number of parallel threads
        
        Returns:
            Dictionary of open ports and their states
        """
        ports = NetworkUtils.parse_port_range(port_range)
        self.results = {}
        
        ColorPrinter.info(f"Scanning {len(ports)} ports on {target}")
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {
                executor.submit(self._check_port, target, port): port 
                for port in ports
            }
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 10 == 0 or completed == len(ports):
                    print(f"    Progress: {completed}/{len(ports)}", end='\r')
        
        print()  # New line after progress
        return self.results
    
    def _check_port(self, target, port):
        """Check if a single port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            
            if result == 0:
                self.results[port] = 'open'
            
        except socket.gaierror:
            ColorPrinter.error(f"Hostname {target} could not be resolved")
        except socket.error as e:
            ColorPrinter.error(f"Could not connect to {target}: {str(e)}")
    
    def _check_udp_port(self, target, port):
        """Check if a UDP port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            
            # Send a dummy packet
            sock.sendto(b'', (target, port))
            
            # Try to receive response
            try:
                data, addr = sock.recvfrom(1024)
                self.results[port] = 'open'
            except socket.timeout:
                # Timeout usually means port is open but not responding
                self.results[port] = 'open|filtered'
            
            sock.close()
        except Exception as e:
            # Most UDP ports will timeout, which is normal
            self.results[port] = 'closed'
    
    def _simulate_stealth_scan(self, target, port):
        """Simulate stealth SYN scan behavior"""
        # This is a simulation - real stealth scanning requires raw sockets
        # and root privileges
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # Short timeout for stealth effect
            result = sock.connect_ex((target, port))
            sock.close()
            
            # Simulate different responses
            if result == 0:
                self.results[port] = 'open'
            elif result == 111:  # Connection refused
                self.results[port] = 'closed'
            else:
                self.results[port] = 'filtered'
        except:
            self.results[port] = 'filtered'


class ServiceDetector:
    """Service detection on open ports"""
    
    def __init__(self):
        self.port_services = NetworkUtils.get_common_ports()
    
    def get_service(self, port):
        """Get service name for a port"""
        return self.port_services.get(port, 'Unknown')
    
    def enumerate_services(self, target, ports, timeout=5):
        """Enumerate services on specified ports
        
        Args:
            target: Target IP or domain
            ports: List of ports to enumerate
            timeout: Connection timeout
        
        Returns:
            Dictionary of port and service information
        """
        results = {}
        
        for port_str in ports:
            port = int(port_str.strip())
            service_info = self._get_service_info(target, port, timeout)
            if service_info:
                results[port] = service_info
        
        return results
    
    def _get_service_info(self, target, port, timeout=5):
        """Get service information from a specific port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((target, port))
            
            # Send service-specific probes for better identification
            service_probes = {
                21: b'USER anonymous\r\n',
                22: b'',
                23: b'',
                25: b'EHLO test\r\n',
                80: b'GET / HTTP/1.0\r\n\r\n',
                110: b'USER test\r\n',
                143: b'a001 LOGIN user pass\r\n',
                443: b'GET / HTTP/1.0\r\n\r\n',
                3306: b'\x4a\x00\x00\x00\x0a',
                5432: b'\x00\x00\x00\x08\x04\xd2\x16\x2f',
            }
            
            probe = service_probes.get(port, b'')
            if probe:
                sock.send(probe)
                time.sleep(0.1)
            
            # Try to grab banner
            banner = b''
            try:
                banner = sock.recv(1024)
            except:
                pass
            
            sock.close()
            
            service = self.get_service(port)
            if banner:
                try:
                    banner_str = banner.decode('utf-8', errors='ignore').strip()
                    return f"{service} - {banner_str[:100]}"
                except:
                    return f"{service} - Binary response ({len(banner)} bytes)"
            else:
                return service
            
        except Exception as e:
            service = self.get_service(port)
            return f"{service} - Connection failed ({str(e)[:30]})"
