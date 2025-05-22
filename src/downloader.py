"""
Core functionality for downloading YouTube videos.
"""
import os
import yt_dlp
from pathlib import Path
from dotenv import load_dotenv
from src.utils import format_filesize, sanitize_filename, get_timestamp

# Load environment variables
load_dotenv()

class YouTubeDownloader:
    """
    Main class for handling YouTube video downloads
    """
    def __init__(self, callback=None):
        """
        Initialize the downloader
        
        Args:
            callback (function): Callback function for progress updates
        """
        self.video_formats = []
        self.video_info = None
        self.callback = callback
        self.format_list = []
        
    def _progress_hook(self, d):
        """
        Progress hook for yt-dlp to track download progress
        """
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'Unknown').strip()
            speed = d.get('_speed_str', 'Unknown')
            eta = d.get('_eta_str', 'Unknown')
            filename = d.get('filename', '').split(os.path.sep)[-1]
            
            # For clearer visibility of download progress
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
            
            # Make progress more detailed
            progress_info = {
                'status': 'downloading',
                'percent': percent,
                'speed': speed,
                'eta': eta,
                'filename': filename,
                'downloaded': downloaded,
                'total': total
            }
            
            if self.callback:
                self.callback(progress_info)
                
        elif d['status'] == 'finished':
            if self.callback:
                self.callback({
                    'status': 'processing',
                    'message': 'Download finished. Now processing...'
                })
                
        elif d['status'] == 'error':
            if self.callback:
                self.callback({
                    'status': 'error',
                    'message': f"Error: {d.get('error', 'Unknown error')}"
                })
    
    def fetch_video_info(self, url):
        """
        Fetch video information and available formats
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            dict: Video info including title, formats, thumbnail, etc.
        """
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'forcejson': True,
            'simulate': True,
            'format': 'bestvideo+bestaudio/best'  # Include all formats
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.video_info = ydl.extract_info(url, download=False)
                formats = self.video_info.get('formats', [])
                
                # Filter for video formats (include both combined and video-only streams)
                video_formats_all = [
                    f for f in formats 
                    if f.get('vcodec') != 'none' and f.get('resolution') != 'audio only'
                ]
                
                # Group formats by resolution to reduce duplicate options
                resolution_formats = {}
                for f in video_formats_all:
                    height = f.get('height', 0) or 0
                    if height == 0:
                        continue
                        
                    # Skip format if we already have a better one for this resolution
                    if height in resolution_formats:
                        current = resolution_formats[height]
                        
                        # Prefer formats with audio included
                        current_has_audio = current.get('acodec') != 'none'
                        new_has_audio = f.get('acodec') != 'none'
                        
                        if current_has_audio and not new_has_audio:
                            continue
                            
                        # For formats with same audio status, prefer mp4 over other formats
                        if current_has_audio == new_has_audio:
                            current_is_mp4 = current.get('ext') == 'mp4'
                            new_is_mp4 = f.get('ext') == 'mp4'
                            
                            if current_is_mp4 and not new_is_mp4:
                                continue
                    
                    # Store this format as the best one for this resolution
                    resolution_formats[height] = f
                
                # Only keep common resolutions and ensure they're sorted
                common_resolutions = [2160, 1440, 1080, 720, 480, 360, 240, 144]
                self.video_formats = []
                
                for res in common_resolutions:
                    if res in resolution_formats:
                        self.video_formats.append(resolution_formats[res])
                
                # Create format display list
                self.format_list = []
                for i, f in enumerate(self.video_formats):
                    resolution = f"{f.get('height', 'N/A')}p" if f.get('height') else "N/A"
                    ext = f.get('ext', 'unknown')
                    filesize = format_filesize(f.get('filesize', None))
                    format_id = f.get('format_id', '')
                    
                    # Check if this is a video-only stream that needs audio
                    has_audio = f.get('acodec') != 'none'
                    format_note = "" if has_audio else " + audio"
                    
                    # Create a cleaner display string with just the essential info
                    self.format_list.append({
                        'index': i,
                        'display': f"{resolution} ({ext}) {filesize}{format_note}",
                        'format_id': format_id,
                        'resolution': resolution,
                        'ext': ext,
                        'filesize': filesize,
                        'needs_audio': not has_audio
                    })
                
                return {
                    'title': self.video_info.get('title', 'Unknown'),
                    'channel': self.video_info.get('channel', 'Unknown'),
                    'duration': self.video_info.get('duration', 0),
                    'thumbnail': self.video_info.get('thumbnail', ''),
                    'formats': self.format_list
                }
                
        except Exception as e:
            if self.callback:
                self.callback({
                    'status': 'error',
                    'message': str(e)
                })
            raise e
    
    def download_video(self, url, format_index, output_dir, filename=None):
        """
        Download video in selected format
        
        Args:
            url (str): YouTube video URL
            format_index (int): Index of selected format
            output_dir (str): Output directory
            filename (str, optional): Custom filename
            
        Returns:
            str: Path to downloaded file
        """
        if not self.video_formats:
            self.fetch_video_info(url)
        
        selected_format = self.video_formats[format_index]['format_id']
        needs_audio = self.format_list[format_index].get('needs_audio', False)
        
        # If this is a video-only stream, we need to add audio
        if needs_audio:
            format_spec = f"{selected_format}+bestaudio/best"
        else:
            format_spec = selected_format
        
        # Create output path
        os.makedirs(output_dir, exist_ok=True)
        
        # Get title for filename
        title = self.video_info.get('title', 'video')
        if filename:
            output_template = filename
        else:
            title = sanitize_filename(title)
            output_template = f"{title}_{get_timestamp()}"
        
        output_file = os.path.join(output_dir, f"{output_template}.%(ext)s")
        
        # Simple options with minimal postprocessing for better compatibility
        ydl_opts = {
            # Use format specification with fallback to best quality
            'format': format_spec,
            'outtmpl': output_file,
            # Make sure to use mp4 as container format
            'merge_output_format': 'mp4',
            # Track progress
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            # Basic postprocessors that won't interfere with audio
            'postprocessors': [{
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            }],
            # Use ffmpeg for merging
            'prefer_ffmpeg': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            if self.callback:
                self.callback({
                    'status': 'complete',
                    'message': 'Download complete!'
                })
                
            return output_file.replace('%(ext)s', 'mp4')
            
        except Exception as e:
            if self.callback:
                self.callback({
                    'status': 'error',
                    'message': str(e)
                })
            raise e
    
    def download_audio(self, url, output_dir, filename=None, quality="192"):
        """
        Download audio only (MP3)
        
        Args:
            url (str): YouTube video URL
            output_dir (str): Output directory
            filename (str, optional): Custom filename
            quality (str): Audio quality (kbps)
            
        Returns:
            str: Path to downloaded file
        """
        if not self.video_info:
            self.fetch_video_info(url)
        
        # Create output path
        os.makedirs(output_dir, exist_ok=True)
        
        # Get title for filename
        title = self.video_info.get('title', 'audio')
        if filename:
            output_template = filename
        else:
            title = sanitize_filename(title)
            output_template = f"{title}_{get_timestamp()}"
        
        output_file = os.path.join(output_dir, f"{output_template}.%(ext)s")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_file,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'progress_hooks': [self._progress_hook],
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            if self.callback:
                self.callback({
                    'status': 'complete',
                    'message': 'Audio download complete!'
                })
                
            return output_file.replace('%(ext)s', 'mp3')
            
        except Exception as e:
            if self.callback:
                self.callback({
                    'status': 'error',
                    'message': str(e)
                })
            raise e
