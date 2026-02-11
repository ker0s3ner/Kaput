"""Vulnerability scanning and CVE detection tools"""

import requests
import json
import time
import socket
from datetime import datetime
from .utils import ColorPrinter


class CVEScanner:
    """CVE (Common Vulnerabilities and Exposures) scanner"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PenTest-Terminal/2.0'
        })
    
    def scan_target(self, target, service_info=None):
        """Scan target for known vulnerabilities
        
        Args:
            target: Target IP/hostname
            service_info: Dictionary of discovered services {port: service_name}
            
        Returns:
            List of found vulnerabilities
        """
        vulnerabilities = []
        ColorPrinter.info(f"Scanning {target} for CVEs")
        
        # If service info provided, scan specific services
        if service_info:
            for port, service in service_info.items():
                vulns = self._scan_service(service, port)
                vulnerabilities.extend(vulns)
        else:
            # Generic scan - try common services
            common_services = {
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
                8080: 'HTTP-Proxy'
            }
            
            for port, service in common_services.items():
                try:
                    # Check if port is open
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((target, port))
                    sock.close()
                    
                    if result == 0:
                        vulns = self._scan_service(service, port)
                        vulnerabilities.extend(vulns)
                except:
                    pass
        
        return vulnerabilities
    
    def _scan_service(self, service, port):
        """Scan specific service for vulnerabilities
        
        Args:
            service: Service name
            port: Port number
            
        Returns:
            List of vulnerabilities for this service
        """
        vulnerabilities = []
        service = service.upper()
        
        # Known vulnerable software versions
        vulnerable_software = {
            'HTTP': [
                {'software': 'Apache 2.4.1', 'cve': 'CVE-2013-6438', 'severity': 'Medium'},
                {'software': 'Nginx 1.0.6', 'cve': 'CVE-2009-3898', 'severity': 'High'},
                {'software': 'IIS 6.0', 'cve': 'CVE-2017-7269', 'severity': 'Critical'}
            ],
            'SSH': [
                {'software': 'OpenSSH 5.x', 'cve': 'CVE-2012-0814', 'severity': 'Medium'},
                {'software': 'OpenSSH 7.2', 'cve': 'CVE-2016-6515', 'severity': 'High'}
            ],
            'FTP': [
                {'software': 'vsftpd 2.3.4', 'cve': 'CVE-2011-2523', 'severity': 'Critical'}
            ],
            'MYSQL': [
                {'software': 'MySQL 5.1.x', 'cve': 'CVE-2010-0733', 'severity': 'Critical'}
            ],
            'POSTGRESQL': [
                {'software': 'PostgreSQL 9.0', 'cve': 'CVE-2010-3739', 'severity': 'High'}
            ]
        }
        
        if service in vulnerable_software:
            for vuln in vulnerable_software[service]:
                # Simulate version detection and matching
                # In real implementation, this would detect actual versions
                vulnerabilities.append({
                    'service': service,
                    'port': port,
                    'cve': vuln['cve'],
                    'severity': vuln['severity'],
                    'description': f"{vuln['software']} vulnerability"
                })
        
        return vulnerabilities
    
    def search_cve(self, keyword):
        """Search CVE database for specific keyword
        
        Args:
            keyword: Search term
            
        Returns:
            List of matching CVEs
        """
        cves = []
        ColorPrinter.info(f"Searching CVE database for: {keyword}")
        
        try:
            # Using NVD (National Vulnerability Database) API
            url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={keyword}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('vulnerabilities', [])[:10]:  # Limit to 10 results
                    cve_item = item.get('cve', {})
                    cve_id = cve_item.get('id', 'Unknown')
                    description = cve_item.get('descriptions', [{}])[0].get('value', 'No description')
                    severity = 'Unknown'
                    
                    # Extract severity if available
                    metrics = cve_item.get('metrics', {})
                    if 'cvssMetricV31' in metrics:
                        severity = metrics['cvssMetricV31'][0]['cvssData'].get('baseSeverity', 'Unknown')
                    elif 'cvssMetricV2' in metrics:
                        severity = metrics['cvssMetricV2'][0]['cvssData'].get('baseScore', 'Unknown')
                    
                    cves.append({
                        'cve': cve_id,
                        'description': description[:100] + '...' if len(description) > 100 else description,
                        'severity': severity
                    })
            else:
                ColorPrinter.warning("NVD API unavailable, using sample data")
                # Return sample data if API fails
                cves = self._get_sample_cves(keyword)
                
        except Exception as e:
            ColorPrinter.warning(f"CVE search failed: {str(e)}, using sample data")
            cves = self._get_sample_cves(keyword)
        
        return cves
    
    def _get_sample_cves(self, keyword):
        """Return sample CVE data for demonstration"""
        sample_cves = [
            {
                'cve': 'CVE-2021-44228',
                'description': 'Apache Log4j2 JNDI features do not protect against...',
                'severity': 'Critical'
            },
            {
                'cve': 'CVE-2021-41773',
                'description': 'A flaw was found in a change made to path normalization...',
                'severity': 'High'
            },
            {
                'cve': 'CVE-2017-0144',
                'description': 'The SMBv1 server in Microsoft Windows Vista SP2...',
                'severity': 'Critical'
            },
            {
                'cve': 'CVE-2014-0160',
                'description': 'The TLS and SSL protocols in OpenSSL do not properly...',
                'severity': 'High'
            }
        ]
        
        # Filter by keyword
        keyword = keyword.lower()
        filtered = [cve for cve in sample_cves if keyword in cve['description'].lower() or keyword in cve['cve'].lower()]
        return filtered


class ConfigurationAuditor:
    """Security configuration auditor"""
    
    def __init__(self):
        pass
    
    def audit_system(self, target):
        """Audit system security configuration
        
        Args:
            target: Target system
            
        Returns:
            Dictionary of audit findings
        """
        findings = {
            'passed': [],
            'warnings': [],
            'failures': []
        }
        
        ColorPrinter.info(f"Auditing security configuration of {target}")
        
        # Simulate various security checks
        checks = [
            ('SSH root login disabled', True, 'pass'),
            ('Firewall enabled', True, 'pass'),
            ('Default passwords changed', False, 'fail'),
            ('SSL/TLS protocols configured', True, 'warn'),
            ('Automatic updates enabled', False, 'fail'),
            ('Antivirus software installed', True, 'pass'),
            ('Unnecessary services disabled', False, 'warn'),
            ('Strong password policy enforced', False, 'fail')
        ]
        
        for check_name, status, severity in checks:
            if severity == 'pass' and status:
                findings['passed'].append(check_name)
            elif severity == 'fail' and not status:
                findings['failures'].append(check_name)
            elif severity == 'warn' and not status:
                findings['warnings'].append(check_name)
        
        return findings


class ComplianceChecker:
    """Security compliance checker"""
    
    def __init__(self):
        pass
    
    def check_compliance(self, target, standard='PCI-DSS'):
        """Check compliance with security standards
        
        Args:
            target: Target system
            standard: Compliance standard (PCI-DSS, HIPAA, ISO27001)
            
        Returns:
            Dictionary of compliance report
        """
        ColorPrinter.info(f"Checking {standard} compliance for {target}")
        
        # Sample compliance data
        compliance_data = {
            'PCI-DSS': {
                'encryption_at_rest': 85,
                'access_controls': 70,
                'audit_logging': 45,
                'vulnerability_management': 75,
                'network_security': 80
            },
            'HIPAA': {
                'data_encryption': 75,
                'access_auditing': 60,
                'incident_response': 65,
                'risk_assessment': 55,
                'training_awareness': 70
            },
            'ISO27001': {
                'information_security_policy': 80,
                'asset_management': 70,
                'human_resource_security': 65,
                'physical_security': 75,
                'communications_security': 85
            }
        }
        
        results = compliance_data.get(standard.upper(), compliance_data['PCI-DSS'])
        
        # Calculate overall score
        total_score = sum(results.values()) / len(results)
        
        return {
            'standard': standard,
            'scores': results,
            'overall_score': round(total_score, 1),
            'compliant': total_score >= 70
        }


# Convenience functions
def scan_for_cves(target, service_info=None):
    """Convenience function for CVE scanning"""
    scanner = CVEScanner()
    return scanner.scan_target(target, service_info)

def search_cve_database(keyword):
    """Convenience function for CVE search"""
    scanner = CVEScanner()
    return scanner.search_cve(keyword)

def audit_configuration(target):
    """Convenience function for configuration audit"""
    auditor = ConfigurationAuditor()
    return auditor.audit_system(target)

def check_compliance(target, standard='PCI-DSS'):
    """Convenience function for compliance checking"""
    checker = ComplianceChecker()
    return checker.check_compliance(target, standard)