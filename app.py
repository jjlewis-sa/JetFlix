import json
import threading
import os
import subprocess
import time
import re
from flask import Flask, render_template, jsonify, send_from_directory, request, Response
from scrape_tmdb import scrape_popular_movies, get_genres as scrape_get_genres, scrape_genre_movies, scrape_popular_series, get_series_genres, scrape_series_genre
from scrape_piratebay import scrape_piratebay, scrape_series_torrents

try:
    from qbittorrentapi import Client
    QB_AVAILABLE = True
except ImportError:
    QB_AVAILABLE = False
    print("qbittorrent-api not available. Server-side downloads disabled.")

app = Flask(__name__)

progress = {'status': 'idle', 'progress': 0, 'message': ''}
transcoding_status = {}
transcoding_progress = {}

# qBittorrent setup
def ensure_qb_running():
    global qb_client, qb_process
    if not QB_AVAILABLE:
        return False
    try:
        qb_client = Client(host='localhost:5001', username='admin', password='admin123')
        qb_client.auth_log_in()
        return True
    except Exception as e:
        print(f"qBittorrent already running or connection failed: {e}")
        # Try to start qBittorrent
        qb_exe = os.path.join(os.getcwd(), 'qBittorrentPortable', 'qBittorrentPortable.exe')
        if os.path.exists(qb_exe):
            print("Starting qBittorrent Portable...")
            qb_process = subprocess.Popen([qb_exe, '--webui-port=5001'],
                                        cwd=os.path.join(os.getcwd(), 'qBittorrentPortable'))
            # Wait for qBittorrent to be ready
            max_attempts = 30  # 30 seconds
            for attempt in range(max_attempts):
                time.sleep(1)
                try:
                    qb_client = Client(host='localhost:5001', username='admin', password='admin123')
                    qb_client.auth_log_in()
                    # Set download directory
                    qb_client.app_set_preferences({'save_path': downloads_dir})
                    print("qBittorrent connected successfully")
                    return True
                except Exception as e:
                    if attempt == max_attempts - 1:
                        print(f"Failed to connect to qBittorrent after starting: {e}")
                        return False
                    continue
        else:
            print(f"qBittorrent exe not found at {qb_exe}")
        return False

