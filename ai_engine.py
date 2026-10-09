def goi_ai_stylist(
    user_prompt: str,
    image_input=None,
    api_key: str = None,
    model_name: str = "gemini-2.5-flash",  # ⚡ DÙNG DUY NHẤT 1 MODEL NÀY
) -> dict:
    """Hàm điều phối gọi AI Stylist - Chỉ sử dụng đúng 1 mô hình gemini-2.5-flash duy nhất."""
    key_to_use = (
        api_key
        or (st.secrets.get("GEMINI_API_KEY") if hasattr(st, "secrets") else None)
        or os.environ.get("GEMINI_API_KEY")
    )

    if not key_to_use:
        return {
            "status": "GLITCH_DETECTED",
            "error_code": None,
            "canh_bao": "Chưa cấu hình API Key! Vui lòng kiểm tra lại secrets/môi trường.",
            "loi_khuyen": "Hệ thống tạm ngắt kết nối do thiếu API Key.",
            "kien_thuc_lich_su": None,
            "prompt_image": None,
            "chi_tiet_phoi": None,
        }

    client = genai.Client(api_key=key_to_use)

    # Đóng gói dữ liệu gửi đi (Ảnh chân dung + Prompt)
    contents = []
    if image_input is not None:
        if hasattr(image_input, "read"):
            img_bytes = image_input.read()
        elif isinstance(image_input, bytes):
            img_bytes = image_input
        else:
            buf = io.BytesIO()
            image_input.save(buf, format="JPEG")
            img_bytes = buf.getvalue()

        contents.append(
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
        )

    contents.append(user_prompt)

    # Cấu hình duy nhất chuẩn xác
    config = types.GenerateContentConfig(
        temperature=0.2,
        top_p=0.85,
        system_instruction=SYSTEM_INSTRUCTION_TEXT,
        response_mime_type="application/json",
        response_schema=STRUCTURED_OUTPUT_SCHEMA,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )

    # Gọi trực tiếp API duy nhất 1 lần, không thử model khác
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )
        return json.loads(response.text)
    except Exception as e:
        err_str = str(e)
        return {
            "status": "GLITCH_DETECTED",
            "error_code": None,
            "canh_bao": f"Lỗi gọi Gemini ({model_name}): {err_str}",
            "loi_khuyen": "Nếu báo 429 RESOURCE_EXHAUSTED, bạn hãy đổi GEMINI_API_KEY sang một Gmail khác để có lại lượt gọi miễn phí.",
            "kien_thuc_lich_su": None,
            "prompt_image": None,
            "chi_tiet_phoi": None,
        }
