# app.py
import streamlit as st
import os
import glob
from PIL import Image
import firebase_admin
from firebase_admin import credentials, db

# ==============================================================================
# KHU VỰC GEMINI API (TẠM THỜI GHI CHÚ ĐỂ TEST GIAO DIỆN)
# Khi nào có API Key từ Google AI Studio, bỏ dấu # ở 2 dòng import này:
# ==============================================================================
# from google import genai
# from google.genai import types

st.set_page_config(
    page_title="AI Stylist - Bách Khoa Cổ Phục Việt Nam",
    page_icon="👘",
    layout="wide"
)

# ==========================================
# 1. KHỞI TẠO FIREBASE REALTIME DATABASE
# ==========================================
@st.cache_resource
def init_firebase_rtdb():
    if not firebase_admin._apps:
        # Lấy thông tin cấu hình từ Secrets trên Streamlit Cloud
        firebase_dict = dict(st.secrets["firebase"])
        firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")
        
        cred = credentials.Certificate(firebase_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://ai-stylist---take-my-vibe-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })

init_firebase_rtdb()

# Tải toàn bộ tri thức từ Firebase Realtime Database
@st.cache_data(ttl=600)
def load_knowledge_base():
    try:
        ref = db.reference('/')
        return ref.get() or {}
    except Exception as e:
        st.error(f"Lỗi khi kết nối Firebase: {str(e)}")
        return {}

KNOWLEDGE_DATA = load_knowledge_base()

# ==============================================================================
# 2. KHỞI TẠO GEMINI AI CLIENT (TẠM THỜI GHI CHÚ)
# Khi nào có API Key, bỏ dấu # ở toàn bộ hàm bên dưới:
# ==============================================================================
# @st.cache_resource
# def init_gemini():
#     api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
#     if not api_key:
#         st.error("⚠️ Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets!")
#         st.stop()
#     return genai.Client(api_key=api_key)
#
# gemini_client = init_gemini()

# ==========================================
# 3. GIAO DIỆN CHÍNH STREAMLIT
# ==========================================
st.title("👘 AI STYLIST - BÁCH KHOA CỔ PHỤC VIỆT NAM")

col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📋 Cấu Hình Yêu Cầu")
    
    user_name = st.text_input("1. Tên của bạn (Để lưu lịch sử):", placeholder="Ví dụ: Nguyễn Văn A")
    
    # Lấy danh mục áo động từ Firebase (danh_muc_ao)
# Lấy danh mục áo an toàn (xử lý được cả dạng Dict lẫn List trên Firebase)
    danh_muc_node = KNOWLEDGE_DATA.get("danh_muc_ao") if isinstance(KNOWLEDGE_DATA, dict) else None

    if isinstance(danh_muc_node, dict):
        danh_sach_ao = list(danh_muc_node.keys())
    elif isinstance(danh_muc_node, list):
        danh_sach_ao = [str(x) for x in danh_muc_node if x]
    else:
        danh_sach_ao = ["ao_chit", "ao_tac", "ao_nhat_binh"]

    loai_ao_selected = st.selectbox("2. Chọn loại cổ phục:", options=danh_sach_ao)    loai_ao_selected = st.selectbox("2. Chọn loại cổ phục:", options=danh_sach_ao)
    
    vibe_style = st.selectbox(
        "3. Định hình phong cách (Vibe):",
        ["Thư sinh quý tộc", "Hoài cổ thanh lịch", "Dạo phố hiện đại", "Dự lễ hội / Lễ cưới"]
    )
    
    user_context = st.text_area("4. Mô tả thêm / Phụ kiện muốn kết hợp:")

    # ----------------------------------------------------
    # PHẦN TỰ ĐỘNG QUÉT VÀ HIỂN THỊ ẢNH TỪ THƯ MỤC ASSETS/
    # ----------------------------------------------------
    st.write("---")
    st.subheader("📸 Chọn Mẫu Ảnh Từ Thư Mục Assets")
    
    # Quét tất cả các file ảnh trong thư mục assets và thư mục con
    search_jpg = os.path.join("assets", "**", "*.[jJ][pP][gG]")
    search_jpeg = os.path.join("assets", "**", "*.[jJ][pP][eE][gG]")
    search_png = os.path.join("assets", "**", "*.[pP][nN][gG]")
    image_files = glob.glob(search_jpg, recursive=True) + glob.glob(search_jpeg, recursive=True) + glob.glob(search_png, recursive=True)
    
    selected_image = None
    chosen_img_name = "Khong_chon_anh"
    
    if image_files:
        img_options = {os.path.basename(path): path for path in image_files}
        chosen_img_name = st.selectbox("Chọn 1 ảnh từ thư mục assets để AI phân tích:", list(img_options.keys()))
        
        chosen_img_path = img_options[chosen_img_name]
        selected_image = Image.open(chosen_img_path)
        
        # Hiển thị ảnh vừa chọn
        st.image(selected_image, caption=f"Mẫu đã chọn: {chosen_img_name}", width=280)
    else:
        st.warning("⚠️ Chưa thấy ảnh trong thư mục `assets/`. Hãy tải ảnh vào thư mục `assets/` trên GitHub.")

    btn_submit = st.button("✦ CHẠY THỬ NGHIỆM & LƯU FIREBASE ✦", type="primary", use_container_width=True)

with col_right:
    st.subheader("💡 Kết Quả Phân Tích (Chế Độ Test Giao Diện)")
    
    if btn_submit:
        if not user_name:
            st.warning("⚠️ Vui lòng nhập Tên của bạn trước khi bấm!")
        else:
            with st.spinner("🧪 Đang xử lý chế độ TEST (Chưa dùng Gemini API)..."):
                
                # ----------------------------------------------------------------------
                # A. CÂU TRẢ LỜI GIẢ LẬP ĐỂ TEST GIAO DIỆN & DỮ LIỆU
                # ----------------------------------------------------------------------
                ai_result_text = f"""
### 🧪 [CÂU TRẢ LỜI GIẢ LẬP - TEST MODE]
* **Người dùng:** {user_name}
* **Loại áo chọn:** {loai_ao_selected}
* **Phong cách (Vibe):** {vibe_style}
* **Ảnh đính kèm:** {chosen_img_name}
* **Ghi chú bổ sung:** {user_context if user_context else 'Không có'}

---
#### 📌 Xem trước cấu hình tư vấn:
1. **Định hình phong cách:** Trang phục **{loai_ao_selected}** phối theo tinh thần **{vibe_style}**.
2. **Chất liệu & Phối màu:** Khuyên dùng lụa tơ tằm / gấm mờ nhã nhặn.
3. **Phụ kiện đi kèm:** Khăn đóng, quần đũi ống rộng, hài thêu hoặc guốc mộc.

> 💡 *Lưu ý: Ứng dụng đang chạy Chế độ Test. Khi bạn thêm API Key từ Google AI Studio và mở ghi chú đoạn code Gemini bên dưới, Gemini AI sẽ tự động phân tích chi tiết hình ảnh và văn bản tại đây!*
"""

                # ----------------------------------------------------------------------
                # B. KHI CÓ GEMINI API KEY: BỎ DẤU # Ở ĐOẠN CODE BÊN DƯỚI VÀ XÓA ĐOẠN A
                # ----------------------------------------------------------------------
                # base_prompt = KNOWLEDGE_DATA.get("aivibecode", {}).get("system_base_promt", "Bạn là chuyên gia cố vấn cổ phục Việt Nam.")
                # SYSTEM_PROMPT = f"{base_prompt}\n\nTRI THỨC VÀ LUẬT CẤM KỲ TỪ FIREBASE:\n{KNOWLEDGE_DATA}"
                # 
                # user_prompt = f"Tư vấn cho {user_name}:\n- Áo: {loai_ao_selected}\n- Vibe: {vibe_style}\n- Ghi chú: {user_context}"
                # payload = [user_prompt]
                # if selected_image:
                #     payload.append(selected_image)
                # 
                # response = gemini_client.models.generate_content(
                #     model="gemini-2.5-flash",
                #     contents=payload,
                #     config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0.7)
                # )
                # ai_result_text = response.text

                # Hiển thị kết quả ra màn hình
                st.markdown(ai_result_text)
                
                # ----------------------------------------------------------------------
                # C. GHI LỊCH SỬ THỬ NGHIỆM LÊN FIREBASE REALTIME DATABASE
                # ----------------------------------------------------------------------
                try:
                    ref_history = db.reference('/lich_su_tu_van')
                    ref_history.push({
                        "ten_nguoi_dung": user_name,
                        "loai_ao": loai_ao_selected,
                        "vibe": vibe_style,
                        "ghi_chu": user_context,
                        "anh_assets_chon": chosen_img_name,
                        "ket_qua_ai": ai_result_text,
                        "thoi_gian": firebase_admin.db.ServerValue.TIMESTAMP
                    })
                    st.success("💾 Đã lưu dữ liệu Test thành công vào Firebase Realtime Database!")

                except Exception as e:
                    st.error(f"Lỗi khi lưu Firebase: {str(e)}")

# ==========================================
# 4. HIỂN THỊ LỊCH SỬ TƯ VẤN TỪ FIREBASE
# ==========================================
st.write("---")
st.subheader("📜 Lịch Sử Tư Vấn Đã Lưu Trên Firebase")

if st.button("🔄 Tải Lại Lịch Sử Tư Vấn"):
    try:
        history_data = db.reference('/lich_su_tu_van').order_to_back().limit_to_last(5).get()
        if history_data:
            for key, item in list(history_data.items())[::-1]:
                with st.expander(f"👤 {item.get('ten_nguoi_dung')} - {item.get('loai_ao')} ({item.get('vibe')})"):
                    st.write(f"• **Ảnh đã chọn:** {item.get('anh_assets_chon')}")
                    st.write(f"• **Ghi chú:** {item.get('ghi_chu')}")
                    st.markdown(f"• **Nội dung:**\n{item.get('ket_qua_ai')}")
        else:
            st.info("Chưa có lịch sử tư vấn nào trong Database.")
    except Exception as e:
        st.error(f"Lỗi khi tải lịch sử từ Firebase: {str(e)}")
