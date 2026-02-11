"""OSINT (Open Source Intelligence) gathering tools"""

import requests
import re
import json
import time
import socket
from bs4 import BeautifulSoup
from .utils import ColorPrinter


class EmailFinder:
    """Email address discovery tool"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def find_emails(self, domain):
        """Find email addresses associated with domain
        
        Args:
            domain: Target domain
            
        Returns:
            List of found email addresses
        """
        emails = set()
        ColorPrinter.info(f"Searching for emails from {domain}")
        
        # Search engines and common sources
        sources = [
            f"https://www.google.com/search?q=site:{domain}+email",
            f"https://www.google.com/search?q=site:{domain}+contact",
            f"https://www.google.com/search?q=site:{domain}+@{domain}",
        ]
        
        email_pattern = re.compile(r'[\w\.-]+@' + re.escape(domain), re.IGNORECASE)
        
        for source in sources:
            try:
                response = self.session.get(source, timeout=10)
                found_emails = email_pattern.findall(response.text)
                emails.update(found_emails)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                ColorPrinter.warning(f"Error searching {source}: {str(e)[:50]}")
        
        # Check common pages
        common_pages = [
            '',
            'contact',
            'about',
            'team',
            'staff',
            'directory'
        ]
        
        for page in common_pages:
            try:
                url = f"http://{domain}/{page}" if page else f"http://{domain}"
                response = self.session.get(url, timeout=10)
                found_emails = email_pattern.findall(response.text)
                emails.update(found_emails)
                time.sleep(0.5)
            except:
                pass
        
        return list(emails)


class SocialMediaSearch:
    """Social media profile discovery"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_profiles(self, name, company=None):
        """Search for social media profiles
        
        Args:
            name: Person/company name
            company: Company name (optional)
            
        Returns:
            Dictionary of found profiles
        """
        profiles = {}
        ColorPrinter.info(f"Searching social media for: {name}")
        
        # LinkedIn search
        linkedin_url = f"https://www.linkedin.com/search/results/people/?keywords={name}"
        profiles['LinkedIn'] = linkedin_url
        
        # Twitter search
        twitter_url = f"https://twitter.com/search?q={name}&f=user"
        profiles['Twitter'] = twitter_url
        
        # Facebook search
        facebook_url = f"https://www.facebook.com/search/people/?q={name}"
        profiles['Facebook'] = facebook_url
        
        # GitHub search (for developers)
        github_url = f"https://github.com/search?q={name}&type=users"
        profiles['GitHub'] = github_url
        
        # Instagram search
        instagram_url = f"https://www.instagram.com/web/search/topsearch/?query={name}"
        profiles['Instagram'] = instagram_url
        
        return profiles


