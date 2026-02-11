"""Cryptographic tools for encryption, decryption, and hashing"""

import hashlib
import base64
import codecs
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from .utils import ColorPrinter


class EncryptionTools:
    """Encryption and decryption utilities"""
    
    @staticmethod
    def caesar_cipher(text, shift, decrypt=False):
        """Caesar cipher encryption/decryption
        
        Args:
            text: Text to encrypt/decrypt
            shift: Shift amount
            decrypt: Whether to decrypt (negative shift)
            
        Returns:
            Encrypted/decrypted text
        """
        if decrypt:
            shift = -shift
            
        result = ""
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
            else:
                result += char
        return result
    
    @staticmethod
    def rot13(text):
        """ROT13 cipher
        
        Args:
            text: Text to encode/decode
            
        Returns:
            ROT13 encoded/decoded text
        """
        return codecs.encode(text, 'rot_13')
    
    @staticmethod
    def base64_encode(text):
        """Base64 encoding
        
        Args:
            text: Text to encode
            
        Returns:
            Base64 encoded text
        """
        try:
            return base64.b64encode(text.encode()).decode()
        except Exception:
            return text
    
    @staticmethod
    def base64_decode(encoded_text):
        """Base64 decoding
        
        Args:
            encoded_text: Base64 encoded text
            
        Returns:
            Decoded text
        """
        try:
            return base64.b64decode(encoded_text).decode()
        except Exception:
            return encoded_text
    
    @staticmethod
    def aes_encrypt(text, key):
        """AES encryption (using Fernet)
        
        Args:
            text: Text to encrypt
            key: Encryption key (32 bytes base64 encoded)
            
        Returns:
            Encrypted text
        """
        try:
            if isinstance(key, str):
                key = key.encode()
            f = Fernet(key)
            return f.encrypt(text.encode()).decode()
        except Exception as e:
            ColorPrinter.error(f"AES encryption failed: {str(e)}")
            return text
    
    @staticmethod
    def aes_decrypt(encrypted_text, key):
        """AES decryption (using Fernet)
        
        Args:
            encrypted_text: Encrypted text
            key: Decryption key (32 bytes base64 encoded)
            
        Returns:
            Decrypted text
        """
        try:
            if isinstance(key, str):
                key = key.encode()
            f = Fernet(key)
            return f.decrypt(encrypted_text.encode()).decode()
        except Exception as e:
            ColorPrinter.error(f"AES decryption failed: {str(e)}")
            return encrypted_text
    
    @staticmethod
    def generate_key():
        """Generate a new encryption key
        
        Returns:
            Base64 encoded key
        """
        return Fernet.generate_key().decode()


class HashGenerator:
    """Hash generation utilities"""
    
    @staticmethod
    def generate_hashes(text):
        """Generate multiple hash types for text
        
        Args:
            text: Text to hash
            
        Returns:
            Dictionary of hash types and values
        """
        if isinstance(text, str):
            text_bytes = text.encode()
        else:
            text_bytes = text
            
        hashes = {
            'MD5': hashlib.md5(text_bytes).hexdigest(),
            'SHA1': hashlib.sha1(text_bytes).hexdigest(),
            'SHA224': hashlib.sha224(text_bytes).hexdigest(),
            'SHA256': hashlib.sha256(text_bytes).hexdigest(),
            'SHA384': hashlib.sha384(text_bytes).hexdigest(),
            'SHA512': hashlib.sha512(text_bytes).hexdigest(),
            'SHA3_224': hashlib.sha3_224(text_bytes).hexdigest(),
            'SHA3_256': hashlib.sha3_256(text_bytes).hexdigest(),
            'SHA3_384': hashlib.sha3_384(text_bytes).hexdigest(),
            'SHA3_512': hashlib.sha3_512(text_bytes).hexdigest()
        }
        
        return hashes
    
    @staticmethod
    def identify_hash(hash_value):
        """Attempt to identify hash type based on length
        
        Args:
            hash_value: Hash value to identify
            
        Returns:
            List of possible hash types
        """
        hash_length = len(hash_value)
        
        hash_types = {
            32: ['MD5'],
            40: ['SHA1'],
            56: ['SHA224', 'SHA3_224'],
            64: ['SHA256', 'SHA3_256'],
            96: ['SHA384', 'SHA3_384'],
            128: ['SHA512', 'SHA3_512']
        }
        
        return hash_types.get(hash_length, ['Unknown'])


