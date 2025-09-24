import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the FastAPI app directly (for PythonAnywhere single folder structure)
from fastapi_app import app

# Export the app for Vercel
__all__ = ["app"]
