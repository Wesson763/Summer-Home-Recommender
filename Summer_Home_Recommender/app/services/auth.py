"""
Authentication service for the Summer Home Finder application.

Handles user account creation, authentication, and profile management.
"""

import uuid
from app.models.user import User

def create_user_account(name: str, email: str, password: str) -> tuple[User, str]:
    """
    Create a new user account with password validation.
    
    Args:
        name: User's full name
        email: User's email address
        password: User's password (will be validated)
    
    Returns:
        Tuple of (User object, success/error message)
    """
    user_id = str(uuid.uuid4())
    
    # Validate password
    is_valid, message = User.validate_password(password)
    if not is_valid:
        return None, message
    
    user = User(user_id=user_id, name=name, email=email, password=password)
    return user, "Account created successfully"

def authenticate_user(email: str, password: str) -> User:
    """
    Authenticate user by email and password.
    
    Args:
        email: User's email address
        password: User's password
    
    Returns:
        User object if authentication successful, None otherwise
    """
    return User.authenticate(email, password)

def create_user_from_input() -> User:
    """
    Create a user from command line input (for CLI usage).
    
    Returns:
        User object if creation successful, None otherwise
    """
    # Generate a unique ID
    while True:
        user_id = str(uuid.uuid4())
        if user_id not in User.all_users:
            break

    name = input("Your Name: ").strip()
    email = input("Your Email: ").strip()
    
    # Password input with validation
    while True:
        password = input("Your Password: ").strip()
        is_valid, message = User.validate_password(password)
        if is_valid:
            break
        else:
            print(f"❌ {message}")
            print("Password requirements:")
            print("  - At least 8 characters long")
            print("  - At least one uppercase letter")
            print("  - At least one lowercase letter")
            print("  - At least one number")
            print("  - At least one symbol")
    
    # Confirm password
    confirm_password = input("Confirm Password: ").strip()
    if password != confirm_password:
        print("❌ Passwords do not match!")
        return None
    
    return User(user_id=user_id, name=name, email=email, password=password)

def validate_user_credentials(email: str, password: str) -> bool:
    """
    Validate user credentials without creating a session.
    
    Args:
        email: User's email address
        password: User's password
    
    Returns:
        True if credentials are valid, False otherwise
    """
    user = User.find_by_email(email)
    if user and user.check_password(password):
        return True
    return False

def get_user_by_email(email: str) -> User:
    """
    Get user by email address.
    
    Args:
        email: User's email address
    
    Returns:
        User object if found, None otherwise
    """
    return User.find_by_email(email)
