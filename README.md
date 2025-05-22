# YouTube Video Downloader

A modern, feature-rich desktop application for downloading YouTube videos with customizable quality options, built with Python and CustomTkinter.

![YouTube Downloader](assets/app_screenshot.png)

## ✨ Features

- **Intuitive Modern UI** - Clean, responsive interface built with CustomTkinter
- **Multiple Format Support** - Download videos in various resolutions (4K, 1080p, 720p, etc.)
- **Audio Extraction** - Option to download audio-only files in MP3 format
- **Real-time Progress Tracking** - Visual download progress with speed and ETA display
- **Video Preview** - Display video thumbnails and metadata before downloading
- **Custom Download Location** - Choose where to save your downloads
- **Download History** - Keep track of your previously downloaded videos
- **Cross-platform** - Works on Windows, macOS, and Linux

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- FFmpeg (required for audio conversion)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd youtube_downloader
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your preferred settings.

4. **FFmpeg Installation**
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

## 🎮 Usage

1. **Launch the application**
   ```bash
   python main.py
   ```

2. **Download a video**
   - Enter a valid YouTube URL in the input field
   - Click "Fetch Video" to load video information
   - Select your preferred quality from the dropdown menu
   - Choose between video or audio-only download
   - Select destination folder (optional)
   - Click "Download" and monitor the progress

## 📋 Project Structure

```
youtube_downloader/
├── assets/              # Icons and UI resources
├── downloads/           # Default directory for downloaded files
├── src/                 # Source code modules
│   ├── downloader.py    # Core YouTube download functionality using yt-dlp
│   ├── gui.py           # CustomTkinter UI components and layout
│   └── utils.py         # Helper functions and utilities
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore rules
├── main.py              # Application entry point
├── README.md            # This documentation
└── requirements.txt     # Python dependencies
```

## 📦 Dependencies

- **yt-dlp** (2023.11.16) - Backend for YouTube video downloading
- **customtkinter** (5.2.0) - Modern UI toolkit for desktop applications
- **tkinter-page** (0.5.1) - UI page management
- **python-dotenv** (1.0.0) - Environment variable management
- **Pillow** (10.0.0) - Image processing for thumbnails
- **ffmpeg-python** (0.2.0) - FFmpeg integration for media processing

## 🔒 Privacy

This application downloads videos locally and does not collect any personal data. All operations are performed on your local machine.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💖 Acknowledgements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the excellent YouTube download library
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern UI components
