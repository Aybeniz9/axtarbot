from fastapi import FastAPI
from pydantic import BaseModel
from database import User, hash_password
from cache import get_cached, set_cache
from vector_store import semantic_search
import json
from database import SessionLocal, SearchLog, Order, generate_order_number, get_order_status
import os
import os

# Server ilk dəfə işə düşəndə (və ya restart-dan sonra) avtomatik indeksləmə
if not os.path.exists("./chroma_data"):
    from vector_store import index_all_products
    print("ChromaData tapılmadı, məhsullar indekslənir...")
    index_all_products()
    print("İndeksləmə tamamlandı ✅")
if not os.path.exists("./chroma_data"):
    from vector_store import index_all_products
    index_all_products()


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
        if distance > 0.75:
            continue
        if req.max_price and meta["price"] > req.max_price:
            continue
        if req.category and meta["category"] != req.category:
            continue
        similarity = round((1 - distance) * 100)
        results.append({
            "id": raw["ids"][0][i],
            "name": meta["name"],
            "category": meta["category"],
            "price": meta["price"],
            "similarity": similarity

        })

    set_cache(req.query, results)

    # Axtarışı qeyd et (analitika üçün)
    session = SessionLocal()
    session.add(SearchLog(query=req.query, category=req.category, result_count=len(results)))
    session.commit()
    session.close()

    return {"results": results, "source": "live"}
class OrderItem(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int


class OrderRequest(BaseModel):
    items: list[OrderItem]
    total_price: float
    customer_name: str
    address: str
    phone: str
    card_number: str  # yalnız son 4 rəqəm saxlanılacaq



class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/signup")
def signup(req: SignupRequest):
    session = SessionLocal()
    existing = session.query(User).filter(User.email == req.email).first()
    if existing:
        session.close()
        return {"success": False, "message": "Bu email artıq qeydiyyatdan keçib."}

    new_user = User(email=req.email, password_hash=hash_password(req.password))
    session.add(new_user)
    session.commit()
    user_id = new_user.id
    session.close()
    return {"success": True, "user_id": user_id, "email": req.email}


@app.post("/login")
def login(req: LoginRequest):
    session = SessionLocal()
    user = session.query(User).filter(User.email == req.email).first()
    session.close()

    if not user or user.password_hash != hash_password(req.password):
        return {"success": False, "message": "Email və ya şifrə səhvdir."}

    return {"success": True, "user_id": user.id, "email": user.email}



class OrderRequest(BaseModel):
    items: list[OrderItem]
    total_price: float
    customer_name: str
    address: str
    phone: str
    card_number: str
    user_id: int | None = None   # ➕ yeni sətir


@app.post("/order")
def create_order(req: OrderRequest):
    order_number = generate_order_number()
    card_last4 = req.card_number.replace(" ", "")[-4:] if req.card_number else "0000"

    session = SessionLocal()
    new_order = Order(
        user_id=req.user_id,   # ➕ yeni sətir
        order_number=order_number,
        items_json=json.dumps([item.dict() for item in req.items]),
        total_price=req.total_price,
        customer_name=req.customer_name,
        address=req.address,
        phone=req.phone,
        card_last4=card_last4,
        status="📝 Qəbul edildi"
    )
    session.add(new_order)
    session.commit()
    session.close()

    return {"order_number": order_number, "total_price": req.total_price}


@app.get("/orders")
def list_orders(user_id: int | None = None):
    session = SessionLocal()
    query = session.query(Order).order_by(Order.created_at.desc())
    if user_id is not None:
        query = query.filter(Order.user_id == user_id)
    orders = query.all()

    result = []
    for o in orders:
        result.append({
            "order_number": o.order_number,
            "items": json.loads(o.items_json),
            "total_price": o.total_price,
            "customer_name": o.customer_name,
            "address": o.address,
            "card_last4": o.card_last4,
            "status": get_order_status(o.created_at),
            "created_at": o.created_at.isoformat()
        })
    session.close()
    return {"orders": result}