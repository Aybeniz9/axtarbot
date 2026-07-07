from fastapi import FastAPI
from pydantic import BaseModel

from cache import get_cached, set_cache
from vector_store import semantic_search
from database import SessionLocal, SearchLog


app = FastAPI(title="AxtarBot API")


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    max_price: float | None = None
    category: str | None = None


@app.post("/search")
def search_products(req: SearchRequest):
    cached = get_cached(req.query)
    if cached:
        return {"results": cached, "source": "cache"}

    raw = semantic_search(req.query, req.top_k)
    results = []
    for i, meta in enumerate(raw["metadatas"][0]):
        distance = raw["distances"][0][i]
        if distance > 0.75:  # çox uzaq nəticələri atır
            continue
        if req.max_price and meta["price"] > req.max_price:
            continue
        if req.category and meta["category"] != req.category:
            continue
        results.append({
            "id": raw["ids"][0][i],
            "name": meta["name"],
            "category": meta["category"],
            "price": meta["price"]
        })

    set_cache(req.query, results)

    # Axtarışı qeyd et (analitika üçün)
    session = SessionLocal()
    session.add(SearchLog(query=req.query, category=req.category, result_count=len(results)))
    session.commit()
    session.close()

    return {"results": results, "source": "live"}