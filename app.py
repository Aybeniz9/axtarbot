import streamlit as st
import requests
from models import Cart
from clarify import needs_clarification, merge_query
from image_search import describe_image

st.set_page_config(page_title="AxtarBot", page_icon="🔍", layout="wide")

API_URL = "http://127.0.0.1:8000/search"

# --- Session state ---
if "cart" not in st.session_state:
    st.session_state.cart = Cart()
if "pending_clarification" not in st.session_state:
    st.session_state.pending_clarification = None
if "original_query" not in st.session_state:
    st.session_state.original_query = None
if "last_results" not in st.session_state:
    st.session_state.last_results = None

st.title("🔍 AxtarBot — Semantik Məhsul Axtarışı")
st.caption("Açar sözə deyil, mənaya əsaslanan axtarış sistemi")

# --- Sidebar: Filtrlər + Səbət ---
with st.sidebar:
    st.header("Filtrlər")
    max_price = st.number_input("Maksimum qiymət (AZN)", min_value=0.0, value=0.0, step=5.0)
    category = st.text_input("Kateqoriya (boş buraxsan hamısı)", value="")
    top_k = st.slider("Neçə nəticə göstərilsin?", min_value=1, max_value=10, value=5)

    st.divider()
    st.header(f"🛒 Səbət ({st.session_state.cart.item_count})")
    if st.session_state.cart.items:
        for pid, item in list(st.session_state.cart.items.items()):
            col1, col2 = st.columns([3, 1])
            col1.write(f"{item.name} x{item.quantity} — {item.total} AZN")
            if col2.button("❌", key=f"remove_{pid}"):
                st.session_state.cart.remove(pid)
                st.rerun()
        st.metric("Ümumi", f"{st.session_state.cart.total_price} AZN")
    else:
        st.caption("Səbət boşdur")


def run_search(search_query, max_price, category, top_k):
    payload = {"query": search_query, "top_k": top_k}
    if max_price > 0:
        payload["max_price"] = max_price
    if category.strip():
        payload["category"] = category.strip()

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ API-yə qoşulmaq mümkün olmadı. `uvicorn main:app --reload` işə düşübmü?")
        return None


def show_results():
    """Session state-dəki son nəticələri göstərir — hər rerun-da işləyir."""
    data = st.session_state.last_results
    if not data:
        return

    results = data.get("results", [])
    source = data.get("source", "live")
    st.caption(f"Mənbə: {'💾 keş' if source == 'cache' else '🔴 canlı'}")

    if not results:
        st.info("Heç bir nəticə tapılmadı. Filtrləri yumşaltmağı sınayın.")
        return

    cols = st.columns(3)
    for i, item in enumerate(results):
        with cols[i % 3]:
            st.subheader(item["name"])
            st.write(f"**Kateqoriya:** {item['category']}")
            st.write(f"**Qiymət:** {item['price']} AZN")
            if st.button("🛒 Səbətə at", key=f"add_{item['id']}_{i}"):
                st.session_state.cart.add(item["id"], item["name"], item["price"])
                st.rerun()
            st.divider()


# --- Tab-lar: Mətn axtarışı / Şəkil axtarışı ---
tab1, tab2 = st.tabs(["🔤 Mətn ilə axtarış", "📷 Şəkil ilə axtarış"])

with tab1:
    query = st.text_input("Nə axtarırsınız?", placeholder="Məsələn: qışda isti qalmaq üçün geyim")

    if st.button("Axtar", type="primary") and query:
        with st.spinner("Sorğu təhlil edilir..."):
            clarification = needs_clarification(query)

        if clarification:
            st.session_state.pending_clarification = clarification
            st.session_state.original_query = query
            st.session_state.last_results = None
        else:
            st.session_state.pending_clarification = None
            with st.spinner("Axtarılır..."):
                st.session_state.last_results = run_search(query, max_price, category, top_k)

    # Aydınlaşdırıcı sual axını
    if st.session_state.pending_clarification:
        st.info(f"🤔 {st.session_state.pending_clarification}")
        answer = st.text_input("Cavabınız:", key="clarify_answer")
        if st.button("Davam et") and answer:
            with st.spinner("Sorğu zənginləşdirilir..."):
                enriched_query = merge_query(st.session_state.original_query, answer)
            st.caption(f"🔎 Yeni sorğu: _{enriched_query}_")
            with st.spinner("Axtarılır..."):
                st.session_state.last_results = run_search(enriched_query, max_price, category, top_k)
            st.session_state.pending_clarification = None
            st.rerun()

    # Nəticələr həmişə session_state-dən göstərilir — "Səbətə at" basılanda itmir
    show_results()

with tab2:
    uploaded_image = st.file_uploader("Məhsul şəkli yüklə", type=["jpg", "jpeg", "png"])
    if uploaded_image and st.button("Şəklə görə axtar", type="primary"):
        image_bytes = uploaded_image.read()
        st.image(image_bytes, width=200)

        with st.spinner("Şəkil təhlil edilir..."):
            description = describe_image(image_bytes, mime_type=uploaded_image.type)
        st.caption(f"🖼️ Aşkarlanan təsvir: _{description}_")

        with st.spinner("Bənzər məhsullar axtarılır..."):
            st.session_state.last_results = run_search(description, max_price, category, top_k)
        st.rerun()