from fuzzywuzzy import process, fuzz
import pandas as pd

dtype_ratings = {
    'User-ID': str,
    'ISBN': str,
    'Book-Rating': int,
}
dtype_books = {
    'User-ID': str,
    'Book-Title': str,
    'Book-Author': str,
    'Year-Of-Publication': str,
    'Publisher': str,
    'Image-URL-S': str,
    'Image-URL-M': str,
    'Image-URL-L': str,
}

# load ratings
ratings = pd.read_csv('../backend/BX-Book-Ratings.csv', encoding='cp1251', sep=';', dtype=dtype_ratings)
ratings = ratings[ratings['Book-Rating']!=0]

# load books
books = pd.read_csv('../backend/BX-Books.csv',  encoding='cp1251', sep=';', dtype=dtype_books, on_bad_lines='skip')

titles = books[['Book-Title']].drop_duplicates()

dataset = pd.merge(ratings, books, on=['ISBN'])
dataset_lowercase=dataset.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)

# Assuming titles is a DataFrame containing unique book titles
titles_list = titles['Book-Title'].tolist()

# This dictionary will hold titles as keys and their matches as values
matches = {}

# Set a threshold for considering titles as a match
threshold = 85  # You can adjust this value based on trial and error

for title in titles_list:
    # Process.extract returns a list of matches and their scores
    potential_matches = process.extract(title, titles_list, scorer=fuzz.token_sort_ratio, limit=None)
    # Filter matches based on the threshold
    matches[title] = [match for match, score in potential_matches if score >= threshold and match != title]

# Note: This operation is computationally expensive. Consider parallelizing or optimizing.