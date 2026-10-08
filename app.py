# app.py
import streamlit as st
import os
import json
from ai_engine import call_gemini_brain, generate_imagen_photo

# ==============================================================================
# CẤU HÌNH TRANG STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="AI Stylist - Cổ Phục Việt Nam",
    page_icon="👘",
    layout="wide"
)

# ==============================================================================
# LẤY API KEY
# ==============================================================================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

# ==============================================================================
# DỮ LIỆU UI LẤY TỪ CODE 1
# ==============================================================================

TRANG_PHUC_CHINH = [
    "Áo Ngũ Thân Tay Chẽn",
    "Áo Tấc",
    "Áo Nhật Bình"
]

DO_DOI_DAU = [
    "Khăn Đóng Cổ Truyền",
    "Nón Quai Thao",
    "Khăn Vành Dây Cung Đình"
]

TRANG_SUC = [
    "Kiềng Cổ Chạm Khắc",
    "Trâm Cài Tóc Gỗ / Ngọc",
    "Quạt Lụa Vẽ Tay"
]

VIBE_OPTIONS = [
    "Công sở thanh lịch",
    "Trà bánh hoàng gia",
    "Cà phê cuối tuần",
    "Dạo phố hoài cổ",
    "Hoài cổ thanh lịch (Vintage Retro)",
    "Dự lễ hội truyền thống",
    "Trang trọng & Nghi lễ"
]

# ==============================================================================
# KHỞI TẠO STATE QUẢN LÝ LUỒNG 3 CHẶNG
# ==============================================================================
if "step" not in st.session_state:
    st.session_state.step = 1

if "prompt_a" not in st.session_state:
    st.session_state.prompt_a = ""

if "prompt_b" not in st.session_state:
    st.session_state.prompt_b = ""

if "img_a" not in st.session_state:
    st.session_state.img_a = None

if "img_b" not in st.session_state:
    st.session_state.img_b = None

if "chosen_option" not in st.session_state:
    st.session_state.chosen_option = "A"

if "final_img" not in st.session_state:
    st.session_state.final_img = None

if "final_result_data" not in st.session_state:
    st.session_state.final_result_data = None

# ==============================================================================
# HEADER
# ==============================================================================
st.title("👘 VIETNAMESE TRADITIONAL COSTUMES AI STYLIST")
st.caption(
    "Ứng dụng phối đồ Cổ phục Việt Nam chuẩn lịch sử & Quy chuẩn văn hóa thời Nguyễn"
)

progress_values = {1: 33, 2: 66, 3: 100}
st.progress(progress_values[st.session_state.step])
st.markdown(f"**Đang ở: Chặng {st.session_state.step} / 3**")
st.divider()

