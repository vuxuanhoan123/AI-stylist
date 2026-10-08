# app.py
import streamlit as st
import json
import os

# ==============================================================================
# TẠM COMMENT THƯ VIỆN & CLIENT GOOGLE GENAI
# ==============================================================================
# from google import genai
# from google.genai import types

# @st.cache_resource
# def get_genai_client():
#     api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
#     if not api_key:
#         st.error("⚠️ Chưa tìm thấy GEMINI_API_KEY trong Streamlit secrets hoặc biến môi trường!")
#         st.stop()
#     return genai.Client(api_key=api_key)
# client = get_genai_client()

st.set_page_config(
    page_title="AI Stylist - Cổ Phục Việt Nam", 
    page_icon="👘", 
    layout="wide"
)

# ==============================================================================
# 1. DATA SCHEMA & CẤU TRÚC DỮ LIỆU CHUẨN
# ==============================================================================
DATA_SCHEMA = {
    "chang_1_ui_inputs": {
        "thong_tin_nguoi_dung": [
            {"id": "nhap_ten", "type": "text_input", "label": "Tên người dùng"},
            {"id": "nhap_bmi", "type": "number_input", "label": "Chỉ số BMI (Tự động tính từ Chiều cao & Cân nặng)"},
            {"id": "upload_anh_chan_dung", "type": "file_uploader", "label": "Tải ảnh chân dung"}
        ],
        "danh_muc_thoi_trang": [
            {
                "id": "trang_phuc_chinh",
                "label": "Trang phục chính",
                "options": [
                    {
                        "ten_nut_ui": "Áo Ngũ Thân Tay Chẽn",
                        "kien_thuc_lich_su": {
                            "ten_trang_phuc": "Áo Ngũ Thân Tay Chẽn",
                            "nguon_goc_lich_su": "Ra đời từ cuộc cải cách trang phục của Võ Vương Nguyễn Phúc Khoát tại Đàng Trong năm 1744 nhằm tạo ra bản sắc văn hóa độc lập. Đây là trang phục phổ biến nhất thời Nguyễn, đóng vai trò là tiền thân của áo dài hiện đại, gói gọn những triết lý nhân sinh và đạo đức Nho giáo của người Việt.",
                            "y_nghia_chi_tiet": {
                                "y_nghia_phom_dang_va_vat": "Được ghép từ 5 thân vải: 2 thân trước, 2 thân sau và 1 thân con ẩn dưới vạt phải. Bốn thân ngoài tượng trưng cho tứ thân phụ mẫu (cha mẹ ruột và cha mẹ vợ/chồng), thân con bên trong tượng trưng cho bản thân người mặc luôn được gia đình che chở, ôm ấp.",
                                "y_nghia_5_nut_ngu_thuong": "Sử dụng 5 hạt cúc (thường làm bằng ngà, đồng, mây, hoặc thủy tinh) đính dọc từ cổ xuống eo phải. Năm hạt cúc này đại diện cho Ngũ Thường: Nhân, Nghĩa, Lễ, Trí, Tín, như một lời nhắc nhở người mặc luôn giữ gìn đạo đức tôn nghiêm.",
                                "y_nghia_hoa_van_mau_sac": "Người bình dân thường mặc vải thô, lụa trơn màu sẫm, nâu, đen do quy định cấm dùng màu sắc lộng lẫy. Giới tinh hoa và quý tộc dùng lụa, gấm, sa, the với các màu sắc đa dạng hơn, dệt vân chìm họa tiết tứ quý, chữ thọ.",
                                "y_nghia_phu_kien": "Thường mặc cùng quần lụa trắng hoặc đen ống rộng, đội khăn xếp (khăn đóng) đối với nam hoặc vấn tóc gọn gàng đối với nữ. Kèm theo có thể là quạt giấy, thẻ bài, guốc mộc, tôn lên vẻ thư sinh, đĩnh đạc."
                            }
                        }
                    },
                    {
                        "ten_nut_ui": "Áo Tấc",
                        "kien_thuc_lich_su": {
                            "ten_trang_phuc": "Áo Tấc (Áo Lễ / Áo Thụng)",
                            "nguon_goc_lich_su": "Xuất hiện đồng thời với áo ngũ thân tay chẽn dưới thời chúa Nguyễn Phúc Khoát. Áo Tấc là loại lễ phục trang nghiêm mang tính chuẩn mực, được sử dụng phổ biến bởi mọi tầng lớp từ vua quan đến thứ dân trong các dịp quan hôn tang tế, hội hè, đại lễ.",
                            "y_nghia_chi_tiet": {
                                "y_nghia_phom_dang_va_vat": "Áo có tà dài chớm gót, điểm đặc trưng nhất là phần tay áo thụng rộng, viền tay áo chùng xuống đúng bằng một tấc (theo thước mộc cổ). Khi chắp tay trước ngực hành lễ, phần ống tay rộng sẽ che kín đôi bàn tay, biểu thị sự khiêm cung, tôn kính.",
                                "y_nghia_5_nut_ngu_thuong": "Kế thừa triết lý của hệ trang phục ngũ thân, 5 nút áo của áo Tấc không chỉ đại diện cho Ngũ Thường mà còn tượng trưng cho Ngũ Luân (đạo Quân thần, Phụ tử, Phu phụ, Huynh đệ, Bằng hữu), thể hiện trật tự xã hội bền vững.",
                                "y_nghia_hoa_van_mau_sac": "Màu sắc được quy định nghiêm ngặt theo hoàn cảnh: màu đỏ/hồng cho hỷ sự, lễ cưới; màu đen/tối cho tang lễ hoặc người cao tuổi; xanh lam/lục cho lễ hội thi cử. Họa tiết trên vải thượng lưu thường là hoa sen, cúc, dơi ngậm chữ thọ dệt chìm.",
                                "y_nghia_phu_kien": "Nam giới mặc Áo Tấc bắt buộc phải đội khăn đóng chữ Nhân hoặc chữ Nhất, chân đi hài mũi vót. Nữ giới vấn khăn vành, đội nón quai thao, đeo kiềng chạm trổ và cài trâm bối. Áo Tấc tôn vinh trọn vẹn vẻ bệ vệ, trang trọng của nghi lễ Á Đông."
                            }
                        }
                    },
                    {
                        "ten_nut_ui": "Áo Nhật Bình",
                        "kien_thuc_lich_su": {
                            "ten_trang_phuc": "Áo Nhật Bình",
                            "nguon_goc_lich_su": "Là thường phục cao cấp của Hoàng hậu, Phi tần, Công chúa và là đại lễ phục của các bậc Mệnh phụ phu nhân triều Nguyễn. Lấy cảm hứng từ áo Phi Phong thời Minh nhưng được cải biên mạnh mẽ, Nhật Bình mang đậm nghệ thuật cung đình Huế và quy chế trang phục vương triều nghiêm ngặt.",
                            "y_nghia_chi_tiet": {
                                "y_nghia_phom_dang_va_vat": "Đặc trưng lớn nhất là thiết kế áo xẻ trần trước ngực, phần cổ áo to bản khi mặc ghép lại tạo thành một khối hình chữ nhật (nhật bình) cân xứng. Thân áo rộng, vạt dài qua gối, mang lại vẻ uy nghi, bề thế, đoan trang của các bậc mẫu nghi và nữ lưu quý tộc.",
                                "y_nghia_5_nut_ngu_thuong": "Khác với áo ngũ thân dùng cúc đính dọc, áo Nhật Bình dùng một dải vải hoặc dải ngọc thắt lại trước ngực để cố định vạt áo. Việc luôn phải giữ cho vạt áo phẳng phiu, ngay ngắn qua dải thắt thể hiện sự gìn giữ đức hạnh, khuôn phép Tứ Đức Tam Tòng của người phụ nữ hoàng tộc.",
                                "y_nghia_hoa_van_mau_sac": "Phân cấp nghiêm ngặt theo điển lệ: Hoàng hậu dùng màu vàng chính sắc với họa tiết Đoàn phượng (phượng múa vòng tròn); Công chúa dùng màu đỏ với họa tiết Loan dệt; Phi tần dùng màu tím, xanh lục. Phần cổ áo luôn được ghép và thêu họa tiết ngũ sắc tỉ mỉ, lộng lẫy.",
                                "y_nghia_phu_kien": "Luôn phối cùng quần ống rộng màu trắng lụa trơn, trước ngực đeo dải thùy lưu (dải lụa thắt hoa thị với tua rua rủ xuống). Đầu đội mấn vành to (khăn vành dây) quấn nhiều vòng màu lam, đính các loại trâm cài bằng vàng, ngọc, phỉ thúy, đi kèm hài thêu mũi vót cong."
                            }
                        }
                    }
                ]
            },
            {
                "id": "do_doi_dau",
                "label": "Đồ đội đầu",
                "options": [
                    {"ten_nut_ui": "Khăn Đóng Cổ Truyền"},
                    {"ten_nut_ui": "Nón Quai Thao"},
                    {"ten_nut_ui": "Khăn Vành Dây Cung Đình"}
                ]
            },
            {
                "id": "trang_suc",
                "label": "Trang sức",
                "options": [
                    {"ten_nut_ui": "Kiềng Cổ Chạm Khắc"},
                    {"ten_nut_ui": "Trâm Cài Tóc Gỗ / Ngọc"},
                    {"ten_nut_ui": "Quạt Lụa Vẽ Tay"}
                ]
            }
        ],
        "dinh_hinh_vibe": [
            "Công sở thanh lịch",
            "Trà bánh hoàng gia",
            "Cà phê cuối tuần",
            "Dạo phố hoài cổ",
            "Hoài cổ thanh lịch (Vintage Retro)",
            "Dự lễ hội truyền thống",
            "Trang trọng & Nghi lễ"
        ],
        "ghi_chu_them": {
            "id": "ghi_chu_them",
            "type": "text_area",
            "label": "Ghi chú thêm về chất liệu, màu sắc, góc chụp, bối cảnh..."
        }
    },
    "chang_2_ui_inputs": {
        "chon_option_anh": {
            "id": "chon_option_anh",
            "type": "radio",
            "options": ["Option A", "Option B"],
            "label": "Chọn Option ảnh"
        },
        "feedback_text": {
            "id": "feedback_text",
            "type": "text_area",
            "label": "Phản hồi / Góp ý"
        }
    },
    "system_base_promt": {
        "tags": "8k resolution, photorealistic, ultra detailed, cinematic lighting, professional photography, masterpiece, sharp focus, highly textured fabric, unreal engine 5 render"
    }
}

