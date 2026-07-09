from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy import DateTime
from datetime import datetime
import json
import random
import string
import hashlib


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    stock = Column(Integer, default=0)

def init_db():
    Base.metadata.create_all(bind=engine)



class SearchLog(Base):
    __tablename__ = "search_logs"
    id = Column(Integer, primary_key=True)
    query = Column(String, nullable=False)
    category = Column(String, nullable=True)
    result_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    order_number = Column(String, unique=True, nullable=False)
    items_json = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)
    customer_name = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    card_last4 = Column(String, nullable=True)
    status = Column(String, default="Qəbul edildi")
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, nullable=True)   # ➕ yeni sətir



def generate_order_number():
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"AXB-{suffix}"


def get_order_status(created_at: datetime) -> str:
    """Sifarişin yaranma vaxtına görə simulyasiya edilmiş status qaytarır."""
    elapsed = (datetime.utcnow() - created_at).total_seconds()
    if elapsed < 30:
        return "📝 Qəbul edildi"
    elif elapsed < 90:
        return "📦 Hazırlanır"
    elif elapsed < 180:
        return "🚚 Yola çıxıb"
    else:
        return "✅ Çatdırıldı"


def generate_order_number():
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"AXB-{suffix}"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()