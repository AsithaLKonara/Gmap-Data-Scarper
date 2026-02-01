
import os
import sys

# Add the root directory to sys.path so 'backend' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

# Vercel needs 'app' to be exposed
app = app
