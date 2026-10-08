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
                    st.markdown("**Ý nghĩa 4 yếu tố đặc trưng:**")
                    
                    st.markdown(f"1. **Phom dáng & Vạt áo:**\n   {kt['y_nghia_chi_tiet']['y_nghia_phom_dang_va_vat']}")
                    st.markdown(f"2. **5 Nút Ngũ Thường:**\n   {kt['y_nghia_chi_tiet']['y_nghia_5_nut_ngu_thuong']}")
                    st.markdown(f"3. **Họa tiết & Màu sắc:**\n   {kt['y_nghia_chi_tiet']['y_nghia_hoa_van_mau_sac']}")
                    st.markdown(f"4. **Phụ kiện đi kèm:**\n   {kt['y_nghia_chi_tiet']['y_nghia_phu_kien']}")

        elif danh_muc_selected == "do_doi_dau":
            options_list = DATA_SCHEMA["chang_1_ui_inputs"]["danh_muc_thoi_trang"][1]["options"]
            item_names = [opt["ten_nut_ui"] for opt in options_list]
            selected_name = st.selectbox("Chọn Loại Đồ Đội Đầu:", options=item_names)
            selected_item_data = {"ten_nut_ui": selected_name}

        else:
            options_list = DATA_SCHEMA["chang_1_ui_inputs"]["danh_muc_thoi_trang"][2]["options"]
            item_names = [opt["ten_nut_ui"] for opt in options_list]
            selected_name = st.selectbox("Chọn Loại Trang Sức:", options=item_names)
            selected_item_data = {"ten_nut_ui": selected_name}

        dinh_hinh_vibe = st.selectbox(
            "Định hình phong cách (Vibe):", 
            options=DATA_SCHEMA["chang_1_ui_inputs"]["dinh_hinh_vibe"]
        )
        
        ghi_chu_them = st.text_area(
            DATA_SCHEMA["chang_1_ui_inputs"]["ghi_chu_them"]["label"],
            placeholder="Màu sắc ưu thích, chất liệu, phụ kiện khác đi kèm..."
        )

    st.markdown("---")
    if st.button("✦ TIẾP TỤC SANG CHẶNG 2 (GỬI DỮ LIỆU SANG GEMINI) ✦", type="primary", use_container_width=True):
        if not nhap_ten.strip():
            st.error("⚠️ Vui lòng nhập Tên người dùng trước khi tiếp tục!")
        else:
            st.session_state.payload_chang_1 = {
                "thong_tin_nguoi_dung": {
                    "nhap_ten": nhap_ten,
                    "nhap_bmi": nhap_bmi,
                    "upload_anh_chan_dung": upload_anh_chan_dung.name if upload_anh_chan_dung else None
                },
                "danh_muc_thoi_trang": {
                    "id": danh_muc_selected,
                    "chi_tiet": selected_item_data
                },
                "dinh_hinh_vibe": dinh_hinh_vibe,
                "ghi_chu_them": ghi_chu_them
            }
            
            # ==================================================================
            # ĐOẠN API TỰ ĐỘNG GỬI GOOGLE AI STUDIO (TẠM COMMENT OUT)
            # ==================================================================
            # system_prompt_chang_1 = "..."
            # response = client.models.generate_content(...)
            # res_json = json.loads(response.text)
            # ==================================================================

            # GIẢ LẬP KẾT QUẢ TRẢ VỀ TỪ GEMINI LẦN 1
            item_name_str = selected_item_data.get("ten_nut_ui", "Cổ Phục")
            st.session_state.payload_chang_2_prompts = {
                "status": "OK",
                "reason": None,
                "prompt_option_a": f"Traditional Vietnamese costume '{item_name_str}', authentic fabric texture, classic colors, 8k resolution, photorealistic, cinematic lighting, sharp focus",
                "prompt_option_b": f"Modernized Vietnamese outfit '{item_name_str}', stylish fashion mix, pastel colors, high quality, highly textured fabric, unreal engine 5 render"
            }
            
            st.session_state.current_step = 2
            st.rerun()

