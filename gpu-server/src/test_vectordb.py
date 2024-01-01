import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",
                                persist_directory="./wikihow_db_store"
                            ))

collection = client.get_collection("cleaned_wikihow_0607")

def search_vector_db(query, topN):
    results = collection.query(
        query_texts=query,
        n_results=topN
    )
    return results


collection.delete(
    where={"title": "How to Jump Start a Car"}
)
collection.delete(
    where={"title": "How to Hook up Jumper Cables"}
)
res = search_vector_db("jumper cable", 30)["metadatas"][0]
titles = []
for i in range(len(res)):
    titles.append(res[i]["title"])

print(titles)
