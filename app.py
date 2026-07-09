import streamlit as st
import requests
from models import Cart
from clarify import needs_clarification, merge_query
from image_search import describe_image

st.set_page_config(page_title="AxtarBot", page_icon="🔍", layout="wide")
st.markdown("""
<style>
    .stButton > button {
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 8px;
    }
    h3 {
        color: #2c3e50;
    }
    .stProgress > div > div > div > div {
        background-color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

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
if "last_order" not in st.session_state:
    st.session_state.last_order = None
if "checkout_step" not in st.session_state:
    st.session_state.checkout_step = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

st.title("🔍 AxtarBot — Semantik Məhsul Axtarışı")
st.caption("Açar sözə deyil, mənaya əsaslanan axtarış sistemi")

# --- Sidebar: Giriş/Qeydiyyat + Filtrlər ---
with st.sidebar:
    if st.session_state.user_id is None:
        st.header("🔐 Giriş / Qeydiyyat")
        auth_mode = st.radio("Seçim:", ["Giriş", "Qeydiyyat"], horizontal=True)
        auth_email = st.text_input("Email", key="auth_email")
        auth_password = st.text_input("Şifrə", type="password", key="auth_password")

        if auth_mode == "Qeydiyyat":
            if st.button("Qeydiyyatdan keç"):
                try:
                    r = requests.post("http://127.0.0.1:8000/signup", json={"email": auth_email, "password": auth_password})
                    data = r.json()
                    if data.get("success"):
                        st.session_state.user_id = data["user_id"]
                        st.session_state.user_email = data["email"]
                        st.rerun()
                    else:
                        st.error(data.get("message", "Xəta baş verdi."))
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ API-yə qoşulmaq mümkün olmadı.")
        else:
            if st.button("Giriş et"):
                try:
                    r = requests.post("http://127.0.0.1:8000/login", json={"email": auth_email, "password": auth_password})
                    data = r.json()
                    if data.get("success"):
                        st.session_state.user_id = data["user_id"]
                        st.session_state.user_email = data["email"]
                        st.rerun()
                    else:
                        st.error(data.get("message", "Xəta baş verdi."))
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ API-yə qoşulmaq mümkün olmadı.")

        st.divider()
    else:
        st.success(f"👤 {st.session_state.user_email}")
        if st.button("Çıxış et"):
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.rerun()
        st.divider()

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

    sort_option = st.radio(
        "Sırala:",
        ["🎯 Ən uyğun", "💰 Ucuzdan bahaya", "💎 Bahadan ucuza"],
        horizontal=True,
        key=f"sort_{key_prefix}"
    )

    if sort_option == "💰 Ucuzdan bahaya":
        results = sorted(results, key=lambda x: x["price"])
    elif sort_option == "💎 Bahadan ucuza":
        results = sorted(results, key=lambda x: x["price"], reverse=True)

    cols = st.columns(3)
    for i, item in enumerate(results):
        with cols[i % 3]:
            with st.container(border=True):
                category_emoji = {
                    "geyim": "👕", "ayaqqabı": "👟", "aksesuar": "🧣",
                    "elektronika": "🔌", "ev əşyaları": "🏠", "idman": "⚽"
                }.get(item["category"], "📦")

                st.subheader(f"{category_emoji} {item['name']}")
                st.write(f"**Kateqoriya:** {item['category']}")
                st.write(f"**Qiymət:** {item['price']} AZN")

                similarity = item.get("similarity")
                if similarity is not None:
                    st.progress(min(max(similarity, 0), 100) / 100, text=f"🎯 {similarity}% uyğunluq")

                if st.button("🛒 Səbətə at", key=f"add_{key_prefix}_{item['id']}_{i}"):
                    st.session_state.cart.add(item["id"], item["name"], item["price"])
                    st.success(f"{item['name']} səbətə əlavə olundu ✅")


# --- Tab-lar ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🔤 Mətn ilə axtarış",
    "📷 Şəkil ilə axtarış",
    f"🛒 Səbətim ({st.session_state.cart.item_count})",
    "📦 Sifarişlərim"
])

# ============ TAB 1: Mətn axtarışı ============
with tab1:
    st.write("🎤 İstəsən, sualını səslə də deyə bilərsən:")
    audio_value = st.audio_input("Səs qeydi et", key="voice_input")

    voice_query = None
    if audio_value is not None:
        with st.spinner("Səs mətnə çevrilir..."):
            from gemini_transcribe import transcribe_audio
            voice_query = transcribe_audio(audio_value.getvalue(), mime_type="audio/wav")
        st.caption(f"🗣️ Eşidilən: _{voice_query}_")

    query = st.text_input(
        "Nə axtarırsınız?",
        value=voice_query or "",
        placeholder="Məsələn: qışda isti qalmaq üçün geyim"
    )

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

    if st.session_state.get("last_order"):
        order = st.session_state.last_order
        st.success(f"✅ Sifarişiniz qəbul edildi! Sifariş nömrəsi: **{order['order_number']}**")
        st.write(f"Ümumi məbləğ: **{order['total_price']} AZN**")
        st.caption("Sifarişinizin statusunu 'Sifarişlərim' bölməsindən izləyə bilərsiniz.")
        if st.button("Yeni sifarişə başla"):
            st.session_state.last_order = None
            st.session_state.checkout_step = False
            st.rerun()

    elif not cart.items:
        st.info("Səbətiniz hələ boşdur. Axtarış edib məhsul əlavə edə bilərsiniz.")

    elif not st.session_state.checkout_step:
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

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🗑️ Səbəti tam boşalt"):
                st.session_state.cart = Cart()
                st.rerun()
        with col_b:
            if st.button("✅ Sifarişi tamamla", type="primary"):
                st.session_state.checkout_step = True
                st.rerun()

    else:
        st.subheader("📍 Çatdırılma məlumatları")
        customer_name = st.text_input("Ad Soyad")
        address = st.text_area("Ünvan", placeholder="Şəhər, küçə, ev/mənzil nömrəsi")
        phone = st.text_input("Telefon nömrəsi", placeholder="+994 XX XXX XX XX")

        st.divider()
        st.subheader("💳 Ödəniş məlumatları")
        st.caption("⚠️ Bu, tədris məqsədli simulyasiyadır — real ödəniş aparılmır.")
        card_number = st.text_input("Kart nömrəsi", placeholder="XXXX XXXX XXXX XXXX", max_chars=19)
        col_exp, col_cvv = st.columns(2)
        with col_exp:
            expiry = st.text_input("Son istifadə tarixi", placeholder="AA/İİ")
        with col_cvv:
            cvv = st.text_input("CVV", placeholder="XXX", type="password", max_chars=3)

        st.divider()
        st.metric("Ödəniləcək məbləğ", f"{cart.total_price} AZN")

        col_back, col_confirm = st.columns(2)
        with col_back:
            if st.button("← Geri"):
                st.session_state.checkout_step = False
                st.rerun()
        with col_confirm:
            can_submit = customer_name and address and phone and len(card_number.replace(" ", "")) >= 4
            if st.button("💳 Ödə və Sifarişi Təsdiqlə", type="primary", disabled=not can_submit):
                order_payload = {
                    "items": [
                        {
                            "product_id": item.product_id,
                            "name": item.name,
                            "price": item.price,
                            "quantity": item.quantity
                        }
                        for item in cart.items.values()
                    ],
                    "total_price": cart.total_price,
                    "customer_name": customer_name,
                    "address": address,
                    "phone": phone,
                    "card_number": card_number,
                    "user_id": st.session_state.user_id
                }
                try:
                    response = requests.post("http://127.0.0.1:8000/order", json=order_payload)
                    response.raise_for_status()
                    order_data = response.json()
                    st.session_state.last_order = order_data
                    st.session_state.cart = Cart()
                    st.session_state.checkout_step = False
                    st.rerun()
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ API-yə qoşulmaq mümkün olmadı.")
            if not can_submit:
                st.caption("Zəhmət olmasa, bütün sahələri doldurun.")

# ============ TAB 4: Sifarişlərim ============
with tab4:
    st.subheader("📦 Sifarişləriniz")

    try:
        params = {"user_id": st.session_state.user_id} if st.session_state.user_id else {}
        response = requests.get("http://127.0.0.1:8000/orders", params=params)
        response.raise_for_status()
        orders = response.json().get("orders", [])
    except requests.exceptions.ConnectionError:
        st.error("⚠️ API-yə qoşulmaq mümkün olmadı.")
        orders = []

    if not orders:
        st.info("Hələ heç bir sifarişiniz yoxdur.")
    else:
        for order in orders:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Sifariş №:** {order['order_number']}")
                    st.write(f"**Ünvan:** {order.get('address', '-')}")
                    st.write(f"**Kart:** •••• {order.get('card_last4', '----')}")
                with col2:
                    st.metric("Məbləğ", f"{order['total_price']} AZN")

                st.write(f"**Status:** {order['status']}")

                statuses = ["📝 Qəbul edildi", "📦 Hazırlanır", "🚚 Yola çıxıb", "✅ Çatdırıldı"]
                current_index = statuses.index(order['status']) if order['status'] in statuses else 0
                st.progress((current_index + 1) / len(statuses))

                with st.expander("Məhsullar"):
                    for item in order["items"]:
                        st.write(f"- {item['name']} × {item['quantity']} = {item['price'] * item['quantity']} AZN")