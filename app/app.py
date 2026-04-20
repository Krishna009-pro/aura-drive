"""
Core FastAPI application logic for Aura Drive.

Architecture Notes:
- **Dependency Injection**: We use FastAPI's 'Depends' to inject the database session and the current user.
- **Asynchrony**: Every route is 'async', meaning the server doesn't wait for one request to finish before starting another—it "pauses" during slow I/O (like database or network calls), allowing for much higher performance.
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager

from app.images import image_kit 
import shutil
import os
import uuid
import tempfile

# Local project imports
from app.schema import createPost, responsePost
from app.db import Post, create_db_and_tables, get_async_session
from app.users import auth_backend, current_active_user, fastapi_users, User
from app.schema import UserCreate, UserUpdate, UserRead, UserAuth

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events handle startup and shutdown tasks.
    WHY: This ensures our database is ready as soon as the server accepts its first request.
    """
    await create_db_and_tables()
    yield

# Initialize the FastAPI app with the lifespan manager
app = FastAPI(
    title="Aura Drive API",
    description="Backend for Aura Drive - A Premium Cloud Storage platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS (Cross-Origin Resource Sharing)
# This is REQUIRED for production if your frontend and backend are hosted on different domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your specific deployment domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (HTML, CSS, JS) from the 'static' directory
# WHY: This allows the backend to host the frontend directly, making deployment simpler.
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """
    Redirect the root URL to the frontend UI for a seamless user experience.
    """
    return RedirectResponse(url="/static/index.html")

@app.post("/uploadfile")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    How the Upload Process Works:
    1. **Temporary Storage**: We save the uploaded file to the local disk temporarily. 
       WHY: Sending large files directly through memory can be risky; disks are safer and more scalable.
    2. **Cloud Hand-off**: We send that local file to ImageKit cloud storage.
    3. **Metadata Persistence**: We save the Cloud URL back into our SQLite database, linked to the user's ID.
    4. **Safety**: We use a 'try/finally' block to ensure the temporary file is deleted even if something crashes.
    """
    temp_file_path = None
    try:
        # Step 1: Create a temporary file to store the upload before sending to ImageKit
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        
        # Step 2: Upload the temporary file to ImageKit cloud storage
        # ImageKit handles CDN distribution and storage optimization for us.
        with open(temp_file_path, "rb") as f:
            upload_result = image_kit.files.upload(
                file=f,
                file_name=file.filename,
                tags=["backend-upload"],
                use_unique_file_name=True
            )

        if upload_result:
            # Step 3: Create a new database record for the post
            post = Post(
                caption = caption,
                url = upload_result.url,
                file_type = upload_result.file_type,
                file_name = upload_result.name,
                user_id = user.id 
            )
            session.add(post)
            await session.commit()
            await session.refresh(post) # Sync 'post' with any DB-generated fields (like created_at)
            
            return {
                "id": str(post.id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at
            }

    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    finally:
        # Step 4: Clean up the temporary file from the server disk
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Retrieve all posts (assets) from the database.
    HOW: We use SQLAlchemy's 'select' to fetch all records from the 'posts' table, 
    ordering them so the most recent uploads appear at the top of the user's feed.
    """
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()] 
    
    posts_data = []
    for post in posts:
        posts_data.append({
            "id": post.id,
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at,
            "user_id": post.user_id 
        })
    return {"posts": posts_data }

@app.delete("/posts/{post_id}")
async def delete_post( 
    post_id: str, 
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Delete a post safely.
    HOW: 
    1. Convert the 'post_id' string into a proper 'UUID' object for database comparison.
    2. AUTHORIZATION CHECK: We compare the 'user_id' stored on the post with the 'id' of the currently 
       logged-in user. This ensures that only the owner can delete their files.
    """
    try:
        post_uuid = uuid.UUID(post_id)
        
        # Look up the post in the database
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # AUTHORIZATION CHECK: Prevent users from deleting each other's content
        if post.user_id != user.id and not user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        
        await session.delete(post)
        await session.commit()
        
        return {"success": True, "message": "Post deleted successfully"}
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Delete operation failed: {str(e)}")

# --- Authentication Routers ---
# These routes are automatically handled by fastapi-users to provide standard auth features:
# - JWT login (returns an access token)
# - Registration (validates email uniqueness and hashes passwords)
# - User profile management (GET/PATCH)
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

