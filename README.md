# JetFlix

JetFlix is a comprehensive media streaming and downloading application built with Flask. It combines movie and TV series information from TMDB (The Movie Database), torrent data from PirateBay, and integrates with qBittorrent for seamless torrent downloading and management. The application also includes video transcoding capabilities using FFmpeg for optimal playback.

## Features

### Core Functionality
- **Movie and Series Discovery**: Browse popular movies and TV series by genre
- **Torrent Integration**: Automatic torrent scraping and downloading via qBittorrent
- **Real-time Downloads**: Monitor download progress and manage active torrents
- **Video Transcoding**: Automatic transcoding of downloaded videos to MP4 for web playback
- **Web Interface**: Clean, responsive web UI for browsing and managing media

### Technical Features
- **RESTful API**: Comprehensive API for media data and download management
- **Background Processing**: Asynchronous scraping and transcoding operations
- **Portable Design**: Includes portable versions of qBittorrent and FFmpeg
- **Cross-platform**: Built with Python and deployable as a standalone executable
- **Database Integration**: SQLite database for persistent data storage

## Prerequisites

- Python 3.8 or higher
- Internet connection for scraping and downloading
- Windows (for portable qBittorrent and FFmpeg binaries included)

## Installation

### Option 1: From Source

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd JetFlix
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up portable tools**
   - **qBittorrent Portable**: Should be in `qBittorrentPortable/` directory
   - **FFmpeg Setup**:
     1. Download FFmpeg essentials build from https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
     2. Extract the ZIP file to `ffmpeg-8.0.1-essentials_build/` directory
     3. Ensure `ffmpeg.exe`, `ffplay.exe`, and `ffprobe.exe` are in `ffmpeg-8.0.1-essentials_build/bin/`

### Option 2: Standalone Executable

1. **Download the built executable** (`JetFlix.exe`)
2. **Run the executable directly** - no installation required

## Usage

### Running the Application

#### From Source:
```bash
python app.py
```

#### From Executable:
Double-click `JetFlix.exe` or run from command line:
```bash
JetFlix.exe
```

The application will start a web server on `http://localhost:5000`

### Initial Setup

1. **Populate Media Data**: Click the "Scrape Data" button in the web interface to fetch movie and series information from TMDB
2. **Start qBittorrent**: The application will automatically start the portable qBittorrent instance if available

### Web Interface

- **Home (/)**: Main dashboard
- **Movies (/movies)**: Browse movies by genre and popularity
- **Series (/series)**: Browse TV series by genre and popularity
- **Downloads (/downloads)**: Manage downloads and view transcoding status

### API Endpoints

#### Media Data
- `GET /api/media` - Get all movies
- `GET /api/popular` - Get popular movies
- `GET /api/series` - Get all TV series
- `GET /api/popular-series` - Get popular TV series
- `GET /genres.json` - Get movie genres
- `GET /series-genres.json` - Get series genres
- `GET /api/genre/<genre>` - Get movies by genre
- `GET /api/series-genre/<genre>` - Get series by genre

#### Downloads and Torrents
- `POST /api/download` - Start a torrent download
- `GET /api/downloads` - Get download status
- `DELETE /api/download/<hash>` - Stop a download
- `GET /api/downloaded-files` - List downloaded files
- `DELETE /api/downloaded-files/<filename>` - Delete a downloaded file

#### Transcoding
- `GET /api/transcoding-status/<filename>` - Get transcoding progress

#### Scraping
- `POST /api/scrape` - Start data scraping process
- `GET /api/progress` - Get scraping progress

#### System
- `GET /api/qb-status` - Check qBittorrent status

## Building the Executable

To build a standalone executable using PyInstaller:

1. **Install PyInstaller** (if not already installed):
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**:
   ```bash
   pyinstaller JetFlix.spec
   ```

3. **Find the executable** in the `dist/` directory as `JetFlix.exe`

The build process includes all necessary dependencies, templates, static files, and portable tools.

## Configuration

### qBittorrent Settings
- Default web UI port: 5001
- Default credentials: admin/admin123
- Downloads are saved to the `downloads/` directory

### FFmpeg Transcoding
- Input formats supported: MKV, AVI, WEBM
- Output format: MP4 (H.264 video, AAC audio)
- Transcoded files are saved to the `transcoded/` directory

## Project Structure

```
JetFlix/
├── app.py                      # Main Flask application
├── JetFlix.spec               # PyInstaller specification
├── requirements.txt           # Python dependencies
├── media.db                   # SQLite database
├── templates/                 # HTML templates
│   ├── index.html
│   ├── movies.html
│   ├── series.html
│   └── downloads.html
├── static/                    # CSS and JavaScript files
│   ├── style.css
│   └── script.js
├── qBittorrentPortable/       # Portable qBittorrent
├── ffmpeg-8.0.1-essentials_build/  # Portable FFmpeg
├── scrape_tmdb.py            # TMDB scraping module
├── scrape_piratebay.py       # PirateBay scraping module
├── populate_db.py            # Database population script
├── *-movielist.json          # Movie data files
├── *-serieslist.json         # Series data files
├── genres.json               # Movie genres
├── series-genres.json        # Series genres
└── downloads/                # Download directory
```

## Dependencies

- **Flask**: Web framework
- **requests**: HTTP requests
- **beautifulsoup4**: HTML parsing
- **qbittorrent-api**: qBittorrent integration
- **PyInstaller**: Executable building (build-time only)

## Troubleshooting

### qBittorrent Issues
- Ensure qBittorrent Portable is in the correct directory
- Check that port 5001 is not blocked by firewall
- The application will attempt to start qBittorrent automatically

### Transcoding Problems
- Ensure FFmpeg binaries are present and executable
- Check file permissions for input/output directories
- Large files may take significant time to transcode

### Scraping Failures
- Ensure internet connection is stable
- TMDB and PirateBay may have rate limits or blocking
- Check API keys if required (currently uses public TMDB API)

### Performance
- Initial scraping may take several minutes
- Large downloads and transcoding require significant disk space
- Monitor system resources during intensive operations

## License

[Add license information here]

## Contributing

[Add contribution guidelines here]

## Disclaimer

This application is for educational and personal use only. Ensure compliance with local laws regarding torrent downloading and copyright material. The developers are not responsible for misuse of this software.