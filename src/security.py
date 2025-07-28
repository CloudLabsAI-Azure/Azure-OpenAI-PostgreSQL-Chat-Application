"""
Security Module for Azure OpenAI PostgreSQL Chat Application
Provides comprehensive security features including authentication, authorization, and input validation.
"""

import os
import logging
import jwt
import bcrypt
import secrets
import re
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Dict, Any, Optional, List
from flask import request, jsonify, session
import ipaddress
from cryptography.fernet import Fernet

# Configure logging
logger = logging.getLogger(__name__)

class SecurityManager:
    """
    Comprehensive security manager for the application.
    """
    
    def __init__(self):
        """Initialize security manager with configurations."""
        self.jwt_secret = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32))
        self.encryption_key = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Rate limiting configurations
        self.rate_limits = {
            'chat': {'requests': 30, 'window': 60},  # 30 requests per minute
            'analytics': {'requests': 10, 'window': 60},  # 10 requests per minute
            'health': {'requests': 100, 'window': 60}  # 100 requests per minute
        }
        
        # SQL injection patterns
        self.sql_injection_patterns = [
            r'(\b(?:union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
            r'(--|\#|\/\*|\*\/)',
            r'(\b(?:or|and)\s+\d+\s*=\s*\d+)',
            r'(\b(?:or|and)\s+[\'"].*[\'"])',
            r'(;|\|\||&&)'
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r'<\s*script[^>]*>.*?<\s*/\s*script\s*>',
            r'javascript\s*:',
            r'on\w+\s*=',
            r'<\s*iframe[^>]*>',
            r'<\s*object[^>]*>',
            r'<\s*embed[^>]*>'
        ]
        
        # Allowed IP ranges (example - adjust as needed)
        self.allowed_ip_ranges = [
            '127.0.0.0/8',     # localhost
            '10.0.0.0/8',      # private networks
            '172.16.0.0/12',   # private networks
            '192.168.0.0/16'   # private networks
        ]

    def generate_session_token(self, user_id: str, expiry_hours: int = 24) -> str:
        """
        Generate a secure JWT session token.
        
        Args:
            user_id: User identifier
            expiry_hours: Token expiry in hours
            
        Returns:
            JWT token string
        """
        try:
            payload = {
                'user_id': user_id,
                'iat': datetime.now(timezone.utc),
                'exp': datetime.now(timezone.utc) + timedelta(hours=expiry_hours),
                'session_id': secrets.token_urlsafe(16)
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            logger.info(f"Session token generated for user: {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating session token: {str(e)}")
            raise

    def validate_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT session token.
        
        Args:
            token: JWT token to validate
            
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check if token is expired
            if datetime.now(timezone.utc) > datetime.fromtimestamp(payload['exp'], timezone.utc):
                logger.warning("Token expired")
                return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None

    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            hashed: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def encrypt_data(self, data: str) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data as string
        """
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted data as string
        """
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

    def validate_input(self, input_text: str, max_length: int = 1000) -> Dict[str, Any]:
        """
        Comprehensive input validation.
        
        Args:
            input_text: Input to validate
            max_length: Maximum allowed length
            
        Returns:
            Validation result dictionary
        """
        result = {
            'valid': True,
            'sanitized': input_text.strip(),
            'warnings': []
        }
        
        # Length check
        if len(input_text) > max_length:
            result['valid'] = False
            result['warnings'].append(f"Input exceeds maximum length of {max_length} characters")
            return result
        
        # SQL injection check
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                result['valid'] = False
                result['warnings'].append("Potential SQL injection detected")
                logger.warning(f"SQL injection attempt detected: {input_text[:100]}...")
                break
        
        # XSS check
        for pattern in self.xss_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                result['valid'] = False
                result['warnings'].append("Potential XSS attack detected")
                logger.warning(f"XSS attempt detected: {input_text[:100]}...")
                break
        
        # Sanitize input
        if result['valid']:
            # Remove potentially dangerous characters
            result['sanitized'] = re.sub(r'[<>"\']', '', input_text.strip())
        
        return result

    def check_ip_whitelist(self, ip_address: str) -> bool:
        """
        Check if IP address is in allowed ranges.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            True if allowed, False otherwise
        """
        try:
            ip = ipaddress.ip_address(ip_address)
            
            for range_str in self.allowed_ip_ranges:
                if ip in ipaddress.ip_network(range_str):
                    return True
                    
            logger.warning(f"IP address not in whitelist: {ip_address}")
            return False
            
        except ValueError:
            logger.warning(f"Invalid IP address: {ip_address}")
            return False

    def get_client_ip(self) -> str:
        """
        Get client IP address from request.
        
        Returns:
            Client IP address
        """
        # Check for forwarded headers (behind proxy/load balancer)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
            
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
            
        return request.remote_addr

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """
        Log security events for monitoring.
        
        Args:
            event_type: Type of security event
            details: Event details
        """
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'ip_address': self.get_client_ip(),
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'details': details
        }
        
        logger.warning(f"Security Event: {event_type} - {log_entry}")

# Security decorators
def require_valid_session(f):
    """Decorator to require valid session token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
            
        token = auth_header.split(' ')[1]
        security_manager = SecurityManager()
        payload = security_manager.validate_session_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
            
        # Add user info to request context
        request.user_id = payload['user_id']
        request.session_id = payload['session_id']
        
        return f(*args, **kwargs)
    return decorated_function

def validate_input_security(max_length: int = 1000):
    """Decorator to validate input security."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            security_manager = SecurityManager()
            
            # Validate JSON input if present
            if request.is_json:
                data = request.get_json()
                if data and isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, str):
                            validation = security_manager.validate_input(value, max_length)
                            if not validation['valid']:
                                security_manager.log_security_event('invalid_input', {
                                    'field': key,
                                    'warnings': validation['warnings']
                                })
                                return jsonify({
                                    'error': 'Invalid input detected',
                                    'warnings': validation['warnings']
                                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_ip_whitelist_decorator(f):
    """Decorator to check IP whitelist."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        security_manager = SecurityManager()
        client_ip = security_manager.get_client_ip()
        
        if not security_manager.check_ip_whitelist(client_ip):
            security_manager.log_security_event('ip_blocked', {
                'ip_address': client_ip
            })
            return jsonify({'error': 'Access denied'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

# Initialize global security manager
security_manager = SecurityManager()
