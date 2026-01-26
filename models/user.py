import re
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, validates, Session
from sqlalchemy.exc import IntegrityError

# Base class for declarative models
Base = declarative_base()

class User(Base):
    """
    User model with enforced validation logic.
    
    Attributes:
        id (int): Primary key.
        username (str): Unique username, must be 3-20 characters.
        email (str): Unique email address, must match standard format.
        full_name (str): Optional full name of the user.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)

    # Regex for basic email validation (RFC 5322 is too complex for a simple regex, 
    # this covers 99% of standard use cases)
    _EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    @validates('username')
    def validate_username(self, key, username):
        """
        Validates the username field.
        
        Rules:
        - Cannot be None/Empty.
        - Must be between 3 and 20 characters.
        - Must be alphanumeric (plus underscore).
        """
        if not username:
            raise ValueError("Username is required.")
        
        if not (3 <= len(username) <= 20):
            raise ValueError("Username must be between 3 and 20 characters.")
        
        # Ensure username is clean (alphanumeric + underscore)
        if not username.replace("_", "").isalnum():
            raise ValueError("Username must contain only alphanumeric characters or underscores.")

        return username

    @validates('email')
    def validate_email(self, key, email):
        """
        Validates the email field.
        
        Rules:
        - Cannot be None/Empty.
        - Must match standard email regex pattern.
        """
        if not email:
            raise ValueError("Email is required.")
        
        if not self._EMAIL_REGEX.match(email):
            raise ValueError("Invalid email format.")
        
        return email

    @validates('full_name')
    def validate_full_name(self, key, full_name):
        """
        Validates the full_name field.
        
        Rules:
        - If provided, must not be an empty string.
        """
        # Allow None (nullable), but reject empty strings if passed
        if full_name is not None and len(full_name.strip()) == 0:
            raise ValueError("Full name cannot be an empty string.")
            
        return full_name.strip() if full_name else None

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

# Example Usage Block
if __name__ == "__main__":
    # In-memory SQLite database for demonstration
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    session = Session(engine)

    print("--- Testing Valid User ---")
    try:
        user = User(username="jdoe_99", email="john@example.com", full_name="John Doe")
        session.add(user)
        session.commit()
        print(f"Success: {user}")
    except ValueError as e:
        print(f"Validation Error: {e}")
    except Exception as e:
        print(f"Database Error: {e}")

    print("\n--- Testing Invalid Username (Too Short) ---")
    try:
        bad_user = User(username="ab", email="alice@example.com")
        session.add(bad_user)
        session.commit()
    except ValueError as e:
        print(f"Caught Expected Error: {e}")

    print("\n--- Testing Invalid Email Format ---")
    try:
        bad_user = User(username="alice", email="alice-at-example.com")
        session.add(bad_user)
        session.commit()
    except ValueError as e:
        print(f"Caught Expected Error: {e}")

    print("\n--- Testing Missing Required Field ---")
    try:
        bad_user = User(username="bob")
        # Email is missing, defaults to None in constructor if not passed
        # but validator catches None
        session.add(bad_user)
        session.commit()
    except ValueError as e:
        print(f"Caught Expected Error: {e}")