class DomainScraper:
    """Domain and subdomain enumeration"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_subdomains(self, domain):
        """Find subdomains for a domain
        
        Args:
            domain: Target domain
            
        Returns:
            List of found subdomains
        """
        subdomains = set()
        ColorPrinter.info(f"Scraping subdomains for {domain}")
        
        # Certificate transparency logs
        ct_logs = [
            "https://crt.sh/?q=%25." + domain,
            "https://certspotter.com/api/v1/issuances?domain=" + domain + "&include_subdomains=true&expand=dns_names"
        ]
        
        for url in ct_logs:
            try:
                response = self.session.get(url, timeout=15)
                if "crt.sh" in url:
                    # Parse HTML for subdomains
                    soup = BeautifulSoup(response.text, 'html.parser')
                    links = soup.find_all('a')
                    for link in links:
                        href = link.get('href', '')
                        if domain in href and '://' not in href:
                            subdomain = href.split('?')[0].strip()
                            if subdomain.endswith('.' + domain):
                                subdomains.add(subdomain)
                else:
                    # JSON API response
                    data = response.json()
                    for entry in data:
                        if 'dns_names' in entry:
                            for dns_name in entry['dns_names']:
                                if dns_name.endswith('.' + domain):
                                    subdomains.add(dns_name)
                time.sleep(1)
            except Exception as e:
                ColorPrinter.warning(f"Error scraping {url}: {str(e)[:50]}")
        
        # DNS brute force with common subdomains
        common_subdomains = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
            'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'm', 'imap', 'test',
            'ns', 'blog', 'pop3', 'dev', 'www2', 'admin', 'forum', 'news', 'vpn',
            'ns3', 'mail2', 'new', 'mysql', 'old', 'lists', 'support', 'mobile',
            'mx', 'static', 'docs', 'beta', 'shop', 'sql', 'secure', 'demo', 'cp',
            'calendar', 'wiki', 'media', 'email', 'images', 'img', 'www1', 'intranet',
            'portal', 'video', 'sip', 'dns2', 'api', 'cdn', 'stats', 'dns1', 'ns4',
            'www3', 'dns', 'search', 'staging', 'server', 'mx1', 'chat', 'wap', 'my',
            'svn', 'mail1', 'sites', 'proxy', 'ads', 'host', 'crm', 'cms', 'backup',
            'mx2', 'lyncdiscover', 'info', 'apps', 'download', 'remote', 'db', 'forums',
            'store', 'relay', 'files', 'newsletter', 'app', 'live', 'owa', 'en',
            'start', 'sms', 'office', 'exchange', 'ipv4'
        ]
        
        ColorPrinter.info("Testing common subdomains...")
        for sub in common_subdomains:
            try:
                full_domain = f"{sub}.{domain}"
                socket.gethostbyname(full_domain)
                subdomains.add(full_domain)
                print(f"  Found: {full_domain}")
            except socket.gaierror:
                pass  # Subdomain doesn't exist
            except Exception:
                pass
        
        return list(subdomains)


class MetadataExtractor:
    """Extract metadata from files and websites"""
    
    def __init__(self):
        pass
    
    def extract_from_url(self, url):
        """Extract metadata from webpage
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        ColorPrinter.info(f"Extracting metadata from {url}")
        
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.text.strip()
            
            # Meta tags
            meta_tags = soup.find_all('meta')
            for tag in meta_tags:
                name = tag.get('name') or tag.get('property')
                content = tag.get('content')
                if name and content:
                    metadata[name] = content
            
            # Links
            links = soup.find_all('a', href=True)
            metadata['links'] = [link['href'] for link in links[:10]]  # First 10 links
            
            # Images
            images = soup.find_all('img', src=True)
            metadata['images'] = [img['src'] for img in images[:5]]  # First 5 images
            
        except Exception as e:
            ColorPrinter.error(f"Error extracting metadata: {str(e)}")
        
        return metadata
    
    def extract_from_file(self, file_path):
        """Extract metadata from local file (placeholder)
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        ColorPrinter.info(f"Extracting metadata from {file_path}")
        
        # This would integrate with libraries like exifread, python-docx, etc.
        # For now, return basic file information
        try:
            import os
            stat = os.stat(file_path)
            metadata['size'] = stat.st_size
            metadata['modified'] = time.ctime(stat.st_mtime)
            metadata['created'] = time.ctime(stat.st_ctime)
        except Exception as e:
            ColorPrinter.error(f"Error reading file: {str(e)}")
        
        return metadata


# Convenience functions
def find_emails(domain):
    """Convenience function for email finding"""
    finder = EmailFinder()
    return finder.find_emails(domain)

def search_social_media(name, company=None):
    """Convenience function for social media search"""
    searcher = SocialMediaSearch()
    return searcher.search_profiles(name, company)

def scrape_subdomains(domain):
    """Convenience function for subdomain scraping"""
    scraper = DomainScraper()
    return scraper.scrape_subdomains(domain)

def extract_metadata(url_or_file):
    """Convenience function for metadata extraction"""
    extractor = MetadataExtractor()
    if url_or_file.startswith(('http://', 'https://')):
        return extractor.extract_from_url(url_or_file)
    else:
        return extractor.extract_from_file(url_or_file)