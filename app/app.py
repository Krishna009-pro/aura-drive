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

@app.post("/uploadfile")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(...),
    session: AsyncSession = Depends(get_async_session)
):

    temp_file_path = None
    try:
        # Create a temporary file to store the uploaded file
        # Fixed typo: os.path.splittext -> os.path.splitext
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        
        # Upload to ImageKit using the modern files.upload method
        with open(temp_file_path, "rb") as f:
            upload_result = image_kit.files.upload(
                file=f,
                file_name=file.filename,
                tags=["backend-upload"],
                use_unique_file_name=True
            )

        # In the modern SDK, upload_result is usually a model with attributes
        if upload_result:
            # Creating a new Post object using the data from the ImageKit response
            post = Post(
                caption = caption,
                url = upload_result.url,
                file_type = upload_result.file_type,
                file_name = upload_result.name
            )
            session.add(post) # Add to the session
            await session.commit() # Save to the database
            await session.refresh(post) # Refresh to get the auto-generated ID
            
            # Return as a dictionary for safe serialization
            return {
                "id": str(post.id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at
            }

    except Exception as e:
        # Log the error for debugging
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
):
    # Querying the database for all posts, ordered by the newest first
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    
    # Extracting the Post objects from the query result
    posts = [row[0] for row in result.all()] 
    
    # Formatting the data for the response
    posts_data = []
    for post in posts:
        posts_data.append({
            "id": post.id,
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at
        })
    return posts_data

@app.delete("/posts/{post_id}")
async def delete_post( post_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        post_uuid = uuid.UUID(post_id)
        
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        await session.delete(post)
        await session.commit()
        
        return {"sucess": True, "message": "Post deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    