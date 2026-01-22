import sqlite3

# Connect to the database
conn = sqlite3.connect('media.db')
cursor = conn.cursor()

# Sample data: list of tuples (title, description, poster_path, video_path, genre, type)
sample_data = [
    ('Inception', 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.', 'inception_poster.jpg', 'inception.mp4', 'Action, Thriller', 'movie'),
    ('The Dark Knight', 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.', 'dark_knight_poster.jpg', 'dark_knight.mp4', 'Action, Thriller', 'movie'),
    ('The Shawshank Redemption', 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.', 'shawshank_poster.jpg', 'shawshank.mp4', 'Drama', 'movie'),
    ('Pulp Fiction', 'The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.', 'pulp_fiction_poster.jpg', 'pulp_fiction.mp4', 'Crime, Thriller', 'movie'),
    ('Forrest Gump', 'The presidencies of Kennedy and Johnson, the events of Vietnam, Watergate, and other historical events unfold through the perspective of an Alabama man with an IQ of 75.', 'forrest_gump_poster.jpg', 'forrest_gump.mp4', 'Drama, Comedy', 'movie'),
    ('The Matrix', 'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.', 'matrix_poster.jpg', 'matrix.mp4', 'Action, Sci-Fi', 'movie'),
    ('Interstellar', 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.', 'interstellar_poster.jpg', 'interstellar.mp4', 'Adventure, Drama, Sci-Fi', 'movie'),
    ('Fight Club', 'An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.', 'fight_club_poster.jpg', 'fight_club.mp4', 'Drama', 'movie'),
    ('The Godfather', 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.', 'godfather_poster.jpg', 'godfather.mp4', 'Crime, Drama', 'movie'),
    ('Avatar', 'A paraplegic Marine dispatched to the moon Pandora on a unique mission becomes torn between following his orders and protecting the world he feels is his home.', 'avatar_poster.jpg', 'avatar.mp4', 'Action, Adventure, Fantasy', 'movie'),
]

# Insert the data using executemany
cursor.executemany('''
    INSERT INTO media (title, description, poster_path, video_path, genre, type)
    VALUES (?, ?, ?, ?, ?, ?)
''', sample_data)

# Commit the changes
conn.commit()

# Close the connection
conn.close()

print("Database populated with 10 sample media records.")