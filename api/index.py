import sys
import os

# Add the root directory to sys.path so Vercel can find the 'backend' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