def do_transcode(input_path, output_path, filename):
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Get duration with ffprobe
        ffprobe_cmd = [ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_format', input_path]
        result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
        duration = None
        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
        # Start transcoding
        cmd = [ffmpeg_path, '-i', input_path, '-c:v', 'libx264', '-preset', 'fast', '-c:a', 'aac', '-y', output_path]
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
        transcoding_progress[filename] = 0
        while True:
            line = process.stderr.readline()
            if not line:
                break
            if duration and 'time=' in line:
                match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                if match:
                    h, m, s = map(float, match.groups())
                    current_time = h * 3600 + m * 60 + s
                    pct = min(100, (current_time / duration) * 100)
                    transcoding_progress[filename] = pct
        process.wait()
        if process.returncode == 0:
            print(f"Transcoded {input_path} to {output_path}")
            transcoding_status[filename] = 'done'
            transcoding_progress[filename] = 100
        else:
            print(f"Error transcoding {input_path}")
            transcoding_status[filename] = 'error'
    except Exception as e:
        print(f"Error transcoding {input_path}: {e}")
        transcoding_status[filename] = 'error'


if QB_AVAILABLE:
    downloads_dir = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    transcoded_dir = os.path.join(os.getcwd(), 'transcoded')
    os.makedirs(transcoded_dir, exist_ok=True)
    ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg.exe')
    ffprobe_path = os.path.join(os.getcwd(), 'ffprobe.exe')
    qb_client = None
    qb_process = None
else:
    downloads_dir = None
    transcoded_dir = None
    ffmpeg_path = None
    ffprobe_path = None
    qb_client = None
    qb_process = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/media')
def get_media():
    with open('movielist.json', 'r') as f:
        media_list = json.load(f)
    return jsonify(media_list)

@app.route('/api/popular')
def get_popular():
    with open('popular-movielist.json', 'r') as f:
        popular_list = json.load(f)
    return jsonify(popular_list)

@app.route('/movies')
def movies():
    return render_template('movies.html')

@app.route('/api/series')
def get_series():
    with open('serieslist.json', 'r') as f:
        series_list = json.load(f)
    return jsonify(series_list)

@app.route('/api/popular-series')
def get_popular_series():
    with open('popular-serieslist.json', 'r') as f:
        popular_series_list = json.load(f)
    return jsonify(popular_series_list)

@app.route('/series')
def series():
    return render_template('series.html')

@app.route('/downloads')
def downloads():
    return render_template('downloads.html')

@app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory('media', filename)

@app.route('/downloads/<path:filename>')
def serve_download(filename):
    full_path = os.path.join(downloads_dir, filename)
    if not os.path.exists(full_path):
        return "File not found", 404
    if filename.endswith('.mp4'):
        return send_from_directory(downloads_dir, filename)
    else:
        # Check if transcoded exists
        transcoded_rel = filename.rsplit('.', 1)[0] + '.mp4'
        transcoded_path = os.path.join(transcoded_dir, transcoded_rel)
        if os.path.exists(transcoded_path):
            return send_from_directory(transcoded_dir, transcoded_rel)
        else:
            # Start transcoding if not already
            if filename not in transcoding_status or transcoding_status[filename] == 'done':
                transcoding_status[filename] = 'in_progress'
                threading.Thread(target=do_transcode, args=(full_path, transcoded_path, filename)).start()
            return jsonify({'status': 'transcoding', 'message': 'Video is being transcoded for playback. Please wait...'})

@app.route('/genres.json')
def get_genres():
    with open('genres.json', 'r') as f:
        genres = json.load(f)
    return jsonify(genres)

@app.route('/api/genre/<genre>')
def get_genre(genre):
    try:
        with open(f'{genre}-movielist.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Genre not found"}), 404

@app.route('/series-genres.json')
def get_series_genres():
    with open('series-genres.json', 'r') as f:
        genres = json.load(f)
    return jsonify(genres)

@app.route('/api/series-genre/<genre>')
def get_series_genre(genre):
    try:
        with open(f'{genre}-serieslist.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Genre not found"}), 404

@app.route('/api/scrape', methods=['POST'])
def start_scrape():
    if progress['status'] == 'running':
        return jsonify({'error': 'Scraping already running'}), 400
    progress['status'] = 'running'
    progress['progress'] = 0
    progress['message'] = 'Starting scrape...'
    threading.Thread(target=run_scrape).start()
    return jsonify({'message': 'Scraping started'})

def update_movielist_with_torrents():
    try:
        with open('movielist.json', 'r') as f:
            movies = json.load(f)
        for movie in movies:
            if 'torrents' not in movie:
                movie['torrents'] = scrape_piratebay(movie['title'])
        with open('movielist.json', 'w') as f:
            json.dump(movies, f, indent=4)
        print("Updated movielist.json with torrents")
    except Exception as e:
        print(f"Error updating movielist: {e}")

def update_serieslist_with_torrents():
    try:
        with open('serieslist.json', 'r') as f:
            series = json.load(f)
        for serie in series:
            if 'torrents' not in serie:
                serie['torrents'] = scrape_series_torrents(serie['title'])
        with open('serieslist.json', 'w') as f:
            json.dump(series, f, indent=4)
        print("Updated serieslist.json with torrents")
    except Exception as e:
        print(f"Error updating serieslist: {e}")

def add_torrent(magnet_uri, name):
    if not ensure_qb_running():
        return False
    try:
        qb_client.torrents_add(urls=[magnet_uri], save_path=downloads_dir)
        return True
    except Exception as e:
        print(f"Error adding torrent: {e}")
        return False

def get_download_status():
    if not ensure_qb_running():
        return []
    try:
        torrents = qb_client.torrents_info()
        status_list = []
        for torrent in torrents:
            status_list.append({
                'name': torrent.name,
                'hash': torrent.hash,
                'progress': torrent.progress * 100,
                'download_rate': torrent.dlspeed,
                'upload_rate': torrent.upspeed,
                'num_peers': torrent.num_leechs + torrent.num_seeds,
                'state': torrent.state
            })
        return status_list
    except Exception as e:
        print(f"Error getting torrent status: {e}")
        return []

def run_scrape():
    def update_progress(pct, msg):
        print(f"Progress update: pct={pct}, msg={msg}")
        if pct is not None:
            progress['progress'] = pct
        progress['message'] = msg
    try:
        scrape_popular_movies(update_progress)
        scrape_get_genres(update_progress)
        with open('genres.json', 'r') as f:
            genres = json.load(f)
        for i, genre in enumerate(genres):
            genre_name = genre['name']
            scrape_genre_movies(genre['id'], genre_name, update_progress)
            pct = 20 + int((30 / len(genres)) * (i + 1))
            update_progress(pct, f'Scraped {genre_name} movies')

        scrape_popular_series(update_progress)
        get_series_genres(update_progress)
        with open('series-genres.json', 'r') as f:
            series_genres = json.load(f)
        for i, genre in enumerate(series_genres):
            genre_name = genre['name']
            scrape_series_genre(genre['id'], genre_name, update_progress)
            pct = 50 + int((40 / len(series_genres)) * (i + 1))
            update_progress(pct, f'Scraped {genre_name} series')

        update_movielist_with_torrents()
        update_serieslist_with_torrents()
        progress['status'] = 'completed'
        progress['progress'] = 100
        progress['message'] = 'Scraping completed'
    except Exception as e:
        print(f"Exception in scraping: {e}")
        progress['status'] = 'error'
        progress['message'] = str(e)

@app.route('/api/progress')
def get_progress():
    return jsonify(progress)

@app.route('/api/download', methods=['POST'])
def start_download():
    if not QB_AVAILABLE:
        return jsonify({'error': 'Server-side torrent client not available'}), 503
    data = request.json
    magnet = data.get('magnet')
    name = data.get('name', 'Unknown')
    if magnet and add_torrent(magnet, name):
        return jsonify({'message': 'Download started'})
    return jsonify({'error': 'Failed to start download'}), 400

@app.route('/api/downloads')
def get_downloads():
    return jsonify(get_download_status())

@app.route('/api/transcoding-status/<path:filename>')
def get_transcoding_status(filename):
    status = transcoding_status.get(filename, 'not_started')
    progress = transcoding_progress.get(filename, 0)
    if status == 'done':
        transcoded_rel = filename.rsplit('.', 1)[0] + '.mp4'
        if os.path.exists(os.path.join(transcoded_dir, transcoded_rel)):
            return jsonify({'status': 'done', 'progress': 100})
    return jsonify({'status': status, 'progress': progress})

@app.route('/api/downloaded-files')
def get_downloaded_files():
    if not QB_AVAILABLE or not downloads_dir:
        return jsonify([])
    files = []
    for root, dirs, filenames in os.walk(downloads_dir):
        for filename in filenames:
            if filename.endswith(('.mp4', '.mkv', '.avi', '.webm')):
                rel_path = os.path.relpath(os.path.join(root, filename), downloads_dir)
                rel_path = rel_path.replace(os.sep, '/')  # Normalize to forward slashes
                if filename.endswith('.mp4'):
                    status = 'ready'
                    progress = 100
                else:
                    status = transcoding_status.get(rel_path, 'not_started')
                    progress = transcoding_progress.get(rel_path, 0)
                files.append({
                    'name': filename,
                    'path': rel_path,
                    'serve_prefix': 'downloads',
                    'size': os.path.getsize(os.path.join(root, filename)),
                    'transcoding_status': status,
                    'transcoding_progress': progress
                })
    return jsonify(files)

@app.route('/api/download/<path:name>', methods=['DELETE'])
def stop_download(name):
    if not ensure_qb_running():
        return jsonify({'error': 'Server-side torrent client not available'}), 503
    try:
        qb_client.torrents_delete(delete_files=False, torrent_hashes=[name])
        return jsonify({'message': 'Download stopped'})
    except Exception as e:
        print(f"Error stopping torrent: {e}")
        return jsonify({'error': 'Failed to stop download'}), 400

@app.route('/api/downloaded-files/<path:filename>', methods=['DELETE'])
def delete_downloaded_file(filename):
    if not downloads_dir:
        return jsonify({'error': 'Downloads directory not available'}), 503
    try:
        file_path = os.path.join(downloads_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            # Delete transcoded version if exists
            transcoded_rel = filename.rsplit('.', 1)[0] + '.mp4'
            transcoded_path = os.path.join(transcoded_dir, transcoded_rel)
            if os.path.exists(transcoded_path):
                os.remove(transcoded_path)
            # Clean up transcoding status
            if filename in transcoding_status:
                del transcoding_status[filename]
            if filename in transcoding_progress:
                del transcoding_progress[filename]
            # Also stop the corresponding torrent if it's active
            if QB_AVAILABLE and ensure_qb_running():
                # Extract torrent name from path (first part before /)
                path_parts = filename.split('/')
                if path_parts:
                    torrent_name = path_parts[0]
                    try:
                        torrents = qb_client.torrents_info()
                        for torrent in torrents:
                            if torrent.name == torrent_name:
                                qb_client.torrents_delete(delete_files=False, torrent_hashes=[torrent.hash])
                                break
                    except Exception as e:
                        print(f"Error stopping torrent: {e}")
            return jsonify({'message': 'File deleted'})
        else:
            # File not found, but return success to update the UI
            return jsonify({'message': 'File not found, but removed from list'})
    except Exception as e:
        print(f"Error deleting file: {e}")
        return jsonify({'error': 'Failed to delete file'}), 400

@app.route('/api/qb-status')
def get_qb_status():
    if not QB_AVAILABLE:
        return jsonify({'status': 'unavailable'})
    try:
        client = Client(host='localhost:5001', username='admin', password='admin123')
        client.auth_log_in()
        return jsonify({'status': 'ready'})
    except:
        return jsonify({'status': 'starting'})

if __name__ == '__main__':
    if QB_AVAILABLE:
        threading.Thread(target=ensure_qb_running).start()
    app.run(debug=True)