"""
User management and authentication configuration for Aura Drive.

Architecture Notes:
- **FastAPI Users**: An off-the-shelf library that handles the "messy" parts of auth, like 
  password hashing, email verification, and token generation.
- **JWT (JSON Web Token)**: We use JWTs for authentication. These are small, encrypted, 
  tamper-proof strings that the backend gives to the frontend.
- **Stateless Auth**: Since we use JWTs, the backend doesn't need to "remember" every user 
  in memory. It just validates the incoming token on every request.
"""

from fastapi_users.authentication import AuthenticationBackend
import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy
)
from fastapi_users.db import SQLAlchemyBaseUserTable
from app.db import User, get_user_db

# SECRET: A string used to encrypt your JWT tokens. 
# SECURITY: Never share this. If someone knows your secret, they can fake tokens for any user.
SECRET = "oiwankdlnringnaa"

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """
    Handles user lifecycle logic. 
    It communicates with the database via SQLAlchemy and triggers the 'callbacks' below.
    """
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """ Logged after someone creates a new account via the /auth/register route. """
        print(f"User {user.id} has registered")

    async def on_after_request_verify(self, user: User, request: Optional[Request] = None):
        """ Logged after someone verifies their email. """
        print(f"User {user.id} has verified their email")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        """ Logged after someone requests a reset password link. """
        print(f"User {user.id} has forgot their password")


async def get_user_manager(user_db = Depends(get_user_db)):
    """ 
    Dependency provider that builds a UserManager instance for our routes. 
    """
    yield UserManager(user_db)

# Bearer_transport: Tells the browser how to send the token back to us.
# 'Bearer' means the token goes in the 'Authorization' header of every request.
Bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    """ 
    Defines how the token itself is created (using our SECRET) and how long it lasts (3600 seconds = 1 hour).
    """
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

# auth_backend: Combines the 'Transport' and 'Strategy' into a single authentication plan.
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=Bearer_transport,
    get_strategy=get_jwt_strategy,
)

# fastapi_users: The main engine. We feed it our UserManager and our Auth Backend, 
# and it generates all the routes (Login, Register, Users, etc.) automatically.
fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend]
)

# current_active_user: A helper that we can use in any route to find out 
# who is making the request. It automatically validates the JWT token.
current_active_user = fastapi_users.current_user(active=True)
