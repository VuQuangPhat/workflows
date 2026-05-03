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
    """LÕI TƯ DUY V14: KHẮC PHỤC LỖI QUOTA (429) & CHUẨN HÓA TRI THỨC"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Thiếu API Key."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    # MASTER PROMPT: Tích hợp sẵn tri thức để AI không bị lệ thuộc hoàn toàn vào Search
    prompt = f"""
    CONTEXT: Today is {current_time}. Bạn là Senior Legal Advisor cho Vũ Quang Phát.
    
    LUẬT ĐỊNH HIỆN HÀNH (TRUTH DATA):
    - Hiệu lực: Luật số 43/2024/QH15 khẳng định Luật Đất đai, Nhà ở, Kinh doanh BĐS có hiệu lực từ 01/08/2024.
    - Cơ quan: Tại TP.HCM năm 2026, sử dụng 'Sở Nông nghiệp và Môi trường' và 'Sở Tài chính'.
    - Cơ chế: Tập trung vào NQ 171/2024/QH15 (Thí điểm thỏa thuận nhận quyền SDĐ).

    YÊU CẦU BÁO CÁO (IRAC):
    1. ISSUE: Soi chiếu TIN TỨC với dự án thực tế: {project_status}.
    2. RULE & REALITY: Phân tích 'Ý đồ nhà lập pháp' (triệt tiêu địa tô) & 'Hệ quả thực tế' (thận trọng thẩm định).
    3. APPLICATION: Quy trình tích hợp tại Sở Nông nghiệp và Môi trường cho NQ 171.
    4. ACTION PLAN: Giải pháp 1:1 cho Vũ Quang Phát kèm deadline.
    """

    try:
        # Tự động tìm model khả dụng để tránh lỗi 404
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_id = next((m for m in available_models if 'flash' in m), "gemini-1.5-flash")
        
        model = genai.GenerativeModel(
            model_name=model_id,
            tools=[{"google_search_retrieval": {}}]
        )
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        if "429" in str(e):
            return "THÔNG BÁO: Tài khoản Free Tier của bạn đã hết hạn mức 20 requests/ngày. Vui lòng thử lại sau hoặc nâng cấp API key."
        return f"Lỗi hệ thống: {str(e)}"

def send_email(markdown_content):
    """UI/UX: Chữ to rõ (18px), Scannable, Đẳng cấp Senior"""
    sender = "phat.clover@gmail.com"
    msg = MIMEMultipart()
    msg["Subject"] = f"[TOP PRIORITY] LEGAL STRATEGY REPORT - #{datetime.now().strftime('%d%m')}"
    msg["From"] = f"Senior Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'tables'])
    full_html = f"""
    <div style="font-family: 'Times New Roman', serif; max-width: 850px; margin: auto; border-top: 12px solid #002D62; padding: 50px; color: #1a1a1a; line-height: 1.8;">
        <h1 style="color: #002D62; text-align: center; font-size: 28px;">BÁO CÁO THAM MƯU PHÁP LÝ TUẦN</h1>
        <p style="text-align: center; border-bottom: 2px solid #eee; padding-bottom: 20px; font-style: italic;">Strictly Confidential | For: Vũ Quang Phát</p>
        <div style="font-size: 18px; text-align: justify;">{html_body}</div>
        <div style="margin-top: 60px; text-align: center; font-size: 11px; color: #888;">
            AI Strategic Advisor | V14 Anti-Quota | 2026 Compliance Framework
        </div>
    </div>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, os.environ.get('GMAIL_PASSWORD'))
            server.sendmail(sender, sender, msg.as_string())
        print("[+] Báo cáo đã gửi.")
    except Exception as e: print(f"[-] Email Error: {e}")

if __name__ == "__main__":
    REAL_PROJECT_STATUS = """
    - DA Hung Thinh: Nghẽn thẩm định giá (thặng dư) tại Sở Tài chính TP.HCM.
    - DA Saigonres: Vướng chuyển đổi đất nông nghiệp theo NQ 171/2024/QH15.
    - DA Hoa Sen: Khảo sát đấu giá tại Long An, Tiền Giang.
    """
    news = get_real_estate_news()
    report = get_ai_report(news, REAL_PROJECT_STATUS)
    send_email(report)
