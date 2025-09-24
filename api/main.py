import os
import sys

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the FastAPI app from the same directory
from fastapi_app import app

# Export the app for Vercel
__all__ = ["app"]
