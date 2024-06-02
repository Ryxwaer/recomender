from fastapi import FastAPI, Query
from pydantic import BaseModel
import pandas as pd
import os
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# MongoDB connection setup
client = AsyncIOMotorClient(os.getenv('DB_URI'))
db = client['DataSentics']
books_collection = db['books']
ratings_collection = db['ratings']


class BookRequest(BaseModel):
    book: str


@app.get("/all")
async def get_all_documents():
    # Retrieve all Book-Tile from books_collection
    entries = books_collection.find({}, {'Book-Title': 1}).to_list(length=100)

    return entries


async def fetch_books():
    books_cursor = books_collection.find()
    books = await books_cursor.to_list(None)
    return pd.DataFrame(books)


async def fetch_ratings():
    ratings_cursor = ratings_collection.find()
    ratings = await ratings_cursor.to_list(None)
    return pd.DataFrame(ratings)


@app.get("/books/")
async def get_books_by_title(query: str = Query(default=None, min_length=1)):
    books_df = await fetch_books()
    titles = books_df[['Book-Title']].drop_duplicates()
    
    if query:
        query_words = query.lower().split()
        
        def query_in_title(title):
            title_lower = title.lower()
            return all(word in title_lower for word in query_words)
        
        filtered_books = titles[titles['Book-Title'].apply(query_in_title)]
        return filtered_books['Book-Title'].head(50).tolist()
    
    return []


@app.post("/recommend/")
async def recommend_book(book_request: BookRequest):
    selected_book = book_request.book.lower()

    books_df = await fetch_books()
    ratings_df = await fetch_ratings()
    dataset = pd.merge(ratings_df, books_df, on=['ISBN'])
    dataset_lowercase = dataset.apply(lambda x: x.str.lower() if x.dtype == 'object' else x)

    selected_readers = dataset_lowercase['User-ID'][dataset_lowercase['Book-Title'] == selected_book]
    selected_readers = set(selected_readers)

    books_of_selected_readers = dataset_lowercase[dataset_lowercase['User-ID'].isin(selected_readers)]
    number_of_rating_per_book = books_of_selected_readers.groupby(['Book-Title']).agg('count').reset_index()
    books_to_compare = number_of_rating_per_book['Book-Title'][number_of_rating_per_book['User-ID'] >= 8]
    books_to_compare = set(books_to_compare)

    ratings_data_raw = books_of_selected_readers[['User-ID', 'Book-Rating', 'Book-Title']][books_of_selected_readers['Book-Title'].isin(books_to_compare)]
    ratings_data_raw_nodup = ratings_data_raw.groupby(['User-ID', 'Book-Title'])['Book-Rating'].mean().to_frame().reset_index()
    dataset_for_corr = ratings_data_raw_nodup.pivot(index='User-ID', columns='Book-Title', values='Book-Rating')

    top = []
    dataset_of_other_books = dataset_for_corr.copy(deep=False)
    dataset_of_other_books.drop([selected_book], axis=1, inplace=True)

    book_titles = []
    correlations = []
    avgrating = []

    for book_title in list(dataset_of_other_books.columns.values):
        book_titles.append(book_title)
        correlations.append(dataset_for_corr[selected_book].corr(dataset_of_other_books[book_title]))
        tab = ratings_data_raw[ratings_data_raw['Book-Title'] == book_title].groupby(ratings_data_raw['Book-Title']).mean(numeric_only=True)
        avgrating.append(tab['Book-Rating'].min())
    
    corr_fellowship = pd.DataFrame(list(zip(book_titles, correlations, avgrating)), columns=['title', 'corr', 'avg_rating'])
    top = corr_fellowship.sort_values('corr', ascending=False).head(10)
    return top.to_dict(orient='records')