# ==============================================================================
# CHẶNG 1: NHẬP THÔNG TIN & KHỞI TẠO PROMPT
# ==============================================================================
if st.session_state.step == 1:
    st.header("📝 Chặng 1: Nhập thông tin & Yêu cầu phối đồ")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 1. Thông tin người dùng")

        # UI tên lấy từ Code 1
        ten_nguoi_dung = st.text_input(
            "Tên người dùng:",
            value="Nguyễn Văn A",
            placeholder="Ví dụ: Nguyễn Văn A"
        )

        # Giữ phần mô tả người mặc của Code 2
        mo_ta_nguoi = st.text_input(
            "Mô tả người mặc (BMI, giới tính, gương mặt):",
            value="Nam thanh niên Việt Nam, vóc dáng cân đối, đeo kính gọng tròn cổ điển"
        )

        ghi_chu = st.text_area(
            "Ghi chú thêm (Màu sắc, bối cảnh, phụ kiện):",
            value="Tông màu xanh lam nhã nhặn, phối quần âu sáng màu, bối cảnh quán cà phê phố cổ"
        )

    with col2:
        st.markdown("### 2. Trang phục & Phong cách")

        # ----------------------------------------------------------------------
        # TRANG PHỤC CHÍNH - lấy từ Code 1
        # ----------------------------------------------------------------------
        trang_phuc_chinh = st.selectbox(
            "1. Chọn trang phục chính:",
            TRANG_PHUC_CHINH
        )

        # ----------------------------------------------------------------------
        # ĐỒ ĐỘI ĐẦU - lấy từ Code 1
        # ----------------------------------------------------------------------
        do_doi_dau = st.selectbox(
            "2. Chọn đồ đội đầu:",
            DO_DOI_DAU
        )

        # ----------------------------------------------------------------------
        # TRANG SỨC - lấy từ Code 1
        # ----------------------------------------------------------------------
        trang_suc = st.selectbox(
            "3. Chọn trang sức / phụ kiện:",
            TRANG_SUC
        )

        # ----------------------------------------------------------------------
        # VIBE - giữ các lựa chọn từ Code 1
        # ----------------------------------------------------------------------
        vibe = st.selectbox(
            "4. Chọn phong cách (Vibe):",
            VIBE_OPTIONS
        )

    st.divider()

    # Hiển thị lại lựa chọn trước khi gửi
    st.markdown("### 📋 Tóm tắt lựa chọn")
    sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)

    with sum_col1:
        st.info(f"**Tên**\n\n{ten_nguoi_dung}")

    with sum_col2:
        st.info(f"**Trang phục**\n\n{trang_phuc_chinh}")

    with sum_col3:
        st.info(f"**Đội đầu**\n\n{do_doi_dau}")

    with sum_col4:
        st.info(f"**Trang sức**\n\n{trang_suc}")

    if st.button(
        "🚀 Khởi tạo Phối đồ (Tạo 2 Option A & B)",
        type="primary"
    ):
        if not GEMINI_API_KEY:
            st.error("Chưa cấu hình GEMINI_API_KEY trong secrets/môi trường!")
        elif not ten_nguoi_dung.strip():
            st.error("Vui lòng nhập tên người dùng!")
        else:
            with st.spinner(
                "🤖 AI đang kiểm tra quy chuẩn văn hóa & tạo 2 phong cách..."
            ):
                # ==============================================================
                # GIỮ NGUYÊN CÁCH GỌI GEMINI CỦA CODE 2
                # Chỉ bổ sung các trường UI mới vào input
                # ==============================================================

                input_giai_doan_1 = f"""
[GIAI_DOAN_1_KHOI_TAO]
- Tên người dùng: {ten_nguoi_dung}
- Trang phục chính: {trang_phuc_chinh}
- Đồ đội đầu: {do_doi_dau}
- Trang sức / Phụ kiện: {trang_suc}
- Phong cách (Vibe): {vibe}
- Người mặc: {mo_ta_nguoi}
- Yêu cầu & Ghi chú: {ghi_chu}
"""

                # GIỮ NGUYÊN HÀM CỦA CODE 2
                res = call_gemini_brain(
                    input_giai_doan_1,
                    GEMINI_API_KEY
                )

                # ==============================================================
                # KIỂM TRA CẢNH BÁO ĐỎ
                # ==============================================================
                if res.get("status") == "GLITCH_DETECTED":
                    st.error(
                        f"⛔ {res.get('thong_diep_pop_up', 'Vi phạm quy chuẩn văn hóa cổ phục!')}"
                    )

                elif res.get("status") == "SUCCESS":
                    prompt_str = res.get("prompt_image", "")

                    # Tách chuỗi OPTION_A và OPTION_B
                    if "|||" in prompt_str:
                        parts = prompt_str.split("|||")

                        st.session_state.prompt_a = (
                            parts[0]
                            .replace("OPTION_A:", "")
                            .strip()
                        )

                        st.session_state.prompt_b = (
                            parts[1]
                            .replace("OPTION_B:", "")
                            .strip()
                        )
                    else:
                        st.session_state.prompt_a = prompt_str
                        st.session_state.prompt_b = prompt_str

                    # ==========================================================
                    # GIỮ NGUYÊN HÀM GENERATE IMAGEN CỦA CODE 2
                    # ==========================================================
                    with st.spinner(
                        "🎨 Đang sinh ảnh Imagen 3 cho Option A và Option B..."
                    ):
                        st.session_state.img_a = generate_imagen_photo(
                            st.session_state.prompt_a,
                            GEMINI_API_KEY
                        )

                        st.session_state.img_b = generate_imagen_photo(
                            st.session_state.prompt_b,
                            GEMINI_API_KEY
                        )

                    st.session_state.step = 2
                    st.rerun()

                else:
                    st.error(f"Lỗi hệ thống: {res.get('message')}")

