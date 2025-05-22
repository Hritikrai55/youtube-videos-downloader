"""
GUI components for the YouTube Downloader application.
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import threading
import urllib.request
from io import BytesIO
import base64

from src.utils import get_default_download_path, format_time, is_valid_youtube_url
from src.downloader import YouTubeDownloader

# Set appearance mode and theme
ctk.set_appearance_mode("System")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class VideoThumbnail(ctk.CTkFrame):
    """Frame for displaying video thumbnail with info"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Default thumbnail 
        self.default_img = self._create_default_thumbnail()
        
        # Thumbnail image
        self.thumbnail_label = ctk.CTkLabel(self, text="", image=self.default_img)
        self.thumbnail_label.pack(pady=10, padx=10)
        
        # Video info
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(fill="x", expand=True, padx=10, pady=5)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.info_frame, 
            text="Enter a YouTube URL to get started",
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=400
        )
        self.title_label.pack(pady=(5, 2), padx=10, anchor="w")
        
        # Channel
        self.channel_label = ctk.CTkLabel(
            self.info_frame, 
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.channel_label.pack(pady=2, padx=10, anchor="w")
        
        # Duration
        self.duration_label = ctk.CTkLabel(
            self.info_frame, 
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.duration_label.pack(pady=2, padx=10, anchor="w")
    
    def _create_default_thumbnail(self):
        """Create a default thumbnail image"""
        # Create a blank gray image
        img = Image.new('RGB', (320, 180), color=(100, 100, 100))
        
        # Add a simple play button icon
        draw = ImageDraw.Draw(img)
        # Draw a triangle (play button)
        draw.polygon([(120, 70), (120, 110), (160, 90)], fill=(255, 255, 255))
        
        # Add a border
        draw.rectangle([0, 0, 319, 179], outline=(70, 70, 70), width=2)
        
        return ctk.CTkImage(light_image=img, dark_image=img, size=(320, 180))
    
    def update_thumbnail(self, video_info):
        """Update thumbnail and info with video data"""
        if not video_info:
            self.thumbnail_label.configure(image=self.default_img)
            self.title_label.configure(text="Enter a YouTube URL to get started")
            self.channel_label.configure(text="")
            self.duration_label.configure(text="")
            return
            
        # Update video info
        self.title_label.configure(text=video_info.get('title', 'Unknown Title'))
        self.channel_label.configure(text=f"Channel: {video_info.get('channel', 'Unknown')}")
        
        duration = video_info.get('duration', 0)
        if duration:
            self.duration_label.configure(text=f"Duration: {format_time(duration)}")
        else:
            self.duration_label.configure(text="")
            
        # Get thumbnail
        thumbnail_url = video_info.get('thumbnail', '')
        if thumbnail_url:
            try:
                # Run in a thread to avoid blocking
                threading.Thread(target=self._load_thumbnail, args=(thumbnail_url,)).start()
            except Exception:
                self.thumbnail_label.configure(image=self.default_img)
    
    def _load_thumbnail(self, url):
        """Load thumbnail from URL"""
        try:
            with urllib.request.urlopen(url) as response:
                img_data = response.read()
                img = Image.open(BytesIO(img_data))
                img = img.resize((320, 180), Image.LANCZOS)
                
                # Convert to CTkImage
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(320, 180))
                
                # Update label in main thread
                self.after(0, lambda: self.thumbnail_label.configure(image=ctk_img))
                
                # Keep a reference to prevent garbage collection
                self.current_img = ctk_img
        except Exception:
            # Fallback to default on error
            self.after(0, lambda: self.thumbnail_label.configure(image=self.default_img))


class ProgressFrame(ctk.CTkFrame):
    """Frame for showing download progress"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Main progress label
        self.progress_title = ctk.CTkLabel(
            self, 
            text="Download Progress",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.progress_title.pack(pady=(10, 5))
        
        # Progress bar with percentage display
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress_percent = ctk.CTkLabel(
            self.progress_frame,
            text="0%",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=50
        )
        self.progress_percent.pack(side="left", padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=15)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.progress_bar.set(0)
        
        # Status frame with detailed info
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(fill="x", padx=10, pady=5)
        
        # Status layout with two columns
        self.status_left = ctk.CTkFrame(self.status_frame)
        self.status_left.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        
        self.status_right = ctk.CTkFrame(self.status_frame)
        self.status_right.pack(side="right", fill="x", expand=True, padx=10, pady=5)
        
        # Left column - File info
        self.file_label = ctk.CTkLabel(
            self.status_left, 
            text="File:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.file_label.pack(anchor="w")
        
        self.filename_label = ctk.CTkLabel(
            self.status_left, 
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.filename_label.pack(anchor="w")
        
        # Right column - Speed & ETA
        self.speed_title = ctk.CTkLabel(
            self.status_right, 
            text="Speed:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.speed_title.pack(anchor="w")
        
        self.speed_label = ctk.CTkLabel(
            self.status_right, 
            text="-",
            font=ctk.CTkFont(size=12)
        )
        self.speed_label.pack(anchor="w")
        
        self.eta_title = ctk.CTkLabel(
            self.status_right, 
            text="ETA:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.eta_title.pack(anchor="w")
        
        self.eta_label = ctk.CTkLabel(
            self.status_right, 
            text="-",
            font=ctk.CTkFont(size=12)
        )
        self.eta_label.pack(anchor="w")
        
        # Output text
        self.output_text = ctk.CTkTextbox(self, height=100)
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)
        
    def update_progress(self, progress_data):
        """Update progress display"""
        status = progress_data.get('status', '')
        
        if status == 'downloading':
            percent = progress_data.get('percent', '0%')
            speed = progress_data.get('speed', 'Unknown')
            eta = progress_data.get('eta', 'Unknown')
            filename = progress_data.get('filename', '')
            downloaded = progress_data.get('downloaded', 0)
            total = progress_data.get('total', 0)
            
            # Extract percentage value
            percent_value = 0
            try:
                percent_value = float(percent.strip('%')) / 100
            except ValueError:
                # Try to calculate it from downloaded/total if available
                if total > 0:
                    percent_value = downloaded / total
                
            # Update progress bar and percentage
            self.progress_bar.set(percent_value)
            self.progress_percent.configure(text=f"{percent}")
            
            # Update status labels
            self.progress_title.configure(text="Downloading...")
            self.filename_label.configure(text=filename)
            self.speed_label.configure(text=speed)
            self.eta_label.configure(text=eta)
            
            # Update log with detailed info
            self.log(f"Downloading: {percent} | Speed: {speed} | ETA: {eta}")
            
        elif status == 'processing':
            self.progress_bar.set(1.0)  # 100%
            self.progress_percent.configure(text="100%")
            self.progress_title.configure(text="Processing...")
            self.filename_label.configure(text=progress_data.get('filename', ''))
            self.speed_label.configure(text="-")
            self.eta_label.configure(text="-")
            self.log(progress_data.get('message', 'Processing video...'))
            
        elif status == 'complete':
            self.progress_bar.set(1.0)  # 100%
            self.progress_percent.configure(text="100%")
            self.progress_title.configure(text="Complete!")
            self.filename_label.configure(text=progress_data.get('filename', ''))
            self.speed_label.configure(text="-")
            self.eta_label.configure(text="-")
            self.log(progress_data.get('message', 'Download complete!'))
            
        elif status == 'error':
            self.progress_title.configure(text="Error!")
            self.filename_label.configure(text=progress_data.get('message', 'Unknown error'))
            self.speed_label.configure(text="-")
            self.eta_label.configure(text="-")
            self.log(f"ERROR: {progress_data.get('message', 'Unknown error')}")
            
        elif status == 'info':
            self.log(progress_data.get('message', ''))
    
    def reset(self):
        """Reset progress display"""
        self.progress_bar.set(0)
        self.progress_percent.configure(text="0%")
        self.progress_title.configure(text="Download Progress")
        self.filename_label.configure(text="Ready")
        self.speed_label.configure(text="-")
        self.eta_label.configure(text="-")
    
    def log(self, message):
        """Add message to output text"""
        self.output_text.insert("end", f"{message}\n")
        self.output_text.see("end")  # Scroll to end
        

class YouTubeDownloaderApp(ctk.CTk):
    """Main application window"""
    def __init__(self):
        super().__init__()
        
        # Setup window
        self.title("YouTube Video Downloader")
        self.geometry("800x700")
        self.minsize(700, 600)
        
        # Initialize downloader
        self.downloader = YouTubeDownloader(callback=self.progress_callback)
        
        # Create GUI components
        self.create_widgets()
        
        # Default download directory
        self.output_entry.insert(0, get_default_download_path())
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame for all components
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # URL frame
        self.url_frame = ctk.CTkFrame(self.main_frame)
        self.url_frame.pack(fill="x", padx=10, pady=10)
        
        self.url_label = ctk.CTkLabel(self.url_frame, text="YouTube URL:")
        self.url_label.pack(side="left", padx=10)
        
        self.url_entry = ctk.CTkEntry(self.url_frame, width=400)
        self.url_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        self.fetch_button = ctk.CTkButton(
            self.url_frame, 
            text="Fetch Video", 
            command=self.fetch_video
        )
        self.fetch_button.pack(side="right", padx=10)
        
        # Thumbnail frame
        self.thumbnail_frame = VideoThumbnail(self.main_frame)
        self.thumbnail_frame.pack(fill="x", padx=10, pady=10)
        
        # Formats frame
        self.formats_frame = ctk.CTkFrame(self.main_frame)
        self.formats_frame.pack(fill="x", padx=10, pady=10)
        
        self.formats_label = ctk.CTkLabel(
            self.formats_frame, 
            text="Select Video Quality:", 
            font=ctk.CTkFont(size=14)
        )
        self.formats_label.pack(pady=5, padx=10, anchor="w")
        
        self.format_var = ctk.StringVar(value="")
        self.format_combo = ctk.CTkComboBox(
            self.formats_frame, 
            width=400,
            variable=self.format_var,
            state="readonly",
            values=[]
        )
        self.format_combo.pack(pady=5, padx=10)
        
        # Download type frame
        self.type_frame = ctk.CTkFrame(self.main_frame)
        self.type_frame.pack(fill="x", padx=10, pady=10)
        
        self.download_type_var = ctk.StringVar(value="Video")
        self.video_radio = ctk.CTkRadioButton(
            self.type_frame, 
            text="Download as Video", 
            variable=self.download_type_var, 
            value="Video"
        )
        self.video_radio.pack(side="left", padx=20, pady=10)
        
        self.audio_radio = ctk.CTkRadioButton(
            self.type_frame, 
            text="Download as Audio (MP3)", 
            variable=self.download_type_var, 
            value="Audio"
        )
        self.audio_radio.pack(side="left", padx=20, pady=10)
        
        # Output directory frame
        self.output_frame = ctk.CTkFrame(self.main_frame)
        self.output_frame.pack(fill="x", padx=10, pady=10)
        
        self.output_label = ctk.CTkLabel(self.output_frame, text="Output Folder:")
        self.output_label.pack(side="left", padx=10)
        
        self.output_entry = ctk.CTkEntry(self.output_frame, width=400)
        self.output_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        self.browse_button = ctk.CTkButton(
            self.output_frame, 
            text="Browse", 
            command=self.browse_folder
        )
        self.browse_button.pack(side="right", padx=10)
        
        # Download button
        self.download_button = ctk.CTkButton(
            self.main_frame, 
            text="Download", 
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.download
        )
        self.download_button.pack(pady=10)
        
        # Progress frame
        self.progress_frame = ProgressFrame(self.main_frame)
        self.progress_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def fetch_video(self):
        """Fetch video information and update UI"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube video URL.")
            return
            
        if not is_valid_youtube_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL format.")
            return
        
        # Reset UI
        self.format_combo.configure(values=[])
        self.progress_frame.reset()
        self.progress_frame.log(f"Fetching info for: {url}")
        
        # Run in thread to avoid blocking UI
        threading.Thread(target=self._fetch_video_thread, args=(url,)).start()
    
    def _fetch_video_thread(self, url):
        """Thread function for fetching video info"""
        try:
            video_info = self.downloader.fetch_video_info(url)
            
            # Update UI in main thread
            self.after(0, lambda: self._update_ui_with_video_info(video_info))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self.progress_frame.update_progress({
                'status': 'error',
                'message': str(e)
            }))
    
    def _update_ui_with_video_info(self, video_info):
        """Update UI with fetched video info"""
        # Update thumbnail and info
        self.thumbnail_frame.update_thumbnail(video_info)
        
        # Update format dropdown
        formats = video_info.get('formats', [])
        format_values = [f"{fmt['resolution']} | {fmt['ext']} | {fmt['filesize']}" for fmt in formats]
        
        self.format_combo.configure(values=format_values)
        if format_values:
            self.format_var.set(format_values[0])
            
        self.progress_frame.log(f"Found {len(formats)} video formats")
    
    def browse_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, folder)
    
    def download(self):
        """Start the download process"""
        url = self.url_entry.get().strip()
        output_dir = self.output_entry.get().strip()
        download_type = self.download_type_var.get()
        
        if not url or not output_dir:
            messagebox.showerror("Error", "Please enter all required fields.")
            return
            
        if not is_valid_youtube_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL format.")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Reset progress
        self.progress_frame.reset()
        
        # Initialize progress display immediately
        self.progress_frame.progress_title.configure(text="Starting Download...")
        self.progress_frame.log("Preparing to download...")
        
        # Get selected format index
        format_str = self.format_var.get()
        format_index = 0  # Default to first format
        
        if format_str:
            format_values = self.format_combo.cget("values")
            if format_values:
                try:
                    format_index = format_values.index(format_str)
                except ValueError:
                    # If not found, use first format
                    format_index = 0
        
        # Disable download button while downloading
        self.download_button.configure(state="disabled", text="Downloading...")
        
        # Download in thread
        threading.Thread(
            target=self._download_thread, 
            args=(url, format_index, output_dir, download_type)
        ).start()
    
    def _download_thread(self, url, format_index, output_dir, download_type):
        """Thread function for downloading"""
        try:
            # First ensure we have video info
            if not self.downloader.video_info:
                self.progress_frame.log("Fetching video information...")
                self.downloader.fetch_video_info(url)
            
            # Initialize progress display with more information
            self.after(0, lambda: self.progress_frame.progress_percent.configure(text="0%"))
            
            # Show what's being downloaded
            file_type = "video" if download_type == "Video" else "audio"
            selected_format = ""
            if format_index < len(self.downloader.format_list):
                selected_format = self.downloader.format_list[format_index]['display']
            
            self.after(0, lambda: self.progress_frame.log(
                f"Starting {file_type} download in {selected_format}..."
            ))
            
            # Start the actual download
            if download_type == "Video":
                self.downloader.download_video(url, format_index, output_dir)
            else:
                self.downloader.download_audio(url, output_dir)
            
            # Enable download button again when complete
            self.after(0, lambda: self.download_button.configure(
                state="normal", 
                text="Download"
            ))
            
            # Show success message
            self.after(0, lambda: messagebox.showinfo(
                "Success", 
                f"{file_type.capitalize()} downloaded successfully to {output_dir}"
            ))
                
        except Exception as e:
            # Handle errors and update UI
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self.progress_frame.update_progress({
                'status': 'error',
                'message': str(e)
            }))
            
            # Re-enable download button on error
            self.after(0, lambda: self.download_button.configure(
                state="normal", 
                text="Download"
            ))
    
    def progress_callback(self, progress_data):
        """Callback for download progress updates"""
        # Update UI in main thread
        self.after(0, lambda: self.progress_frame.update_progress(progress_data))
