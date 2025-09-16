import hashlib
import secrets

def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with salt
    For a student project, this is sufficient
    """
    # Generate a random salt
    salt = secrets.token_hex(16)
    
    # Combine password and salt
    password_salt = password + salt
    
    # Hash using SHA-256
    password_hash = hashlib.sha256(password_salt.encode()).hexdigest()
    
    # Return salt + hash (salt is first 32 chars, hash is last 64 chars)
    return salt + password_hash

def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against its stored hash
    """
    if not stored_hash or len(stored_hash) != 96:  # 32 (salt) + 64 (hash)
        return False
    
    # Extract salt and hash
    salt = stored_hash[:32]
    stored_password_hash = stored_hash[32:]
    
    # Hash the provided password with the same salt
    password_salt = password + salt
    password_hash = hashlib.sha256(password_salt.encode()).hexdigest()
    
    # Compare hashes
    return password_hash == stored_password_hash
