"""
Main entry point for the Aura Drive application.
This script initializes and runs the FastAPI server using Uvicorn.
"""

import uvicorn
import os

if __name__ == "__main__":
    # Dynamically read the port from the environment variable (provided by most hosts)
    # Default to 8000 for local development
    port = int(os.getenv("PORT", 8000))
    reload_enabled = os.getenv("RELOAD", "0") == "1"
    
    # Use 0.0.0.0 as the host to allow the app to be reachable within a Docker container or server
    uvicorn.run("app.app:app", host="0.0.0.0", port=port, reload=reload_enabled)
