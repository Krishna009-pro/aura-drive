"""
ImageKit client initialization for cloud storage.

Architecture Notes:
- **Cloud Storage**: We use ImageKit.io to handle file storage and global CDN delivery. 
  Instead of storing files on our own server (which is slow and fills up disk space), 
  we offload them to a specialized service.
- **Environment Variables**: Sensitive keys are loaded from a '.env' file using 'python-dotenv'.
  This is a security best-practice to keep secrets out of the source code.
"""

import os
from dotenv import load_dotenv
from imagekitio import ImageKit

# Load environment variables from the .env file 
load_dotenv()

IS_VERCEL = os.getenv("VERCEL") == "1" or bool(os.getenv("VERCEL_ENV"))
IMAGEKIT_PRIVATE_KEY = os.getenv("IMAGEKIT_PRIVATE_KEY")
if not IMAGEKIT_PRIVATE_KEY:
    if IS_VERCEL:
        raise RuntimeError("IMAGEKIT_PRIVATE_KEY is required when running on Vercel.")
    IMAGEKIT_PRIVATE_KEY = ""

# Initialize the ImageKit client
# The SDK uses your private key to authorize our backend to 'write' files to your account.
# Note: public_key and url_endpoint are not used in the main ImageKit constructor in this version.
image_kit = ImageKit(
    private_key=IMAGEKIT_PRIVATE_KEY
)


