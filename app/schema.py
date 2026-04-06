"""
Pydantic schemas for data validation and serialization in Aura Drive.

Architecture Notes:
- **Pydantic**: We use Pydantic to ensure that data coming from the frontend is 'safe' and correctly formatted.
  If a user sends a string where a number is expected, Pydantic catches it immediately before our logic runs.
- **Separation of Concerns**: We define separate schemas for 'Read', 'Create', and 'Update' operations.
  This allows us to control exactly which fields a user is allowed to see or modify.
"""

from pydantic import BaseModel
from fastapi_users import schemas
import uuid
from typing import Optional

# --- Post Schemas ---

class createPost(BaseModel):
    """
    Schema for creating a new post.
    HOW: The frontend sends a 'title' and 'description' as JSON. 
    FastAPI uses this class to validate that both fields exist and are strings.
    """
    title: str
    description: str

class responsePost(BaseModel):
    """
    Schema for the post data returned by our API.
    HOW: This defines the 'shape' of the JSON the frontend receives. 
    We can exclude internal database fields here if needed.
    """
    title: str
    description: str

# --- User Schemas ---
# These classes extend the 'fastapi-users' base schemas to integrate with our UUID primary key.

class UserRead(schemas.BaseUser[uuid.UUID]):
    """
    Returned when someone asks for user details.
    """
    pass

class UserCreate(schemas.BaseUserCreate):
    """
    Required fields for new user registration.
    """
    pass

class UserUpdate(schemas.BaseUserUpdate):
    """
    Fields that a user is allowed to change on their own profile.
    """
    pass

class UserAuth(BaseModel):
    """
    Structure used for basic email/password authentication checks.
    """
    email: str
    password: str
    is_active: Optional[bool] = True


    