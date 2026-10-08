# ai_engine.py
import os
import json
from google import genai
from google.genai import types

# System Instruction lấy từ Google AI Studio
SYSTEM_INSTRUCTION = """
{
  "luat_khoa_sinh_anh": {
    "mo_ta": "Cơ chế an toàn ngắt luồng visual khi vi phạm quy chuẩn văn hóa hoặc giải phẫu trang phục",
    "dieu_kien_kich_hoat": { "status": "GLITCH_DETECTED" },
    "hanh_dong_bat_buoc": { "prompt_image": null, "chi_tiet_phoi": null, "kien_thuc_lich_su": null },
    "nghiem_cam": [
      "TUYỆT ĐỐI KHÔNG tự ý sửa đồ của người dùng để sinh prompt tạo ảnh thay thế",
      "TUYỆT ĐỐI KHÔNG xuất chuỗi 'null' dạng text, phải trả về giá trị null chuẩn",
      "TUYỆT ĐỐI KHÔNG mô tả trang phục đã chỉnh sửa trong trường prompt_image khi có lỗi"
    ]
  },
  "project": "Vietnamese Traditional Costumes Dataset & Rules",
  "version": "2_1",
  "target_dynasty": "Nguyen Dynasty",
  "academic_sources": [
    "Trang phục Việt Nam - Đoàn Thị Tình (1987)",
    "Khâm định Đại Nam hội điển sự lệ",
    "Đại Nam thực lục",
    "Nghệ thuật minh họa áo mũ thời Nguyễn - Trần Minh Nhựt"
  ],
  "luat_cam_ky": {
    "RED_ALERT": [
      {
        "id_loi": "ERR_MA_DIEN",
        "mo_ta_loi": "Phối cổ phục với Váy Mã diện (Hán phục) hoặc các trang phục ngoại quốc (Sườn xám, Hanbok, Kimono...).",
        "thong_diep_pop_up": "Cảnh báo Đỏ: Việc kết hợp Việt phục với Váy Mã diện của Hán phục hoặc các trang phục ngoại quốc làm sai lệch hoàn toàn đặc trưng văn hóa!"
      },
      {
        "id_loi": "ERR_HO_NACH",
        "mo_ta_loi": "Lỗi hở nách (không khâu liền).",
        "thong_diep_pop_up": "Cảnh báo Đỏ: Hai bên nách áo trở xuống phải khâu liền cho kín, không được để hở hang!"
      },
      {
        "id_loi": "ERR_SO_LUONG_NUT",
        "mo_ta_loi": "Lỗi vi phạm số lượng nút (không đủ 5 nút).",
        "thong_diep_pop_up": "Cảnh báo Đỏ: Áo bắt buộc phải có đủ 5 hột nút, là biểu tượng của Ngũ thường (Nhân, Lễ, Nghĩa, Trí, Tín)!"
      },
      {
        "id_loi": "ERR_MAU_HOA_TIET_TIEM_QUYEN",
        "mo_ta_loi": "Lỗi lạm dụng màu sắc/họa tiết (dùng màu vàng hoàng đế, họa tiết rồng ngũ trảo).",
        "thong_diep_pop_up": "Cảnh báo Đỏ: Lỗi tiếm quyền! Cấm dân gian mặc áo màu vàng và dùng hình rồng 5 móng vì đây là đặc quyền của Hoàng đế!"
      },
      {
        "id_loi": "ERR_NHAT_BINH_CASUAL",
        "mo_ta_loi": "Phối Áo Nhật Bình với phong cách/item thường nhật (jeans, sneaker, streetwear...) hoặc cắt ngắn làm mất điển chế.",
        "thong_diep_pop_up": "Cảnh báo Đỏ: Áo Nhật Bình là lễ phục cung đình trang trọng bậc nhất, phải giữ nguyên bản 100%, tuyệt đối không được phối với item thời trang thường nhật!"
      },
      {
        "id_loi": "ERR_ANH_LAC_NHUA",
        "mo_ta_loi": "Sử dụng chất liệu nhựa công nghiệp làm chuỗi anh lạc.",
        "thong_diep_pop_up": "Cảnh báo Đỏ: Chuỗi anh lạc tượng trưng cho trí tuệ và sự tôn nghiêm, tuyệt đối không dùng chất liệu nhựa công nghiệp!"
      }
    ]
  },
  "huong_dan_dieu_phoi_he_thong": {
    "quy_trinh_hai_giai_doan": {
      "giai_doan_1_khoi_tao": {
        "mo_ta": "Kích hoạt khi người dùng gửi thông tin ở Chặng 1.",
        "xu_ly_vi_pham": "Nếu vi phạm, trả về JSON có status = 'GLITCH_DETECTED', id_loi, thong_diep_pop_up.",
        "xu_ly_hop_le": "Trả về JSON dạng: {\"status\": \"SUCCESS\", \"prompt_image\": \"OPTION_A: <Prompt A> ||| OPTION_B: <Prompt B>\"}"
      },
      "giai_doan_2_chot_ha": {
        "mo_ta": "Kích hoạt khi chọn Option A/B + feedback.",
        "xu_ly_hop_le": "Trả về JSON dạng: {\"status\": \"SUCCESS\", \"prompt_image\": \"<Prompt Final>\", \"loi_khuyen\": \"...\", \"chi_tiet_phoi\": {\"ao_chinh\": \"...\", \"tone_mau\": \"...\", \"item_hien_dai\": \"...\"}, \"kien_thuc_lich_su\": {\"ten_trang_phuc\": \"...\", \"nguon_goc\": \"...\", \"y_nghia\": \"...\"}}"
      }
    }
  }
}
"""

def get_client(api_key: str = None):
    key = api_key or os.environ.get("GEMINI_API_KEY")
    return genai.Client(api_key=key)

def call_gemini_brain(user_prompt: str, api_key: str = None):
    """
    Gọi Gemini Model với System Instruction chuẩn từ AI Studio
    """
    client = get_client(api_key)
    
    # Cấu hình gọi model Gemini
    config = types.GenerateContentConfig(
        temperature=0.2,
        top_p=0.85,
        system_instruction=SYSTEM_INSTRUCTION,
        response_mime_type="application/json"
    )
    
    response = client.models.generate_content(
        model='gemini-2.5-flash', # Hoặc gemini-3.1-pro-preview
        contents=user_prompt,
        config=config
    )
    
    try:
        data = json.loads(response.text)
        return data
    except Exception as e:
        return {"status": "ERROR", "message": f"Không thể đọc kết quả JSON từ Gemini: {e}\nResponse: {response.text}"}

def generate_imagen_photo(prompt_text: str, api_key: str = None):
    """
    Gọi Imagen 3 để sinh ảnh từ Prompt tiếng Anh
    """
    client = get_client(api_key)
    try:
        response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt_text,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="3:4",
                output_mime_type="image/jpeg"
            )
        )
        return response.generated_images[0].image.image_bytes
    except Exception as e:
        print(f"Lỗi Imagen API: {e}")
        return None
