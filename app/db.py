"""
Database configuration and models for Aura Drive.

Architecture Notes:
- **aiosqlite**: We use the 'aiosqlite' driver because standard SQLite drivers are blocking (synchronous). 
  This allows our database calls to be non-blocking, keeping the FastAPI server responsive.
- **SQLAlchemy 2.0**: We use the modern Declarative model style for better type hinting and cleaner code.
"""

from sqlalchemy import ForeignKey
from typing import AsyncGenerator
import uuid 
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, UUID, Boolean 
from sqlalchemy.orm import DeclarativeBase, relationship 
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession 
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends

# The URL for connecting to the SQLite database
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

class Base(DeclarativeBase):
    """
    Base class for all database models.
    HOW: All models (User, Post) inherit from this so they are tracked by SQLAlchemy.
    """
    pass

class Post(Base):
    """
    Represents an uploaded asset in the system.
    """
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # user_id: Links this post to a specific user. 
    # ForeignKey ensures that we can't have a post without a valid user.
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    caption = Column(Text) 
    url = Column(String, nullable=False) 
    file_type = Column(String, nullable=False) 
    file_name = Column(String, nullable=False) 
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # user: A helper property that lets us access the user object directly from a post.
    # e.g., print(post.user.email)
    user = relationship("User", back_populates="posts")

# --- Engine & Session Setup ---

# engine: The main entry point for the database connection.
# echo=True: Logs every SQL query generated to your console (great for learning/debugging).
engine = create_async_engine(DATABASE_URL, echo=True)

# async_session_maker: A factory that creates new database sessions for each request.
# expire_on_commit=False: Prevents objects from being detached after a commit, 
# which is necessary for async workflows.
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_db_and_tables():
    """
    Creates the .db file and all tables if they don't exist yet.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency: Provides a fresh DB session for each API call.
    'async with' ensures the session is automatically closed (cleanup) after the route finishes.
    """
    async with async_session_maker() as session:
        yield session

class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    User model for authentication.
    """
    __tablename__ = "users"
    
    # cascade="all, delete-orphan": 
    # WHY: If a user deletes their account, we automatically delete all their posts too.
    # This keeps the database clean and prevents "ghost" data.
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """
    Adapter that connects our SQLAlchemy User model to the fastapi-users library.
    """
    yield SQLAlchemyUserDatabase(session, User)