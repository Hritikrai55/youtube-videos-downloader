"""
Utility functions for the YouTube Downloader application.
"""
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def get_default_download_path():
    """
    Get the default download path from environment variables or use the downloads folder
    """
    default_path = os.getenv("DEFAULT_DOWNLOAD_PATH", "./downloads")
    path = Path(default_path).resolve()
    
    # Create directory if it doesn't exist
    os.makedirs(path, exist_ok=True)
    
    return str(path)

def format_filesize(bytes, decimals=2):
    """
    Format file size in bytes to human-readable format
    """
    if bytes is None:
        return "Unknown"
        
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0 or unit == 'TB':
            break
        bytes /= 1024.0
    
    return f"{bytes:.{decimals}f} {unit}"

def sanitize_filename(filename):
    """
    Remove invalid characters from filename
    """
    # Replace invalid characters with underscore
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def format_time(seconds):
    """
    Format seconds to MM:SS format
    """
    if seconds is None:
        return "Unknown"
    
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def get_timestamp():
    """
    Get current timestamp in YYYY-MM-DD_HH-MM-SS format
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def is_valid_youtube_url(url):
    """
    Check if URL is a valid YouTube URL
    """
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    
    match = re.match(youtube_regex, url)
    return match is not None

def get_video_id(url):
    """
    Extract video ID from YouTube URL
    """
    if not url:
        return None
        
    video_id = None
    url_parsed = re.search(
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    if url_parsed:
        video_id = url_parsed.group(1)
    
    return video_id
