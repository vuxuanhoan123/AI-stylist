import io
import json
import os
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. CẤU HÌNH STRUCTURED OUTPUT SCHEMA
STRUCTURED_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["SUCCESS", "GLITCH_DETECTED"],
        },
        "error_code": {
            "type": "string",
            "nullable": True,
            "enum": [
                "ERR_MA_DIEN",
                "ERR_HO_NACH",
                "ERR_SO_LUONG_NUT",
                "ERR_MAU_HOA_TIET_TIEM_QUYEN",
                "ERR_NHAT_BINH_CASUAL",
                "ERR_ANH_LAC_NHUA",
            ],
        },
        "canh_bao": {"type": "string", "nullable": True},
        "loi_khuyen": {"type": "string"},
        "kien_thuc_lich_su": {
            "type": "object",
            "nullable": True,
            "properties": {
                "ten_trang_phuc": {"type": "string"},
                "nguon_goc_lich_su": {"type": "string"},
                "y_nghia_chi_tiet": {
                    "type": "object",
                    "properties": {
                        "y_nghia_phom_dang_va_vat": {"type": "string"},
                        "y_nghia_5_nut_ngu_thuong": {"type": "string"},
                        "y_nghia_hoa_van_mau_sac": {"type": "string"},
                        "y_nghia_phu_kien": {"type": "string"},
                    },
                },
            },
        },
        "prompt_image": {"type": "string", "nullable": True},
        "chi_tiet_phoi": {
            "type": "object",
            "nullable": True,
            "properties": {
                "ao_chinh": {"type": "string"},
                "tone_mau": {"type": "string"},
                "item_hien_dai": {"type": "string"},
            },
        },
    },
    "required": ["status", "loi_khuyen"],
}

