"""JWT authentication service."""
import os
import jwt
import hashlib
import secrets
from typing import Optional, Dict
from datetime import datetime, timedelta
from backend.models.database import get_session
from backend.models.token_blacklist import TokenBlacklist

# Try to use passlib, fallback to bcrypt directly if passlib has issues
try:
    from passlib.context import CryptContext
    # Initialize with error handling for bcrypt bug detection issue
    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # Test initialization - this may fail during passlib's bug detection
        _test_hash = pwd_context.hash("test_init")
        _verify_ok = pwd_context.verify("test_init", _test_hash)
        USE_PASSLIB = True
    except (ValueError, AttributeError, Exception) as e:
        # If passlib fails, we'll use bcrypt directly
        USE_PASSLIB = False
        pwd_context = None
except ImportError:
    USE_PASSLIB = False
    pwd_context = None

# Fallback to bcrypt directly if passlib doesn't work
if not USE_PASSLIB:
    try:
        import bcrypt
        USE_BCRYPT_DIRECT = True
    except ImportError:
        USE_BCRYPT_DIRECT = False
        raise ImportError("Neither passlib nor bcrypt are available for password hashing")

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))


class AuthService:
    """Handles JWT authentication and user management."""
    
    def __init__(self):
        """Initialize auth service."""
        self.secret_key = JWT_SECRET_KEY
        self.algorithm = JWT_ALGORITHM
    
    def create_access_token(self, user_id: str, email: Optional[str] = None) -> str:
        """
        Create JWT access token.
        
        Args:
            user_id: User identifier
            email: User email (optional)
            
        Returns:
            Encoded JWT token
        """
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Create JWT refresh token.
        
        Args:
            user_id: User identifier
            
        Returns:
            Encoded JWT refresh token
        """
        expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token to verify
            token_type: Type of token (access or refresh)
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != token_type:
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Create new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token or None if refresh token invalid
        """
        payload = self.verify_token(refresh_token, token_type="refresh")
        if not payload:
            return None
        
        user_id = payload.get("sub")
        email = payload.get("email")
        return self.create_access_token(user_id, email)
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        if USE_PASSLIB and pwd_context:
            # Bcrypt has a 72-byte limit, truncate if necessary
            if isinstance(password, str):
                password_bytes = password.encode('utf-8')
                if len(password_bytes) > 72:
                    password = password_bytes[:72].decode('utf-8', errors='ignore')
            return pwd_context.hash(password)
        else:
            # Use bcrypt directly
            import bcrypt
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        if USE_PASSLIB and pwd_context:
            try:
                return pwd_context.verify(plain_password, hashed_password)
            except Exception:
                # Fallback to direct bcrypt if passlib fails
                pass
        
        # Use bcrypt directly (fallback or primary method)
        import bcrypt
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        try:
            # Handle both string and bytes hash
            if isinstance(hashed_password, str):
                hash_bytes = hashed_password.encode('utf-8')
            else:
                hash_bytes = hashed_password
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            return False
    
    def generate_user_id(self, email: str) -> str:
        """
        Generate a user ID from email.
        
        Args:
            email: User email
            
        Returns:
            User ID (hash of email)
        """
        return hashlib.sha256(email.encode()).hexdigest()[:16]
    
    def blacklist_token(self, token: str, user_id: str, token_type: str = "access") -> bool:
        """
        Add a token to the blacklist.
        
        Args:
            token: JWT token to blacklist
            user_id: User ID who owns the token
            token_type: Type of token (access or refresh)
            
        Returns:
            True if token was blacklisted successfully
        """
        try:
            # Decode token to get expiration
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            expires_at = datetime.utcfromtimestamp(payload.get("exp", 0))
            
            # Create token hash
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            db = get_session()
            try:
                # Check if already blacklisted
                existing = db.query(TokenBlacklist).filter(TokenBlacklist.token_hash == token_hash).first()
                if existing:
                    return True
                
                # Add to blacklist
                blacklist_entry = TokenBlacklist(
                    id=token_hash[:32],  # Use first 32 chars as ID
                    token_hash=token_hash,
                    user_id=user_id,
                    token_type=token_type,
                    expires_at=expires_at,
                    blacklisted_at=datetime.utcnow()
                )
                db.add(blacklist_entry)
                db.commit()
                return True
            finally:
                db.close()
        except Exception as e:
            # Log error but don't fail
            import logging
            logging.error(f"Failed to blacklist token: {e}")
            return False
    
    def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted.
        
        Args:
            token: JWT token to check
            
        Returns:
            True if token is blacklisted
        """
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            db = get_session()
            try:
                blacklisted = db.query(TokenBlacklist).filter(
                    TokenBlacklist.token_hash == token_hash
                ).first()
                return blacklisted is not None
            finally:
                db.close()
        except Exception:
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """
        Remove expired tokens from blacklist.
        
        Returns:
            Number of tokens removed
        """
        try:
            db = get_session()
            try:
                deleted = db.query(TokenBlacklist).filter(
                    TokenBlacklist.expires_at < datetime.utcnow()
                ).delete()
                db.commit()
                return deleted
            finally:
                db.close()
        except Exception:
            return 0


# Global auth service instance
auth_service = AuthService()


def get_auth_service() -> AuthService:
    """Return the global AuthService instance (for DI/testing)."""
    return auth_service