# ==============================================================================
# 2. KHỞI TẠO STATE QUẢN LÝ 3 CHẶNG
# ==============================================================================
if "current_step" not in st.session_state:
    st.session_state.current_step = 1

if "payload_chang_1" not in st.session_state:
    st.session_state.payload_chang_1 = {}

if "payload_chang_2_prompts" not in st.session_state:
    st.session_state.payload_chang_2_prompts = {}

if "final_json_result" not in st.session_state:
    st.session_state.final_json_result = None

# ==============================================================================
# HEADER BÁO TIẾN TRÌNH
# ==============================================================================
st.title("👘 AI STYLIST - TƯ VẤN & PHỐI ĐỒ CỔ PHỤC VIỆT NAM")

col_step1, col_step2, col_step3 = st.columns(3)
with col_step1:
    if st.session_state.current_step == 1:
        st.info("📌 **CHẶNG 1: Khai báo Thông tin**")
    else:
        st.success("✅ **CHẶNG 1: Hoàn thành**")

with col_step2:
    if st.session_state.current_step == 2:
        st.info("📌 **CHẶNG 2: Gemini Tạo Prompt & Chọn Ảnh**")
    elif st.session_state.current_step > 2:
        st.success("✅ **CHẶNG 2: Hoàn thành**")
    else:
        st.text("⏳ **CHẶNG 2: Chưa mở**")

