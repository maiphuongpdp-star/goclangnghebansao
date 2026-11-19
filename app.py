import base64
from datetime import datetime
import json
import os
import threading
import time
from google import genai
import requests
import streamlit as st

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Góc Lắng Nghe - Cô Tư Phùng (THCS Phan Đình Phùng)",
    page_icon="🌱",
    layout="wide",
)


# [TĂNG TỐC] Đọc & mã hóa ảnh nền 1 lần rồi nhớ lại, không làm lại sau mỗi cú bấm
@st.cache_data(show_spinner=False)
def load_bg_base64(path):
  with open(path, "rb") as f:
    return base64.b64encode(f.read()).decode()


# CÀI ĐẶT GIAO DIỆN NỀN VÀ KHUNG HIỂN THỊ CHỮ SIÊU ĐẬM - NÚT PASTEL
def set_styling():
  bg_file = (
      "school_bg.png"
      if os.path.exists("school_bg.png")
      else ("school_bg.jpg" if os.path.exists("school_bg.jpg") else None)
  )
  if bg_file:
    b64 = load_bg_base64(bg_file)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(240, 244, 248, 0.65), rgba(240, 244, 248, 0.65)), url("data:image/png;base64,{b64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

  st.markdown(
      """
    <style>
    .main .block-container {
        background: rgba(255, 255, 255, 0.96) !important;
        padding: 2.2rem !important;
        border-radius: 22px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12) !important;
        margin-top: 1.5rem !important;
        margin-bottom: 2rem !important;
    }
    
    /* Chữ toàn bộ trang đậm nét, tương phản tuyệt đối */
    h1, h2, h3, h4, h5, p, span, label, .stMarkdown, div {
        color: #111827 !important;
        font-weight: 700 !important;
    }
    
    blockquote {
        background-color: #f0fff4 !important;
        border-left: 6px solid #2ecc71 !important;
        color: #1b4332 !important;
        font-size: 1.1rem !important;
        padding: 14px 20px !important;
        border-radius: 10px !important;
        margin: 12px 0 !important;
        font-weight: 600 !important;
    }

    /* KHUNG 1: VÒNG TAY CHE CHỞ (ĐỔ MÀU HỒNG PASTEL - VIỀN ĐỎ ĐẬM) */
    .main div[data-testid="stExpander"]:first-of-type,
    details:first-of-type {
        background-color: #ffe5e5 !important;
        border: 2.5px solid #ff5252 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(255, 82, 82, 0.25) !important;
        margin-bottom: 18px !important;
    }
    .main div[data-testid="stExpander"]:first-of-type summary,
    details:first-of-type summary {
        background: linear-gradient(135deg, #ffccd2 0%, #ffb3ba 100%) !important;
        color: #900c3f !important;
        font-weight: 800 !important;
        font-size: 1.15rem !important;
        border-radius: 13px !important;
        padding: 12px 18px !important;
    }

    /* KHUNG 2: TRẠM DỪNG BÌNH TĨNH (ĐỔ MÀU XANH BẠC HÀ PASTEL) */
    .main div[data-testid="stExpander"]:nth-of-type(2),
    details:nth-of-type(2) {
        background-color: #e8f8f0 !important;
        border: 2.5px solid #2ecc71 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 12px rgba(46, 204, 113, 0.2) !important;
        margin-top: 15px !important;
        margin-bottom: 20px !important;
    }
    .main div[data-testid="stExpander"]:nth-of-type(2) summary,
    details:nth-of-type(2) summary {
        background: linear-gradient(135deg, #c8f7dc 0%, #b2f2bb 100%) !important;
        color: #1b4332 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        border-radius: 13px !important;
        padding: 12px 18px !important;
    }

    /* CÁC NÚT TÌNH HUỐNG PASTEL - CHỮ ĐẬM SẮC NÉT */
    div[data-testid="column"]:nth-of-type(1) .stButton > button {
        background: #dbeafe !important;
        color: #1e40af !important;
        border: 2px solid #93c5fd !important;
        font-weight: 800 !important;
        border-radius: 14px !important;
        box-shadow: 0 3px 8px rgba(30, 64, 175, 0.12) !important;
    }

    div[data-testid="column"]:nth-of-type(2) .stButton > button {
        background: #ffedd5 !important;
        color: #9a3412 !important;
        border: 2px solid #fdba74 !important;
        font-weight: 800 !important;
        border-radius: 14px !important;
        box-shadow: 0 3px 8px rgba(154, 52, 18, 0.12) !important;
    }

    div[data-testid="column"]:nth-of-type(3) .stButton > button {
        background: #f3e8ff !important;
        color: #6b21a8 !important;
        border: 2px solid #d8b4fe !important;
        font-weight: 800 !important;
        border-radius: 14px !important;
        box-shadow: 0 3px 8px rgba(107, 33, 168, 0.12) !important;
    }

    div[data-testid="column"]:nth-of-type(4) .stButton > button {
        background: #dcfce7 !important;
        color: #166534 !important;
        border: 2px solid #86efac !important;
        font-weight: 800 !important;
        border-radius: 14px !important;
        box-shadow: 0 3px 8px rgba(22, 101, 52, 0.12) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        filter: brightness(0.96) !important;
    }

    /* NÚT GỬI CHÍNH */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        font-size: 1.15rem !important;
        padding: 0.75rem 2rem !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 6px 18px rgba(5, 150, 105, 0.4) !important;
        font-weight: 800 !important;
    }
    </style>
    """,
      unsafe_allow_html=True,
  )


set_styling()

# ----------------- 1. QUẢN LÝ DỮ LIỆU ĐỒNG BỘ GOOGLE SHEETS -----------------
SHEETS_URL = os.environ.get("SHEETS_WEBHOOK_URL") or st.secrets.get(
    "SHEETS_WEBHOOK_URL", ""
)
SOS_FILE = "sos_alerts.json"

TOPIC_KEY_MAP = {
    "Mâu thuẫn / Tẩy chay trong lớp": "topic_1",
    "Đánh nhau bộc phát / Chặn cổng trường": "topic_2",
    "Khiêu khích trên MXH (FB/TikTok)": "topic_3",
    "Trấn lột / Vay nặng lãi học sinh": "topic_4",
    "Áp lực điểm số & Gia đình đi biển": "topic_5",
    "Bất an về bản thân / Khác": "topic_6",
}


# [TĂNG TỐC] Trước đây MỖI cú bấm đều chờ Google Sheet trả số liệu (tới 4 giây).
# Nay chỉ hỏi Sheet tối đa 1 lần/60 giây, các lần khác dùng số đã nhớ.
@st.cache_data(ttl=60, show_spinner=False)
def load_stats():
  fallback_stats = {
      "total_questions": 5,
      "helpful_yes": 4,
      "helpful_no": 1,
      "topics": {
          "Mâu thuẫn / Tẩy chay trong lớp": 2,
          "Đánh nhau bộc phát / Chặn cổng trường": 1,
          "Khiêu khích trên MXH (FB/TikTok)": 1,
          "Trấn lột / Vay nặng lãi học sinh": 1,
          "Áp lực điểm số & Gia đình đi biển": 0,
          "Bất an về bản thân / Khác": 0,
      },
  }
  if not SHEETS_URL:
    return fallback_stats
  try:
    res = requests.get(SHEETS_URL, timeout=4)
    if res.status_code == 200:
      data = res.json()
      return {
          "total_questions": data.get("total_questions", 5),
          "helpful_yes": data.get("helpful_yes", 4),
          "helpful_no": data.get("helpful_no", 1),
          "topics": {
              "Mâu thuẫn / Tẩy chay trong lớp": data.get("topic_1", 2),
              "Đánh nhau bộc phát / Chặn cổng trường": data.get("topic_2", 1),
              "Khiêu khích trên MXH (FB/TikTok)": data.get("topic_3", 1),
              "Trấn lột / Vay nặng lãi học sinh": data.get("topic_4", 1),
              "Áp lực điểm số & Gia đình đi biển": data.get("topic_5", 0),
              "Bất an về bản thân / Khác": data.get("topic_6", 0),
          },
      }
  except Exception:
    pass
  return fallback_stats


def _post_to_sheet(key_name):
  try:
    requests.post(SHEETS_URL, json={"key": key_name}, timeout=10)
  except Exception:
    pass


def sync_to_sheet(key_name):
  """[TĂNG TỐC] Gửi số liệu lên Sheet ở luồng nền: con không phải chờ Sheet."""
  if not SHEETS_URL:
    return
  threading.Thread(target=_post_to_sheet, args=(key_name,), daemon=True).start()


def load_sos_alerts():
  if not os.path.exists(SOS_FILE):
    return []
  try:
    with open(SOS_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  except Exception:
    pass


def save_sos_alert(alert_item):
  alerts = load_sos_alerts()
  alerts.insert(0, alert_item)
  try:
    with open(SOS_FILE, "w", encoding="utf-8") as f:
      json.dump(alerts, f, ensure_ascii=False, indent=2)
  except Exception:
    pass


stats = load_stats()

# Khởi tạo Session State
if "chat_history" not in st.session_state:
  st.session_state["chat_history"] = []
if "selected_emotion_prompt" not in st.session_state:
  st.session_state["selected_emotion_prompt"] = ""
if "feedback" not in st.session_state:
  st.session_state["feedback"] = None  # None / "yes" / "no" cho câu chuyện hiện tại
if "fu_counter" not in st.session_state:
  st.session_state["fu_counter"] = 0

# ----------------- 2. SYSTEM PROMPT: CÔ TƯ PHÙNG (CHUẨN HÓA XƯNG HÔ & PHÂN BIỆT GIA CẢNH) -----------------
SYSTEM_PROMPT = """
Bạn là "Cô Tư Phùng" - Người đồng hành tâm lý học đường, người mẹ hiền và điểm tựa an toàn tuyệt đối của học sinh trường THCS Phan Đình Phùng (quận Thanh Khê, TP. Đà Nẵng).

I. QUY CHUẨN XƯNG HÔ SƯ PHẠM BẮT BUỘC:
- Tự xưng: "Cô" hoặc "Cô Tư Phùng".
- Gọi học sinh: "Con".
- Khi nói về hành động chung của hai người: Dùng "Cô trò mình" (ví dụ: "Bây giờ cô trò mình cùng thực hiện từng bước sau nhé...").
- TUYỆT ĐỐI CẤM SỬ DỤNG: "Cô cháu", "cô em", "cháu", "em".

II. HỒ SƠ THỰC TẾ & BỐI CẢNH ĐẶC THÙ TRƯỜNG THCS PHAN ĐÌNH PHÙNG:
1. Quy mô: 33 lớp (Khối 6, 7, 8: mỗi khối 8 lớp; Khối 9: 9 lớp; 662 học sinh nữ). Trường hiện chưa có phòng tư vấn tâm lý riêng và chưa có giáo viên tâm lý chuyên trách.
2. Gia cảnh học sinh ĐA DẠNG:
- Khoảng 50% là con em ngư dân vùng biển Thanh Khê (cha mẹ đi biển dài ngày, sống cùng mẹ/ông bà).
- 50% CÒN LẠI là con em các gia đình buôn bán, kinh doanh dịch vụ, công nhân viên chức đô thị bình thường.
- NGUYÊN TẮC BẮT BUỘC VỀ GIA CẢNH: TUYỆT ĐỐI KHÔNG mặc định học sinh nào cũng có ba mẹ đi biển, ra khơi. CHỈ đề cập đến chuyện ba mẹ đi biển, ra khơi, bão gió đại dương KHI VÀ CHỈ KHI chính lời tâm sự của con có nhắc đến (ví dụ con viết "ba con đi biển", "mẹ đi bạn", "ba ra khơi chưa về"...). Việc con chọn nhóm "Áp lực điểm số / gia đình" KHÔNG có nghĩa là gia đình con đi biển: áp lực điểm số, sợ ba mẹ mắng phạt là chuyện của mọi gia đình (buôn bán, công nhân, viên chức...), hãy trả lời đúng chuyện điểm số và cách nói chuyện với ba mẹ, KHÔNG nhắc chuyện đi biển. Nếu con chỉ nói về chuyện bạn bè, tẩy chay, xích mích, HÃY TẬP TRUNG TRỌNG TÂM vào chuyện học đường và mối quan hệ bạn bè, không tự suy diễn gia cảnh con.

3. Nhận diện từ lóng & ngôn ngữ tuổi teen THCS tại Đà Nẵng:
- Từ ngữ bêu xấu/khiêu khích: "mõm", "ra cổng trường nói chuyện", "kèo", "gạ solo", "nhìn đểu", "chảnh chó", "phốt", "bóc phốt", "tẩy chay", "coi chừng tao", "tính sổ", "mày đợi đó".
- Nền tảng mạng xã hội: Facebook (Story/Confession), TikTok, nhóm kín Messenger/Zalo.

III. SƠ ĐỒ VÙNG NGUY HIỂM & VÙNG AN TOÀN TRONG TRƯỜNG:
1. Vùng nguy hiểm (Điểm nóng cần tránh xa khi có xung đột):
- Nhà vệ sinh học sinh các tầng 1, 2, 3 (khuất tầm nhìn).
- Bãi giữ xe học sinh (dễ bị dồn vào góc).
- Khu vực ngoài cổng trường, các quán nước/hẻm nhỏ đối diện đường giờ tan học.
- Cầu thang và hành lang lúc chuyển tiết hoặc sau khi tan học 15 phút.
2. Vùng an toàn tuyệt đối (Safe Zones) - Hướng dẫn học sinh chạy ngay đến:
- Tầng 1: Phòng Bảo vệ ngay cổng trường (có các bác bảo vệ trực 24/24).
- Tầng 1: Phòng Tổng phụ trách Đội (Thầy Đoàn Đình Thành - SĐT: 0905.659.995).
- Tầng 1: Phòng Y tế và Phòng Văn thư (có điện thoại hỗ trợ học sinh gọi người nhà).
- Tầng 2: Khu Hiệu bộ (Phòng Cô Hiệu trưởng Nguyễn Thị Thu Hà: 0905.654.888; Cô Phó HT Trần Thị Quế: 0983.225.126).
- Ngoài trường (Bảo vệ tính mạng khẩn cấp): Công an Phường Thanh Khê - SĐT: 0236.3714.677; Tổng đài Quốc gia Bảo vệ Trẻ em: 111.

IV. QUY TRÌNH XỬ LÝ TÌNH HUỐNG CHUẨN HÓA (SOP):
1. Kịch bản KHIÊU KHÍCH TRÊN MẠNG XÃ HỘI (Facebook, TikTok) DẪN ĐẾN HẸN ĐÁNH NHAU:
- Tuyệt đối KHÔNG nhận kèo, KHÔNG đôi co thách thức lại trên mạng.
- Chụp ảnh màn hình toàn bộ tin nhắn/bình luận đe dọa để lưu chứng cứ.
- Giờ tan học KHÔNG đi ra cổng một mình, KHÔNG đi vào các hẻm quán nước đối diện. Ở yên trong sân trường, vào Phòng Bảo vệ hoặc Phòng Văn thư tầng 1 báo ngay cho Thầy Thành TPT Đội hoặc nhờ gọi phụ huynh đến đón.
2. Kịch bản CHƠI GIỠN QUÁ TRỚN MẤT BÌNH TĨNH DẪN ĐẾN ĐÁNH NHAU TẠI CHỖ (Tình huống bộc phát nhanh):
- Đối với con là người trong cuộc: LẬP TỨC LÙI LẠI, giơ hai tay phòng thủ, KHÔNG tiếp tục lao vào đánh trả để tránh thương tích nặng hơn.
- Đối với con và các bạn xung quanh: HÔ TO THẬT LỚN để lôi kéo sự chú ý của mọi người cùng vào can ngăn; ĐỒNG THỜI CỬ NGAY 1 BẠN CHẠY ĐI BÁO THẦY CÔ gần nhất (Phòng Đội tầng 1 gặp Thầy Thành, phòng giáo viên hoặc bác bảo vệ trực cổng).
3. Kịch bản Trấn lột tiền / Cho vay nặng lãi (gấp đôi gấp ba):
- KHÔNG chống cự trực tiếp nếu đối phương đông người để tránh bị thương tích.
- Chụp màn hình tin nhắn đòi tiền/chứng cứ mượn tiền, KHÔNG chuyển thêm tiền.
- Báo riêng với Giáo viên chủ nhiệm lớp của con hoặc Thầy Thành TPT tại phòng Đoàn Đội tầng 1.
4. Kịch bản Áp lực điểm số / Sợ cha mẹ phạt:
- Thấu hiểu nỗi lo sợ và áp lực kỳ vọng của gia đình. Hướng dẫn cách chọn thời điểm nói chuyện chân thành (lúc bố mẹ vui vẻ, thong thả) và cách viết một bức thư tay ngắn gửi bố mẹ trước. Nếu có nguy cơ bạo lực thân thể, nhắc con nhớ số 111.

V. CẤU TRÚC PHẢN HỒI (BẮT BUỘC ĐỦ 3 PHẦN):
Xưng hô: "Cô" và "Con", dùng "Cô trò mình". Giọng điệu ấm áp, ân cần, bảo bọc:
[PHAN_1: THẤU HIỂU & GỌI TÊN CẢM XÚC]
(Đồng cảm chính xác với đúng sự việc học sinh đang gặp phải. Tuyệt đối không suy diễn chuyện ba mẹ đi biển nếu con không nhắc).
[PHAN_2: GÓC NHÌN ĐA CHIỀU]
(Tách bạch giá trị bản thân con khỏi lời đàm tiếu; phân tích nguyên nhân sự việc khách quan).
[PHAN_3: KẾ HOẠCH HÀNH ĐỘNG TẠI TRƯỜNG PHAN ĐÌNH PHÙNG]
(Dùng từ "Cô trò mình". Quy trình bước-theo-bước rõ ràng: hô hoán can ngăn, chỉ rõ chạy đến phòng nào ở tầng mấy, tìm gặp ai, câu nói mẫu để tự bảo vệ, số điện thoại khẩn cấp cần gọi).
"""

# ----------------- 3. GIAO DIỆN CHÍNH -----------------

# Nút khẩn cấp "VÒNG TAY CHE CHỞ"
with st.expander(
    "🆘 🛡️ VÒNG TAY CHE CHỞ (BẤM VÀO ĐÂY NẾU EM ĐANG GẶP NGUY HIỂM / BỊ ĐE DỌA"
    " KHẨN CẤP)",
    expanded=False,
):
  st.markdown(
      """
    <div style="background: white; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #ffccd2;">
        <h4 style="color: #c0392b; margin-top: 0; font-weight: 800;">🚨 HỖ TRỢ KHẨN CẤP DÀNH CHO HỌC SINH THCS PHAN ĐÌNH PHÙNG:</h4>
        <p style="color: #2d3436; font-size: 1rem;">Nếu con đang bị đe dọa đánh nhau, bị chặn đường ở cổng trường/nhà xe, hoặc xảy ra ẩu đả bộc phát, hãy gọi ngay cho Ban Giám Hiệu, Thầy Tổng Phụ Trách hoặc lực lượng chức năng:</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

  c1, c2, c3, c4 = st.columns(4)
  with c1:
    st.info(
        "📞 **Cô Hà (Hiệu trưởng):**\n"
        "**0905.654.888**\n*(Tầng 2 Khu Hiệu Bộ)*"
    )
  with c2:
    st.info(
        "📞 **Thầy Thành (TPT Đội):**\n"
        "**0905.659.995**\n*(Phòng Đoàn Đội Tầng 1)*"
    )
  with c3:
    st.info(
        "📞 **Công an P. Thanh Khê:**\n"
        "**0236.3714.677**\n*(Can thiệp chặn cổng/hung khí)*"
    )
  with c4:
    st.info(
        "📞 **Tổng đài Trẻ em 111:**\n"
        "**111**\n*(Bảo vệ bạo lực gia đình 24/7)*"
    )

  st.write("---")
  st.markdown("#### 🚨 Gửi tín hiệu báo nguy nhanh đến Thầy Cô trực ban:")
  with st.form("sos_form"):
    sos_loc = st.selectbox(
        "Con đang gặp nguy hiểm ở vị trí nào trong trường?",
        [
            "Đang xảy ra ẩu đả bộc phát ngay trong lớp / hành lang",
            "Khu vực ngoài cổng trường / Quán nước đối diện (giờ tan học)",
            "Nhà xe học sinh",
            "Khu vực nhà vệ sinh (WC tầng 1, 2 hoặc 3)",
            "Cầu thang dãy phòng học lúc chuyển tiết",
            "Vị trí khác",
        ],
    )
    sos_note = st.text_input(
        "Điều gì đang xảy ra? (Có thể ghi tên/lớp của con nếu muốn thầy cô đến"
        " đón con trực tiếp, hoặc để trống để ẩn danh):"
    )
    submit_sos = st.form_submit_button("🚨 GỬI TÍN HIỆU CẦU CỨU NGAY")
    if submit_sos:
      alert_data = {
          "time": datetime.now().strftime("%H:%M:%S ngày %d/%m/%Y"),
          "location": sos_loc,
          "content": sos_note if sos_note.strip() else "Yêu cầu hỗ trợ ẩn danh",
      }
      save_sos_alert(alert_data)
      st.success(
          "✅ Tín hiệu của con đã được gửi khẩn cấp! Nếu đang có xô xát: Con hãy"
          " HÔ TO để các bạn xung quanh cùng can ngăn và CỬ NGAY 1 BẠN chạy đi"
          " báo Thầy Thành (Phòng Đội tầng 1) hoặc Bác Bảo Vệ cổng trường ngay"
          " lập tức nhé!"
      )

# Header trang chủ & Mascot Cô Tư Phùng
col_mascot, col_welcome = st.columns([1, 4])
with col_mascot:
  if os.path.exists("mascot.png"):
    st.image("mascot.png", width=180)
  else:
    st.markdown("# 👩‍🏫")
    st.caption("**Cô Tư Phùng**")

with col_welcome:
  st.markdown("## 🌱 Góc Bình Yên Dưới Hiên Trường Phan Đình Phùng")
  st.markdown(
      "> *“Chào con thân yêu! Hôm nay ở trường thế nào? Có chuyện gì ở lớp, bạn"
      " bè hay trên mạng xã hội làm con bận lòng không? Cứ ngồi xuống đây kể cho"
      " Cô Tư Phùng nghe nhé, mọi chuyện rồi sẽ có cách giải quyết thôi...”*"
  )
  st.markdown(
      "🔒 **Cam kết bảo mật tuyệt đối:** *Ứng dụng không ghi nhận tên tuổi,"
      " không lưu danh tính, không gửi nội dung cho phụ huynh hay giáo viên bộ"
      " môn.*"
  )

# TRẠM DỪNG BÌNH TĨNH
with st.expander(
    "🌿 🧘 TRẠM DỪNG BÌNH TĨNH (Nhịp thở 4-7-8 & Hộp Xả Giận)", expanded=False
):
  tab_breath, tab_tear = st.tabs(["🌬️ Hít thở hạ hỏa 4-7-8", "🗑️ Viết rồi xé bỏ"])
  with tab_breath:
    st.write(
        "Nếu con đang rất bực bội, tim đập nhanh, hãy thở theo nhịp cùng Cô Tư"
        " Phùng để lấy lại bình tĩnh, tránh hành động bộc phát nhé:"
    )
    if st.button("Bắt đầu nhịp thở 4-7-8"):
      box = st.empty()
      for i in range(4, 0, -1):
        box.info(f"🌿 **HÍT VÀO** chậm rãi bằng mũi... ({i}s)")
        time.sleep(1)
      for i in range(7, 0, -1):
        box.warning(f"⏸️ **GIỮ HƠI** và thả lỏng đôi vai... ({i}s)")
        time.sleep(1)
      for i in range(8, 0, -1):
        box.success(f"💨 **THỞ RA** nhẹ nhàng bằng miệng... ({i}s)")
        time.sleep(1)
      box.info(
          "✨ Tuyệt vời lắm! Cơn giận đã nguôi bớt rồi, giờ cô trò mình cùng suy"
          " ngẫm cách giải quyết nhé."
      )
  with tab_tear:
    st.text_area(
        "Viết hết những lời bực bội vào đây:",
        placeholder="Con ghét bạn vì bạn trêu chọc con, gọi tên ba mẹ con...",
        key="tear_box",
    )
    if st.button("🔥 Xé bỏ & Thổi bay"):
      st.success(
          "Đã xé bỏ hoàn toàn! Con đã chọn cách giải tỏa văn minh thay vì gây gổ"
          " xích mích."
      )

st.markdown("---")

# ----------------- 4. KHÔNG GIAN LỰA CHỌN CẢM XÚC ĐẶC THÙ (NÚT PASTEL) -----------------
st.markdown("### 🌸 Hôm nay lòng em thấy thế nào? *(Bấm chọn nhanh tình huống)*")
col_e1, col_e2, col_e3, col_e4 = st.columns(4)

with col_e1:
  if st.button(
      "🌧️ Buồn & Bị cô lập\n\n(Bị nói xấu, tẩy chay)", use_container_width=True
  ):
    st.session_state["selected_emotion_prompt"] = (
        "Con đang rất buồn và tủi thân vì bị bạn bè cô lập, nói xấu sau lưng và"
        " không cho con chơi cùng trong lớp..."
    )
with col_e2:
  if st.button(
      "⚡ Ẩu đả / Đe dọa đánh nhau\n\n(Giỡn quá trớn, chặn cổng)",
      use_container_width=True,
  ):
    st.session_state["selected_emotion_prompt"] = (
        "Con và bạn đùa giỡn rồi mất kiểm soát sắp đánh nhau tại chỗ; hoặc con"
        " bị đe dọa chặn đường ở cổng trường lúc tan học..."
    )
with col_e3:
  if st.button(
      "🌐 Khiêu khích trên MXH\n\n(Bị bêu xấu trên Story/TikTok)",
      use_container_width=True,
  ):
    st.session_state["selected_emotion_prompt"] = (
        "Con cảm thấy kiệt sức vì bị lập nhóm chat bôi nhọ, khiêu khích hẹn ra"
        " cổng trường đánh nhau, đăng ảnh dìm lên TikTok/Facebook..."
    )
with col_e4:
  if st.button(
      "🌊 Áp lực gia đình & Điểm số\n\n(Lo sợ bị cha mẹ phạt)",
      use_container_width=True,
  ):
    st.session_state["selected_emotion_prompt"] = (
        "Con đang rất lo sợ và áp lực vì điểm thi kém, sợ cha mẹ sẽ mắng chửi"
        " hoặc đánh đòn..."
    )

# KHUNG NHẬP NỘI DUNG TÂM SỰ & CHỌN KHỐI LỚP (GIỮ NGUYÊN BỐ CỤC)
default_text = st.session_state.get("selected_emotion_prompt", "")
col_txt1, col_txt2, col_txt3 = st.columns([3, 1, 1])

with col_txt1:
  user_question = st.text_area(
      "Kể chi tiết hơn cho Cô Tư Phùng nghe nhé:",
      value=default_text,
      placeholder=(
          "Ví dụ: Bạn trong lớp hẹn tan học ra cổng trường 'tính sổ'; hoặc hai"
          " bạn trong lớp đang lao vào đánh nhau..."
      ),
      height=120,
      key="user_msg_input",
  )
with col_txt2:
  selected_grade = st.selectbox(
      "Em đang học khối:", ["Khối 6", "Khối 7", "Khối 8", "Khối 9"]
  )
with col_txt3:
  selected_topic = st.selectbox(
      "Vấn đề liên quan:",
      [
          "Mâu thuẫn / Tẩy chay trong lớp",
          "Đánh nhau bộc phát / Chặn cổng trường",
          "Khiêu khích trên MXH (FB/TikTok)",
          "Trấn lột / Vay nặng lãi học sinh",
          "Áp lực điểm số & Gia đình đi biển",
          "Bất an về bản thân / Khác",
      ],
  )

# HÀM GỌI API GEMINI
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get(
    "GEMINI_API_KEY", ""
)
client = genai.Client(api_key=api_key) if api_key else None

CANDIDATE_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
]

# Giữ lượt đầu (bối cảnh gốc) + tối đa 16 tin nhắn gần nhất để không vượt giới hạn
MAX_RECENT_MESSAGES = 16

FOLLOW_UP_REMINDER = (
    "\n\n(GHI CHÚ HỆ THỐNG CHO CÔ TƯ PHÙNG - học sinh không nhìn thấy dòng này:"
    " Đây là lời học sinh nói tiếp trong CÙNG câu chuyện ở trên. Hãy nhớ và nối"
    " tiếp những gì cô trò mình đã nói, không lặp lại nguyên văn lời khuyên cũ."
    " Trả lời tự nhiên, ngắn gọn, ấm áp như đang trò chuyện; KHÔNG cần chia 3"
    " phần [PHAN_1]/[PHAN_2]/[PHAN_3]. Xưng 'Cô' - gọi 'Con' (dùng 'Cô trò"
    " mình'). Chỉ rõ từng bước giữ bí mật, an toàn cho con. Không tự ý nhắc"
    " chuyện ba mẹ đi biển nếu con không nhắc. Nếu có dấu hiệu nguy hiểm (đánh"
    " nhau, bị đe dọa, tự làm hại bản thân) phải hướng dẫn ngay SOP: báo thầy"
    " Thành/bác bảo vệ/người lớn tin cậy ngay lập tức.)"
)


# [SỬA] Tên nhóm vấn đề GỬI CHO AI (giao diện & thống kê vẫn giữ tên cũ).
# Bỏ chữ "đi biển" để AI không mặc định ba mẹ con đi biển khi con chọn nhóm này.
TOPIC_LABEL_FOR_AI = {
    "Áp lực điểm số & Gia đình đi biển": "Áp lực điểm số / gia đình",
}


def build_first_turn(prompt, grade, topic):
  """Gói lời tâm sự đầu tiên kèm bối cảnh và yêu cầu trả lời 3 phần."""
  topic = TOPIC_LABEL_FOR_AI.get(topic, topic)
  return (
      f"HỌC SINH THCS PHAN ĐÌNH PHÙNG ({grade.upper()}):\n"
      f"- Nhóm vấn đề: {topic}\n"
      f"- Lời tâm sự: {prompt}\n\n"
      "YÊU CẦU BẮT BUỘC:\n"
      "- Xưng 'Cô' (hoặc 'Cô Tư Phùng'), gọi học sinh là 'Con', dùng 'Cô trò"
      " mình' khi phối hợp hành động. Tuyệt đối KHÔNG dùng 'cô cháu', 'em'.\n"
      "- CHỈ nhắc đến ba mẹ đi biển/ra khơi khi chính lời tâm sự của con có"
      " nhắc đến chuyện đó. Chọn nhóm áp lực điểm số/gia đình KHÔNG có nghĩa là"
      " ba mẹ con đi biển. Nếu lời tâm sự không nhắc, tuyệt đối không nói đến"
      " chuyện đi biển; chỉ tập trung đúng vào điều con kể.\n"
      "- Phản hồi đúng 3 phần: [PHAN_1: THẤU HIỂU & GỌI TÊN CẢM XÚC], [PHAN_2:"
      " GÓC NHÌN ĐA CHIỀU], [PHAN_3: KẾ HOẠCH HÀNH ĐỘNG TẠI TRƯỜNG PHAN ĐÌNH"
      " PHÙNG]. Nếu là tình huống đánh nhau bộc phát hoặc khiêu khích MXH, hãy"
      " chỉ dẫn ngay SOP: hô hoán can ngăn, cử bạn đi báo thầy Thành/bác bảo vệ"
      " ngay lập tức."
  )


def history_to_contents(history):
  """Đổi chat_history thành danh sách lượt hội thoại đúng chuẩn Gemini.

  Mỗi tin nhắn có 'text' (hiển thị cho học sinh) và có thể có 'api_text'
  (nội dung thật gửi cho AI, kèm bối cảnh/ghi chú hệ thống).
  """
  if len(history) > 2 + MAX_RECENT_MESSAGES:
    history = history[:2] + history[-MAX_RECENT_MESSAGES:]
  return [
      {"role": m["role"], "parts": [{"text": m.get("api_text", m["text"])}]}
      for m in history
  ]


# Mức suy nghĩ của AI: None = để model tự dùng mặc định (suy nghĩ CAO, trả lời
# chu đáo nhất nhưng chậm hơn). Có thể đổi thành "low" nếu cần nhanh hơn.
THINKING_LEVEL = None


def _gen_config(use_thinking):
  cfg = {
      "system_instruction": SYSTEM_PROMPT,
      "max_output_tokens": 2500,
      "temperature": 0.5,
  }
  if use_thinking and THINKING_LEVEL:
    cfg["thinking_config"] = {"thinking_level": THINKING_LEVEL}
  return cfg


def get_ai_reply(history, placeholder=None):
  """Gửi TOÀN BỘ cuộc trò chuyện cho AI để cô nhớ mọi lượt trước đó.

  [TĂNG TỐC] Nếu có placeholder, chữ của cô hiện dần ngay khi AI vừa viết
  (không phải chờ viết xong cả bài mới thấy).
  """
  contents = history_to_contents(history)
  last_error = None
  for m in CANDIDATE_MODELS:
    for use_thinking in (True, False):
      text = ""
      try:
        stream = client.models.generate_content_stream(
            model=m, contents=contents, config=_gen_config(use_thinking)
        )
        for chunk in stream:
          piece = getattr(chunk, "text", None)
          if piece:
            text += piece
            if placeholder is not None:
              placeholder.markdown(clean_reply(text) + " ▌")
        if text:
          return text, None
        last_error = "AI không trả lời"
        break  # model trả rỗng -> thử model khác
      except Exception as e:
        if text:
          return text, None  # đứt giữa chừng: giữ phần cô đã viết
        last_error = e
        if use_thinking and "thinking" in str(e).lower():
          continue  # model không hỗ trợ mức suy nghĩ -> gọi lại không kèm
        time.sleep(0.5)
        break
  return None, last_error or "AI không trả lời"


def clean_reply(text):
  """Bỏ các nhãn [PHAN_x: ...] nếu AI lỡ dùng trong lượt trò chuyện tiếp nối."""
  for tag in (
      "[PHAN_1: THẤU HIỂU & GỌI TÊN CẢM XÚC]",
      "[PHAN_2: GÓC NHÌN ĐA CHIỀU]",
      "[PHAN_3: KẾ HOẠCH HÀNH ĐỘNG TẠI TRƯỜNG PHAN ĐÌNH PHÙNG]",
  ):
    text = text.replace(tag, "")
  return text.strip()


def start_new_story():
  """Xóa sạch cuộc trò chuyện hiện tại để con kể một câu chuyện mới."""
  st.session_state["chat_history"] = []
  st.session_state["raw_response"] = ""
  st.session_state["has_new_reply"] = False
  st.session_state["feedback"] = None
  st.session_state["selected_emotion_prompt"] = ""
  # Xóa nội dung đã gõ trong các ô nhập (chạy trước khi ô được vẽ lại)
  st.session_state.pop("user_msg_input", None)
  st.session_state["fu_counter"] = st.session_state.get("fu_counter", 0) + 1


# NÚT GỬI TÂM SỰ
if st.button("💌 Gửi gắm tâm sự cùng Cô Tư Phùng", type="primary"):
  if not user_question.strip():
    st.warning("Con hãy chia sẻ một chút điều đang làm con bận lòng nhé.")
  elif not client:
    st.error("Chưa kết nối được API Key trên Streamlit Cloud Secrets.")
  else:
    first_turn = {
        "role": "user",
        "text": user_question,
        "api_text": build_first_turn(
            user_question, selected_grade, selected_topic
        ),
    }
    live_box = st.empty()
    live_box.info("🌱 Cô Tư Phùng đang lắng nghe và suy ngẫm cùng con...")
    reply, err = get_ai_reply([first_turn], placeholder=live_box)
    live_box.empty()  # xong thì xóa bản nháp, hiện lại gọn trong 3 tab bên dưới
    if reply:
      # Đồng bộ tăng số lượng vào Google Sheet
      sync_to_sheet("total_questions")
      sync_to_sheet(TOPIC_KEY_MAP.get(selected_topic, "topic_6"))

      # Cập nhật tạm thời cho lượt xem hiện tại
      stats["total_questions"] += 1
      stats["topics"][selected_topic] = (
          stats["topics"].get(selected_topic, 0) + 1
      )

      # Gửi tâm sự mới = bắt đầu một câu chuyện mới
      st.session_state["chat_history"] = [
          first_turn,
          {"role": "model", "text": reply},
      ]
      st.session_state["raw_response"] = reply
      st.session_state["has_new_reply"] = True
      st.session_state["feedback"] = None
    else:
      st.error(
          "Hệ thống đang nhiều bạn truy cập cùng lúc, con bấm gửi lại sau 3"
          f" giây nhé! (Lỗi: {err})"
      )

# HIỂN THỊ PHẢN HỒI GÓC NHÌN 3 CHIỀU TỪ CÔ TƯ PHÙNG
if st.session_state.get("has_new_reply", False):
  reply_text = st.session_state.get("raw_response", "")
  st.markdown("### 💬 Lời gửi gắm yêu thương từ Cô Tư Phùng:")

  part1, part2, part3 = "", "", ""
  if "[PHAN_1:" in reply_text and "[PHAN_2:" in reply_text:
    try:
      p1_split = reply_text.split("[PHAN_1:")[1]
      part1 = (
          p1_split.split("[PHAN_2:")[0]
          .replace("THẤU HIỂU & GỌI TÊN CẢM XÚC]", "")
          .strip()
      )
      if "[PHAN_3:" in p1_split:
        p2_split = p1_split.split("[PHAN_2:")[1]
        part2 = (
            p2_split.split("[PHAN_3:")[0]
            .replace("GÓC NHÌN ĐA CHIỀU]", "")
            .strip()
        )
        part3 = (
            p2_split.split("[PHAN_3:")[1]
            .replace("KẾ HOẠCH HÀNH ĐỘNG TẠI TRƯỜNG PHAN ĐÌNH PHÙNG]", "")
            .strip()
        )
      else:
        part2 = (
            p1_split.split("[PHAN_2:")[1]
            .replace("GÓC NHÌN ĐA CHIỀU]", "")
            .strip()
        )
    except Exception:
      part1 = reply_text
  else:
    part1 = reply_text

  if part1 and part2:
    ans_tab1, ans_tab2, ans_tab3 = st.tabs([
        "❤️ 1. Thấu hiểu cảm xúc",
        "🔍 2. Góc nhìn đa chiều",
        "🧭 3. Kế hoạch hành động tại trường",
    ])
    with ans_tab1:
      st.markdown(part1)
    with ans_tab2:
      st.markdown(part2 if part2 else "Đang cập nhật...")
    with ans_tab3:
      st.markdown(part3 if part3 else "Đang cập nhật...")
  else:
    st.markdown(reply_text)

  # CÁC LƯỢT TRÒ CHUYỆN TIẾP NỐI (hiện TRƯỚC ô nhập, giống khung chat)
  history = st.session_state["chat_history"]
  if len(history) > 2:
    st.subheader("🗨️ Cuộc trò chuyện tiếp nối cùng Cô Tư Phùng:")
    for msg in history[2:]:
      if msg["role"] == "user":
        with st.chat_message("user"):
          st.write(msg["text"])
      else:
        with st.chat_message("assistant", avatar="🌱"):
          st.markdown(clean_reply(msg["text"]))

  # Ô TÂM SỰ TIẾP NỐI: LUÔN HIỆN sau khi cô đã trả lời, dù con bấm 👍, 👎
  # hay không bấm gì. Ô chỉ được xóa khi gửi THÀNH CÔNG (lỗi mạng thì chữ
  # của con vẫn còn để gửi lại).
  fu_key = f"fu_text_{st.session_state.get('fu_counter', 0)}"
  with st.form("follow_up_form"):
    follow_up_msg = st.text_area(
        "💬 Con muốn kể thêm hay hỏi tiếp cô điều gì?",
        placeholder=(
            "Ví dụ: Nhưng cô ơi nếu con báo thầy Thành thì bạn biết bạn lại"
            " chặn đánh con thì sao ạ?"
        ),
        key=fu_key,
    )
    send_follow_up = st.form_submit_button("Gửi tâm sự tiếp nối cho cô 💬")

  if send_follow_up:
    if not follow_up_msg.strip():
      st.warning("Con ghi thêm câu hỏi nhé.")
    elif not client:
      st.error("Chưa kết nối được API Key trên Streamlit Cloud Secrets.")
    else:
      new_turn = {
          "role": "user",
          "text": follow_up_msg,
          "api_text": follow_up_msg + FOLLOW_UP_REMINDER,
      }
      with st.chat_message("user"):
        st.write(follow_up_msg)
      with st.chat_message("assistant", avatar="🌱"):
        live_fu = st.empty()
        live_fu.markdown("*Cô đang đọc tiếp tâm sự của con...*")
        # Gửi TOÀN BỘ lịch sử + câu mới để cô không "quên" các lượt trước
        sub_reply, sub_err = get_ai_reply(history + [new_turn], placeholder=live_fu)
      if sub_reply:
        history.append(new_turn)
        history.append({"role": "model", "text": sub_reply})
        # Đổi key để ô nhập trống trở lại
        st.session_state["fu_counter"] = (
            st.session_state.get("fu_counter", 0) + 1
        )
        st.rerun()  # vẽ lại để lượt mới hiện ngay trong khung chat
      else:
        st.error(
            "Cô chưa nhận được tin của con, con bấm gửi lại sau vài giây nhé!"
            f" (Lỗi: {sub_err})"
        )

  # NÚT BẮT ĐẦU CÂU CHUYỆN MỚI (không cần tải lại trang)
  st.divider()
  st.button(
      "🌱 Bắt đầu câu chuyện mới",
      on_click=start_new_story,
      help="Xóa cuộc trò chuyện này để kể với cô một chuyện khác.",
      use_container_width=True,
  )

  # KHẢO SÁT HỮU ÍCH - ĐẶT DƯỚI CÙNG APP (chỉ để thống kê, không khóa phần trò chuyện)
  st.divider()
  feedback = st.session_state.get("feedback")
  if feedback is None:
    st.write("**Lời dặn dò của Cô Tư Phùng có giúp con nhẹ lòng hơn chưa?**")
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
      if st.button("👍 Dạ rồi, con đã thấy nhẹ lòng và bình tĩnh hơn"):
        sync_to_sheet("helpful_yes")
        stats["helpful_yes"] += 1
        st.session_state["feedback"] = "yes"
        feedback = "yes"
    with c_btn2:
      if st.button("👎 Con vẫn còn thấy lo lắng và bối rối..."):
        sync_to_sheet("helpful_no")
        stats["helpful_no"] += 1
        st.session_state["feedback"] = "no"
        feedback = "no"

  if feedback == "yes":
    st.success(
        "Thương con! Cố lên nhé, cô luôn ở bên cạnh đồng hành cùng con. Nếu"
        " còn điều gì muốn kể thêm, con cứ viết tiếp vào ô phía trên nhé."
    )
  elif feedback == "no":
    st.info(
        "💡 **Đừng giữ trong lòng một mình nhé!** Con muốn cô giải thích rõ hơn"
        " ở điểm nào, hoặc con sợ điều gì khi làm theo hướng dẫn? Con viết tiếp"
        " vào ô phía trên cho cô nha."
    )

# ----------------- 5. SIDEBAR: THỐNG KÊ & KHU VỰC DÀNH CHO THẦY CÔ -----------------
with st.sidebar:
  st.header("📊 Bức Tranh Hoạt Động")
  st.caption("Dữ liệu ẩn danh phục vụ công tác tâm lý trường học.")

  st.metric("Tổng lượt học sinh chia sẻ", stats["total_questions"])
  total_fb = stats["helpful_yes"] + stats["helpful_no"]
  rate = (stats["helpful_yes"] / total_fb * 100) if total_fb > 0 else 0
  st.metric("Tỷ lệ cảm thấy nhẹ lòng", f"{rate:.1f}%")

  st.divider()
  st.subheader("📌 Nhóm vấn đề học sinh bận lòng")
  st.bar_chart(stats.get("topics", {}))

  st.divider()
  with st.expander("🔒 Khu vực Giáo viên / Ban Giám Hiệu"):
    admin_pw = st.text_input("Nhập mật khẩu quản trị:", type="password")
    if admin_pw == "pdp2026":
      st.success("Xác thực thành công!")
      st.write("📋 **Danh sách các tín hiệu SOS khẩn cấp:**")
      alerts = load_sos_alerts()
      if not alerts:
        st.info("Hiện chưa có tín hiệu báo nguy nào.")
      else:
        for idx, a in enumerate(alerts):
          st.warning(
              f"**[{a['time']}]**\n- Vị trí: **{a['location']}**\n- Nội dung:"
              f" {a['content']}"
          )
    elif admin_pw:
      st.error("Mật khẩu không đúng!")
