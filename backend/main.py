from fastapi import FastAPI, Query
from pydantic import BaseModel
import pandas as pd

app = FastAPI()


def load_data():
    dtype_ratings = {
        'User-ID': str,
        'ISBN': str,
        'Book-Rating': int,
    }
    dtype_books = {
        'ISBN': str,
        'Book-Title': str,
        'Book-Author': str,
        'Year-Of-Publication': str,
        'Publisher': str,
        'Image-URL-S': str,
        'Image-URL-M': str,
        'Image-URL-L': str,
    }

    ratings = pd.read_csv('./datasets/BX-Book-Ratings-Cleaned.csv', encoding='latin1', sep=';', dtype=dtype_ratings)
    ratings = ratings[ratings['Book-Rating'] != 0]

    books = pd.read_csv('./datasets/BX-Books-Cleaned.csv', encoding='latin1', sep=';', dtype=dtype_books,
                        on_bad_lines='skip')
    titles = books[['Book-Title']].drop_duplicates()

    dataset = pd.merge(ratings, books, on=['ISBN'])
    dataset_lowercase = dataset.apply(lambda x: x.str.lower() if x.dtype == 'object' else x)

    return dataset, dataset_lowercase, titles


dataset, dataset_lowercase, titles = load_data()


class BookRequest(BaseModel):
    book: str


@app.get("/books/")
async def get_books_by_title(query: str = Query(None, min_length=1)):
    if not query:
        return []

    query_words = query.lower().split()

    def query_in_title(title):
        return all(word in title.lower() for word in query_words)

    filtered_books = titles[titles['Book-Title'].apply(query_in_title)]
    return filtered_books['Book-Title'].head(50).tolist()


@app.post("/recommend/")
async def recommend_book(book_request: BookRequest):
    try:
        selected_book = book_request.book.lower()
        print("selected_book", selected_book)

        selected_readers = dataset_lowercase['User-ID'][(dataset_lowercase['Book-Title'] == selected_book)]
        selected_readers = set(selected_readers)

        # final dataset
        books_of_selected_readers = dataset_lowercase[(dataset_lowercase['User-ID'].isin(selected_readers))]

        # Number of ratings per other books in dataset
        number_of_rating_per_book = books_of_selected_readers.groupby(['Book-Title']).agg('count').reset_index()

        # select only books which have actually higher number of ratings than threshold
        books_to_compare = number_of_rating_per_book['Book-Title'][number_of_rating_per_book['User-ID'] >= 8]
        books_to_compare = set(books_to_compare)

        ratings_data_raw = books_of_selected_readers[['User-ID', 'Book-Rating', 'Book-Title']][
            books_of_selected_readers['Book-Title'].isin(books_to_compare)]

        # group by User and Book and compute mean
        ratings_data_raw_nodup = ratings_data_raw.groupby(['User-ID', 'Book-Title'])['Book-Rating'].mean()

        # reset index to see User-ID in every row
        ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()

        dataset_for_corr = ratings_data_raw_nodup.pivot(index='User-ID', columns='Book-Title', values='Book-Rating')

        # Take out the Lord of the Rings selected book from correlation dataframe
        dataset_of_other_books = dataset_for_corr.copy(deep=False)
        dataset_of_other_books.drop([selected_book], axis=1, inplace=True)

        # empty lists
        book_titles = []
        correlations = []
        avg_rating = []

        # corr computation
        for book_title in list(dataset_of_other_books.columns.values):
            book_titles.append(book_title)
            correlations.append(dataset_for_corr[selected_book].corr(dataset_of_other_books[book_title]))
            tab = (ratings_data_raw[ratings_data_raw['Book-Title'] == book_title]
                   .groupby(ratings_data_raw['Book-Title']).mean(numeric_only=True))
            avg_rating.append(tab['Book-Rating'].min())
        # final dataframe of all correlation of each book   
        correlated = pd.DataFrame(list(zip(book_titles, correlations, avg_rating)),
                                  columns=['title', 'corr', 'avg_rating'])

        # top 10 books with highest corr
        top = correlated.sort_values('corr', ascending=False).head(10)

        if top.empty:
            return top_books_overall()

        return top.to_dict(orient='records')
    except:
        print("returning top_books_overall")
        return top_books_overall()


# weighted_rating = ((v * R) + (m * C)) / (v + m)
def top_books_overall():
    dataset_nonzero = dataset[dataset['Book-Rating'] != 0]

    book_stats = dataset_nonzero.groupby('ISBN').agg(
        Rating_Count=('Book-Rating', 'size'),
        Avg_Rating=('Book-Rating', 'mean')
    ).reset_index()

    threshold = book_stats['Rating_Count'].quantile(.96)
    c = book_stats['Avg_Rating'].mean()
    m = threshold

    book_stats['Weighted_Rating'] = (book_stats['Rating_Count'] * book_stats['Avg_Rating'] + m * c) / (
                book_stats['Rating_Count'] + m)

    books_to_compare = book_stats[book_stats['Rating_Count'] > threshold]
    top_books = books_to_compare.nlargest(10, 'Weighted_Rating')

    top_books = top_books.merge(dataset[['ISBN', 'Book-Title']].drop_duplicates(), on='ISBN', how='left')

    return [{'title': row['Book-Title'], 'corr': 0, 'avg_rating': row['Weighted_Rating']} for _, row in
            top_books.iterrows()]
