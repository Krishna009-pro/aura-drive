import os
from dotenv import load_dotenv
from imagekitio import ImageKit

# Load environment variables from the .env file
load_dotenv()

# Initialize the ImageKit client for SDK v5.x (Stainless)
# The constructor expects 'private_key'.
# It automatically looks for IMAGEKIT_PRIVATE_KEY in the environment if not provided.
image_kit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY")
)
