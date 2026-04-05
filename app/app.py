from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select # Importing 'select' for querying the database
from contextlib import asynccontextmanager

from app.images import image_kit # Import the initialized client
import shutil
import os
import uuid
import tempfile

# Importing our local schemas and database tools
from app.schema import createPost, responsePost
from app.db import Post, create_db_and_tables, get_async_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the app starts: it creates the database tables
    await create_db_and_tables()
    yield

# Initializing our FastAPI application with the lifespan manager
app = FastAPI(lifespan=lifespan)

from app.users import auth_backend, current_active_user, fastapi_users, User
from app.schema import UserCreate, UserUpdate, UserRead, UserAuth

@app.post("/uploadfile")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user) # Require authentication
):

    temp_file_path = None
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        
        with open(temp_file_path, "rb") as f:
            upload_result = image_kit.files.upload(
                file=f,
                file_name=file.filename,
                tags=["backend-upload"],
                use_unique_file_name=True
            )

        if upload_result:
            # Associate the post with the current logged-in user
            post = Post(
                caption = caption,
                url = upload_result.url,
                file_type = upload_result.file_type,
                file_name = upload_result.name,
                user_id = user.id
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
                "created_at": post.created_at
            }

    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
):
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
            "user_id": post.user_id # Included user info
        })
    return {"posts": posts_data }

@app.delete("/posts/{post_id}")
async def delete_post( 
    post_id: str, 
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user) # Only logged in users
):
    try:
        post_uuid = uuid.UUID(post_id)
        
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Check if the user is the owner or a superuser
        if post.user_id != user.id and not user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        
        await session.delete(post)
        await session.commit()
        
        return {"success": True, "message": "Post deleted successfully"}
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])
