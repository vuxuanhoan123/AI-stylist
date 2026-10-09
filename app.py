# app.py
import base64
import io
import os
import requests

import urllib.parse
import requests
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

from ai_engine import goi_ai_stylist


# ==============================================================================
# CẤU HÌNH TRANG
# ==============================================================================
st.set_page_config(
    page_title="AI Stylist - Cổ Phục Việt Nam",
    page_icon="👘",
    layout="wide",
)


# ==============================================================================
# API KEY
# ==============================================================================
def get_api_key():
    """Ưu tiên Streamlit Secrets, sau đó mới dùng biến môi trường."""
    try:
        key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        key = None

    return key or os.environ.get("GEMINI_API_KEY")


GEMINI_API_KEY = get_api_key()


# ==============================================================================
# TẠO ẢNH BẰNG IMAGEN 3 TỪ GOOGLE AI STUDIO REST API
# ==============================================================================

def generate_image(prompt_text, api_key=None):
    """
    Sinh ảnh miễn phí qua Pollinations AI với cơ chế tự chuyển model chống lỗi HTTP 402 (Payment Required).
    """
    encoded_prompt = urllib.parse.quote(prompt_text)
    
    # Danh sách các mô hình miễn phí 100% của Pollinations AI
    free_models = ["turbo", "flux-realism", "default"]
    
    last_error = ""

    for model_name in free_models:
        if model_name == "default":
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&nologo=true"
        else:
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&nologo=true&model={model_name}"

        try:
            response = requests.get(url, timeout=35)
            # Nếu trả về ảnh thành công 200 OK
            if response.status_code == 200:
                return response.content
            else:
                last_error = f"Model '{model_name}' báo mã HTTP {response.status_code}"
        except Exception as e:
            last_error = f"Lỗi kết nối '{model_name}': {str(e)}"

    raise RuntimeError(f"Không thể tạo ảnh từ Pollinations AI: {last_error}")
# ==============================================================================
# DỮ LIỆU UI
# ==============================================================================

TRANG_PHUC_CHINH = [
    "Áo Ngũ Thân Tay Chẽn",
    "Áo Tấc",
    "Áo Nhật Bình",
]

DO_DOI_DAU = [
    "Khăn Đóng Cổ Truyền",
    "Nón Quai Thao",
    "Khăn Vành Dây Cung Đình",
]

TRANG_SUC = [
    "Kiềng Cổ Chạm Khắc",
    "Trâm Cài Tóc Gỗ / Ngọc",
    "Quạt Lụa Vẽ Tay",
]

VIBE_OPTIONS = [
    "Công sở thanh lịch",
    "Trà bánh hoàng gia",
    "Cà phê cuối tuần",
    "Dạo phố hoài cổ",
    "Hoài cổ thanh lịch (Vintage Retro)",
    "Dự lễ hội truyền thống",
    "Trang trọng & Nghi lễ",
]


# ==============================================================================
# SESSION STATE
# ==============================================================================

