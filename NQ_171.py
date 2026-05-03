import os, re, smtplib, feedparser, markdown, pytz
from datetime import datetime
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_real_estate_news():
    """Lọc nguồn tin: Chỉ lấy các biến động về Pháp lý & Dự án đầu tư"""
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
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {desc[:400]}...\nLink: {entry.link}\n\n"
        except: continue
    return summary

def get_ai_report(news_data):
    """Lõi tư duy Cố vấn cấp cao: Tự động dò tìm Model khả dụng"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    # --- PROMPT CHIẾN LƯỢC: NQ 171 & QUY TRÌNH 11 BƯỚC ---
    prompt = f"""
    CONTEXT: Today is {current_time}. You are the Senior Legal Advisor to expert Vũ Quang Phát.
    ROLE: High-level peer. Focus strictly on Project lifecycle (Step 1 to 11).
    
    INTERNAL KNOWLEDGE:
    - NQ 171/2024/QH15: Pilot mechanism for land assembly (Gom đất).
    - 11-STEP PROCESS: From Survey (Step 1) to Sales (Step 11).
    
    STRICT COMMANDS:
    1. NO META-TALK: Do NOT say "I found models" or "I filtered news". Jump into the strategy.
    2. NO EXPLANATIONS: Use terms like Project, Permit, Sales, Holding cost naturally.
    3. POSITIONING: Identify which Step (1-11) is impacted by today's news.
    4. ACTION PLAN: Provide 1:1 strategic steps for Vũ Quang Phát.

    DATA: {news_data}
    """

    try:
        # CHIẾN THUẬT TỰ PHỤC HỒI: Dò tìm mọi model có hỗ trợ generateContent
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Sắp xếp ưu tiên: Flash (để tránh 429), rồi mới đến Pro
        priority_models = sorted(available_models, key=lambda x: (0 if 'flash' in x else 1))
        
        report_text = "Không thể kết nối với bất kỳ trí tuệ nhân tạo nào."
        for model_name in priority_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                report_text = response.text
                break # Thành công thì dừng lại
            except Exception as e:
                if "429" in str(e) or "404" in str(e): continue
                else: return f"Lỗi nghiêm trọng: {str(e)}"

        # Firewall hành chính TP.HCM 2026
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "tỉnh Bình Dương": "TP.HCM", "tỉnh Bà Rịa": "TP.HCM"
        }
        for old, new in replacements.items():
            report_text = re.compile(re.escape(old), re.IGNORECASE).sub(new, report_text)
        return report_text
    except Exception as e: return f"System Error: {str(e)}"

def send_email(markdown_content):
    """Giao diện Memo Executive: Đẳng cấp và Tinh gọn"""
    sender = "phat.clover@gmail.com"
    msg = MIMEMultipart()
    msg["Subject"] = f"[TOP PRIORITY] THAM MƯU CHIẾN LƯỢC DỰ ÁN #{datetime.now().strftime('%d%m')}"
    msg["From"] = f"Senior Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'tables'])
    full_html = f"""
    <div style="font-family: 'Times New Roman', serif; max-width: 800px; margin: auto; border-top: 10px solid #002D62; padding: 40px; background: #fff;">
        <h1 style="color: #002D62; text-align: center; text-transform: uppercase;">Memo: Tham mưu dự án BĐS</h1>
        <p style="text-align: center; border-bottom: 1px solid #eee; padding-bottom: 20px;">Strictly Confidential | For: Vũ Quang Phát</p>
        <div style="line-height: 1.8; font-size: 16px; text-align: justify;">{html_body}</div>
        <div style="margin-top: 50px; text-align: center; font-size: 11px; color: #999; border-top: 1px solid #eee; padding-top: 20px;">
            Hệ thống Cố vấn Chiến lược | Nền tảng NQ 171 & Quy trình 11 bước.
        </div>
    </div>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, os.environ.get('GMAIL_PASSWORD'))
            server.sendmail(sender, sender, msg.as_string())
        print("Báo cáo chiến lược đã được gửi.")
    except Exception as e: print(f"Email Error: {e}")

if __name__ == "__main__":
    news = get_real_estate_news()
    report = get_ai_report(news)
    send_email(report)
