import streamlit as st
import requests
from models import Cart
from clarify import needs_clarification, merge_query
from image_search import describe_image
from models import Cart, Wishlist

st.set_page_config(page_title="AxtarBot", page_icon="🔍", layout="wide")
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Lora:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #F7F3ED;
    }

    h1 {
        font-family: 'Lora', serif;
        color: #1B2A4A;
        font-weight: 700;
    }

    h2, h3 {
        font-family: 'Lora', serif;
        color: #1B2A4A;
    }

    /* Kartlar */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 10px;
        border: 1px solid #E8E2D6;
        box-shadow: 0 2px 8px rgba(27, 42, 74, 0.06);
    }

    /* Düymələr */
    .stButton > button {
        border-radius: 8px;
        border: none;
        background-color: #E8985E;
        color: #ffffff;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #d6813f;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(232, 152, 94, 0.35);
    }

    /* Əsas "Axtar" / "primary" düymələr üçün fərqli görünüş */
    .stButton > button[kind="primary"] {
        background-color: #1B2A4A;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #2a3f66;
    }

    /* Uyğunluq faizi zolağı - kəhrəba -> yaşıl gradient */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #E8985E 0%, #2ECC91 100%);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1B2A4A;
    }
    section[data-testid="stSidebar"] * {
        color: #F7F3ED !important;
    }
    section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] textarea {
        color: #1B2A4A !important;
    }

    /* Tab-lar */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #3D5A73;
    }
    .stTabs [aria-selected="true"] {
        color: #E8985E !important;
        border-bottom-color: #E8985E !important;
    }

    /* Caption/kiçik mətnlər */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #3D5A73;
    }
    /* Başlıqdakı ikon nəbz kimi döyünsün */
    h1 {
        animation: none;
    }
    h1::before {
        content: "";
    }

    /* Kartlar səhifəyə "sürüşərək" gəlsin */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        animation: fadeInUp 0.5s ease-out;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(15px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Uyğunluq zolağı dolarkən animasiyalı görünsün */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #E8985E 0%, #2ECC91 100%);
        background-size: 200% 100%;
        animation: shimmer 2s ease-in-out infinite;
    }

    @keyframes shimmer {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Düymə basılanda "sıçrayış" */
    .stButton > button:active {
        transform: scale(0.96);
    }

    /* Axtarış ikonu (🔍) yüngül nəbz kimi böyüyüb-kiçilsin */
    .stApp > header + div h1 {
        display: inline-flex;
        align-items: center;
        gap: 12px;
    }
</style>

<script>
    // Başlıqdakı 🔍 emojisini tapıb nəbz animasiyası veririk
    setTimeout(function() {
        const h1 = window.parent.document.querySelector('h1');
        if (h1 && !h1.dataset.animated) {
            h1.dataset.animated = "true";
            h1.style.transition = "none";
            const style = document.createElement('style');
            style.innerHTML = `
                @keyframes iconPulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.15); }
                }
            `;
            window.parent.document.head.appendChild(style);
        }
    }, 300);
</script>
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
if "wishlist" not in st.session_state:
    st.session_state.wishlist = Wishlist()

st.markdown("""
<h1 style="display:flex; align-items:center; gap:14px; font-family:'Lora',serif; color:#1B2A4A;">
    <span style="display:inline-block; animation: iconPulse 2s ease-in-out infinite;">🔍</span>
    AxtarBot — Semantik Məhsul Axtarışı
</h1>
<style>
@keyframes iconPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.15) rotate(-8deg); }
}
</style>
""", unsafe_allow_html=True)
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
                        st.toast(f"Xoş gəldin, {data['email']}!", icon="👋")
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

def show_skeleton(count=3):
    """Yüklənmə zamanı boş kart konturları göstərir."""
    cols = st.columns(3)
    for i in range(count):
        with cols[i % 3]:
            st.markdown('<div style="background:#ffffff; border-radius:14px; border:1px solid #E8E2D6; padding:16px; margin-bottom:12px; animation: skeletonPulse 1.4s ease-in-out infinite;"><div style="height:22px; width:70%; background:#E8E2D6; border-radius:4px; margin-bottom:12px;"></div><div style="height:14px; width:50%; background:#E8E2D6; border-radius:4px; margin-bottom:8px;"></div><div style="height:14px; width:40%; background:#E8E2D6; border-radius:4px; margin-bottom:12px;"></div><div style="height:8px; width:100%; background:#E8E2D6; border-radius:4px;"></div></div><style>@keyframes skeletonPulse {0%, 100% { opacity: 1; } 50% { opacity: 0.5; }}</style>', unsafe_allow_html=True)
def show_results(data, key_prefix):
    """Nəticələri kart şəklində göstərir. key_prefix hər tab üçün unikal button key yaradır."""
    if not data:
        return

    results = data.get("results", [])
    source = data.get("source", "live")
    st.caption(f"Mənbə: {'💾 keş' if source == 'cache' else '🔴 canlı'}")

    if not results:
        st.markdown(
            '<div style="text-align:center; padding: 50px 20px; background:#ffffff; border-radius:14px; border:1px solid #E8E2D6;"><div style="font-size:48px; margin-bottom:10px;">🔎</div><div style="font-family:\'Lora\',serif; font-size:18px; color:#1B2A4A; margin-bottom:6px;">Uyğun məhsul tapılmadı</div><div style="color:#3D5A73; font-size:14px;">Filtrləri (qiymət, kateqoriya) yumşaltmağı və ya sorğunu fərqli sözlərlə yenidən yazmağı sına.</div></div>',
            unsafe_allow_html=True)
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

                col_cart, col_heart = st.columns([3, 1])
                with col_cart:
                    if st.button("🛒 Səbətə at", key=f"add_{key_prefix}_{item['id']}_{i}", use_container_width=True):
                        st.session_state.cart.add(item["id"], item["name"], item["price"])
                        st.toast(f"{item['name']} səbətə əlavə olundu!", icon="🛒")
                with col_heart:
                    is_liked = st.session_state.wishlist.contains(item["id"])
                    heart_icon = "❤️" if is_liked else "🤍"
                    if st.button(heart_icon, key=f"wish_{key_prefix}_{item['id']}_{i}"):
                        added = st.session_state.wishlist.toggle(item["id"], item["name"], item["price"],
                                                                 item["category"])
                        if added:
                            st.toast(f"{item['name']} istək siyahısına əlavə olundu!", icon="❤️")
                        else:
                            st.toast(f"{item['name']} istək siyahısından silindi", icon="💔")
                        st.rerun()


# --- Tab-lar ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔤 Mətn ilə axtarış",
    "📷 Şəkil ilə axtarış",
    f"🛒 Səbətim ({st.session_state.cart.item_count})",
    "📦 Sifarişlərim",
    f"❤️ İstəklərim ({st.session_state.wishlist.count})"
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
            skeleton_placeholder = st.empty()
            with skeleton_placeholder.container():
                show_skeleton()
            st.session_state.last_results = run_search(query, max_price, category, top_k)
            skeleton_placeholder.empty()

    if st.session_state.pending_clarification:
        st.info(f"🤔 {st.session_state.pending_clarification}")
        answer = st.text_input("Cavabınız:", key="clarify_answer")
        if st.button("Davam et") and answer:
            with st.spinner("Sorğu zənginləşdirilir..."):
                enriched_query = merge_query(st.session_state.original_query, answer)
            st.caption(f"🔎 Yeni sorğu: _{enriched_query}_")
            skeleton_placeholder = st.empty()
            with skeleton_placeholder.container():
                show_skeleton()
            st.session_state.last_results = run_search(enriched_query, max_price, category, top_k)
            skeleton_placeholder.empty()
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

            skeleton_placeholder = st.empty()
            with skeleton_placeholder.container():
                show_skeleton()
            st.session_state.last_image_results = run_search(description, max_price, category, top_k)
            skeleton_placeholder.empty()

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
        st.markdown(
            '<div style="text-align:center; padding: 60px 20px; background:#ffffff; border-radius:14px; border:1px solid #E8E2D6;"><div style="font-size:56px; margin-bottom:12px;">🛍️</div><div style="font-family:\'Lora\',serif; font-size:20px; color:#1B2A4A; margin-bottom:6px;">Səbətin hələ boşdur</div><div style="color:#3D5A73; font-size:14px;">Yuxarıdakı sekmələrdən axtarış edib bəyəndiyin məhsulları buraya əlavə et.</div></div>',
            unsafe_allow_html=True)
    elif not st.session_state.checkout_step:
        st.subheader("Səbətinizdəki məhsullar")
        for pid, item in list(cart.items.items()):
            col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
            col1.write(f"**{item.name}**")
            col2.write(f"{item.price} AZN × {item.quantity}")
            col3.write(f"= {item.total} AZN")
            if col4.button("❌ Sil", key=f"cart_remove_{pid}"):
                item_name = item.name
                cart.remove(pid)
                st.toast(f"{item_name} səbətdən silindi", icon="🗑️")
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
                    st.toast("Sifarişiniz uğurla qəbul edildi!", icon="✅")
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
        st.markdown(
            '<div style="text-align:center; padding: 60px 20px; background:#ffffff; border-radius:14px; border:1px solid #E8E2D6;"><div style="font-size:56px; margin-bottom:12px;">📦</div><div style="font-family:\'Lora\',serif; font-size:20px; color:#1B2A4A; margin-bottom:6px;">Hələ sifarişin yoxdur</div><div style="color:#3D5A73; font-size:14px;">Səbətə məhsul əlavə edib sifariş verəndə, burada görəcəksən.</div></div>',
            unsafe_allow_html=True)
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

# ============ TAB 5: İstəklərim ============
with tab5:
    wishlist = st.session_state.wishlist

    if not wishlist.items:
        st.markdown('<div style="text-align:center; padding: 60px 20px; background:#ffffff; border-radius:14px; border:1px solid #E8E2D6;"><div style="font-size:56px; margin-bottom:12px;">❤️</div><div style="font-family:\'Lora\',serif; font-size:20px; color:#1B2A4A; margin-bottom:6px;">İstək siyahın hələ boşdur</div><div style="color:#3D5A73; font-size:14px;">Bəyəndiyin məhsulların yanındakı 🤍 düyməsinə bas ki, buraya əlavə olunsun.</div></div>', unsafe_allow_html=True)
    else:
        st.subheader("Bəyəndiyin məhsullar")
        cols = st.columns(3)
        for i, (pid, item) in enumerate(list(wishlist.items.items())):
            with cols[i % 3]:
                with st.container(border=True):
                    category_emoji = {
                        "geyim": "👕", "ayaqqabı": "👟", "aksesuar": "🧣",
                        "elektronika": "🔌", "ev əşyaları": "🏠", "idman": "⚽"
                    }.get(item["category"], "📦")

                    st.subheader(f"{category_emoji} {item['name']}")
                    st.write(f"**Qiymət:** {item['price']} AZN")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("🛒 Səbətə köçür", key=f"wish_to_cart_{pid}"):
                            st.session_state.cart.add(pid, item["name"], item["price"])
                            wishlist.remove(pid)
                            st.toast(f"{item['name']} səbətə köçürüldü!", icon="🛒")
                            st.rerun()
                    with col_b:
                        if st.button("🗑️ Sil", key=f"wish_remove_{pid}"):
                            wishlist.remove(pid)
                            st.rerun()