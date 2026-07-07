import chromadb
from database import SessionLocal, ProductDB
from embeddings import get_embedding

client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection(name="products")

def index_all_products():
    session = SessionLocal()
    products = session.query(ProductDB).all()

    for p in products:
        embedding = get_embedding(p.description)
        collection.add(
            ids=[str(p.id)],
            embeddings=[embedding],
            metadatas=[{"name": p.name, "category": p.category, "price": p.price}]
        )
    session.close()
    print(f"{len(products)} məhsul indeksləndi ✅")

def semantic_search(query: str, top_k: int = 5):
    query_embedding = get_embedding(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results
def semantic_search(query: str, top_k: int = 5, max_distance: float = 0.6):
    query_embedding = get_embedding(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    # Uzaq (uyğun olmayan) nəticələri süz
    filtered_ids = [[], []]
    for i, dist in enumerate(results["distances"][0]):
        if dist <= max_distance:
            filtered_ids[0].append(results["ids"][0][i])

    # ... (bu hissəni main.py-da distance-a görə filtrləmək daha rahatdır, aşağıya bax)
    return results