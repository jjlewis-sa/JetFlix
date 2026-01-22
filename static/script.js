function addScrollOverlays(container) {
    const leftOverlay = document.createElement('div');
    leftOverlay.className = 'scroll-overlay scroll-left';
    leftOverlay.innerHTML = '&larr;';
    leftOverlay.style.display = 'flex';
    container.appendChild(leftOverlay);

    const rightOverlay = document.createElement('div');
    rightOverlay.className = 'scroll-overlay scroll-right';
    rightOverlay.innerHTML = '&rarr;';
    rightOverlay.style.display = 'flex';
    container.appendChild(rightOverlay);

    leftOverlay.addEventListener('click', () => {
        container.scrollBy({ left: -300, behavior: 'smooth' });
    });

    rightOverlay.addEventListener('click', () => {
        container.scrollBy({ left: 300, behavior: 'smooth' });
    });
}

function showHome() {
    document.getElementById('home-view').style.display = 'block';
    document.getElementById('downloads-view').style.display = 'none';
}

function showDownloads() {
    document.getElementById('home-view').style.display = 'none';
    document.getElementById('downloads-view').style.display = 'block';
    updateDownloads();
    updateVideos();
}

document.addEventListener('DOMContentLoaded', function() {
    // qBittorrent status check
    const qbNotification = document.getElementById('qb-notification');
    const qbMessage = document.getElementById('qb-message');
    let qbStatusChecked = false;

    function checkQbStatus() {
        fetch('/api/qb-status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'starting') {
                    qbMessage.textContent = 'Starting qBittorrent...';
                    qbNotification.style.display = 'block';
                    qbNotification.style.backgroundColor = '#fff3cd'; // Yellow
                    setTimeout(checkQbStatus, 5000); // Check again in 5 seconds
                } else if (data.status === 'ready') {
                    qbMessage.textContent = 'qBittorrent is ready!';
                    qbNotification.style.display = 'block';
                    qbNotification.style.backgroundColor = '#d4edda'; // Green
                    setTimeout(() => {
                        qbNotification.style.display = 'none';
                    }, 3000); // Hide after 3 seconds
                } else if (data.status === 'unavailable') {
                    qbNotification.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error checking qB status:', error);
            });
    }

    // Start checking qB status
    checkQbStatus();

    // Modal references
    const modal = document.getElementById('movie-modal');
    const modalPoster = document.getElementById('modal-poster');
    const modalTitle = document.getElementById('modal-title');
    const modalDescription = document.getElementById('modal-description');
    const modalTorrents = document.getElementById('modal-torrents');
    const playButton = document.getElementById('play-button');
    const closeBtn = document.querySelector('.close');

    // Close modal functionality
    if (closeBtn) {
        closeBtn.onclick = function() {
            modal.style.display = 'none';
        }
    }
    if (modal) {
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
    }

    // Stream modal functionality
    const streamModal = document.getElementById('stream-modal');
    const closeStreamBtn = document.querySelector('.close-stream');
    const fullscreenBtn = document.getElementById('fullscreen-btn');

    if (closeStreamBtn) {
        closeStreamBtn.onclick = function() {
            streamModal.style.display = 'none';
            // Stop any ongoing streams
            const video = document.querySelector('#stream-container video');
            if (video) {
                video.pause();
                video.src = '';
            }
        }
    }

    if (fullscreenBtn) {
        fullscreenBtn.onclick = function() {
            const video = document.querySelector('#stream-container video');
            if (video) {
                if (video.requestFullscreen) {
                    video.requestFullscreen();
                } else if (video.webkitRequestFullscreen) {
                    video.webkitRequestFullscreen();
                } else if (video.msRequestFullscreen) {
                    video.msRequestFullscreen();
                }
            }
        }
    }

    if (streamModal) {
        window.onclick = function(event) {
            if (event.target == streamModal) {
                streamModal.style.display = 'none';
                const video = document.querySelector('#stream-container video');
                if (video) {
                    video.pause();
                    video.src = '';
                }
            }
        }
    }

    // Video player modal for downloads
    const videoModal = document.getElementById('video-player-modal');
    const closeVideoBtn = document.querySelector('.close-video');

    if (closeVideoBtn) {
        closeVideoBtn.onclick = function() {
            videoModal.style.display = 'none';
            const video = document.getElementById('video-player');
            if (video) {
                video.pause();
                video.src = '';
            }
        }
    }

    if (videoModal) {
        window.onclick = function(event) {
            if (event.target == videoModal) {
                videoModal.style.display = 'none';
                const video = document.getElementById('video-player');
                if (video) {
                    video.pause();
                    video.src = '';
                }
            }
        }
    }

    // Function to show modal
    function showModal(item) {
        if (!modal) return;
        modalPoster.src = item.poster_path;
        modalTitle.textContent = item.title;
        modalDescription.textContent = item.description;
        modalTorrents.innerHTML = '';

        if (item.type === 'tv' && item.torrents && typeof item.torrents === 'object' && !Array.isArray(item.torrents)) {
            // Series torrents organized by seasons
            const seasonsContainer = document.createElement('div');
            seasonsContainer.className = 'seasons-container';

            for (const [seasonName, torrents] of Object.entries(item.torrents)) {
                if (torrents.length > 0) {
                    const seasonDiv = document.createElement('div');
                    seasonDiv.className = 'season-section';
                    seasonDiv.innerHTML = `<h3>${seasonName}</h3>`;

                    const torrentList = document.createElement('ul');
                    torrents.forEach(torrent => {
                        const li = document.createElement('li');
                        const episodeInfo = torrent.episode ? ` (${torrent.episode})` : '';
                        li.innerHTML = `
                            <strong>${torrent.title}${episodeInfo}</strong><br>
                            Size: ${torrent.size}<br>
                            Seeders: ${torrent.seeders} | Leechers: ${torrent.leechers}<br>
                            <button onclick="downloadTorrent('${torrent.magnet}')">Download</button>
                            <button onclick="downloadToServer('${torrent.magnet}', '${torrent.title.replace(/'/g, "\\'")}')">Download to Server</button>
                            <button onclick="streamTorrent('${torrent.magnet}')">Stream</button>
                            <span class="copy-icon" onclick="copyToClipboard('${torrent.magnet}')">📋</span>
                        `;
                        torrentList.appendChild(li);
                    });
                    seasonDiv.appendChild(torrentList);
                    seasonsContainer.appendChild(seasonDiv);
                }
            }

            if (seasonsContainer.children.length > 0) {
                modalTorrents.appendChild(seasonsContainer);
            } else {
                modalTorrents.textContent = 'No torrents available.';
            }
        } else if (item.torrents && Array.isArray(item.torrents) && item.torrents.length > 0) {
            // Movie torrents (flat list)
            const torrentList = document.createElement('ul');
            item.torrents.forEach(torrent => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <strong>${torrent.title}</strong><br>
                    Size: ${torrent.size}<br>
                    Seeders: ${torrent.seeders} | Leechers: ${torrent.leechers}<br>
                    <button onclick="downloadTorrent('${torrent.magnet}')">Download</button>
                    <button onclick="downloadToServer('${torrent.magnet}', '${torrent.title.replace(/'/g, "\\'")}')">Download to Server</button>
                    <button onclick="streamTorrent('${torrent.magnet}')">Stream</button>
                    <span class="copy-icon" onclick="copyToClipboard('${torrent.magnet}')">📋</span>
                `;
                torrentList.appendChild(li);
            });
            modalTorrents.appendChild(torrentList);
        } else {
            modalTorrents.textContent = 'No torrents available.';
        }

        playButton.onclick = function() {
            alert(`Playing: ${item.video_path || item.title}`);
        }
        modal.style.display = 'block';
    }

    // Fetch popular movies and populate trending posters
    fetch('/api/popular')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const trendingPosters = document.querySelector('#trending-posters');
            if (trendingPosters) {
                data.forEach(item => {
                    const img = document.createElement('img');
                    img.src = item.poster_path;
                    img.className = 'row-poster';
                    img.alt = item.title;
                    const overlay = document.createElement('div');
                    overlay.className = 'overlay';
                    overlay.innerHTML = `<h3>${item.title}</h3><p>${item.description}</p>`;
                    overlay.style.display = 'none';
                    overlay.style.position = 'absolute';
                    overlay.style.backgroundColor = 'rgba(0,0,0,0.8)';
                    overlay.style.color = 'white';
                    overlay.style.padding = '10px';
                    overlay.style.borderRadius = '5px';
                    overlay.style.zIndex = '10';
                    img.appendChild(overlay);
                    img.addEventListener('mouseover', function() {
                        overlay.style.display = 'block';
                    });
                    img.addEventListener('mouseout', function() {
                        overlay.style.display = 'none';
                    });
                    img.addEventListener('click', function() {
                        showModal(item);
                    });
                    trendingPosters.appendChild(img);
                });
                addScrollOverlays(trendingPosters);
            }
        })
        .catch(error => {
            console.error('Error fetching popular data:', error);
        });

    // Create Movies section
    const main = document.querySelector('.main');
    const moviesSection = document.createElement('section');
    moviesSection.className = 'content-section';
    const moviesTitle = document.createElement('h1');
    moviesTitle.textContent = 'Movies';
    moviesSection.appendChild(moviesTitle);
    main.appendChild(moviesSection);

    // Fetch movie genres and create subsections
    fetch('/genres.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(genres => {
            genres.forEach(genre => {
                const section = document.createElement('section');
                section.className = 'row';
                const h2 = document.createElement('h2');
                h2.textContent = genre.name;
                section.appendChild(h2);
                const rowPosters = document.createElement('div');
                rowPosters.className = 'row-posters';
                section.appendChild(rowPosters);
                moviesSection.appendChild(section);

                // Fetch movies for this genre
                const slug = genre.name.toLowerCase();
                const url = `/api/genre/${slug}`;
                fetch(url)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        data.forEach(item => {
                            const img = document.createElement('img');
                            img.src = item.poster_path;
                            img.className = 'row-poster';
                            img.alt = item.title;
                            const overlay = document.createElement('div');
                            overlay.className = 'overlay';
                            overlay.innerHTML = `<h3>${item.title}</h3><p>${item.description}</p>`;
                            overlay.style.display = 'none';
                            overlay.style.position = 'absolute';
                            overlay.style.backgroundColor = 'rgba(0,0,0,0.8)';
                            overlay.style.color = 'white';
                            overlay.style.padding = '10px';
                            overlay.style.borderRadius = '5px';
                            overlay.style.zIndex = '10';
                            img.appendChild(overlay);
                            img.addEventListener('mouseover', function() {
                                overlay.style.display = 'block';
                            });
                            img.addEventListener('mouseout', function() {
                                overlay.style.display = 'none';
                            });
                            img.addEventListener('click', function() {
                                showModal(item);
                            });
                            rowPosters.appendChild(img);
                        });
                        addScrollOverlays(rowPosters);
                    })
                    .catch(error => {
                        console.error('Error fetching data for genre:', genre.name, error);
                    });
            });
        })
        .catch(error => {
            console.error('Error fetching movie genres:', error);
        });

    // Create Series section
    const seriesSection = document.createElement('section');
    seriesSection.className = 'content-section';
    const seriesTitle = document.createElement('h1');
    seriesTitle.textContent = 'Series';
    seriesSection.appendChild(seriesTitle);
    main.appendChild(seriesSection);

    // Fetch series genres and create subsections
    fetch('/series-genres.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(seriesGenres => {
            seriesGenres.forEach(genre => {
                const section = document.createElement('section');
                section.className = 'row';
                const h2 = document.createElement('h2');
                h2.textContent = genre.name;
                section.appendChild(h2);
                const rowPosters = document.createElement('div');
                rowPosters.className = 'row-posters';
                section.appendChild(rowPosters);
                seriesSection.appendChild(section);

                // Fetch series for this genre
                const slug = genre.name.toLowerCase();
                const url = `/api/series-genre/${slug}`;
                fetch(url)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        data.forEach(item => {
                            const img = document.createElement('img');
                            img.src = item.poster_path;
                            img.className = 'row-poster';
                            img.alt = item.title;
                            const overlay = document.createElement('div');
                            overlay.className = 'overlay';
                            overlay.innerHTML = `<h3>${item.title}</h3><p>${item.description}</p>`;
                            overlay.style.display = 'none';
                            overlay.style.position = 'absolute';
                            overlay.style.backgroundColor = 'rgba(0,0,0,0.8)';
                            overlay.style.color = 'white';
                            overlay.style.padding = '10px';
                            overlay.style.borderRadius = '5px';
                            overlay.style.zIndex = '10';
                            img.appendChild(overlay);
                            img.addEventListener('mouseover', function() {
                                overlay.style.display = 'block';
                            });
                            img.addEventListener('mouseout', function() {
                                overlay.style.display = 'none';
                            });
                            img.addEventListener('click', function() {
                                showModal(item);
                            });
                            rowPosters.appendChild(img);
                        });
                        addScrollOverlays(rowPosters);
                    })
                    .catch(error => {
                        console.error('Error fetching data for series genre:', genre.name, error);
                    });
            });
        })
        .catch(error => {
            console.error('Error fetching series genres:', error);
        });

    // Handle clicks for movies page
    const moviePosters = document.querySelectorAll('.row-poster[data-movie]');
    moviePosters.forEach(poster => {
        poster.addEventListener('click', function() {
            const movieData = JSON.parse(this.getAttribute('data-movie'));
            showModal(movieData);
        });
    });

    // Handle clicks for series page
    const seriesPosters = document.querySelectorAll('.row-poster[data-serie]');
    seriesPosters.forEach(poster => {
        poster.addEventListener('click', function() {
            const serieData = JSON.parse(this.getAttribute('data-serie'));
            showModal(serieData);
        });
    });
});

// Scraping functionality
const scrapeButton = document.getElementById('scrape-button');
const progressContainer = document.getElementById('progress-container');
const progressBar = document.getElementById('progress-bar');
const progressMessage = document.getElementById('progress-message');

scrapeButton.addEventListener('click', () => {
    fetch('/api/scrape', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            progressContainer.style.display = 'block';
            pollProgress();
        })
        .catch(error => console.error('Error starting scrape:', error));
});

function pollProgress() {
    fetch('/api/progress')
        .then(response => response.json())
        .then(data => {
            progressBar.value = data.progress;
            progressMessage.textContent = data.message;
            if (data.status === 'running') {
                setTimeout(pollProgress, 1000);
            } else if (data.status === 'completed') {
                alert('Scraping completed!');
                progressContainer.style.display = 'none';
                location.reload();
            } else if (data.status === 'error') {
                alert('Error: ' + data.message);
                progressContainer.style.display = 'none';
            }
        })
        .catch(error => console.error('Error polling progress:', error));
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Magnet link copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
}

function updateDownloads() {
    fetch('/api/downloads')
    .then(response => response.json())
    .then(data => {
        const downloadsList = document.getElementById('downloads-list');
        if (!downloadsList) return;
        if (data.length === 0) {
            downloadsList.innerHTML = '<p>No active downloads</p>';
            return;
        }
        downloadsList.innerHTML = data.map(download => `
            <div class="download-item">
                <h3>${download.name}</h3>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${download.progress}%"></div>
                </div>
                <p>${download.progress.toFixed(1)}% complete</p>
                <p>Download: ${(download.download_rate / 1000).toFixed(1)} KB/s | Upload: ${(download.upload_rate / 1000).toFixed(1)} KB/s</p>
                <p>Peers: ${download.num_peers} | State: ${download.state}</p>
                <button onclick="stopDownload('${download.hash}')">Stop</button>
            </div>
        `).join('');
    });
}

function updateVideos() {
    fetch('/api/downloaded-files')
    .then(response => response.json())
    .then(data => {
        const videosList = document.getElementById('videos-list');
        if (!videosList) return;
        if (data.length === 0) {
            videosList.innerHTML = '<p>No downloaded videos yet</p>';
            return;
        }
        videosList.innerHTML = data.map(video => `
            <div class="video-item" data-path="${video.path.replace(/"/g, '"')}">
                <div class="video-info">
                    <h3>${video.name}</h3>
                    <p>Size: ${(video.size / (1024*1024*1024)).toFixed(2)} GB</p>
                </div>
                <div class="video-actions">
                    <button onclick="playVideo('${video.path.replace(/'/g, "\\'")}')">Play</button>
                    <button onclick="deleteVideo('${video.path.replace(/'/g, "\\'")}')" style="background-color: #dc3545;">Delete</button>
                </div>
            </div>
        `).join('');
    });
}

function stopDownload(hash) {
    fetch(`/api/download/${hash}`, { method: 'DELETE' })
    .then(response => response.json())
    .then(data => {
        alert(data.message || data.error);
        updateDownloads();
    });
}

function playVideo(path) {
    const modal = document.getElementById('video-player-modal');
    if (!modal) return;
    const video = document.getElementById('video-player');
    video.src = `/downloads/${encodeURIComponent(path)}`;
    video.autoplay = true;
    modal.style.display = 'block';
}

function deleteVideo(path) {
    if (confirm('Are you sure you want to delete this video file?')) {
        fetch(`/api/downloaded-files/${encodeURIComponent(path)}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            // Always remove from UI after delete attempt
            const videoItems = document.querySelectorAll('#videos-list .video-item');
            videoItems.forEach(item => {
                if (item.getAttribute('data-path') === path) {
                    item.remove();
                }
            });
            // Don't refresh immediately, let periodic update handle it
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to delete file');
            updateVideos(); // Refresh the list
        });
    }
}