# 2. BỘ NỘI DUNG SYSTEM INSTRUCTION
SYSTEM_INSTRUCTION_TEXT = """{
  "luat_khoa_sinh_anh": {
    "mo_ta": "Cơ chế an toàn ngắt luồng visual khi vi phạm quy chuẩn văn hóa hoặc giải phẫu trang phục",
    "dieu_kien_kich_hoat": {
      "status": "GLITCH_DETECTED"
    },
    "hanh_dong_bat_buoc": {
      "prompt_image": null,
      "chi_tiet_phoi": null,
      "kien_thuc_lich_su": null
    },
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
        "thong_diep_pop_up": "Cảnh báo Đỏ: Việc kết hợp Việt phục với Váy Mã diện của Hán phục hoặc các trang phục ngoại quốc (Sườn xám, Hanbok, Kimono) làm sai lệch hoàn toàn đặc trưng văn hóa. Vui lòng chọn chân váy dài hoặc quần ống sớ truyền thống!"
      },
      {
        "id_loi": "ERR_HO_NACH",
        "mo_ta_loi": "Lỗi hở nách (không khâu liền).",
        "thong_diep_pop_up": "Cảnh báo Đỏ: Hai bên nách áo trở xuống phải khâu liền cho kín, không được để hở hang. Vui lòng điều chỉnh lại phom dáng để tuân thủ quy chuẩn trang phục!"
      },
      {
        "id_loi": "ERR_SO_LUONG_NUT",
        "mo_ta_loi": "Lỗi vi phạm số lượng nút (không đủ 5 nút).",
        "thong_diep_pop_up": "Cảnh báo Đỏ: Áo bắt buộc phải có đủ 5 hột nút, là biểu tượng của năm đức hạnh con người nhân, lễ, nghĩa, trí, tín. Sự sai lệch số lượng nút sẽ phá vỡ triết lý cốt lõi của áo!"
      },
      {
        "id_loi": "ERR_MAU_HOA_TIET_TIEM_QUYEN",
        "mo_ta_loi": "Lỗi lạm dụng màu sắc/họa tiết (dùng màu vàng hoàng đế, họa tiết rồng ngũ trảo).",
        "thong_diep_pop_up": "Cảnh báo Đỏ: Lỗi tiếm quyền! Cấm dân gian mặc áo màu vàng và không được dùng sắc vàng và hình rồng 5 móng vì đây là đặc quyền của Hoàng đế. Vui lòng đổi màu hoặc thay đổi họa tiết!"
      },
      {
        "id_loi": "ERR_NHAT_BINH_CASUAL",
        "mo_ta_loi": "Phối Áo Nhật Bình với phong cách/item thường nhật (jeans, sneaker, streetwear, áo thun...) hoặc cắt ngắn/cải biên làm mất điển chế.",
        "thong_diep_pop_up": "Cảnh báo Đỏ: Áo Nhật Bình là lễ phục cung đình trang trọng bậc nhất, phải giữ nguyên bản 100%, tuyệt đối không được phối với item thời trang thường nhật! Mọi sự cắt xén tà hay biến đổi kết cấu sẽ làm áo thoái hóa về dạng áo Phi Phong hoặc làm sai lệch bản sắc."
      },
      {
        "id_loi": "ERR_ANH_LAC_NHUA",
        "mo_ta_loi": "Sử dụng chất liệu nhựa công nghiệp làm chuỗi anh lạc.",
        "thong_diep_pop_up": "Cảnh báo Đỏ: Chuỗi anh lạc tượng trưng cho trí tuệ, công đức thanh tịnh và khí chất tôn nghiêm. Tuyệt đối không dùng chất liệu nhựa công nghiệp vì làm mất đi linh tính vật liệu và vẻ trang trọng của trang phục truyền thống!"
      }
    ]
  },
  "luat_hien_thi_anh": {
    "quy_tac_che_mat_kem_phu_kien": {
      "dieu_kien_ap_dung": [
        "Nón lá",
        "Nón liên diệp",
        "Nón dấu",
        "Mũ cửu phụng",
        "Mũ thất phụng",
        "Mũ ngũ phụng",
        "Mũ tam phụng",
        "Mũ nhất phụng",
        "Cặp tóc bằng vàng",
        "Trâm ngọc",
        "Trâm hoa",
        "Khăn vành dây",
        "Khăn lươn",
        "Khăn đóng nam",
        "Khăn mỏ quạ"
      ],
      "yeu_cau_hien_thi": "Bắt buộc phải hiển thị đầy đủ phần đầu và tóc của mẫu ảnh để làm nổi bật vẻ đẹp của phụ kiện cung đình hoặc dân gian.",
      "yeu_cau_che_mat": "Yêu cầu làm mờ (blur), che khéo khuôn mặt hoặc chụp góc nghiêng/sau gáy để tập trung vào di sản trang phục.",
      "mac_dinh_khong_phu_kien_dau": "Nếu không có phụ kiện đầu đặc trưng, áp dụng góc chụp từ cổ trở xuống (neck-down photography) chuẩn editorial lookbook."
    }
  },
  "thuat_toan_dieu_phoi_quiet_tradition": {
    "nguyen_ly": "Form over Pattern (Tôn vinh Cấu trúc phom dáng hơn là nhồi nhét Họa tiết) và Minimalism (Thời trang ứng dụng đương đại)",
    "luat_1_cau_truc_va_phom_dang": {
      "co_lap_linh": "Trích xuất cổ đứng 2-3cm áp dụng lên áo sơ mi linen, áo polo, hoặc overshirt tạo phong thái đĩnh đạc, kín đáo thay cho cổ bẻ phương Tây.",
      "duong_vat_ho_va_nut": "Bố cục khuy cài lệch bên phải với 5 nút ngọc/đồng tích hợp lên cardigan, overshirt, hoặc áo vest không cổ.",
      "tay_ao": "Tận dụng độ thụng cánh cung của áo tấc vào sweater/hoodie mùa thu, hoặc độ gọn của tay chẽn vào các mẫu áo tay ôm hiện đại."
    },
    "luat_2_tiet_che_hoa_tiet": {
      "vi_tri_an": "Họa tiết rồng, phượng, thủy ba chỉ đưa vào các vị trí tinh tế như mặt trong viền cổ, lớp lụa lót bên trong áo khoác, gấu quần xắn lên, hoặc viền trong túi áo.",
      "dong_mau_tone_on_tone": "Dập chìm họa tiết (lấy cảm hứng từ lụa vân dệt chìm hoa lá/đám mây cổ truyền) hoặc thêu chỉ cùng tông màu với vải nền.",
      "mini_size": "Thu nhỏ đồ án đoàn long, đoàn phụng, đoàn loan thành logo kích thước nhỏ (2-3cm) đính ở ngực trái hoặc cửa tay áo."
    },
    "luat_3_chat_lieu_va_mau_sac": {
      "chat_lieu_doi_thuong": "Kế thừa vải thanh cát cổ xưa, ưu tiên vải sợi tự nhiên thấm hút: Cotton, Linen (Đũi), Denim, Canvas.",
      "bang_mau_tu_nhien": "Bảng màu lấy từ chất nhuộm thảo mộc tự nhiên: chàm, củ nâu, đen tuyền, mỡ gà, trà xanh, xanh rêu."
    },
    "luat_4_ti_le_80_20_va_overkill_alert": {
      "ty_le": "Yếu tố truyền thống (cổ lập, khuy ngũ thường, chất liệu lụa) tối đa 20% diện tích thị giác; 80% là phom dáng hiện đại (quần âu, jeans, sneaker, loafer).",
      "overkill_alert": "Nếu phát hiện người dùng nhồi nhét quá nhiều chi tiết lễ hội (cổ đứng + khuy tết + gấm đỏ bóng + rồng lớn), AI lập tức chặn và phát pop-up đề xuất chuyển hoa văn sang dập chìm và đổi chất liệu sang Linen."
    }
  },
  "danh_muc_ao": {
    "ao_ngu_than_tay_chen": {
      "ten_chinh_thuc": "Áo ngũ thân tay chẽn",
      "ten_goi_khac": [
        "Áo chít",
        "Áo năm thân",
        "Áo chiến 5 thân tay chẽn"
      ],
      "cau_truc_bat_buoc": [
        "Thân áo được định hình từ 5 thân vải: 4 thân ngoài (tượng trưng cho tứ thân phụ mẫu) và 1 tà con bên trong (người mặc).",
        "Vạt ngoài (vạt cả) được may rộng gấp đôi vạt trong (vạt con) và nằm ở bên phải.",
        "Tà con phía trong được cắt may tinh tế, giữ nguyên chiều dài tương đương chiều dài thân áo.",
        "Cổ áo thiết kế theo kiểu cổ đứng (lập lĩnh), may thẳng, cao 3cm (áo nam) hoặc thấp hơn đôi chút (áo nữ), ôm sát cổ.",
        "Ống tay áo may chẽn hoặc hẹp (áo chít), cửa ống tay rộng tối đa 9 tấc (khoảng 30cm) để đảm bảo hẹp hơn tay áo quan viên.",
        "Dọc theo sườn áo, từ hai bên nách áo trở xuống bắt buộc phải khâu liền cho kín, tuyệt đối không được để hở hang.",
        "Khuy nút sử dụng chuẩn 5 hạt bên vạt phải. Nút thứ 2 và nút giữa cổ phải tạo thành đường thẳng vuông góc với trung phùng đạo.",
        "Đường tà áo lượn, chân vạt cong hình cánh cung hướng lên như hình miệng cười sống động, uyển chuyển.",
        "Khi trải phẳng, phần tay áo và vai áo phải tạo thành một đường thẳng liền mạch, không có đường cắt cầu vai kiểu phương Tây."
      ],
      "bien_the_quan_su": {
        "ao_chien_5_than": "Dành cho tiến sĩ võ, cử nhân võ hoặc võ quan: Áo may bằng gấm hoặc dạ nỉ, vạt áo xẻ giữa, bên trong vạt có may thêm tấm che ngực bụng, thắt lưng vải buộc múi buông gọn phía trước, chân đi giày da cao cổ."
      },
      "loai_ao": {
        "ao_don": "May một lớp bằng vải mỏng, thoáng mát (lụa the, lụa vân).",
        "ao_kep": "May hai lớp công phu (lớp ngoài gấm/dạ, lớp trong lót lụa tơ), bên cạnh nút gài ngoài còn có thêm dây buộc vạt áo phía trong."
      },
      "nguon_goc_lich_su_va_y_nghia": {
        "nguon_goc": "Định hình từ cuộc cải cách trang phục Đàng Trong năm 1744 của Chúa Nguyễn Phúc Khoát nhằm tạo bản sắc riêng biệt, chấm dứt lối mặc giao lĩnh/tứ thân buông thả. Đến thế kỷ 19, Vua Minh Mạng ban hành quy chuẩn toàn quốc, đưa áo ngũ thân trở thành quốc phục của người Việt.",
        "y_nghia_5_than": "Bốn thân bên ngoài tượng trưng cho 'tứ thân phụ mẫu' (cha mẹ đẻ và cha mẹ chồng/vợ), luôn ôm ấp và che chở cho thân thứ 5 bên trong tượng trưng cho người mặc, biểu thị đạo hiếu và sự gắn kết gia đình.",
        "y_nghia_5_nut": "Tượng trưng cho Ngũ Thường (Nhân, Lễ, Nghĩa, Trí, Tín) và Ngũ Luân (Quân - Thần, Phụ - Tử, Phu - Phụ, Huynh - Đệ, Bằng - Hữu). Nhắc nhở người mặc luôn giữ gìn luân thường đạo lý và nhân cách đĩnh đạc.",
        "y_nghia_khau_kin_nach": "Thể hiện sự khiêm nhường, đoan trang, kín đáo, che chở thân thể và giữ gìn phẩm hạnh của người xưa."
      }
    },
    "ao_tac": {
      "ten_chinh_thuc": "Áo Tấc",
      "ten_goi_khac": [
        "Áo rộng",
        "Áo thụng",
        "Áo ngũ thân tay thụng"
      ],
      "cau_truc_bat_buoc": [
        "Cấu tạo từ 5 thân vải cắt thẳng, thiết kế phom suông không chiết eo, vạt xòe cong nhẹ sang hai bên.",
        "Áo có dáng xẻ giữa, thân con bên trong giữ nguyên chiều dài bằng thân ngoài.",
        "Cổ áo lập lĩnh cao 2cm (đối với áo nữ/mệnh phụ) đến 3cm (đối với áo nam), dựng vuông và ôm khít cổ.",
        "Đặc điểm nhận diện tuyệt đối: Ống tay áo may thụng hình chữ nhật rất rộng (từ 30-50cm), chiều dài ống tay đo bằng đúng chiều dài thân áo (buông chùng quá gối hoặc che kín bàn tay; khi chắp tay tạo hình cánh cung trang nghiêm).",
        "Hai bên nách may liền, không bao giờ bó nách.",
        "Gài 5 nút cài bên tay phải, xếp theo hình chữ 'quảng', chế tác từ kim loại mạ vàng, ngọc thạch hoặc đồng.",
        "Tà áo thường dài qua đầu gối từ 7-10cm."
      ],
      "hoan_canh_su_dung": {
        "nam_gioi": "Áo choàng ngoài trang trọng dùng trong các buổi lễ lớn, buổi chầu thường nhật, tiếp tân, lễ chùa chiền, cưới hỏi, kỵ giỗ.",
        "nu_gioi": "Áo choàng ngoài (áo cặp, áo mệnh phụ) dành cho phụ nữ quý tộc, tiểu thư con quan trong ngày lễ cưới hỏi, chúc phúc gia đình."
      },
      "nguon_goc_lich_su_va_y_nghia": {
        "nguon_goc": "Ra đời cùng thời với cuộc định chế y phục Đàng Trong của Chúa Nguyễn Phúc Khoát (khoảng 300 năm lịch sử). Được điển chế hóa thành lễ phục phổ biến cho mọi tầng lớp từ vua chúa đến thường dân trong các dịp trọng đại.",
        "y_nghia_ten_goi": "Tên gọi 'Áo Tấc' bắt nguồn từ phần viền tà áo rộng đúng một tấc xưa (khoảng 4cm), hoặc do tay áo dài rộng buông chùng tôn nghiêm.",
        "y_nghia_tay_thung": "Thể hiện cốt cách ung dung, thanh tịnh, tôn ti trật tự và sự khiêm cung tuyệt đối. Động tác chắp tay hành lễ giấu kín đôi bàn tay trong ống tay thụng biểu đạt sự kính trọng sâu sắc đối với thần linh, tổ tiên và người đối diện."
      }
    },
    "ao_nhat_binh": {
      "ten_chinh_thuc": "Áo Nhật Bình",
      "phan_cap_hoang_cung": [
        {
          "cap_bac": "Hoàng hậu / Hoàng thái hậu",
          "mau_sac": "Màu vàng chính sắc hoặc màu cam (chất liệu sa sợi vàng hoặc gấm thượng hạng)",
          "hoa_van": "Thêu 20 hình rồng, phượng, loan, trĩ bằng sợi kim tuyến; nẹp cổ thêu kim phụng",
          "xiem_thuong": "Xiêm/thường bằng tơ bát ti trắng thêu rồng phượng",
          "phu_kien_dau": "Mũ cửu phụng kim ước phát hoặc mũ Cửu long kim ước phát, 8 trâm vàng",
          "dac_diem_tay": "Đặc biệt: Theo điển chế, tay áo Nhật Bình của bậc Hậu không áp dụng dải ngũ hành 5 màu"
        },
        {
          "cap_bac": "Công chúa",
          "mau_sac": "Màu đỏ chính sắc (sa sợi đỏ)",
          "hoa_van": "Họa tiết phượng ổ, hoa tròn dệt chim loan, chim phượng",
          "xiem_thuong": "Xiêm bằng tơ màu trắng dệt hoa tròn",
          "phu_kien_dau": "Mũ thất phụng kim ước phát, 12 trâm hoa, cặp tóc bằng vàng"
        },
        {
          "cap_bac": "Phi tần Nhị giai",
          "mau_sac": "Màu xích đào (đào đỏ chất liệu sa)",
          "hoa_van": "Đoàn loan (hoa tròn có hình chim loan)",
          "xiem_thuong": "Thường bằng tơ bát ti trắng thêu loan ổ",
          "phu_kien_dau": "Mũ ngũ phụng, 10 trâm, cặp tóc bằng vàng, trâm hoa"
        },
        {
          "cap_bac": "Phi tần Tam giai",
          "mau_sac": "Màu tím chính sắc",
          "hoa_van": "Đoàn phượng (hoa tròn có hình chim phượng)",
          "xiem_thuong": "Thường bằng tơ bát ti trắng thêu loan ổ",
          "phu_kien_dau": "Mũ tam phụng, 8 trâm, cặp tóc bằng vàng, trâm ngọc"
        },
        {
          "cap_bac": "Phi tần Tứ giai",
          "mau_sac": "Màu tím nhạt (chất liệu sa)",
          "hoa_van": "Đoàn loan",
          "xiem_thuong": "Xiêm màu trắng dệt chim loan",
          "phu_kien_dau": "Mũ Phượng kim ước (nhất phụng), 8 trâm, cặp tóc bằng vàng, trâm hoa"
        }
      ],
      "giai_phau_co_hoc": {
        "co_ao": "Dáng đối khâm (xẻ ngực), nẹp cổ to bản tạo thành hình chữ nhật bao quanh cổ rủ thẳng xuống ngực, cài 1 cúc hoặc dây buộc cố định trước ngực, tà dưới buông hở tự nhiên.",
        "than_ao": "May rộng và dài, có xẻ tà hai bên nhấn eo, chất liệu lụa, gấm hoặc sa cao cấp.",
        "tay_ao": "Ống tay rộng buông dài. Đầu cửa tay áo có dải 5 màu ngũ hành (xanh lục, vàng, xanh lam, trắng, đỏ) tượng trưng cho Kim - Mộc - Thủy - Hỏa - Thổ (ngoại trừ áo của bậc Hậu).",
        "chan_ta": "Thêu đồ án Thủy ba (sóng nước đứng), Tam sơn (núi non) và mây ngũ sắc.",
        "dai_thuy_luu": "Dưới cổ tay áo có hai dải dây dài thả lỏng buông rủ, tạo sự uyển chuyển khi cử động."
      },
      "nguon_goc_lich_su_va_y_nghia": {
        "nguon_goc": "Định hình từ năm Gia Long thứ 6 (1807), biến thể từ áo Phi Phong thời Minh nhưng được người Việt bản địa hóa hoàn toàn thành quy chế riêng của triều Nguyễn ('Đại đồng tiểu dị').",
        "y_nghia_ten_goi": "'Nhật Bình' xuất phát từ phần hoa văn cổ áo khi ghép lại ở trước ngực tạo thành một hình chữ nhật nằm ngang giống chữ Nhật (日) và cân đối, hài hòa (Bình).",
        "nguyen_ly_khong_cach_tan": "Nhật Bình là áo lễ tiết cung đình, gắn chặt với tôn ti trật tự và quy chế nghiêm ngặt ('Y phục xứng kì đức'). Việc cắt ngắn vạt hoặc giản lược hoa văn sẽ làm biến chất áo, biến nó trở về dạng áo Phi Phong hoặc áo Đối Khâm chứ không còn danh xưng Nhật Bình nữa.",
        "bien_doi_cuoi_trieu_nguyen": "Từ thời vua Đồng Khánh trở đi, quy chế hậu cung được tinh giản: mũ phượng và kim ước phát dần được thay thế bằng khăn vành dây màu lam đậm to bản, phối cùng quần ống trắng tuyết bạch."
      }
    }
  },
  "he_thong_chat_lieu": {
    "danh_muc_vai": {
      "lua_to_tam": [
        "Lụa the (Lụa lương): Dệt sợi thô, dệt thưa, thuộc dòng lụa Vạn Phúc, hoa văn mỏng tinh xảo.",
        "Lụa vân: Dày dặn mịn màng, dệt chìm họa tiết mây/hoa lá với độ đậm nhạt khác nhau, tạo nét trang nhã thanh lịch.",
        "Lụa hoa: Lụa thượng hạng, bề mặt dệt nổi dày đặc mô típ hoa cỏ quý phái.",
        "Lụa nội hóa: Lụa 100% tơ tằm dệt thủ công trong nước, thường làm lớp lót trong cho áo kép."
      ],
      "gam": [
        "Gấm satin thượng hạng: Dệt từ lụa tơ tằm cao cấp chải bóng dày dặn, nhập khẩu để may triều phục quan lại.",
        "Gấm satin mờ: Mặt vải đanh dày, chải bóng mờ, thường dùng may áo kép màu đen mặc mùa thu."
      ],
      "vai_pha_ni_da_va_vai_khac": [
        "Vải Nỉ (Dạ mông tự): Hợp chất len và lụa 100% dày ấm, dùng may áo chít mặc mùa đông.",
        "Vải Nhiễu cát (Crêpe de chine): 100% tơ không hoa văn, bề mặt ráp nhẹ, chuyên dùng quấn khăn đóng nam và khăn vành dây.",
        "Vải Thanh cát: Vải dệt sợi tự nhiên thô mộc, thoáng mát, thường dân và quan viên dùng may thường phục.",
        "Sa mỏng, Nhiễu bát ti, Vải trừu: Vải dệt cao cấp chuyên dùng cho hoàng tộc và phẩm phục đại lễ."
      ]
    },
    "phoi_do_theo_mua": [
      {
        "mua": "Xuân",
        "phoi_do": "Áo kép hai lớp: Lớp ngoài gấm satin xanh thiên thanh rực rỡ, lớp trong lót lụa tơ màu vàng mơ trang nhã.",
        "y_nghia_lich_su": "Màu xanh thiên thanh tượng trưng cho chồi non và trời xuân, kết hợp vàng mơ nhã nhặn mang sinh khí đầu năm mới."
      },
      {
        "mua": "Hạ",
        "phoi_do": "Áo đơn một lớp: Lụa lương/lụa the hoặc lụa vân đen thoáng khí dệt chìm. Phối bên trong áo lá quạ bằng phin/lụa trắng và quần trắng để hoa văn chìm nổi bật rõ.",
        "y_nghia_lich_su": "Giải pháp chống nóng nhiệt đới hoàn hảo của người xưa, lớp áo trắng bên trong vừa giữ mồ hôi vừa làm nổi bật nếp dệt lụa the bên ngoài."
      },
      {
        "mua": "Thu",
        "phoi_do": "Áo kép hai lớp: Lớp ngoài gấm satin mờ màu đen, lớp trong lót lụa nội hóa màu xanh ngọc thanh thoát.",
        "y_nghia_lich_su": "Tạo sắc thái hoài cổ, khi bước đi mép áo hé lộ sắc xanh ngọc như mặt nước hồ thu."
      },
      {
        "mua": "Đông",
        "phoi_do": "Áo kép hai lớp: Lớp ngoài vải dạ mông tự (nỉ len lụa) đen trơn dày ấm, lớp trong lót lụa trơn xanh nhạt.",
        "y_nghia_lich_su": "Giữ ấm cơ thể trong gió lạnh cố đô Huế mà vẫn giữ nguyên phom đứng nghiêm trang."
      }
    ],
    "nghe_thuat_tuong_phan": {
      "ao_menh_phu_cai_hoa": "May bằng lụa hoa hai lớp: Ngoài màu xanh lục phỉ thúy nhu nhã, trong lót lụa đỏ son thắm.",
      "y_nghia_lich_su": "Nghệ thuật tương phản 'Lục - Điều' kinh điển của thẩm mỹ Huế xưa, rực rỡ hỷ khí cưới hỏi nhưng thanh tao, không lòe loẹt."
    }
  },
  "phu_kien": {
    "do_doi_nam": [
      "Khăn đóng (Khăn xếp): Phụ kiện chuẩn của áo dài nam từ thập niên 1920 thay thế búi tóc. Làm bằng vải nhiễu cát tơ màu đen cao 10cm, trước trán xếp tầng chéo nhau hình chữ Nhân (人), đằng sau có dải khăn bịt búi tóc.",
      "Khăn lươn (Nam giới): Khăn vải mỏng/dày xếp 7 vòng đều đặn như bậc thang. Trước trán tạo hình chữ Nhân (人 - lấy Nhân làm gốc theo Nho giáo) hoặc chữ Nhất (一 - 'Ngô đạo nhất dĩ quán chi' theo Luận Ngữ).",
      "Khăn đầu rìu: Khăn thô màu nâu quấn quanh đầu, thắt nút nhô ra như cái rìu để thấm mồ hôi khi lao động.",
      "Nón lá dân gian: Nón liên diệp (lá sen), nón phương đầu đại, nón ngoan xác, nón xuân lôi tiểu, nón tu lờ, nón viên cơ.",
      "Nón binh lính: Nón dấu sơn đỏ chóp nhọn đính ngù, nón đĩa đan cật tre dẹt chỏm đồng hình mũi giáo, nón Ma Lôi cứng cáp thời kháng Mông."
    ],
    "do_doi_nu": [
      "Khăn vấn tóc (Khăn vành rế) & Tóc đuôi gà: Dải vải dài 80cm rộng 15-20cm bọc quanh cốt độn tóc nhồi bông, chừa lại lọn tóc dài rủ xuống cạnh tai trái tạo thành tóc đuôi gà duyên dáng.",
      "Khăn vuông thâm (Mỏ quạ): Khăn vuông đen gập chéo hình tam giác buộc dưới cằm trùm kín tai, mép gấp nhô ra trước trán hình mỏ quạ nhọn thanh thoát vùng Kinh Bắc.",
      "Khăn vành dây (Cung đình Huế): Dải vải nhiễu cát/crepe de chine dài 15m, rộng 30cm xếp thành 6cm, quấn nhiều vòng từ trán lên gáy hình chữ V ngược xòe rộng như hình phễu/cái đĩa lớn. Thường dùng màu lam đậm (hoàng tộc/cô dâu), chỉ bậc Hậu mới có khăn vàng."
    ],
    "giay_dep": [
      "Giày Hạ (Nam): Giày da xuất hiện thập niên 1930–1940, làm 100% bằng da cả thân lẫn đế, đi kèm áo dài ngũ thân nam thời tân thời.",
      "Hia (Vua / Quan): Đại triều phục do Cẩm Tượng Ty chế tác. Hia có mũi vuông/mũi cong, bên ngoài bọc đoạn đen thêu rồng mây kim tuyến, trong lót lụa đỏ, đi kèm tất lĩnh bóng trắng hoặc lam thẫm.",
      "Hài thêu (Hậu cung / Công chúa): Tơ đỏ hoặc tơ vàng, thêu chim phượng màu lục, đính ngọc san hô, trân châu và vàng tốt."
    ],
    "chuoi_anh_lac": {
      "dinh_nghia": "Keyūra trong tiếng Phạn, chuỗi bảo vật trang nghiêm kết từ các hạt đá quý thiên nhiên buông trước ngực mang năng lượng thiền định.",
      "chat_lieu_hop_le": [
        "Đá quý thiên nhiên (Thạch anh, Ngọc phỉ thúy, Tourmaline, Mã não)",
        "Ngọc trai",
        "Hổ phách",
        "Gỗ trầm hương",
        "Đồng mạ vàng/bạc"
      ],
      "luat_cam_ky": "Tuyệt đối không dùng chất liệu nhựa công nghiệp vì làm mất đi linh tính vật liệu và vẻ tôn nghiêm của trang phục truyền thống.",
      "y_nghia_lich_su": "Tượng trưng cho trí tuệ, công đức viên mãn và sự tịnh hóa tâm hồn. Trong cổ phục, nó là dấu ấn khẳng định phẩm cách cao quý và tầng sâu văn hóa của người mặc.",
      "cach_phoi": {
        "nhat_binh": "Choàng 1 lớp từ vai xuống ngực kết đá đều, màu sắc tương phản tôn vẻ quyền quý cung đình.",
        "giao_linh": "Dạng lưới rủ hoặc xếp lớp ngực, trung tâm kết tua rua, mang vẻ thanh tịnh, thoát tục.",
        "ao_tac": "Chuỗi hạt bản rộng, đá ngọc sáng màu hoặc phối ánh kim tăng sự mực thước trang trọng.",
        "ao_dai_cach_dieu": "Chuỗi hạt mảnh, nhỏ buông nhẹ xương quai xanh tạo vẻ thanh thoát."
      }
    },
    "trang_suc_nam": {
      "nut_ao": "Bộ 5 nút ngọc thạch, mã não hổ phách hoặc đồng mạ vàng đại diện cho Ngũ thường.",
      "dai_lung": "Đai da bọc lụa đỏ/vàng, cẩn phiến ngọc trắng, đồi mồi, sừng tê, xà cừ hoặc bạc/vàng (các phiến phương, trường, viên), đính móc câu đai ngọc chạm rồng theo phẩm trật."
    }
  },
  "phong_cach_ung_dung": [
    {
      "ten_vibe": "Thư sinh (Preppy Scholar)",
      "trang_phuc_chinh": "Áo ngũ thân tay chẽn",
      "tone_mau_chu_dao": [
        "Be",
        "Xanh lam",
        "Xám ghi"
      ],
      "item_hien_dai_phoi_kem": {
        "quan": "Quần âu ống suông (straight pants) hoặc kaki",
        "giay": "Giày Loafer hoặc Oxford da thật",
        "phu_kien": "Kính gọng tròn, túi tote canvas, đồng hồ dây da cổ điển"
      },
      "thuyet_minh_lich_su": "Lấy cảm hứng từ hình ảnh các nho sinh, sĩ tử kinh kỳ thời Nguyễn với phong thái nho nhã, trầm tĩnh. Chiếc áo ngũ thân cổ lập lĩnh 3cm cài 5 cúc tượng trưng cho Ngũ thường kết hợp cùng nét cắt hiện đại của quần âu tạo nên diện mạo trí thức chuẩn mực.",
      "canh_bao_nhat_binh": "Vibe này không áp dụng cho Áo Nhật Bình. Áo Nhật Bình là lễ phục cung đình, phải giữ nguyên bản 100%, không phối với item thường nhật."
    },
    {
      "ten_vibe": "Vintage xưa hoài cổ (Retro Nostalgia)",
      "trang_phuc_chinh": "Áo tấc hoặc Áo ngũ thân tay chẽn",
      "tone_mau_chu_dao": [
        "Nâu đất",
        "Củ nâu",
        "Mỡ gà",
        "Xanh rêu"
      ],
      "item_hien_dai_phoi_kem": {
        "quan": "Quần chất liệu linen hoặc đũi ống rộng thoải mái",
        "giay": "Giày Hạ bằng da (đúng chuẩn thời Nguyễn thập niên 1930) hoặc guốc mộc truyền thống",
        "phu_kien": "Túi vải mộc, quạt xếp nan gỗ, nón lá sen/nón cỏ, khăn vấn tóc đuôi gà (nữ)"
      },
      "thuyet_minh_lich_su": "Tái hiện không gian văn hóa thị thành Việt Nam những năm 1930–1940 trong giai đoạn giao thời. Sự xuất hiện của Giày Hạ da và chất liệu đũi mộc mạc gợi nhắc vẻ đẹp khiêm cung, giản dị của người xưa.",
      "canh_bao_nhat_binh": "Vibe này không áp dụng cho Áo Nhật Bình. Áo Nhật Bình là lễ phục cung đình, phải giữ nguyên bản 100%, không phối với item thường nhật."
    },
    {
      "ten_vibe": "Chill chill mùa thu Hà Nội (Autumn City Boy)",
      "trang_phuc_chinh": "Áo ngũ thân tay chẽn làm áo khoác mỏng bên ngoài (buông lơi 1-2 cúc trên hoặc không cài cúc), lớp trong mặc áo thun trơn cổ tròn hoặc áo len cổ lọ mỏng",
      "tone_mau_chu_dao": [
        "Xanh navy bạc",
        "Đen nhám",
        "Trắng sữa ngả vàng",
        "Nâu ấm"
      ],
      "item_hien_dai_phoi_kem": {
        "quan": "Quần jeans ống suông hoặc quần túi hộp vải đanh",
        "giay": "Giày sneaker canvas (như Converse / Vans)",
        "phu_kien": "Mũ len mỏng (beanie) hoặc khăn choàng nỉ"
      },
      "thuyet_minh_lich_su": "Vận dụng linh hoạt lối mặc áo kép buông cúc của người dân xưa khi lao động hoặc thời tiết chuyển mùa. Áo ngũ thân đóng vai trò như một chiếc cardigan overshirt thanh lịch, mang bản sắc Việt vào nhịp sống phố thị đương đại.",
      "canh_bao_nhat_binh": "Vibe này không áp dụng cho Áo Nhật Bình. Áo Nhật Bình là lễ phục cung đình, phải giữ nguyên bản 100%, không phối với item thường nhật."
    },
    {
      "ten_vibe": "Công sở (Office Wear)",
      "trang_phuc_chinh": "Áo ngũ thân tay chẽn",
      "quy_chuan_khat_khe": [
        "Thân áo phải được định hình từ 5 thân vải, với vạt ngoài (vạt cả) may rộng gấp đôi vạt trong (vạt con).",
        "Cổ áo thiết kế theo kiểu cổ đứng, may cao 3cm.",
        "Hai bên nách áo trở xuống bắt buộc phải khâu liền cho kín, không được để hở hang.",
        "Áo bắt buộc phải có đủ 5 hột nút, tượng trưng cho năm đức hạnh nhân, lễ, nghĩa, trí, tín."
      ],
      "loi_cam_ky_RED_ALERT": [
        "Tuyệt đối không lạm dụng màu vàng hoàng đế hoặc họa tiết rồng 5 móng.",
        "Không được áp dụng Áo Nhật Bình cho phong cách này vì đây là lễ phục cung đình, bắt buộc phải giữ nguyên bản 100% và không phối với các item thường nhật."
      ],
      "thuyet_minh_lich_su": "Thừa kế tính mực thước, kín đáo của trang phục quan viên thời Nguyễn khi làm việc tại công đường. Cổ lập lĩnh 3cm và tay chẽn dưới 30cm giúp cử động thuận lợi nhưng luôn giữ trọn vẻ lịch sự, chuẩn mực nơi công sở."
    },
    {
      "ten_vibe": "Đi cà phê dạo phố (Cafe/Casual Outing)",
      "trang_phuc_chinh": "Có thể mặc áo ngũ thân tay chẽn hoặc áo tấc",
      "quy_chuan_khat_khe": [
        "Nếu sử dụng áo tấc (áo thụng), đặc điểm nhận diện tuyệt đối là ống tay áo phải may rất rộng và có chiều dài bằng đúng chiều dài của thân áo.",
        "Phần cổ áo của áo tấc phải may cao từ 2cm đến 3cm."
      ],
      "loi_cam_ky_RED_ALERT": [
        "Tuyệt đối không phối áo Việt phục với Váy Mã diện của Hán phục hoặc các trang phục ngoại quốc (Sườn xám, Hanbok, Kimono) để tránh làm sai lệch hoàn toàn đặc trưng văn hóa.",
        "Áo Nhật Bình không được phép sử dụng để phối thành đồ thường nhật đi cà phê.",
        "Không được sử dụng chuỗi anh lạc làm từ nhựa công nghiệp để tránh làm mất đi vẻ tôn nghiêm của trang phục."
      ],
      "thuyet_minh_lich_su": "Đưa Việt phục trở lại đời sống thường nhật một cách tự nhiên. Áo tấc hoặc ngũ thân chất liệu nhẹ mang đến vẻ thư thái, tự tin và kết nối sâu sắc với di sản cội nguồn."
    }
  ],
  "huong_dan_dieu_phoi_he_thong": {
    "ky_nang_phan_tich_nhan_trac_hoc": {
      "buoc_1_quet_anh": "Nhận diện các đặc điểm vật lý cốt lõi: dáng khuôn mặt (tròn, trái xoan, góc cạnh...), kiểu tóc (ngắn, dài, búi...), phụ kiện (kính gọng tròn, kính kim loại, có râu...), vóc dáng theo chỉ số BMI (mảnh mai, cân đối, đầm người).",
      "buoc_2_phien_dich": "Tạo cụm từ tiếng Anh miêu tả nhân vật (ví dụ: 'A young Vietnamese woman with oval face, straight black hair, wearing thin round glasses, balanced body build').",
      "buoc_3_tich_hop": "Bắt buộc đặt cụm từ này ở đầu câu lệnh vẽ ảnh để Imagen tạo nhân vật bám sát người dùng thật nhất."
    },
    "quy_trinh_hai_giai_doan": {
      "giai_doan_1_khoi_tao": {
        "mo_ta": "Kích hoạt khi người dùng gửi ảnh + BMI + mẫu áo đã chọn + Vibe + Ghi chú ở lần gọi đầu tiên.",
        "xu_ly_vi_pham": "Nếu vi phạm luật cấm kỵ, đặt status = 'GLITCH_DETECTED', error_code, canh_bao, và khóa prompt_image = null.",
        "xu_ly_hop_le": "Nếu hợp lệ, đặt status = 'SUCCESS'. Trường prompt_image phải xuất đúng chuỗi chứa 2 đoạn prompt tiếng Anh của 2 Style gần nhau theo cú pháp: 'OPTION_A: <Prompt A Option> ||| OPTION_B: <Prompt B Option>' để Frontend Streamlit tách chuỗi gọi Imagen vẽ đúng 2 ảnh. Các trường kien_thuc_lich_su tóm tắt cơ bản."
      },
      "giai_doan_2_chot_ha": {
        "mo_ta": "Kích hoạt khi người dùng gửi lựa chọn (Option A hoặc B) kèm lời feedback tinh chỉnh.",
        "xu_ly_hop_le": "Đặt status = 'SUCCESS'. Trường prompt_image xuất duy nhất 1 câu prompt hoàn chỉnh nhất đã kết hợp feedback để vẽ bức ảnh cuối cùng.",
        "cac_truong_ui_bat_buoc": "Điền trọn vẹn 100% các trường: canh_bao = null, loi_khuyen, chi_tiet_phoi (ao_chinh, tone_mau, item_hien_dai), và khối kien_thuc_lich_su (ten_trang_phuc, nguon_goc_lich_su, y_nghia_chi_tiet đầy đủ)."
      }
    }
  }
}"""


