import streamlit as st
import pandas as pd
from database import SessionLocal, SearchLog, ProductDB
from sqlalchemy import func

st.set_page_config(page_title="Analitika", page_icon="📊")
st.title("📊 Axtarış Analitikası")

session = SessionLocal()

# Ən çox axtarılan sorğular
top_queries = (
    session.query(SearchLog.query, func.count(SearchLog.id).label("say"))
    .group_by(SearchLog.query)
    .order_by(func.count(SearchLog.id).desc())
    .limit(10)
    .all()
)

st.subheader("🔥 Ən çox axtarılan sorğular")
if top_queries:
    df = pd.DataFrame(top_queries, columns=["Sorğu", "Say"])
    st.bar_chart(df.set_index("Sorğu"))
else:
    st.info("Hələ heç bir axtarış qeydə alınmayıb.")

# Kateqoriya üzrə məhsul sayı
st.subheader("📦 Kateqoriya üzrə məhsul bölgüsü")
category_counts = (
    session.query(ProductDB.category, func.count(ProductDB.id).label("say"))
    .group_by(ProductDB.category)
    .all()
)
if category_counts:
    df2 = pd.DataFrame(category_counts, columns=["Kateqoriya", "Say"])
    st.bar_chart(df2.set_index("Kateqoriya"))

# Ümumi statistika
total_searches = session.query(SearchLog).count()
st.metric("Ümumi axtarış sayı", total_searches)

session.close()