class EncodingTools:
    """Various encoding and decoding tools"""
    
    @staticmethod
    def hex_encode(text):
        """Hexadecimal encoding
        
        Args:
            text: Text to encode
            
        Returns:
            Hex encoded text
        """
        return text.encode().hex()
    
    @staticmethod
    def hex_decode(hex_text):
        """Hexadecimal decoding
        
        Args:
            hex_text: Hex encoded text
            
        Returns:
            Decoded text
        """
        try:
            return bytes.fromhex(hex_text).decode()
        except Exception:
            return hex_text
    
    @staticmethod
    def binary_encode(text):
        """Binary encoding
        
        Args:
            text: Text to encode
            
        Returns:
            Binary encoded text
        """
        return ' '.join(format(ord(char), '08b') for char in text)
    
    @staticmethod
    def binary_decode(binary_text):
        """Binary decoding
        
        Args:
            binary_text: Binary encoded text
            
        Returns:
            Decoded text
        """
        try:
            # Remove spaces and decode
            binary_text = binary_text.replace(' ', '')
            chars = [chr(int(binary_text[i:i+8], 2)) for i in range(0, len(binary_text), 8)]
            return ''.join(chars)
        except Exception:
            return binary_text
    
    @staticmethod
    def url_encode(text):
        """URL encoding
        
        Args:
            text: Text to encode
            
        Returns:
            URL encoded text
        """
        import urllib.parse
        return urllib.parse.quote(text)
    
    @staticmethod
    def url_decode(encoded_text):
        """URL decoding
        
        Args:
            encoded_text: URL encoded text
            
        Returns:
            Decoded text
        """
        import urllib.parse
        return urllib.parse.unquote(encoded_text)


# Convenience functions
def encrypt_text(text, method='caesar', **kwargs):
    """Convenience function for encryption
    
    Args:
        text: Text to encrypt
        method: Encryption method (caesar, rot13, base64, aes)
        **kwargs: Method-specific parameters
        
    Returns:
        Encrypted text
    """
    tools = EncryptionTools()
    
    if method == 'caesar':
        shift = kwargs.get('shift', 3)
        return tools.caesar_cipher(text, shift)
    elif method == 'rot13':
        return tools.rot13(text)
    elif method == 'base64':
        return tools.base64_encode(text)
    elif method == 'aes':
        key = kwargs.get('key')
        if not key:
            key = tools.generate_key()
        return tools.aes_encrypt(text, key)
    else:
        return text

def decrypt_text(text, method='caesar', **kwargs):
    """Convenience function for decryption
    
    Args:
        text: Text to decrypt
        method: Decryption method (caesar, rot13, base64, aes)
        **kwargs: Method-specific parameters
        
    Returns:
        Decrypted text
    """
    tools = EncryptionTools()
    
    if method == 'caesar':
        shift = kwargs.get('shift', 3)
        return tools.caesar_cipher(text, shift, decrypt=True)
    elif method == 'rot13':
        return tools.rot13(text)
    elif method == 'base64':
        return tools.base64_decode(text)
    elif method == 'aes':
        key = kwargs.get('key')
        return tools.aes_decrypt(text, key)
    else:
        return text

def generate_all_hashes(text):
    """Convenience function to generate all hashes"""
    generator = HashGenerator()
    return generator.generate_hashes(text)

def identify_hash_type(hash_value):
    """Convenience function to identify hash type"""
    generator = HashGenerator()
    return generator.identify_hash(hash_value)

def encode_text(text, encoding='hex'):
    """Convenience function for encoding"""
    tools = EncodingTools()
    
    encodings = {
        'hex': tools.hex_encode,
        'binary': tools.binary_encode,
        'url': tools.url_encode,
        'base64': lambda x: base64.b64encode(x.encode()).decode()
    }
    
    encoder = encodings.get(encoding, lambda x: x)
    return encoder(text)

def decode_text(encoded_text, encoding='hex'):
    """Convenience function for decoding"""
    tools = EncodingTools()
    
    decodings = {
        'hex': tools.hex_decode,
        'binary': tools.binary_decode,
        'url': tools.url_decode,
        'base64': lambda x: base64.b64decode(x).decode()
    }
    
    decoder = decodings.get(encoding, lambda x: x)
    return decoder(encoded_text)