with col_step3:
    if st.session_state.current_step == 3:
        st.info("📌 **CHẶNG 3: Kết quả Chi tiết AI**")
    else:
        st.text("⏳ **CHẶNG 3: Chưa mở**")

st.divider()

# ==============================================================================
# CHẶNG 1: FRONTEND HIỂN THỊ FORM NHẬP DỮ LIỆU
# ==============================================================================
if st.session_state.current_step == 1:
    st.subheader("📋 CHẶNG 1: Khai Báo Thông Tin Người Dùng & Yêu Cầu Phối Đồ")
    
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown("### 1. Thông tin cá nhân")
        nhap_ten = st.text_input("Tên người dùng (*)", placeholder="Ví dụ: Nguyễn Văn A", value="Nguyễn Văn A")
        
        c_cao, c_nang = st.columns(2)
        with c_cao:
            h_cm = st.number_input("Chiều cao (cm):", min_value=100.0, max_value=220.0, value=165.0, step=0.5)
        with c_nang:
            w_kg = st.number_input("Cân nặng (kg):", min_value=30.0, max_value=150.0, value=58.0, step=0.5)
            
        nhap_bmi = round(w_kg / ((h_cm / 100) ** 2), 2)
        st.caption(f"💡 Chỉ số BMI ngầm được tính: **{nhap_bmi}**")
        
        upload_anh_chan_dung = st.file_uploader(
            "Tải ảnh chân dung (Định dạng JPG, PNG):", 
            type=["jpg", "jpeg", "png"]
        )

    with col_right:
        st.markdown("### 2. Danh mục thời trang & Phong cách")
        
        danh_muc_selected = st.selectbox(
            "Chọn Danh mục Thời trang:", 
            options=["trang_phuc_chinh", "do_doi_dau", "trang_suc"],
            format_func=lambda x: "Trang phục chính" if x == "trang_phuc_chinh" else ("Đồ đội đầu" if x == "do_doi_dau" else "Trang sức")
        )
        
        selected_item_data = None
        
        if danh_muc_selected == "trang_phuc_chinh":
            options_list = DATA_SCHEMA["chang_1_ui_inputs"]["danh_muc_thoi_trang"][0]["options"]
            item_names = [opt["ten_nut_ui"] for opt in options_list]
            selected_name = st.selectbox("Chọn Loại Trang phục Chính:", options=item_names)
            selected_item_data = next(opt for opt in options_list if opt["ten_nut_ui"] == selected_name)
            
            # ------------------------------------------------------------------
            # NÚT Ý NGHĨA CHI TIẾT (POPOVER) HIỂN THỊ KHI ĐANG CHỌN TRANG PHỤC CHÍNH
            # ------------------------------------------------------------------
            if "kien_thuc_lich_su" in selected_item_data:
                kt = selected_item_data["kien_thuc_lich_su"]
                with st.popover(f"📖 Ý nghĩa chi tiết của {selected_name}"):
                    st.markdown(f"### 📜 {kt['ten_trang_phuc']}")
                    st.caption(f"**Nguồn gốc:** {kt['nguon_goc_lich_su']}")
                    st.divider()
                    st.markdown("**Ý
