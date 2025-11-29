"""
Adda P-Bot API Server v5
Wrapper for backwards compatibility - delegates to app.main
"""
from app.main import app, main

if __name__ == '__main__':
    main()
