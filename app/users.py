import os
import uuid
from typing import Optional
from dotenv import load_dotenv
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

# Local imports
from app.db import User, get_user_db

# Load security environment variables
load_dotenv()

# SECRET: A string used to encrypt your JWT tokens. 
# SECURITY: We now load this from a .env file to keep it out of the source code.
SECRET = os.getenv("JWT_SECRET", "fallback-secret-key-for-local-dev-only")

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