# ==============================================================================
# CHẶNG 2: DUYỆT 2 OPTION & THÊM Ý TƯỞNG
# ==============================================================================
elif st.session_state.step == 2:
    st.header("🎨 Chặng 2: Chọn phong cách ưa thích & Thêm ý tưởng")

    st.info(
        "Hãy xem 2 gợi ý phối đồ bên dưới, chọn Option bạn thích nhất "
        "và nhập thêm yêu cầu tinh chỉnh!"
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Option A: Phong cách Truyền thống tinh tế")

        if st.session_state.img_a:
            st.image(
                st.session_state.img_a,
                use_container_width=True
            )
        else:
            st.warning("Không tải được ảnh Option A")

        st.caption(
            f"**Prompt A:** {st.session_state.prompt_a[:120]}..."
        )

    with col_b:
        st.subheader("Option B: Phong cách Modern Mix-match")

        if st.session_state.img_b:
            st.image(
                st.session_state.img_b,
                use_container_width=True
            )
        else:
            st.warning("Không tải được ảnh Option B")

        st.caption(
            f"**Prompt B:** {st.session_state.prompt_b[:120]}..."
        )

    st.divider()

    # Form chọn Option + Feedback
    selected = st.radio(
        "👉 Chọn Option bạn muốn phát triển tiếp:",
        ["Option A", "Option B"]
    )

    feedback_user = st.text_area(
        "✨ Nhập thêm ý tưởng tinh chỉnh:",
        placeholder=(
            "Gợi ý: Cho nhân vật cầm thêm quạt giấy, "
            "đổi màu áo sang xanh rêu..."
        )
    )

    col_btn1, col_btn2 = st.columns([1, 4])

    with col_btn1:
        if st.button("⬅️ Làm lại từ Chặng 1"):
            st.session_state.step = 1
            st.rerun()

    with col_btn2:
        if st.button(
            "✨ Chốt Lựa Chọn & Tạo Bức Ảnh Hoàn Chỉnh (Chặng 3)",
            type="primary"
        ):
            chosen_prompt = (
                st.session_state.prompt_a
                if selected == "Option A"
                else st.session_state.prompt_b
            )

            with st.spinner(
                "🤖 AI đang hoàn thiện bản phối & tổng hợp tri thức di sản..."
            ):
                # ==============================================================
                # GIỮ NGUYÊN CÁCH GỌI GEMINI CỦA CODE 2
                # ==============================================================

                input_giai_doan_2 = f"""
[GIAI_DOAN_2_CHOT_HA]
- Option đã chọn: {selected}
- Base Prompt: {chosen_prompt}
- Lời nhắn feedback/tinh chỉnh từ người dùng: {feedback_user}
"""

                res = call_gemini_brain(
                    input_giai_doan_2,
                    GEMINI_API_KEY
                )

                if res.get("status") == "GLITCH_DETECTED":
                    st.error(
                        f"⛔ {res.get('thong_diep_pop_up', 'Vi phạm quy chuẩn cổ phục trong lời nhắn tinh chỉnh!')}"
                    )

                elif res.get("status") == "SUCCESS":
                    final_prompt = res.get("prompt_image")

                    st.session_state.final_result_data = res

                    # ==========================================================
                    # GIỮ NGUYÊN HÀM GENERATE IMAGEN CỦA CODE 2
                    # ==========================================================
                    with st.spinner(
                        "🖼️ Đang xuất bức ảnh chất lượng cao cuối cùng..."
                    ):
                        st.session_state.final_img = generate_imagen_photo(
                            final_prompt,
                            GEMINI_API_KEY
                        )

                    st.session_state.step = 3
                    st.rerun()

                else:
                    st.error(f"Lỗi: {res.get('message')}")

# ==============================================================================
# CHẶNG 3: HIỂN THỊ KẾT QUẢ CUỐI CÙNG
# ==============================================================================
elif st.session_state.step == 3:
    st.header("🏆 Chặng 3: Bức ảnh hoàn chỉnh & Tri thức Cổ phục")

    data = st.session_state.final_result_data or {}

    col_img, col_info = st.columns([1, 1])

    with col_img:
        st.subheader("🖼️ Bức Ảnh Phối Đồ Hoàn Chỉnh")

        if st.session_state.final_img:
            st.image(
                st.session_state.final_img,
                use_container_width=True,
                caption="Kết quả phối đồ AI Stylist"
            )

            st.download_button(
                label="📥 Tải ảnh về máy",
                data=st.session_state.final_img,
                file_name="vietnamese_costume_ai.jpg",
                mime="image/jpeg"
            )
        else:
            st.error("Không hiển thị được ảnh cuối cùng.")

    with col_info:
        # 1. Lời khuyên Stylist
        st.success(
            f"💡 **Lời khuyên từ AI Stylist:**\n\n"
            f"{data.get('loi_khuyen', 'Trang phục phối hài hòa, tôn vinh nét đẹp truyền thống.')}"
        )

        # 2. Chi tiết phối đồ
        chi_tiet = data.get("chi_tiet_phoi", {})

        if chi_tiet:
            st.subheader("🎨 Chi tiết trang phối")

            st.markdown(
                f"- **Áo chính:** "
                f"{chi_tiet.get('ao_chinh', 'Áo ngũ thân')}"
            )

            st.markdown(
                f"- **Tông màu chủ đạo:** "
                f"{chi_tiet.get('tone_mau', 'Truyền thống')}"
            )

            st.markdown(
                f"- **Item hiện đại / Phụ kiện:** "
                f"{chi_tiet.get('item_hien_dai', 'Không có')}"
            )

        # 3. Tri thức lịch sử
        lich_su = data.get("kien_thuc_lich_su", {})

        if lich_su:
            st.subheader("📚 Tri thức Di sản & Điển chế")

            with st.expander(
                "🔍 Tìm hiểu nguồn gốc & Ý nghĩa văn hóa",
                expanded=True
            ):
                st.markdown(
                    f"**Tên chính thức:** "
                    f"{lich_su.get('ten_trang_phuc', 'Cổ phục Việt Nam')}"
                )

                st.markdown(
                    f"**Nguồn gốc lịch sử:** "
                    f"{lich_su.get('nguon_goc', 'Thời Nguyễn')}"
                )

                st.markdown(
                    f"**Ý nghĩa chi tiết:**\n"
                    f"{lich_su.get('y_nghia', 'Mang ý nghĩa triết lý sâu sắc về Ngũ thường và đạo hiếu.')}"
                )

    st.divider()

    if st.button(
        "🔄 Tạo bộ phối mới từ đầu",
        type="primary"
    ):
        st.session_state.step = 1
        st.session_state.prompt_a = ""
        st.session_state.prompt_b = ""
        st.session_state.img_a = None
        st.session_state.img_b = None
        st.session_state.final_img = None
        st.session_state.final_result_data = None
        st.rerun()
