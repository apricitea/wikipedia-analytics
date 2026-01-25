Here is a comprehensive documentation update for the `User` model, structured for a general project documentation page (e.g., using Sphinx, MkDocs, or a standard `README.md`).

---

# User Model Documentation

## Overview
The `User` model is the core representation of user accounts within the system. It handles authentication, profile management, and role-based access control. This document outlines the database schema, field constraints, relationships, and provides examples of how to utilize the model programmatically in Python.

---

## 1. Schema Definition

The `User` model maps to the `users` table in the database. Below is the attribute breakdown including data types, constraints, and default values.

| Field Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `Integer` | `Primary Key` | Unique identifier for the user. |
| `username` | `String` (max 50) | `Unique`, `Not Null` | The public-facing username used for login. |
| `email` | `String` (max 255) | `Unique`, `Not Null` | User's email address. Stored in lowercase. |
| `password_hash` | `String` (max 255) | `Not Null` | Securely hashed password (bcrypt/Argon2). Plain text is **never** stored. |
| `is_active` | `Boolean` | `Default: True` | Indicates if the account is currently active. |
| `is_staff` | `Boolean` | `Default: False` | Designates if the user can access the admin panel. |
| `role` | `Enum` | `Default: 'member'` | User permission level: `member`, `moderator`, or `admin`. |
| `created_at` | `DateTime` | `Not Null` | Timestamp of account creation. |
| `updated_at` | `DateTime` | `On Update` | Timestamp of last profile update. |

---

## 2. Relationships

The `User` model interacts with other parts of the system via the following relationships:

*   **Posts (One-to-Many):** A User can author multiple Posts.
    *   *Access via:* `user.posts`
*   **Profile (One-to-One):** A User has one extended Profile (bio, avatar URL).
    *   *Access via:* `user.profile`
*   **Followers (Many-to-Many):** A User can follow other Users (Self-referential).
    *   *Access via:* `user.followers` and `user.following`

---

## 3. Usage Examples

This section demonstrates common operations using the Python ORM (e.g., SQLAlchemy, Django ORM, or Peewee).

### 3.1 Creating a New User

When creating a user, **never** store the password in plain text. Always use the model's helper method to hash the password securely.

```python
from project.models import User

# Create a new user instance
new_user = User(
    username="jdoe",
    email="john.doe@example.com",
    role="member"
)

# Hash and set the password
new_user.set_password("secure_password_123")

# Save to database
from project.database import db
db.session.add(new_user)
db.session.commit()

print(f"User created with ID: {new_user.id}")
```

### 3.2 Authenticating a User

To verify login credentials, use the static `verify_password` method or the helper function provided by the model.

```python
username_input = "jdoe"
password_input = "secure_password_123"

# Retrieve user
user = User.query.filter_by(username=username_input).first()

if user and user.check_password(password_input):
    print("Login successful!")
else:
    print("Invalid credentials.")
```

### 3.3 Updating User Information

Standard field updates and password changes are handled as follows:

```python
# Retrieve user
user = User.query.get(1)

# Update simple fields
user.email = "new.email@example.com"

# Update password (handles hashing automatically)
user.set_password("new_secure_password")

# Commit changes
db.session.commit()
```

### 3.4 Querying by Role

You can filter users based on their role or status using standard query filters.

```python
# Find all inactive users
inactive_users = User.query.filter_by(is_active=False).all()

# Find all administrators
admins = User.query.filter_by(role='admin').all()
```

---

## 4. Security Considerations

1.  **Password Storage:** The `password` field is write-only. Reading the `password_hash` provides no utility for verification.
2.  **Email Uniqueness:** The application enforces lowercase email storage to ensure uniqueness (e.g., `User@Example.com` and `user@example.com` are treated as the same).
3.  **Mass Assignment:** For security reasons, certain fields (`is_staff`, `role`) are protected from mass assignment in API endpoints to prevent privilege escalation.