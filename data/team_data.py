"""
data/team_data.py

This module defines the data structures for managing team member information.
It utilizes Pydantic for robust data validation and settings management,
ensuring that team member data adheres to specific constraints before being
used in the application.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class Role(str, Enum):
    """
    Enumeration of possible roles within the team.
    
    Attributes:
        DEVELOPER: Standard software engineer role.
        DESIGNER: UI/UX design role.
        PRODUCT_MANAGER: Product management role.
        QA_ENGINEER: Quality assurance role.
        DEVOPS: Infrastructure and operations role.
    """
    DEVELOPER = "Developer"
    DESIGNER = "Designer"
    PRODUCT_MANAGER = "Product Manager"
    QA_ENGINEER = "QA Engineer"
    DEVOPS = "DevOps"


class TeamMember(BaseModel):
    """
    Represents a single member of the team.
    
    This model enforces data validation on fields such as email format,
    ensures required fields are present, and allows for optional metadata.
    
    Attributes:
        id (int): The unique identifier for the team member.
        name (str): The full name of the team member.
        email (EmailStr): A valid email address for the member.
        role (Role): The specific role the member plays within the team.
        skills (List[str]): A list of technical or professional skills.
        years_experience (int): Number of years the member has been in the workforce.
        is_active (bool): Flag indicating if the member is currently active. Defaults to True.
        bio (Optional[str]): A short biography or description of the member.
    """
    
    id: int = Field(..., description="Unique identifier for the team member")
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the employee")
    email: EmailStr = Field(..., description="Professional email address")
    role: Role = Field(..., description="Job title or role within the team")
    skills: List[str] = Field(default_factory=list, description="List of technical skills")
    years_experience: int = Field(..., ge=0, le=50, description="Total years of professional experience")
    is_active: bool = Field(default=True, description="Employment status")
    bio: Optional[str] = Field(None, max_length=500, description="Short professional biography")

    @field_validator('name')
    @classmethod
    def name_must_not_contain_numbers(cls, v: str) -> str:
        """Validates that the name field does not contain numeric characters."""
        if any(char.isdigit() for char in v):
            raise ValueError('Name must not contain numbers')
        return v

    @field_validator('skills')
    @classmethod
    def skills_must_be_unique(cls, v: List[str]) -> List[str]:
        """Validates that the list of skills contains no duplicates."""
        if len(v) != len(set(v)):
            raise ValueError('Skills list must contain unique items')
        # Return sorted list for consistency
        return sorted([skill.lower() for skill in v])

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "role": "Developer",
                "skills": ["Python", "FastAPI", "Docker"],
                "years_experience": 5,
                "is_active": True,
                "bio": "Senior backend developer passionate about clean architecture."
            }
        }


class TeamDirectory(BaseModel):
    """
    A container structure holding a collection of team members.
    
    This acts as a root object for serialization/deserialization of the entire
    team dataset.
    
    Attributes:
        members (List[TeamMember]): A list of TeamMember objects.
    """
    members: List[TeamMember] = Field(default_factory=list, description="Collection of team members")

    def get_active_members(self) -> List[TeamMember]:
        """Helper method to retrieve only active team members."""
        return [member for member in self.members if member.is_active]

    def find_member_by_id(self, member_id: int) -> Optional[TeamMember]:
        """Helper method to locate a specific member by their ID."""
        for member in self.members:
            if member.id == member_id:
                return member
        return None