#!/usr/bin/env python3
"""
Startup script for PDF Email Extractor
"""

import sys
import os

def main():
    print("PDF Email Extractor")
    print("=" * 50)
    print("Starting web application...")
    print("Open your browser and go to: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=8000)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