# ==============================================================================
# CHẶNG 2: GIẢ LẬP GEMINI TẠO 2 PROMPT -> HIỂN THỊ CỘT CHỌN & PHẢN HỒI
# ==============================================================================
elif st.session_state.current_step == 2:
    st.subheader("🎨 CHẶNG 2: Phân Tích Gemini & Chọn Option Hình Ảnh Phối Đồ")
    
    p1 = st.session_state.payload_chang_1
    prompts_data = st.session_state.payload_chang_2_prompts

    st.write(f"👤 **Người dùng:** {p1['thong_tin_nguoi_dung']['nhap_ten']} | **BMI:** {p1['thong_tin_nguoi_dung']['nhap_bmi']} | **Vibe:** {p1['dinh_hinh_vibe']}")

    if prompts_data.get("status") == "RED_ALERT":
        st.error(f"🔴 **RED_ALERT**: Yêu cầu vi phạm tiêu chuẩn thuần phong mỹ tục ({prompts_data.get('reason', 'Không hợp lệ')}). Vui lòng quay lại Chặng 1 để chỉnh sửa.")
        if st.button("⬅️ Quay lại Chặng 1"):
            st.session_state.current_step = 1
            st.rerun()
    else:
        st.success("✅ Dữ liệu hợp lệ! Gemini đã khởi tạo 2 câu Prompt Tiếng Anh (Mock Simulation):")

        col_opt1, col_opt2 = st.columns(2)
        
        with col_opt1:
            st.markdown("#### 📸 OPTION A (Truyền thống)")
            st.image("https://placehold.co/600x800/2b2b36/ffffff?text=Imagen+Option+A", caption="Mẫu A: Style Traditional", use_container_width=True)
            st.caption(f"**Gemini Prompt A:** `{prompts_data.get('prompt_option_a')}`")
            
        with col_opt2:
            st.markdown("#### 📸 OPTION B (Cách tân)")
            st.image("https://placehold.co/600x800/1e2638/ffffff?text=Imagen+Option+B", caption="Mẫu B: Style Modern Mix", use_container_width=True)
            st.caption(f"**Gemini Prompt B:** `{prompts_data.get('prompt_option_b')}`")

        st.markdown("---")
        st.markdown("### 📝 Chọn Option & Nhập Phản Hồi")
        
        col_select, col_feedback = st.columns([1, 2])
        
        with col_select:
            chon_option_anh = st.radio(
                DATA_SCHEMA["chang_2_ui_inputs"]["chon_option_anh"]["label"],
                options=DATA_SCHEMA["chang_2_ui_inputs"]["chon_option_anh"]["options"],
                index=0
            )
            
        with col_feedback:
            feedback_text = st.text_area(
                DATA_SCHEMA["chang_2_ui_inputs"]["feedback_text"]["label"],
                placeholder="Nhập cảm nhận của bạn về màu sắc, phom dáng hoặc yêu cầu chỉnh sửa cho lần phân tích cuối...",
                value="Tôi thích màu sắc tươi sáng hơn một chút, kết hợp phụ kiện hiện đại."
            )

        col_b1, col_b2 = st.columns([1, 4])
        with col_b1:
            if st.button("⬅️ Sửa Chặng 1"):
                st.session_state.current_step = 1
                st.rerun()
        with col_b2:
            if st.button("✦ GỬI PHẢN HỒI & PHÂN TÍCH LẦN 2 (SANG CHẶNG 3) ✦", type="primary", use_container_width=True):
                
                # ==============================================================
                # ĐOẠN API PHÂN TÍCH TỔNG HỢP TỰ ĐỘNG GỬI GEMINI (TẠM COMMENT OUT)
                # ==============================================================
                # system_prompt_chang_3 = "..."
                # response_final = client.models.generate_content(...)
                # st.session_state.final_json_result = json.loads(response_final.text)
                # ==============================================================

                # GIẢ LẬP KẾT QUẢ HOÀN CHỈNH CHO CHẶNG 3 DỰA TRÊN INPUT NGƯỜI DÙNG
                p1_item = p1["danh_muc_thoi_trang"]["chi_tiet"]
                selected_prompt = prompts_data.get('prompt_option_a') if chon_option_anh == "Option A" else prompts_data.get('prompt_option_b')
                
                if "kien_thuc_lich_su" in p1_item:
                    history_block = p1_item["kien_thuc_lich_su"]
                else:
                    history_block = {
                        "ten_trang_phuc": p1_item.get("ten_nut_ui", "Cổ Phục Việt Nam"),
                        "nguon_goc_lich_su": "Trang phục truyền thống Việt Nam mang đậm giá trị lịch sử qua các thời kỳ vương triều.",
                        "y_nghia_chi_tiet": {
                            "y_nghia_phom_dang_va_vat": "Phom dáng cân xứng thể hiện triết lý ngũ hành và đạo lý làm người.",
                            "y_nghia_5_nut_ngu_thuong": "Tượng trưng cho Ngũ Thường: Nhân, Nghĩa, Lễ, Trí, Tín.",
                            "y_nghia_hoa_van_mau_sac": "Họa tiết tinh xảo thể hiện nét đẹp văn hóa Đông Sơn và triều đại.",
                            "y_nghia_phu_kien": "Kết hợp cùng mấn, kiềng cổ tôn lên vẻ trang trọng."
                        }
                    }

                st.session_state.final_json_result = {
                    "trang_thai_ngam": {
                        "status": "SUCCESS",
                        "error_code": None,
                        "promt_image": selected_prompt
                    },
                    "hien_thi_giao_dien": {
                        "canh_bao": "Không nên giặt máy hoặc phơi trực tiếp dưới ánh nắng gắt đối với chất liệu lụa/gấm tơ tằm.",
                        "loi_khuyen": f"Với chỉ số BMI {p1['thong_tin_nguoi_dung']['nhap_bmi']} và phong cách '{p1['dinh_hinh_vibe']}', lựa chọn {chon_option_anh} giúp tôn vinh chiều cao và che khuyết điểm vùng eo rất hiệu quả.",
                        "chi_tiet_phoi": {
                            "ao_chinh": history_block["ten_trang_phuc"],
                            "tone_mau": "Đỏ đô chủ đạo kết hợp viền vàng hoàng gia (phản hồi: " + (feedback_text if feedback_text else "Không có") + ")",
                            "item_hien_dai": "Giày cao gót mũi nhọn tone nude / Đồng hồ kim loại mảnh"
                        },
                        "kien_thuc_lich_su": history_block
                    }
                }
                
                st.session_state.current_step = 3
                st.rerun()

