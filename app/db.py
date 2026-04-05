from sqlalchemy import ForeignKey
from typing import AsyncGenerator
import uuid # For generating unique IDs
from datetime import datetime # For handling date and time
from sqlalchemy import Column, String, Text, DateTime, UUID, Boolean # Core database types from SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship # Base class for defining our database models
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession # Async database support
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends
# The URL for connecting to the SQLite database (using 'aiosqlite' for async support)
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# A base class for all of our models to inherit from
class Base(DeclarativeBase):
    pass

# Our Post model representing the 'posts' table in the database
class Post(Base):
    __tablename__ = "posts" # The name of the table in the database

    # The unique ID of the post, automatically generated as a UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # The ID of the user who created the post, linked to the 'users' table
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # The text caption of the post
    caption = Column(Text)
    # The URL for the file (required)
    url = Column(String, nullable=False)
    # The type of file (image, video, etc.) (required)
    file_type = Column(String, nullable=False)
    # The name of the file (required)
    file_name = Column(String, nullable=False)
    # The timestamp when the post was created, defaults to the current UTC time
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="posts")


# Creating the async engine to handle the connection to the database
# 'echo=True' will log all generated SQL to your terminal
engine = create_async_engine(DATABASE_URL, echo=True)

# Creating a factory for database sessions
# 'expire_on_commit=False' prevents objects from becoming "stale" after saving
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Function to automatically create our database and tables if they don't exist
async def create_db_and_tables():
    async with engine.begin() as conn:
        # CORRECT: Use 'Base.metadata' (which tracks your models) instead of 'DeclarativeBase'
        await conn.run_sync(Base.metadata.create_all)

# Renamed 'get_async_sessiona' to 'get_async_session' to fix the typo
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseOAuthAccountTableUUID

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    
    # This links the user back to their posts
    # If a user is deleted, their posts will be deleted too (cascade)
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)