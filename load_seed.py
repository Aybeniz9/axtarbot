# load_seed.py
from database import SessionLocal, ProductDB, init_db
from seed_data import sample_products

init_db()
session = SessionLocal()

for p in sample_products:
    session.add(ProductDB(**p))

session.commit()
session.close()
print("Dataset bazaya yükləndi ✅")