import requests
import json
from scrape_piratebay import scrape_piratebay, scrape_series_torrents

# Get your free API key from https://www.themoviedb.org/settings/api
API_KEY = '9de6640aa5f9b0d8ba7c02a55017bf81'

def scrape_popular_movies(progress_callback=None):
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if progress_callback:
            progress_callback(None, 'Fetched popular movies from TMDB')

        movies = []
        for movie in data['results'][:1000]:
            title = movie.get('title', 'Unknown')
            poster_path = 'https://image.tmdb.org/t/p/w500/' + movie.get('poster_path', '') if movie.get('poster_path') else ''
            description = movie.get('overview', 'No description available.')
            genre = 'Movie'
            type_ = 'movie'
            
            movie_dict = {
                'title': title,
                'poster_path': poster_path,
                'description': description,
                'genre': genre,
                'type': type_,
                'torrents': scrape_piratebay(title)
            }
            movies.append(movie_dict)
        
        with open('popular-movielist.json', 'w') as f:
            json.dump(movies, f, indent=4)
        if progress_callback:
            progress_callback(20, 'Saved popular movies')

        print("Scraping completed. Data saved to popular-movielist.json")

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    except KeyError as e:
        print(f"Error parsing data: {e}")

def scrape_genre_movies(genre_id, genre_name, progress_callback=None):
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres={genre_id}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if progress_callback:
            progress_callback(10, 'Fetched ' + genre_name + ' movies from TMDB')

        movies = []
        for movie in data['results'][:1000]:
            title = movie.get('title', 'Unknown')
            poster_path = 'https://image.tmdb.org/t/p/w500/' + movie.get('poster_path', '') if movie.get('poster_path') else ''
            description = movie.get('overview', 'No description available.')
            genre = genre_name
            type_ = 'movie'
            
            movie_dict = {
                'title': title,
                'poster_path': poster_path,
                'description': description,
                'genre': genre,
                'type': type_,
                'torrents': scrape_piratebay(title)
            }
            movies.append(movie_dict)
        
        filename = f'{genre_name.lower()}-movielist.json'
        with open(filename, 'w') as f:
            json.dump(movies, f, indent=4)
        if progress_callback:
            progress_callback(None, 'Saved ' + genre_name + ' movies')

        print(f"Scraping completed for {genre_name}. Data saved to {filename}")

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    except KeyError as e:
        print(f"Error parsing data: {e}")

def get_genres(progress_callback=None):
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        genres = data['genres']
        if progress_callback:
            progress_callback(30, 'Fetched movie genres list')

        with open('genres.json', 'w') as f:
            json.dump(genres, f, indent=4)
        if progress_callback:
            progress_callback(35, 'Saved movie genres')

        print("Movie genres fetched and saved to genres.json")

    except requests.RequestException as e:
        print(f"Error fetching movie genres: {e}")
    except KeyError as e:
        print(f"Error parsing movie genres data: {e}")

def get_series_genres(progress_callback=None):
    url = f'https://api.themoviedb.org/3/genre/tv/list?api_key={API_KEY}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        genres = data['genres']
        if progress_callback:
            progress_callback(None, 'Fetched series genres list')

        with open('series-genres.json', 'w') as f:
            json.dump(genres, f, indent=4)
        if progress_callback:
            progress_callback(None, 'Saved series genres')

        print("Series genres fetched and saved to series-genres.json")

    except requests.RequestException as e:
        print(f"Error fetching series genres: {e}")
    except KeyError as e:
        print(f"Error parsing series genres data: {e}")

def scrape_popular_series(progress_callback=None):
    url = f'https://api.themoviedb.org/3/tv/popular?api_key={API_KEY}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if progress_callback:
            progress_callback(None, 'Fetched popular series from TMDB')

        series = []
        for serie in data['results'][:1000]:
            title = serie.get('name', 'Unknown')
            poster_path = 'https://image.tmdb.org/t/p/w500/' + serie.get('poster_path', '') if serie.get('poster_path') else ''
            description = serie.get('overview', 'No description available.')
            genre = 'Series'
            type_ = 'tv'

            serie_dict = {
                'title': title,
                'poster_path': poster_path,
                'description': description,
                'genre': genre,
                'type': type_,
                'torrents': scrape_series_torrents(title)
            }
            series.append(serie_dict)

        with open('popular-serieslist.json', 'w') as f:
            json.dump(series, f, indent=4)
        if progress_callback:
            progress_callback(None, 'Saved popular series')

        print("Popular series scraping completed. Data saved to popular-serieslist.json")

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    except KeyError as e:
        print(f"Error parsing data: {e}")

def scrape_series_genre(genre_id, genre_name, progress_callback=None):
    url = f'https://api.themoviedb.org/3/discover/tv?api_key={API_KEY}&with_genres={genre_id}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if progress_callback:
            progress_callback(None, 'Fetched ' + genre_name + ' series from TMDB')

        series = []
        for serie in data['results'][:1000]:
            title = serie.get('name', 'Unknown')
            poster_path = 'https://image.tmdb.org/t/p/w500/' + serie.get('poster_path', '') if serie.get('poster_path') else ''
            description = serie.get('overview', 'No description available.')
            genre = genre_name
            type_ = 'tv'

            serie_dict = {
                'title': title,
                'poster_path': poster_path,
                'description': description,
                'genre': genre,
                'type': type_,
                'torrents': scrape_series_torrents(title)
            }
            series.append(serie_dict)

        filename = f'{genre_name.lower()}-serieslist.json'
        with open(filename, 'w') as f:
            json.dump(series, f, indent=4)
        if progress_callback:
            progress_callback(None, 'Saved ' + genre_name + ' series')

        print(f"Series scraping completed for {genre_name}. Data saved to {filename}")

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    except KeyError as e:
        print(f"Error parsing data: {e}")

if __name__ == "__main__":
    scrape_popular_movies()
    get_genres()
    with open('genres.json', 'r') as f:
        genres = json.load(f)
    for i, genre in enumerate(genres):
        genre_name = genre['name']
        scrape_genre_movies(genre['id'], genre_name)

    scrape_popular_series()
    get_series_genres()
    with open('series-genres.json', 'r') as f:
        series_genres = json.load(f)
    for genre in series_genres:
        genre_name = genre['name']
        scrape_series_genre(genre['id'], genre_name)