function downloadTorrent(magnetURI) {
    // Try to open the magnet link
    const newWindow = window.open(magnetURI, '_blank');
    
    // If it fails or no handler, copy to clipboard
    setTimeout(() => {
        if (!newWindow || newWindow.closed) {
            copyToClipboard(magnetURI);
            alert('Magnet link copied to clipboard! Paste it into your torrent client (qBittorrent, uTorrent, etc.) to start downloading.');
        }
    }, 100);
}

function downloadToServer(magnetURI, name) {
    fetch('/api/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ magnet: magnetURI, name: name })
    })
    .then(response => {
        if (response.status === 503) {
            alert('Server-side torrent client not available. Please install libtorrent dependencies or use external torrent client.');
            return;
        }
        return response.json();
    })
    .then(data => {
        if (data && data.message) {
            alert('Download started on server!');
            updateDownloadsList();
        } else if (data) {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to start download');
    });
}

function updateDownloadsList() {
    fetch('/api/downloads')
    .then(response => response.json())
    .then(data => {
        // Update a downloads section if it exists
        console.log('Active downloads:', data);
        // You can add UI to show downloads here
    });
}

function streamTorrent(magnetURI) {
    const streamModal = document.getElementById('stream-modal');
    const streamContainer = document.getElementById('stream-container');

    // Clear previous content
    streamContainer.innerHTML = '<h3>Loading torrent...</h3>';

    // Show the stream modal
    streamModal.style.display = 'block';

    const client = new WebTorrent();

    client.add(magnetURI, function (torrent) {
        // Torrents can contain many files. Let's use the first video file
        const file = torrent.files.find(function (file) {
            return file.name.endsWith('.mp4') || file.name.endsWith('.mkv') || file.name.endsWith('.avi') || file.name.endsWith('.webm');
        });

        if (file) {
            // Create video element
            const video = document.createElement('video');
            video.controls = true;
            video.style.maxWidth = '100%';
            video.style.maxHeight = '100%';

            streamContainer.innerHTML = '<h3>Streaming: ' + file.name + '</h3>';
            streamContainer.appendChild(video);

            file.renderTo(video);
        } else {
            streamContainer.innerHTML = '<p>No compatible video file found in torrent. Supported formats: MP4, MKV, AVI, WebM</p>';
        }
    });

    // Handle errors
    client.on('error', function (err) {
        console.error('WebTorrent error: ', err);
        streamContainer.innerHTML = '<p>Error loading torrent: ' + err.message + '</p>';
    });
}