# Define User Class
class User:

    all_users = [] # Create list to store all user object/instance

    def __init__(self, user_id, name, email, password=None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password  # Store password hash in production

        User.all_users.append(self)  # Add user profile to the list so we can pop/delete later.

    @staticmethod
    def validate_password(password):
        """Validate password strength according to requirements"""
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        # Check for symbols (non-alphanumeric characters)
        if not any(not c.isalnum() for c in password):
            return False, "Password must contain at least one symbol"
        
        return True, "Password meets all requirements"

    def set_password(self, password):
        """Set password with validation"""
        is_valid, message = self.validate_password(password)
        if is_valid:
            self.password = password  # In production, hash this password
            return True, message
        else:
            return False, message

    def check_password(self, password):
        """Check if provided password matches stored password"""
        return self.password == password  # In production, compare hashes

    def update_profile(self, **kwargs):
        """Edits any valid key-value pairs for a given user"""
        for key, value in kwargs.items():
            if key == 'user_id':
                raise ValueError("User ID cannot be edited")
            elif key == 'password':
                # Special handling for password updates
                success, message = self.set_password(value)
                if not success:
                    raise ValueError(f"Password validation failed: {message}")
            elif hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def find_by_email(cls, email):
        """Find a user by email address"""
        for user in cls.all_users:
            if user.email == email:
                return user
        return None

    @classmethod
    def authenticate(cls, email, password):
        """Authenticate user with email and password"""
        user = cls.find_by_email(email)
        if user and user.check_password(password):
            return user
        return None