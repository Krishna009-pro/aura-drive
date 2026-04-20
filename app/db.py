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

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# The URL for connecting to the database. 
# In production, this can be swapped for PostgreSQL via environment variables.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# Render and SQLAlchemy compatibility fix:
# 1. Render provides 'postgres://', but SQLAlchemy 2.0 requires 'postgresql://'
# 2. For async calls, we need the '+asyncpg' driver suffix.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

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
if "sqlite" in DATABASE_URL:
    engine = create_async_engine(DATABASE_URL, echo=True)
else:
    # For PostgreSQL, we add some connection pooling settings for better performance on Render.
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        pool_pre_ping=True, # Automatically reconnects if the cloud database times out
        pool_size=5,        # Keeps 5 connections ready to use
        max_overflow=10     # Allows 10 extra temporary connections during bursts
    )

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
