import requests

def scrape_piratebay(movie_name):
    """
    Scrapes The Pirate Bay for torrent information based on the movie name using the API.
    Returns a list of dictionaries with keys: 'title', 'magnet', 'size', 'seeders', 'leechers'.
    Limits results to top 10 torrents.
    """
    try:
        # Construct search URL using API
        search_url = "https://apibay.org/q.php?q=" + movie_name.replace(' ', '+')
        print("Searching for: " + movie_name)

        # Send request
        response = requests.get(search_url, timeout=30)
        response.raise_for_status()

        data = response.json()
        print("Found " + str(len(data)) + " results")

        torrents = []
        for item in data[:10]:
            torrents.append({
                'title': item['name'],
                'magnet': f"magnet:?xt=urn:btih:{item['info_hash']}",
                'size': item['size'],
                'seeders': item['seeders'],
                'leechers': item['leechers']
            })
        print("Returning " + str(len(torrents)) + " torrents for " + movie_name)
        return torrents

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    except Exception as e:
        print(f"Error parsing data: {e}")
        return []

def scrape_series_torrents(series_name):
    """
    Scrapes The Pirate Bay for series torrents, looking for season packs and individual episodes.
    Returns a dictionary organized by seasons, with each season containing episode torrents.
    """
    import re

    seasons = {}
    max_seasons = 5  # Limit to first 5 seasons to avoid too many requests
    max_episodes_per_season = 5  # Limit episodes per season

    try:
        # First, try to find complete season packs
        for season_num in range(1, max_seasons + 1):
            season_queries = [
                f"{series_name} S{season_num:02d}",
                f"{series_name} Season {season_num}",
                f"{series_name} S{season_num}"
            ]

            season_torrents = []

            for query in season_queries:
                try:
                    search_url = "https://apibay.org/q.php?q=" + query.replace(' ', '+')
                    print(f"Searching for season: {query}")

                    response = requests.get(search_url, timeout=15)
                    response.raise_for_status()

                    data = response.json()
                    print(f"Found {len(data)} results for {query}")

                    # Look for season packs (containing "Complete" or "Season" in title)
                    for item in data[:5]:  # Check top 5 results
                        title = item['name'].lower()
                        if ('complete' in title or 'season' in title) and str(season_num) in title:
                            season_torrents.append({
                                'title': item['name'],
                                'magnet': f"magnet:?xt=urn:btih:{item['info_hash']}",
                                'size': item['size'],
                                'seeders': item['seeders'],
                                'leechers': item['leechers'],
                                'type': 'season_pack'
                            })
                            break  # Take the first good match

                    if season_torrents:
                        break  # Found season pack, no need to try other queries

                except Exception as e:
                    print(f"Error searching for {query}: {e}")
                    continue

            # If no season pack found, look for individual episodes
            if not season_torrents:
                episode_torrents = []
                for episode_num in range(1, max_episodes_per_season + 1):
                    episode_queries = [
                        f"{series_name} S{season_num:02d}E{episode_num:02d}",
                        f"{series_name} Season {season_num} Episode {episode_num}"
                    ]

                    for query in episode_queries:
                        try:
                            search_url = "https://apibay.org/q.php?q=" + query.replace(' ', '+')
                            response = requests.get(search_url, timeout=10)
                            response.raise_for_status()

                            data = response.json()

                            for item in data[:3]:  # Check top 3 results
                                title = item['name']
                                # Check if it matches the episode pattern
                                if re.search(rf'S0?{season_num}E0?{episode_num}', title, re.IGNORECASE):
                                    episode_torrents.append({
                                        'title': title,
                                        'magnet': f"magnet:?xt=urn:btih:{item['info_hash']}",
                                        'size': item['size'],
                                        'seeders': item['seeders'],
                                        'leechers': item['leechers'],
                                        'type': 'episode',
                                        'episode': f"S{season_num:02d}E{episode_num:02d}"
                                    })
                                    break

                            if len(episode_torrents) >= episode_num:  # Found this episode
                                break

                        except Exception as e:
                            print(f"Error searching for episode {query}: {e}")
                            continue

                season_torrents = episode_torrents

            if season_torrents:
                seasons[f"Season {season_num}"] = season_torrents

        return seasons

    except Exception as e:
        print(f"Error in series torrent scraping: {e}")
        return {}
