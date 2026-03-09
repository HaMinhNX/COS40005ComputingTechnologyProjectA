import sys
import os

# Add the backend folder to the Python path so relative imports like 'database' work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
