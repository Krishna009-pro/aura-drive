"""
Main entry point for the Aura Drive application.
This script initializes and runs the FastAPI server using Uvicorn.
"""

import uvicorn

if __name__ == "__main__":
    # Start the Uvicorn server to host the FastAPI application
    # 'app.app:app' refers to: [package].[module]:[FastAPI instance]
    # host='localhost' and port=8000 define the server address
    # reload=True enables auto-restart on code changes (useful for development)
    uvicorn.run("app.app:app", host="localhost", port=8000, reload=True)