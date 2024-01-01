
from chromadb.config import Settings
from src import const
import chromadb

client = chromadb.Client(Settings(chroma_db_impl='duckdb+parquet',
                                  persist_directory=(const.DB_DIR / 'wikihow').as_posix()))

collection = client.get_collection('mini-wikihow-community')

def search_vector_db(query, topN):
     return collection.query(query_texts=query, n_results=topN)
