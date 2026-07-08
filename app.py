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
if "last_image_results" not in st.session_state:
    st.session_state.last_image_results = None
if "last_image_description" not in st.session_state:
    st.session_state.last_image_description = None

st.title("🔍 AxtarBot — Semantik Məhsul Axtarışı")
st.caption("Açar sözə deyil, mənaya əsaslanan axtarış sistemi")

# --- Sidebar: yalnız filtrlər + səbətin qısa xülasəsi ---
with st.sidebar:
    st.header("Filtrlər")
    max_price = st.number_input("Maksimum qiymət (AZN)", min_value=0.0, value=0.0, step=5.0)
    category = st.text_input("Kateqoriya (boş buraxsan hamısı)", value="")
    top_k = st.slider("Neçə nəticə göstərilsin?", min_value=1, max_value=10, value=5)

    st.divider()
    st.metric("🛒 Səbətdəki məhsul sayı", st.session_state.cart.item_count)
    st.caption("Tam səbəti görmək üçün 'Səbətim' bölməsinə keç →")


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


def show_results(data, key_prefix):
    """Nəticələri kart şəklində göstərir. key_prefix hər tab üçün unikal button key yaradır."""
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
            if st.button("🛒 Səbətə at", key=f"add_{key_prefix}_{item['id']}_{i}"):
                st.session_state.cart.add(item["id"], item["name"], item["price"])
                st.success(f"{item['name']} səbətə əlavə olundu ✅")
            st.divider()


# --- Tab-lar ---
tab1, tab2, tab3 = st.tabs(["🔤 Mətn ilə axtarış", "📷 Şəkil ilə axtarış", f"🛒 Səbətim ({st.session_state.cart.item_count})"])

# ============ TAB 1: Mətn axtarışı ============
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

    show_results(st.session_state.last_results, key_prefix="text")

# ============ TAB 2: Şəkil ilə axtarış ============
with tab2:
    uploaded_image = st.file_uploader("Məhsul şəkli yüklə", type=["jpg", "jpeg", "png"], key="image_uploader")

    if uploaded_image:
        st.image(uploaded_image, width=200)

        if st.button("Şəklə görə axtar", type="primary"):
            image_bytes = uploaded_image.getvalue()

            with st.spinner("Şəkil təhlil edilir..."):
                description = describe_image(image_bytes, mime_type=uploaded_image.type)
            st.session_state.last_image_description = description

            with st.spinner("Bənzər məhsullar axtarılır..."):
                st.session_state.last_image_results = run_search(description, max_price, category, top_k)

    if st.session_state.last_image_description:
        st.caption(f"🖼️ Aşkarlanan təsvir: _{st.session_state.last_image_description}_")

    show_results(st.session_state.last_image_results, key_prefix="image")

# ============ TAB 3: Səbətim ============
with tab3:
    cart = st.session_state.cart

    if not cart.items:
        st.info("Səbətiniz hələ boşdur. Axtarış edib məhsul əlavə edə bilərsiniz.")
    else:
        st.subheader("Səbətinizdəki məhsullar")

        for pid, item in list(cart.items.items()):
            col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
            col1.write(f"**{item.name}**")
            col2.write(f"{item.price} AZN × {item.quantity}")
            col3.write(f"= {item.total} AZN")
            if col4.button("❌ Sil", key=f"cart_remove_{pid}"):
                cart.remove(pid)
                st.rerun()

        st.divider()
        st.metric("Ümumi məbləğ", f"{cart.total_price} AZN")

        if st.button("🗑️ Səbəti tam boşalt"):
            st.session_state.cart = Cart()
            st.rerun()