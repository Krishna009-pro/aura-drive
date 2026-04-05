from pydantic import BaseModel # Importing BaseModel to define data schemas

# Schema for creating a new post (Request body)
class createPost(BaseModel):
    title: str # The title of the post (must be a string)
    description: str # The description of the post (must be a string)

# Schema for the API response after a post is handled
class responsePost(BaseModel):
    title: str # The title that will be returned in the response
    description: str # The description that will be returned in the response