import time  # Thêm import time ở đầu file ai_engine.py

def goi_ai_stylist(
    user_prompt: str,
    image_input=None,
    api_key: str = None,
    model_name: str = "gemini-2.5-flash",
) -> dict:
    """Hàm điều phối gọi AI Stylist có tích hợp Auto-Retry & Fallback chống lỗi 503/429."""
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

    config = types.GenerateContentConfig(
        temperature=0.2,
        top_p=0.85,
        max_output_tokens=65536,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        system_instruction=SYSTEM_INSTRUCTION_TEXT,
        response_mime_type="application/json",
        response_schema=STRUCTURED_OUTPUT_SCHEMA,
    )

    # Chuẩn bị nội dung gửi (multimodal)
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

    # Danh sách các model ổn định để tự động thử lần lượt nếu bị nghẽn 503 / 429
    candidate_models = [model_name, "gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    # Bỏ trùng lặp giữ nguyên thứ tự
    candidate_models = list(dict.fromkeys([m for m in candidate_models if m]))

    last_error = None

    for target_model in candidate_models:
        # Thử tối đa 3 lần cho mỗi model nếu gặp lỗi 503/429
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=target_model, contents=contents, config=config
                )
                return json.loads(response.text)
            except Exception as e:
                last_error = str(e)
                # Nếu bị nghẽn mạng 503 hoặc quá tải 429, tạm dừng 2s rồi thử lại
                if "503" in last_error or "UNAVAILABLE" in last_error or "429" in last_error:
                    time.sleep(2)
                    continue
                else:
                    # Nếu là lỗi khác (vd model 404), chuyển ngay sang model tiếp theo
                    break

    # Nếu tất cả các model và lần thử đều thất bại
    return {
        "status": "GLITCH_DETECTED",
        "error_code": None,
        "canh_bao": "Máy chủ Google Gemini đang quá tải toàn hệ thống. Vui lòng đợi 10-15 giây rồi ấn nút thử lại!",
        "loi_khuyen": f"Chi tiết lỗi từ Google: {last_error}",
        "kien_thuc_lich_su": None,
        "prompt_image": None,
        "chi_tiet_phoi": None,
    }
