import os, re, smtplib, feedparser, markdown, pytz
from datetime import datetime
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_real_estate_news():
    """Lọc nguồn tin tinh hoa pháp lý"""
    sources = {
        "Chính phủ - Pháp luật": "https://baochinhphu.vn/rss/phap-luat.rss",
        "Báo Đấu Thầu - Dự án": "https://baodauthau.vn/rss/phap-luat-16.rss",
        "Công Báo": "https://congbao.chinhphu.vn/rss"
    }
    summary = ""
    for cat, url in sources.items():
        try:
            feed = feedparser.parse(url)
            summary += f"\n--- {cat.upper()} ---\n"
            for entry in feed.entries[:6]:
                desc = re.sub('<[^<]+>', '', entry.get('summary', ''))
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {desc[:350]}...\nLink: {entry.link}\n\n"
        except: continue
    return summary

def get_ai_report(news_data, project_status):
    """LÕI TƯ DUY V13: TỰ ĐỘNG KHẮC PHỤC LỖI 404 & SEARCH THỜI GIAN THỰC"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Thiếu API Key."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    # PROMPT ÉP AI PHẢI TỰ KIỂM CHỨNG LẠI KIẾN THỨC CŨ
    prompt = f"""
    CONTEXT: Today is {current_time}. Bạn là Senior Legal Advisor cho chuyên gia Vũ Quang Phát.
    
    MANDATORY GROUNDING RULES:
    - SỬ DỤNG GOOGLE SEARCH để xác nhận: Luật số 43/2024/QH15 đã đẩy hiệu lực Luật Đất đai, Nhà ở, Kinh doanh BĐS lên ngày 01/08/2024. 
    - TUYỆT ĐỐI KHÔNG sử dụng mốc 01/01/2025.
    - XÁC THỰC tên các đơn vị hậu sáp nhập 2026 tại TP.HCM: Sở Nông nghiệp và Môi trường, Sở Tài chính.
    - NQ 171: Áp dụng cơ chế thí điểm NQ 171/2024/QH15 cho các dự án nhà ở thương mại.

    PROJECT CONTEXT: {project_status}
    NEWS DATA: {news_data}

    CẤU TRÚC BÁO CÁO (IRAC):
    - [I] ISSUE: Phân tích điểm nóng ảnh hưởng đến danh mục dự án thực tế.
    - [R] RULE & REALITY: Dẫn luật (mốc 01/08/2024) + Phân tích 'Ý đồ nhà lập pháp' & 'Hệ quả thực tế'.
    - [A] APPLICATION: Quy trình cụ thể tại các Sở hậu sáp nhập.
    - [C] CONCLUSION: Action Plan 1:1 cho chủ nhân với deadline cụ thể.
    """

    final_report = "AI Generation Failed."
    try:
        # TỰ ĐỘNG TÌM ĐÚNG MODEL ĐỂ TRÁNH LỖI 404
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_id = next((m for m in available_models if 'flash' in m), "gemini-1.5-flash")
        
        try:
            # Thử chạy có Search[cite: 1]
            model = genai.GenerativeModel(model_name=model_id, tools=[{"google_search_retrieval": {}}])
            response = model.generate_content(prompt)
            final_report = response.text
        except:
            # Fallback nếu Search bị chặn trên Free Tier[cite: 1]
            model = genai.GenerativeModel(model_name=model_id)
            response = model.generate_content(prompt)
            final_report = response.text + "\n\n*(Lưu ý: Báo cáo dựa trên dữ liệu sẵn có, không dùng Google Search do giới hạn API)*"
            
        return final_report
    except Exception as e: return f"Lỗi hệ thống nghiêm trọng: {str(e)}"

def send_email(markdown_content):
    """Email Executive Style: Chữ to rõ (18px), Scannable"""
    sender = "phat.clover@gmail.com"
    msg = MIMEMultipart()
    msg["Subject"] = f"[TOP PRIORITY] THAM MƯU PHÁP LÝ & NQ 171 - #{datetime.now().strftime('%d%m')}"
    msg["From"] = f"Senior Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'tables'])
    full_html = f"""
    <div style="font-family: 'Times New Roman', serif; max-width: 850px; margin: auto; border-top: 12px solid #002D62; padding: 50px; color: #1a1a1a; line-height: 1.8;">
        <h1 style="color: #002D62; text-align: center; font-size: 28px; text-transform: uppercase;">BÁO CÁO THAM MƯU PHÁP LÝ TUẦN</h1>
        <p style="text-align: center; border-bottom: 2px solid #eee; padding-bottom: 20px; font-style: italic;">Strictly Confidential | For: Vũ Quang Phát</p>
        <div style="font-size: 18px; text-align: justify;">{html_body}</div>
        <div style="margin-top: 60px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; font-size: 12px; color: #777;">
            AI Strategic Advisor System | Gemini V13 Grounded | 2026 Compliance
        </div>
    </div>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, os.environ.get('GMAIL_PASSWORD'))
            server.sendmail(sender, sender, msg.as_string())
        print("[+] Báo cáo đã được gửi thành công.")
    except Exception as e: print(f"[-] Email Error: {e}")

if __name__ == "__main__":
    # --- DANH MỤC DỰ ÁN THỰC TẾ ---
    REAL_PROJECT_STATUS = """
    - DA Hung Thinh: Nghẽn thẩm định giá đất (thặng dư) tại Sở Tài chính TP.HCM.
    - DA Saigonres: Vướng chuyển đổi 2ha đất nông nghiệp sang đất ở theo NQ 171/2024/QH15.
    - DA Hoa Sen: Khảo sát đấu giá tại Long An và Tiền Giang.
    """
    news = get_real_estate_news()
    report = get_ai_report(news, REAL_PROJECT_STATUS)
    send_email(report)