DEFAULT_STATE = {
    "step": 1,
    "portrait_bytes": None,
    "portrait_mime": "image/jpeg",
    "prompt_a": "",
    "prompt_b": "",
    "img_a": None,
    "img_b": None,
    "chosen_option": "Option A",
    "final_img": None,
    "final_result_data": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==============================================================================
# HÀM TIỆN ÍCH
# ==============================================================================

def reset_all():
    for key, value in DEFAULT_STATE.items():
        st.session_state[key] = value


def parse_two_prompts(prompt_string):
    """
    Tách linh hoạt: OPTION_A: ... ||| OPTION_B: ...
    Chống bị treo app nếu AI thiếu kí tự |||.
    """
    if not prompt_string:
        return "", ""

    if "|||" in prompt_string:
        parts = prompt_string.split("|||", 1)
        prompt_a = parts[0].strip()
        prompt_b = parts[1].strip()
    else:
        prompt_a = prompt_string.strip()
        prompt_b = prompt_string.strip() + ", detailed historical view option B"

    if prompt_a.startswith("OPTION_A:"):
        prompt_a = prompt_a[len("OPTION_A:"):].strip()

    if prompt_b.startswith("OPTION_B:"):
        prompt_b = prompt_b[len("OPTION_B:"):].strip()

    return prompt_a, prompt_b


def show_error_from_ai(result):
    """Hiển thị chi tiết lỗi/cảnh báo và bổ sung cơ chế khởi động lại giao diện."""
    error_code = result.get("error_code")
    warning = result.get("canh_bao")
    loi_khuyen = result.get("loi_khuyen")

    if error_code:
        st.error(f"⛔ Lỗi quy chuẩn cổ phục: {error_code}")

    if warning:
        st.error(f"⚠️ {warning}")

    if loi_khuyen:
        st.info(f"💡 Lời khuyên: {loi_khuyen}")

    # 🔄 CƠ CHẾ KHỞI ĐỘNG LẠI LUỒNG TRÊN GIAO DIỆN STREAMLIT
    if st.button("🔄 Thử lại lượt này ngay", type="secondary"):
        st.rerun()


# ==============================================================================
# HEADER
# ==============================================================================

st.title("👘 VIETNAMESE TRADITIONAL COSTUMES AI STYLIST")
st.caption(
    "Ứng dụng phối đồ Cổ phục Việt Nam theo quy chuẩn văn hóa thời Nguyễn"
)

progress_values = {1: 0.33, 2: 0.66, 3: 1.0}
st.progress(progress_values[st.session_state.step])
st.markdown(f"**Đang ở: Chặng {st.session_state.step} / 3**")
st.divider()


# ==============================================================================
# CHẶNG 1: NHẬP THÔNG TIN & KHỞI TẠO
# ==============================================================================

if st.session_state.step == 1:
    st.header("📝 Chặng 1: Nhập thông tin & yêu cầu phối đồ")

    left, right = st.columns(2)

    with left:
        st.markdown("### 1. Thông tin người dùng")

        ten_nguoi_dung = st.text_input(
            "Tên người dùng:",
            value="Nguyễn Văn A",
            placeholder="Ví dụ: Nguyễn Văn A",
        )

        uploaded_file = st.file_uploader(
            "Ảnh chân dung:",
            type=["jpg", "jpeg", "png", "webp"],
            help="Ảnh sẽ được gửi cho Gemini cùng thông tin người dùng.",
        )

        if uploaded_file is not None:
            try:
                preview = Image.open(uploaded_file)
                st.image(
                    preview,
                    caption="Ảnh chân dung đã chọn",
                    width=250,
                )
            except Exception:
                st.error("File ảnh không hợp lệ.")

        h_cm_col, w_kg_col = st.columns(2)

        with h_cm_col:
            h_cm = st.number_input(
                "Chiều cao (cm):",
                min_value=100.0,
                max_value=220.0,
                value=165.0,
                step=0.5,
            )

        with w_kg_col:
            w_kg = st.number_input(
                "Cân nặng (kg):",
                min_value=30.0,
                max_value=150.0,
                value=58.0,
                step=0.5,
            )

        bmi = round(w_kg / ((h_cm / 100) ** 2), 2)

        st.caption(f"💡 BMI được tính tự động: **{bmi}**")

        mo_ta_nguoi = st.text_input(
            "Mô tả người mặc (giới tính, gương mặt, đặc điểm khác):",
            value="Nam thanh niên Việt Nam, đeo kính gọng tròn cổ điển",
        )

        ghi_chu = st.text_area(
            "Ghi chú thêm:",
            value=(
                "Tông màu xanh lam nhã nhặn, bối cảnh quán cà phê phố cổ"
            ),
        )

    with right:
        st.markdown("### 2. Trang phục & phong cách")

        trang_phuc_chinh = st.selectbox(
            "1. Trang phục chính:",
            TRANG_PHUC_CHINH,
        )

        do_doi_dau = st.selectbox(
            "2. Đồ đội đầu:",
            DO_DOI_DAU,
        )

        trang_suc = st.selectbox(
            "3. Trang sức / phụ kiện:",
            TRANG_SUC,
        )

        vibe = st.selectbox(
            "4. Phong cách (Vibe):",
            VIBE_OPTIONS,
        )

    st.divider()

    st.markdown("### 📋 Tóm tắt lựa chọn")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.info(f"**Tên**\n\n{ten_nguoi_dung}")

    with c2:
        st.info(f"**Trang phục**\n\n{trang_phuc_chinh}")

    with c3:
        st.info(f"**Đội đầu**\n\n{do_doi_dau}")

    with c4:
        st.info(f"**Trang sức**\n\n{trang_suc}")

    if st.button(
        "🚀 Khởi tạo phối đồ (Tạo 2 Option A & B)",
        type="primary",
        use_container_width=True,
    ):
        if not GEMINI_API_KEY:
            st.error(
                "Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets "
                "hoặc biến môi trường."
            )
            st.stop()

        if not ten_nguoi_dung.strip():
            st.error("Vui lòng nhập tên người dùng.")
            st.stop()

        if uploaded_file is None:
            st.error("Vui lòng tải ảnh chân dung.")
            st.stop()

        portrait_bytes = uploaded_file.getvalue()
        portrait_mime = uploaded_file.type or "image/jpeg"

        input_giai_doan_1 = f"""
[GIAI_DOAN_1_KHOI_TAO]

Thông tin người dùng:
- Tên người dùng: {ten_nguoi_dung}
- Chiều cao: {h_cm} cm
- Cân nặng: {w_kg} kg
- BMI: {bmi}

Lựa chọn trang phục:
- Trang phục chính: {trang_phuc_chinh}
- Đồ đội đầu: {do_doi_dau}
- Trang sức / Phụ kiện: {trang_suc}
- Phong cách (Vibe): {vibe}

Mô tả người mặc:
{mo_ta_nguoi}

Yêu cầu và ghi chú:
{ghi_chu}

Ảnh chân dung của người dùng đã được gửi kèm theo nội dung này.
Hãy phân tích ảnh chân dung và xử lý đúng GIAI_DOAN_1_KHOI_TAO
theo system instruction.
"""

        with st.spinner(
            "🤖 Gemini đang phân tích ảnh, BMI và kiểm tra quy chuẩn..."
        ):
            result = goi_ai_stylist(
                user_prompt=input_giai_doan_1,
                image_input=portrait_bytes,
                api_key=GEMINI_API_KEY,
            )

        if result.get("status") == "GLITCH_DETECTED":
            show_error_from_ai(result)

        elif result.get("status") == "SUCCESS":
            prompt_a, prompt_b = parse_two_prompts(
                result.get("prompt_image", "")
            )

            if not prompt_a:
                st.error("Gemini không trả về Prompt Option A.")
                st.stop()

            st.session_state.prompt_a = prompt_a
            st.session_state.prompt_b = prompt_b
            st.session_state.portrait_bytes = portrait_bytes
            st.session_state.portrait_mime = portrait_mime

            try:
                with st.spinner("🎨 Đang sinh ảnh Option A bằng Imagen 3..."):
                    st.session_state.img_a = generate_image(prompt_a, api_key=GEMINI_API_KEY)

                with st.spinner("🎨 Đang sinh ảnh Option B bằng Imagen 3..."):
                    st.session_state.img_b = generate_image(prompt_b, api_key=GEMINI_API_KEY)

                st.session_state.step = 2
                st.rerun()

            except Exception as e:
                st.error(f"Lỗi khi gọi Imagen sinh ảnh: {str(e)}")

        else:
            st.error(
                "Gemini trả về kết quả không hợp lệ: "
                + str(result)
            )


# ==============================================================================
# CHẶNG 2: XEM 2 OPTION & TINH CHỈNH
# ==============================================================================

elif st.session_state.step == 2:
    st.header("🎨 Chặng 2: Chọn phong cách & tinh chỉnh")

    st.info(
        "Chọn một trong hai phương án. Sau đó nhập yêu cầu tinh chỉnh "
        "nếu bạn muốn thay đổi."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Option A")

        if st.session_state.img_a:
            st.image(
                st.session_state.img_a,
                caption="Option A",
                use_container_width=True,
            )
        else:
            st.warning("Không có ảnh Option A.")

        with st.expander("Xem prompt A"):
            st.write(st.session_state.prompt_a)

    with col_b:
        st.subheader("Option B")

        if st.session_state.img_b:
            st.image(
                st.session_state.img_b,
                caption="Option B",
                use_container_width=True,
            )
        else:
            st.warning("Không có ảnh Option B.")

        with st.expander("Xem prompt B"):
            st.write(st.session_state.prompt_b)

    st.divider()

    selected = st.radio(
        "👉 Chọn Option muốn phát triển tiếp:",
        ["Option A", "Option B"],
        horizontal=True,
    )

    feedback_user = st.text_area(
        "✨ Yêu cầu tinh chỉnh:",
        placeholder=(
            "Ví dụ: đổi tông màu sang xanh rêu, "
            "giữ nguyên khuôn mặt, thay bối cảnh thành phố cổ..."
        ),
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button("⬅️ Quay lại Chặng 1"):
            st.session_state.step = 1
            st.rerun()

    with c2:
        if st.button(
            "✨ Chốt lựa chọn & tạo ảnh cuối",
            type="primary",
            use_container_width=True,
        ):
            chosen_prompt = (
                st.session_state.prompt_a
                if selected == "Option A"
                else st.session_state.prompt_b
            )

            input_giai_doan_2 = f"""
[GIAI_DOAN_2_CHOT_HA]

- Option đã chọn: {selected}

- Base Prompt:
{chosen_prompt}

- Lời nhắn feedback / tinh chỉnh từ người dùng:
{feedback_user}

Ảnh chân dung ban đầu của người dùng cũng được gửi kèm.
Hãy xử lý đúng GIAI_DOAN_2_CHOT_HA theo system instruction.
"""

            with st.spinner(
                "🤖 Gemini đang hoàn thiện prompt cuối và thông tin phối đồ..."
            ):
                result = goi_ai_stylist(
                    user_prompt=input_giai_doan_2,
                    image_input=st.session_state.portrait_bytes,
                    api_key=GEMINI_API_KEY,
                )

            if result.get("status") == "GLITCH_DETECTED":
                show_error_from_ai(result)

            elif result.get("status") == "SUCCESS":
                final_prompt = result.get("prompt_image")

                if not final_prompt:
                    st.error("Gemini không trả về prompt ảnh cuối.")
                    st.stop()

                st.session_state.final_result_data = result

                try:
                    with st.spinner("🖼️ Đang xuất bức ảnh hoàn chỉnh cuối cùng..."):
                        st.session_state.final_img = generate_image(final_prompt, api_key=GEMINI_API_KEY)

                    st.session_state.chosen_option = selected
                    st.session_state.step = 3
                    st.rerun()

                except Exception as e:
                    st.error(f"Lỗi Imagen: {str(e)}")

            else:
                st.error(
                    "Gemini trả về kết quả không hợp lệ: "
                    + str(result)
                )


# ==============================================================================
# CHẶNG 3: HIỂN THỊ KẾT QUẢ & TRI THỨC DI SẢN CHI TIẾT
# ==============================================================================

elif st.session_state.step == 3:
    st.header("🏆 Chặng 3: Kết quả hoàn chỉnh")

    data = st.session_state.final_result_data or {}

    col_img, col_info = st.columns([1, 1])

    with col_img:
        st.subheader("🖼️ Bức ảnh hoàn chỉnh")

        if st.session_state.final_img:
            st.image(
                st.session_state.final_img,
                caption="Kết quả phối đồ AI Stylist",
                use_container_width=True,
            )

            st.download_button(
                "📥 Tải ảnh về máy",
                data=st.session_state.final_img,
                file_name="vietnamese_costume_ai.png",
                mime="image/png",
                use_container_width=True,
            )
        else:
            st.error("Không có ảnh kết quả.")

    with col_info:
        st.success(
            "💡 **Lời khuyên từ AI Stylist**\n\n"
            + str(
                data.get(
                    "loi_khuyen",
                    "Không có dữ liệu.",
                )
            )
        )

        chi_tiet = data.get("chi_tiet_phoi") or {}

        st.subheader("🎨 Chi tiết phối")

        st.markdown(
            f"**Áo chính:** "
            f"{chi_tiet.get('ao_chinh', 'Không có dữ liệu')}"
        )

        st.markdown(
            f"**Tông màu:** "
            f"{chi_tiet.get('tone_mau', 'Không có dữ liệu')}"
        )

        st.markdown(
            f"**Item hiện đại:** "
            f"{chi_tiet.get('item_hien_dai', 'Không có dữ liệu')}"
        )

        lich_su = data.get("kien_thuc_lich_su") or {}

        st.subheader("📚 Kiến thức lịch sử")

        st.markdown(
            f"**Tên trang phục:** "
            f"{lich_su.get('ten_trang_phuc', 'Không có dữ liệu')}"
        )

        st.markdown(
            f"**Nguồn gốc lịch sử:** "
            f"{lich_su.get('nguon_goc_lich_su', 'Không có dữ liệu')}"
        )

        y_nghia = lich_su.get("y_nghia_chi_tiet") or {}

        with st.expander("Xem ý nghĩa chi tiết", expanded=True):
            st.markdown(
                f"**Phom dáng và vật liệu:**\n\n"
                f"{y_nghia.get('y_nghia_phom_dang_va_vat', 'Không có dữ liệu')}"
            )

            st.markdown(
                f"**5 nút Ngũ thường:**\n\n"
                f"{y_nghia.get('y_nghia_5_nut_ngu_thuong', 'Không có dữ liệu')}"
            )

            st.markdown(
                f"**Hoa văn và màu sắc:**\n\n"
                f"{y_nghia.get('y_nghia_hoa_van_mau_sac', 'Không có dữ liệu')}"
            )

            st.markdown(
                f"**Phụ kiện:**\n\n"
                f"{y_nghia.get('y_nghia_phu_kien', 'Không có dữ liệu')}"
            )

    st.divider()

    with st.expander("🔍 Xem prompt ảnh cuối"):
        st.write(data.get("prompt_image", ""))

    if st.button(
        "🔄 Tạo bộ phối mới từ đầu",
        type="primary",
        use_container_width=True,
    ):
        reset_all()
        st.rerun()
