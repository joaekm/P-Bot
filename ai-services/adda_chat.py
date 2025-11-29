"""
Adda P-Bot CLI v5.1
Wrapper for backwards compatibility - delegates to app.cli
"""
import sys
import os

# Add current directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.cli import main

if __name__ == '__main__':
    main()
