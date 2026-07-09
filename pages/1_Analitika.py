import streamlit as st
import pandas as pd
from database import SessionLocal, SearchLog, ProductDB, Order
from sqlalchemy import func

st.set_page_config(page_title="Analitika", page_icon="📊")
st.title("📊 Axtarış və Satış Analitikası")

session = SessionLocal()

# --- Ümumi statistika ---
col1, col2, col3 = st.columns(3)
col1.metric("Ümumi axtarış sayı", session.query(SearchLog).count())
col2.metric("Ümumi sifariş sayı", session.query(Order).count())
total_revenue = session.query(func.sum(Order.total_price)).scalar() or 0
col3.metric("Ümumi gəlir", f"{total_revenue:.2f} AZN")

st.divider()

# --- Ən çox axtarılan sorğular ---
st.subheader("🔥 Ən çox axtarılan sorğular")
top_queries = (
    session.query(SearchLog.query, func.count(SearchLog.id).label("say"))
    .group_by(SearchLog.query)
    .order_by(func.count(SearchLog.id).desc())
    .limit(10)
    .all()
)
if top_queries:
    df = pd.DataFrame(top_queries, columns=["Sorğu", "Say"])
    st.bar_chart(df.set_index("Sorğu"))
else:
    st.info("Hələ heç bir axtarış qeydə alınmayıb.")

# --- Kateqoriya üzrə məhsul bölgüsü ---
st.subheader("📦 Kateqoriya üzrə məhsul bölgüsü")
category_counts = (
    session.query(ProductDB.category, func.count(ProductDB.id).label("say"))
    .group_by(ProductDB.category)
    .all()
)
if category_counts:
    df2 = pd.DataFrame(category_counts, columns=["Kateqoriya", "Say"])
    st.bar_chart(df2.set_index("Kateqoriya"))

# --- Gündəlik axtarış tendensiyası ---
st.subheader("📈 Günlük axtarış sayı")
daily_searches = (
    session.query(func.date(SearchLog.timestamp).label("tarix"), func.count(SearchLog.id).label("say"))
    .group_by(func.date(SearchLog.timestamp))
    .order_by(func.date(SearchLog.timestamp))
    .all()
)
if daily_searches:
    df3 = pd.DataFrame(daily_searches, columns=["Tarix", "Say"])
    st.line_chart(df3.set_index("Tarix"))

# --- Son sifarişlər ---
st.subheader("🧾 Son sifarişlər")
recent_orders = session.query(Order).order_by(Order.created_at.desc()).limit(5).all()
if recent_orders:
    for o in recent_orders:
        st.write(f"**{o.order_number}** — {o.total_price} AZN — {o.customer_name or 'N/A'}")
else:
    st.info("Hələ sifariş yoxdur.")

session.close()