from chromadb.config import Settings
from src import const
import pandas as pd
import chromadb

client = chromadb.Client(Settings(chroma_db_impl='duckdb+parquet',
                                  persist_directory=(const.DB_DIR / 'recipenlg').as_posix()))

collection = client.get_collection('mini-recipenlg-community')

df = pd.read_csv(const.DATA_DIR / 'recipenlg' / 'test.csv')
df['title'] = df['title'].apply(lambda x: x.replace("'", ''))
df['directions'] = df['directions'].apply(lambda x: eval(x))


def search_vector_db(query, topN):
    res = collection.query(query_texts=query, n_results=topN)
    return [{'title': name.strip(), 'steps': recipe} for name, recipe in zip(res['ids'][0], df[df['title'].isin(res['ids'][0])]['directions'].tolist())]
