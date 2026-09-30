import streamlit as st
import time
import base64
from PIL import Image

# 1. Cấu hình trang web Streamlit
st.set_page_config(
    page_title="AI Stylist - Take My Vibe",
    page_icon="👘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS cho Giao diện & Hiệu ứng Hover Loading 1 giây
st.markdown("""
<style>
    /* Bảng màu di sản & hiện đại */
    :root {
        --bg-color: #121212;
        --card-bg: #1e1e1e;
        --accent-gold: #d4af37;
        --alert-red: #d32f2f;
    }
    
    /* Header styling */
    .main-title {
        text-align: center;
        color: #d4af37;
        font-family: 'Georgia', serif;
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #cccccc;
        font-size: 1rem;
        margin-bottom: 25px;
    }

    /* Hiệu ứng Hover 1s kèm Spinner Loading cho Dropdown Cổ Phục */
    .hover-container {
        position: relative;
        display: inline-block;
        width: 100%;
        padding: 10px;
        background-color: #262626;
        border: 1px solid #d4af37;
        border-radius: 8px;
        cursor: pointer;
        text-align: center;
        color: #ffffff;
        font-weight: 500;
        margin-bottom: 15px;
    }

    .hover-preview-box {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        z-index: 999;
        width: 320px;
        background: #1e1e1e;
        border: 2px solid #d4af37;
        border-radius: 10px;
        padding: 12px;
        box-shadow: 0px 8px 16px rgba(0,0,0,0.7);
    }

    /* Kích hoạt Loading Spinner trong 1 giây trước khi hiện ảnh */
    .hover-container:hover .hover-preview-box {
        display: block;
        animation: fadeIn 0.3s ease-in-out 1s forwards;
        opacity: 0;
    }

    .hover-container:hover::after {
        content: "⏳ Đang tải xem trước ảnh Áo Chít...";
        position: absolute;
        top: 105%;
        left: 10%;
        background: #333;
        color: #d4af37;
        padding: 6px 12px;
        border-radius: 5px;
        font-size: 0.85rem;
        animation: fadeOut 0.1s linear 1s forwards;
    }

    @keyframes fadeIn {
        to { opacity: 1; }
    }
    @keyframes fadeOut {
        to { display: none; opacity: 0; }
    }

    /* Glitch Alert Pop-up Style */
    .red-alert-box {
        background-color: #3e1111;
        border: 2px solid #ff4d4d;
        border-radius: 10px;
        padding: 15px;
        color: #ffcccc;
        margin-bottom: 20px;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 77, 77, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(255, 77, 77, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 77, 77, 0); }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='main-title'>👘 AI STYLIST - TAKE MY VIBE</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Ứng dụng Phối Cổ Phục Việt Nam Chuẩn Văn Hóa dành cho Học Sinh, Sinh Viên</div>", unsafe_allow_html=True)

# Tạo bố cục 2 cột chính (Cột trái: Form nhập | Cột phải: Kết quả Lookbook)
col_left, col_right = st.columns([1, 1.2], gap="large")

# ---------------------------------------------------------
# CỘT TRÁI: FORM NHẬP THÔNG TIN
# ---------------------------------------------------------
with col_left:
    st.subheader("📋 Tùy Chọn Tải Vibe Phối Đồ")
    
    # 1. Thông số cá nhân
    col_h, col_w = st.columns(2)
    with col_h:
        height = st.number_input("Chiều cao (cm)", min_value=140, max_value=200, value=165)
    with col_w:
        weight = st.number_input("Cân nặng (kg)", min_value=40, max_value=120, value=55)

    # 2. Chọn Cổ phục (Giới hạn Áo Chít theo yêu cầu)
    st.write("**Chọn Loại Cổ Phục:**")
    
    # Khối Hover có hiệu ứng Loading 1 giây để hiển thị ảnh cổ phục đã gửi
    st.markdown("""
    <div class="hover-container">
        📌 Rê chuột & giữ 1s vào đây để xem trước ảnh Áo Ngũ Thân Tay Chẽn (Áo Chít)
        <div class="hover-preview-box">
            <p style="color:#d4af37; margin-bottom:5px; font-size:0.9rem;">✨ Bộ sưu tập Áo Chít Truyền Thống:</p>
            <p style="font-size:0.8rem; color:#bbb;">• Áo gấm xám ghi, lụa tím, gấm vàng, áo đỏ son...<br>• Cổ đứng 3cm, ống tay chẽn bó sát.<br>• Chuẩn 5 hột nút biểu tượng Ngũ Thường.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    co_phuc = st.selectbox(
        "Loại áo cổ phục chọn:",
        ["Áo Ngũ Thân Tay Chẽn (Áo Chít)"],
        index=0
    )

    # 3. Chọn Vibe Phong cách
    vibe = st.selectbox(
        "Chọn Vibe Phong cách Hiện đại:",
        [
            "Thư sinh (Preppy Scholar)",
            "Vintage xưa hoài cổ (Retro Nostalgia)",
            "Chill chill mùa thu Hà Nội (Autumn City Boy)"
        ]
    )

    # 4. Chọn Item phối kèm (Để kiểm tra Luật Cấm Kỵ Glitch Fix)
    bottom_item = st.selectbox(
        "Chọn Trang phục / Phụ kiện phối kèm phía dưới:",
        [
            "Quần âu / Kaki ống suông (Chuẩn mực)",
            "Quần đũi / Linen ống rộng thoải mái (Vintage)",
            "Quần Jeans ống suông (City Boy Casual)",
            "Váy Mã diện (Hán phục - Lỗi Cấm Kỵ Red Alert!)",
            "Thiết kế hở nách / Không khâu liền (Lỗi Cấm Kỵ Red Alert!)"
        ]
    )

    # 5. Nút Bấm Tạo Lookbook
    btn_generate = st.button("✦ TẠO LOOKBOOK STYLIST ✦", use_container_width=True, type="primary")

# ---------------------------------------------------------
# CỘT PHẢI: KẾT QUẢ VỚI 3 TAB (MOCK DATA TỪ DỮ LIỆU ĐÃ GỬI)
# ---------------------------------------------------------
with col_right:
    st.subheader("🖼️ Màn Hình Hiển Thị Lookbook & Tư Vấn")
    
    # Xử lý Cảnh Báo Glitch Fix
    if "Váy Mã diện" in bottom_item:
        st.markdown("""
        <div class="red-alert-box">
            <h3>🚨 CẢNH BÁO ĐỎ (RED ALERT): ERR_MA_DIEN</h3>
            <p><b>Lỗi vi phạm:</b> Việc kết hợp Việt phục (Áo ngũ thân tay chẽn) với Váy Mã diện của Hán phục làm sai lệch hoàn toàn đặc trưng văn hóa!</p>
            <p>👉 <i>Vui lòng đổi sang Quần âu, Quần đũi hoặc Quần ống sớ truyền thống để tuân thủ quy chuẩn!</i></p>
        </div>
        """, unsafe_allow_html=True)
    elif "hở nách" in bottom_item:
        st.markdown("""
        <div class="red-alert-box">
            <h3>🚨 CẢNH BÁO ĐỎ (RED ALERT): ERR_HO_NACH</h3>
            <p><b>Lỗi vi phạm:</b> Hai bên nách áo trở xuống bắt buộc phải khâu liền cho kín, tuyệt đối không được hở hang lộ da thịt!</p>
            <p>👉 <i>Vui lòng điều chỉnh lại phom dáng áo chẽn để bảo tồn sự kín đáo mực thước!</i></p>
        </div>
        """, unsafe_allow_html=True)

    # Tạo 3 Tab ở cột phải
    tab1, tab2, tab3 = st.tabs(["📸 Ảnh Lookbook", "💡 Lời Khuyên Stylist", "📜 Triết Lý Văn Hóa"])

    # TAB 1: ÁNH LOOKBOOK (Hiển thị các mẫu ảnh Áo Chít trong tập dữ liệu gửi)
    with tab1:
        st.caption("Lookbook thị giác Áo Ngũ Thân Tay Chẽn phối chuẩn phong cách:")
        
        # Mô phỏng hiển thị hình ảnh mẫu dựa trên Vibe được chọn
        if vibe == "Thư sinh (Preppy Scholar)":
            st.info("🎨 **Bản phối Thư sinh (Preppy Scholar):** Áo chít gấm xám ghi / lụa tím kết hợp quần âu, kính gọng tròn, vòng ngọc trai.")
            col_img1, col_img2 = st.columns(2)
            with col_img1:
                st.caption("Áo chít xám ghi dệt hoa văn")
                # Hiển thị thông tin mô tả thực tế từ ảnh 4
                st.write("• Chất liệu: Lụa/Gấm dệt chìm hoa văn\n• Phụ kiện: Chuỗi anh lạc rủ ngực, quạt xếp")
            with col_img2:
                st.caption("Áo chít lụa the tím nhạt")
                # Thông tin mô tả thực tế từ ảnh 9
                st.write("• Chất liệu: Lụa the tím xuyên thấu nhã nhặn\n• Phụ kiện: Chuỗi ngọc trai 3 vòng, khăn đóng tím")

        elif vibe == "Vintage xưa hoài cổ (Retro Nostalgia)":
            st.info("🎨 **Bản phối Vintage hoài cổ:** Áo chít hồng phấn / gấm đỏ kết hợp guốc mộc, nón lá, túi mây thủ công.")
            col_img1, col_img2 = st.columns(2)
            with col_img1:
                st.caption("Áo chít hồng phấn hoài cổ")
                # Thông tin từ ảnh 5
                st.write("• Chất liệu: Vải đũi/Linen hồng đất\n• Phụ kiện: Chuỗi hạt đỏ, nón lá, guốc mộc cao")
            with col_img2:
                st.caption("Áo chít lụa hồng nhạt")
                # Thông tin từ ảnh 8
                st.write("• Chất liệu: Lụa tơ tằm mỏng nhẹ\n• Phụ kiện: Túi cói/mây bán nguyệt, giày hài đỏ")

        else: # Autumn City Boy
            st.info("🎨 **Bản phối Chill chill Mùa Thu:** Áo chít đỏ son / gấm vàng khoác ngoài nhẹ nhàng, quần ống suông.")
            col_img1, col_img2 = st.columns(2)
            with col_img1:
                st.caption("Áo chít gấm vàng thượng lưu")
                # Thông tin từ ảnh 10
                st.write("• Chất liệu: Gấm satin dệt hoa mây vàng\n• Phụ kiện: Quạt giấy, quần trắng ống suông")
            with col_img2:
                st.caption("Áo chít lụa đỏ thẫm/mận chín")
                # Thông tin từ ảnh 6 & 12
                st.write("• Chất liệu: Lụa tơ bóng màu mận chín\n• Phụ kiện: Chuỗi hạt anh lạc, quạt xếp")

    # TAB 2: LỜI KHUYÊN STYLIST TỪ TÀI LIỆU CỔ PHỤC
    with tab2:
        st.markdown("### 📝 Tư Vấn Lựa Chọn Chất Liệu & Màu Sắc Mùa:")
        st.markdown("""
        - **Cấu trúc ống tay:** Ống tay áo chẽn bó sát và dài (nên mới gọi là *áo chít*), cửa ống tay rộng tối đa 30cm để gọn gàng khi di chuyển.
        - **Chất liệu khuyến nghị theo mùa:**
          - 🌸 **Mùa Xuân:** Mặc áo kép (2 lớp), lớp ngoài gấm satin xanh thiên thanh, lót lụa vàng mơ.
          - ☀️ **Mùa Hạ:** Ưu tiên áo đơn 1 lớp bằng **lụa the** hoặc **lụa vân** màu đen/tím/hồng nhẹ để thoáng mát.
          - 🍂 **Mùa Thu:** Mặc áo kép ngoài gấm satin mờ, lót lụa xanh ngọc.
          - ❄️ **Mùa Đông:** Mặc áo kép bằng **vải nỉ (Dạ mông tự)** ấm áp trơn màu đen, lót lụa xanh nhạt.
        - **Phối Phụ Kiện:** Có thể kết hợp thêm **chuỗi anh lạc** (đá quý, ngọc trai, trầm hương) rủ trước ngực để tôn lên nét thanh cao, tôn nghiêm. *Tuyệt đối không dùng chất liệu nhựa công nghiệp!*
        """)

    # TAB 3: TRIẾT LÝ VĂN HÓA LỊCH SỬ
    with tab3:
        st.markdown("### 🏛️ Triết Lý Cấu Trúc Áo Ngũ Thân Tay Chẽn:")
        st.markdown("""
        1. **Ý nghĩa 5 thân áo:** Thân áo được định hình từ 5 thân vải, tượng trưng cho **"Tứ thân phụ mẫu"** (cha mẹ đẻ, cha mẹ vợ/chồng) và **"Một tà con"** nằm ẩn bên trong thể hiện sự che chở, khiêm nhường.
        2. **Chuẩn 5 hột nút (Khuy cài bên phải):**
           - Đại diện cho **Ngũ Thường**: *Nhân - Lễ - Nghĩa - Trí - Tín*.
           - Nút áo thường làm từ ngọc thạch, ngọc mã não màu hổ phách hoặc đồng mạ vàng.
        3. **Quy tắc Kín đáo:**
           - Từ hai bên nách áo trở xuống **bắt buộc phải khâu liền cho kín**, không hở hang lộ da thịt.
           - Cổ áo đứng may cao 3cm ôm sát cổ giữ nét uy nghi, lịch sự.
        4. **Luật Tiếm Quyền:**
           - Dân gian tuyệt đối không được dùng màu **vàng Hoàng đế** hoặc thêu **họa tiết Rồng 5 móng (ngũ trảo)**.
        """)

# Footer
st.markdown("---")
st.caption("© 2026 Take My Vibe Team - AI Arena Viet Nam 2026. Tất cả dữ liệu quy chuẩn tuân thủ tài liệu lịch sử Việt phục Triều Nguyễn.")