# ==============================================================================
# CHẶNG 3: HIỂN THỊ KẾT QUẢ PHÂN TÍCH TỔNG HỢP GIAO DIỆN & JSON CHUẨN
# ==============================================================================
elif st.session_state.current_step == 3:
    st.subheader("🎉 CHẶNG 3: Kết Quả Phân Tích Chuyên Gia & Khối JSON Chuẩn")

    result = st.session_state.final_json_result
    ui_data = result["hien_thi_giao_dien"]
    kt_data = ui_data["kien_thuc_lich_su"]

    col_res1, col_res2 = st.columns([1.2, 1], gap="large")

    with col_res1:
        st.markdown("### 💡 Lời Khuyên Phối Đồ")
        st.info(ui_data["loi_khuyen"])
        
        st.markdown("### ⚠️ Cảnh Báo Bảo Quản")
        st.warning(ui_data["canh_bao"])

        st.markdown("### 👔 Chi Tiết Phối Đồ")
        st.write(f"- **Áo chính:** {ui_data['chi_tiet_phoi']['ao_chinh']}")
        st.write(f"- **Tone màu đề xuất:** {ui_data['chi_tiet_phoi']['tone_mau']}")
        st.write(f"- **Item hiện đại phối kèm:** {ui_data['chi_tiet_phoi']['item_hien_dai']}")

    with col_res2:
        st.markdown(f"### 📜 Kiến Thức Lịch Sử: {kt_data['ten_trang_phuc']}")
        st.write(f"**Nguồn gốc lịch sử:** {kt_data['nguon_goc_lich_su']}")
        
        st.markdown("**Ý nghĩa chi tiết:**")
        st.write(f"• **Phom dáng & Vạt áo:** {kt_data['y_nghia_chi_tiet']['y_nghia_phom_dang_va_vat']}")
        st.write(f"• **5 Nút Ngũ Thường:** {kt_data['y_nghia_chi_tiet']['y_nghia_5_nut_ngu_thuong']}")
        st.write(f"• **Họa tiết & Màu sắc:** {kt_data['y_nghia_chi_tiet']['y_nghia_hoa_van_mau_sac']}")
        st.write(f"• **Phụ kiện:** {kt_data['y_nghia_chi_tiet']['y_nghia_phu_kien']}")

    st.divider()

    st.markdown("### 📦 KHỐI DỮ LIỆU JSON CHUẨN ĐẦU RA")
    st.json(result)

    if st.button("🔄 Thực hiện phối đồ mới (Quay về Chặng 1)", type="primary"):
        st.session_state.current_step = 1
        st.session_state.payload_chang_1 = {}
        st.session_state.payload_chang_2_prompts = {}
        st.session_state.final_json_result = None
        st.rerun()
