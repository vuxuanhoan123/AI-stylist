# app.py
import streamlit as st
import os
import glob
from PIL import Image
import firebase_admin
from firebase_admin import credentials, db

# ==============================================================================
# KHU VỰC GEMINI API (TẠM THỜI GHI CHÚ ĐỂ TEST GIAO DIỆN)
# ==============================================================================
# from google import genai
# from google.genai import types

st.set_page_config(page_title="AI Stylist - Bách Khoa Cổ Phục", page_icon="👘", layout="wide")

# ==============================================================================
# CSS STICKY MƯỢT MÀ (TỰ ĐỘNG BÁM THEO KHI CUỘN)
# ==============================================================================
st.markdown("""
    <style>
    /* Cuộn trang mượt mà */
    html {
        scroll-behavior: smooth;
    }

    /* 1. Thanh Giỏ hàng bám đỉnh mượt (có làm mờ nền phía sau) */
    div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:first-of-type {
        position: sticky;
        top: 2.8rem;
        z-index: 999;
        background-color: rgba(14, 17, 23, 0.85); /* Nền hơi trong suốt */
        backdrop-filter: blur(8px); /* Làm mờ ảnh khi cuộn lướt qua */
        padding-top: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        transition: background-color 0.3s ease;
    }

    /* 2. Cột trái trượt theo tự nhiên, không bị đóng khung cứng */
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div[data-testid="column"]:nth-of-type(1) {
        position: sticky;
        top: 9rem; /* Khoảng cách an toàn dưới giỏ hàng */
        align-self: flex-start; /* Quan trọng: Để cột có thể trượt mượt */
        z-index: 98;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# KHỞI TẠO BIẾN SESSION (GIỎ HÀNG)
# ==========================================
if 'cart' not in st.session_state:
    st.session_state.cart = []

def toggle_item(img_path):
    if img_path in st.session_state.cart:
        st.session_state.cart.remove(img_path)
    else:
        st.session_state.cart.append(img_path)

# ==========================================
# 1. KHỞI TẠO FIREBASE 
# ==========================================
@st.cache_resource
def init_firebase_rtdb():
    if not firebase_admin._apps:
        firebase_dict = dict(st.secrets["firebase"])
        firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(firebase_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://ai-stylist---take-my-vibe-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
init_firebase_rtdb()

@st.cache_data(ttl=600)
def load_knowledge_base():
    try:
        return db.reference('/').get() or {}
    except:
        return {}

KNOWLEDGE_DATA = load_knowledge_base()

# ==========================================
# MAPPING THƯ MỤC ASSETS
# ==========================================
FOLDER_MAPPING = {
    "Áo Ngũ Thân Tay Chẽn": "Ao ngu than tay chen (ao chit)",
    "Áo Tấc": "ao tac ( ao rong )",
    "Áo Nhật Bình": "ao nhat binh",
}

# ==========================================
# CỬA SỔ HIỂN THỊ KẾT QUẢ AI (POPUP / MODAL)
# ==========================================
@st.dialog("🔮 KẾT QUẢ PHÂN TÍCH CHUYÊN GIA", width="large")
def show_ai_result(name, cat, item, vibe, notes, selected_images):
    with st.spinner("🤖 Đang phân tích dữ liệu..."):
        st.markdown(f"""
        ### Xin chào **{name}**!
        Dưới đây là tư vấn phong cách cho lựa chọn của bạn:
        * **Danh mục:** {cat} 
        * **Chi tiết:** {item}
        * **Phong cách (Vibe):** {vibe}
        * **Ghi chú:** {notes if notes else 'Không có'}
        
        **📸 Số lượng ảnh mẫu bạn đã gửi AI phân tích:** {len(selected_images)} ảnh.
        """)
        
        if selected_images:
            st.write("**Các mẫu đã chọn:**")
            cols = st.columns(min(len(selected_images), 5))
            for idx, img_p in enumerate(selected_images):
                cols[idx % 5].image(Image.open(img_p), use_container_width=True)

        st.info("💡 *Đây là Popup kết quả! Phần nền phía sau đã được làm mờ. Khi kết nối API, kết quả trả về của Gemini sẽ hiển thị chi tiết tại đây.*")
        
        try:
            ref_history = db.reference('/lich_su_tu_van')
            ref_history.push({
                "ten_nguoi_dung": name,
                "danh_muc": cat,
                "chi_tiet": item,
                "vibe": vibe,
                "ghi_chu": notes,
                "so_luong_anh": len(selected_images),
                "thoi_gian": firebase_admin.db.ServerValue.TIMESTAMP
            })
            st.success("💾 Đã lưu lịch sử tư vấn vào Database!")
        except Exception as e:
            st.error("Lỗi lưu DB.")

# ==========================================
# 2. GIAO DIỆN CHÍNH (TOP BAR & GIỎ HÀNG)
# ==========================================
col_title, col_cart = st.columns([4, 1])
with col_title:
    st.title("👘 AI STYLIST - BÁCH KHOA CỔ PHỤC")
with col_cart:
    st.write("") 
    with st.popover(f"🛒 Giỏ hàng ảnh ({len(st.session_state.cart)})", use_container_width=True):
        st.markdown("**Các mẫu đã chọn:**")
        if not st.session_state.cart:
            st.write("Chưa có ảnh nào.")
        else:
            for c_img in st.session_state.cart:
                c_name = os.path.basename(c_img)
                st.image(Image.open(c_img), caption=c_name, width=100)
            if st.button("Xóa toàn bộ", key="clear_cart"):
                st.session_state.cart.clear()
                st.rerun()

st.divider()

# ==========================================
# 3. KHU VỰC CHIA CỘT (NHẬP LIỆU & GALLERY)
# ==========================================
col_left, col_right = st.columns([1.2, 2], gap="large")

with col_left:
    st.subheader("📋 1. Thông Tin & Phân Loại")
    
    user_name = st.text_input("Tên của bạn:", placeholder="Ví dụ: Nguyễn Văn A")
    
    danh_muc_chinh = st.selectbox(
        "Danh mục thời trang:",
        ["Trang phục chính", "Đồ đội đầu", "Trang sức"]
    )
    
    loai_chi_tiet = "Chưa chọn"
    
    if danh_muc_chinh == "Trang phục chính":
        danh_muc_node = KNOWLEDGE_DATA.get("danh_muc_ao") if isinstance(KNOWLEDGE_DATA, dict) else None
        danh_sach_ao = []
        if isinstance(danh_muc_node, dict):
            for k, v in danh_muc_node.items():
                if isinstance(v, dict) and "ten_goi" in v: danh_sach_ao.append(v["ten_goi"])
                else: danh_sach_ao.append(str(k))
        elif isinstance(danh_muc_node, list):
            for item in danh_muc_node:
                if isinstance(item, dict) and "ten_goi" in item: danh_sach_ao.append(item["ten_goi"])
        
        if not danh_sach_ao: danh_sach_ao = ["Áo Ngũ Thân Tay Chẽn", "Áo Tấc", "Áo Nhật Bình"]
        
        loai_chi_tiet = st.selectbox("Chọn loại áo:", options=danh_sach_ao)
    else:
        st.info(f"Phần '{danh_muc_chinh}' hiện chưa có dữ liệu hình ảnh, nhưng bạn vẫn có thể mô tả để AI tư vấn.")
        loai_chi_tiet = danh_muc_chinh

    vibe_style = st.selectbox(
        "Định hình phong cách (Vibe):",
        ["Thư sinh quý tộc", "Hoài cổ thanh lịch", "Dạo phố hiện đại", "Dự lễ hội / Lễ cưới"]
    )
    
    user_context = st.text_area("Ghi chú thêm (Chất liệu, màu sắc,...):")

    btn_submit = st.button("✦ BẮT ĐẦU PHÂN TÍCH AI ✦", type="primary", use_container_width=True)
    if btn_submit:
        if not user_name:
            st.warning("⚠️ Vui lòng nhập Tên của bạn trước!")
        else:
            show_ai_result(user_name, danh_muc_chinh, loai_chi_tiet, vibe_style, user_context, st.session_state.cart)

with col_right:
    st.subheader("📸 2. Bộ Sưu Tập (Chọn để đưa vào Giỏ)")
    
    if danh_muc_chinh == "Trang phục chính":
        target_folder = FOLDER_MAPPING.get(loai_chi_tiet)
        
        if target_folder:
            if "hoang cung" in target_folder.lower():
                st.warning("Bộ sưu tập Hoàng Cung không khả dụng ở mục này.")
            else:
                folder_path = os.path.join("assets", target_folder)
                
                search_jpg = os.path.join(folder_path, "**", "*.[jJ][pP][gG]")
                search_png = os.path.join(folder_path, "**", "*.[pP][nN][gG]")
                image_files = glob.glob(search_jpg, recursive=True) + glob.glob(search_png, recursive=True)
                
                if image_files:
                    st.write(f"Tìm thấy **{len(image_files)}** mẫu cho **{loai_chi_tiet}**. Có thể tick chọn nhiều mẫu!")
                    
                    cols = st.columns(3)
                    for i, img_path in enumerate(image_files):
                        with cols[i % 3]:
                            st.image(Image.open(img_path), use_container_width=True)
                            is_checked = img_path in st.session_state.cart
                            st.checkbox(
                                "Chọn mẫu này", 
                                value=is_checked, 
                                key=f"chk_{img_path}", 
                                on_change=toggle_item, 
                                args=(img_path,)
                            )
                else:
                    st.warning(f"⚠ Thư mục `{target_folder}` trống hoặc chưa có ảnh JPG/PNG.")
        else:
            st.info(f"Chưa có thư mục hình ảnh được cấu hình cho '{loai_chi_tiet}'.")
    else:
        st.write("Hình ảnh minh họa cho Đồ đội đầu và Trang sức đang được cập nhật...")
