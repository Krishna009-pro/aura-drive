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
from sqlalchemy.orm import selectinload
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
cors_origins_env = os.getenv("CORS_ORIGINS", "")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
if not cors_origins:
    cors_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=os.getenv("CORS_ORIGIN_REGEX"),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

serve_static_frontend = os.getenv("SERVE_STATIC_FRONTEND", "0") == "1"
static_dist_dir = "static/dist"
if serve_static_frontend and os.path.isdir(static_dist_dir):
    app.mount("/static", StaticFiles(directory=static_dist_dir), name="static")

@app.get("/")
async def root():
    """
    API health endpoint by default.
    Optionally redirects to the bundled frontend when SERVE_STATIC_FRONTEND=1.
    """
    if serve_static_frontend and os.path.isdir(static_dist_dir):
        return RedirectResponse(url="/static/index.html")
    return {"status": "ok", "service": "Aura Drive API"}

@app.post("/uploadfile")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(...),
    is_public: bool = Form(False),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    How the Upload Process Works:
    1. **Temporary Storage**: We save the uploaded file to the local disk temporarily. 
    2. **Cloud Hand-off**: We send that local file to ImageKit cloud storage.
    3. **Metadata Persistence**: We save the Cloud URL back into our SQLite database.
    4. **Visibility**: We store whether this asset should be 'Public' or 'Private'.
    """
    temp_file_path = None
    try:
        # Step 1: Create a temporary file
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        
        # Step 2: Upload to ImageKit
        with open(temp_file_path, "rb") as f:
            upload_result = image_kit.files.upload(
                file=f,
                file_name=file.filename,
                tags=["backend-upload"],
                use_unique_file_name=True
            )

        # Step 3: Create a new database record
        # Handle cases where is_public might arrive as a string ('true'/'false') from FormData
        final_is_public = is_public
        if isinstance(is_public, str):
            final_is_public = is_public.lower() == "true"

        post = Post(
            file_id = upload_result.file_id,
            caption = caption,
            url = upload_result.url,
            file_type = upload_result.file_type,
            file_name = upload_result.name,
            user_id = user.id,
            is_public = final_is_public
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        
        return {
            "id": str(post.id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "is_public": post.is_public,
            "created_at": post.created_at
        }

    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    finally:
        # Step 4: Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/feed")
async def get_feed(
    mode: str = "private",
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Retrieve assets based on the selected mode.
    - **mode=private**: Returns only the personal assets of the logged-in user.
    - **mode=public**: Returns all assets shared with the community.
    """
    if mode == "public":
        # Fetch all public posts + their uploader emails
        # Using .where(Post.is_public.is_(True)) is more resilient for SQLite/Postgres boolean types
        result = await session.execute(
            select(Post)
            .options(selectinload(Post.user))
            .where(Post.is_public.is_(True))
            .order_by(Post.created_at.desc())
        )
    else:
        # Default: Fetch only the user's private vault
        result = await session.execute(
            select(Post)
            .options(selectinload(Post.user))
            .where(Post.user_id == user.id)
            .order_by(Post.created_at.desc())
        )
    
    posts = result.scalars().all() 
    
    posts_data = []
    for post in posts:
        posts_data.append({
            "id": post.id,
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "is_public": post.is_public,
            "created_at": post.created_at,
            "user_id": post.user_id,
            "uploader_email": post.user.email if post.user else "Aura Member"
        })
    return {"posts": posts_data }

@app.delete("/posts/{post_id}")
async def delete_post( 
    post_id: str, 
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Permanent deletion of an asset.
    """
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.user_id != user.id and not user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")

        if not post.file_id:
            raise HTTPException(status_code=400, detail="Missing ImageKit file ID for this post")

        # Delete the file from ImageKit first so we do not remove the DB row
        # unless the cloud asset was actually removed.
        image_kit.files.delete(file_id=post.file_id)

        await session.delete(post)
        await session.commit()
        
        return {"success": True, "message": "Post deleted permanently"}
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Delete operation failed: {str(e)}")

@app.patch("/posts/{post_id}/visibility")
async def update_post_visibility(
    post_id: str,
    is_public: bool,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Toggle visibility (Unshare/Share).
    """
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.user_id != user.id and not user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized to modify this post")
        
        post.is_public = is_public
        await session.commit()
        
        status = "Public" if is_public else "Private"
        return {"success": True, "message": f"Asset is now {status}"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Visibility update failed: {str(e)}")

# --- Authentication Routers ---
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])
