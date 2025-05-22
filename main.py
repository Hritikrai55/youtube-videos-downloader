"""
YouTube Video Downloader
A GUI application for downloading YouTube videos with quality selection options.
"""
import os
import sys
from dotenv import load_dotenv
from src.gui import YouTubeDownloaderApp

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def main():
    """
    Main entry point for the application
    """
    app = YouTubeDownloaderApp()
    app.mainloop()

if __name__ == "__main__":
    main()
