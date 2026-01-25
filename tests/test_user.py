import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

# Assuming the User model is in a module named 'models'
# If your structure is different, adjust the import accordingly.
# from models import User

# --- Mocking the User Model for Context ---
# In a real scenario, you would import this. 
# I am defining it here so the tests are runnable and demonstrate the logic.
from pydantic import BaseModel, EmailStr, Field, validator

class User(BaseModel):
    id: int
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    age: int = Field(..., ge=18, le=120)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('must be alphanumeric')
        return v

# --- End Mock Model ---

class TestUserInstantiation:
    """
    Tests focusing on the successful instantiation and default values
    of the User model.
    """

    def test_user_creation_with_valid_data(self):
        """
        Test that a User object is created successfully with all valid fields.
        """
        # Arrange
        user_data = {
            "id": 1,
            "username": "jdoe",
            "email": "john.doe@example.com",
            "age": 30
        }

        # Act
        user = User(**user_data)

        # Assert
        assert user.id == 1
        assert user.username == "jdoe"
        assert user.email == "john.doe@example.com"
        assert user.age == 30
        assert user.is_active is True  # Checking default value

    def test_user_default_values(self):
        """
        Test that default values are correctly assigned when optional fields 
        are omitted.
        """
        # Arrange
        user_data = {
            "id": 2,
            "username": "alice",
            "email": "alice@test.com",
            "age": 25
        }

        # Act
        user = User(**user_data)

        # Assert
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)
        # Check that created_at is very recent (within last second)
        assert (datetime.utcnow() - user.created_at) < timedelta(seconds=1)

    def test_user_model_export_to_dict(self):
        """
        Test that the model can be correctly exported back to a dictionary.
        """
        # Arrange
        user_data = {
            "id": 3,
            "username": "bob",
            "email": "bob@example.com",
            "age": 40
        }
        user = User(**user_data)

        # Act
        user_dict = user.dict()

        # Assert
        assert user_dict["username"] == "bob"
        assert user_dict["is_active"] is True


class TestUsernameValidation:
    """
    Tests specifically for username field constraints (length, characters).
    """

    def test_username_too_short(self):
        """
        Test that validation fails if username is shorter than 3 characters.
        """
        # Arrange
        user_data = {
            "id": 1,
            "username": "ab",  # Too short
            "email": "test@example.com",
            "age": 20
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            User(**user_data)
        
        # Verify the error message contains context about length
        assert "ensure this value has at least 3 characters" in str(exc_info.value).lower()

    def test_username_too_long(self):
        """
        Test that validation fails if username exceeds 20 characters.
        """
        # Arrange
        user_data = {
            "id": 1,
            "username": "a" * 21,  # Too long
            "email": "test@example.com",
            "age": 20
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            User(**user_data)
        assert "ensure this value has at most 20 characters" in str(exc_info.value).lower()

    def test_username_non_alphanumeric(self):
        """
        Test that validation fails if username contains special characters.
        """
        # Arrange
        user_data = {
            "id": 1,
            "username": "user@name",  # Invalid character
            "email": "test@example.com",
            "age": 20
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            User(**user_data)
        assert "must be alphanumeric" in str(exc_info.value).lower()


class TestEmailValidation:
    """
    Tests for email format validation.
    """

    def test_email_invalid_format(self):
        """
        Test that validation fails for malformed email addresses.
        """
        # Arrange
        invalid_emails = [
            "plainaddress",
            "@missingusername.com",
            "username@.com",
            "username@com"
        ]

        for email in invalid_emails:
            user_data = {
                "id": 1,
                "username": "validuser",
                "email": email,
                "age": 20
            }

            # Act & Assert
            with pytest.raises(ValidationError):
                User(**user_data)


class TestAgeValidation:
    """
    Tests for age boundary conditions (min/max values).
    """

    def test_age_below_minimum(self):
        """
        Test that validation fails if age is less than 18.
        """
        # Arrange
        user_data = {
            "id": 1,
            "username": "younguser",
            "email": "young@example.com",
            "age": 17
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            User(**user_data)
        assert "ensure this value is greater than or equal to 18" in str(exc_info.value).lower()

    def test_age_above_maximum(self):
        """
        Test that validation fails if age is greater than 120.
        """
        # Arrange
        user_data = {
            "id": 1,
            "username": "olduser",
            "email": "old@example.com",
            "age": 121
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            User(**user_data)
        assert "ensure this value is less than or equal to 120" in str(exc_info.value).lower()

    def test_age_boundary_values(self):
        """
        Test that boundary values (18 and 120) are accepted.
        """
        # Arrange & Act (Lower Boundary)
        user_min = User(id=1, username="min_age", email="min@test.com", age=18)
        
        # Arrange & Act (Upper Boundary)
        user_max = User(id=2, username="max_age", email="max@test.com", age=120)

        # Assert
        assert user_min.age == 18
        assert user_max.age == 120


class TestRequiredFields:
    """
    Tests to ensure required fields raise errors when missing.
    """

    def test_missing_id(self):
        """Test that 'id' is required."""
        with pytest.raises(ValidationError) as exc_info:
            User(username="test", email="test@test.com", age=20)
        assert "field required" in str(exc_info.value).lower()
        assert "id" in str(exc_info.value).lower()

    def test_missing_username(self):
        """Test that 'username' is required."""
        with pytest.raises(ValidationError) as exc_info:
            User(id=1, email="test@test.com", age=20)
        assert "field required" in str(exc_info.value).lower()
        assert "username" in str(exc_info.value).lower()

    def test_missing_email(self):
        """Test that 'email' is required."""
        with pytest.raises(ValidationError) as exc_info:
            User(id=1, username="test", age=20)
        assert "field required" in str(exc_info.value).lower()
        assert "email" in str(exc_info.value).lower()

    def test_missing_age(self):
        """Test that 'age' is required."""
        with pytest.raises(ValidationError) as exc_info:
            User(id=1, username="test", email="test@test.com")
        assert "field required" in str(exc_info.value).lower()
        assert "age" in str(exc_info.value).lower()