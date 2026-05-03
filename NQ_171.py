import os, re, smtplib, feedparser, markdown, pytz
from datetime import datetime
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_real_estate_news():
    """Lọc nguồn tin tinh hoa: Chỉ lấy tin Chính phủ và Pháp lý dự án"""
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
            for entry in feed.entries[:6]: # Chỉ lấy top 6 tin nóng nhất
                desc = re.sub('<[^<]+>', '', entry.get('summary', ''))
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {desc[:350]}...\nLink: {entry.link}\n\n"
        except: continue
    return summary

def get_ai_report(news_data):
    """LÕI TƯ DUY: SENIOR LEGAL ADVISOR (NQ 171 SPECIALIST)"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Thiếu API Key."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    # --- PROMPT CHIẾN LƯỢC (THE MASTER PROMPT) ---
    prompt = f"""
    CONTEXT: Today is {current_time}. You are the Senior Legal Advisor to expert Vũ Quang Phát.
    ROLE: A high-level legal peer, not a student or a robot. 
    CORE FOCUS: NQ 171/2024/QH15 (Pilot mechanism for land assembly in housing projects).
    
    STRICT GUIDELINES:
    1. NO META-TALK: Do NOT mention "I have filtered news", "Based on your rules", or "I checked the laws". Jump straight into the strategy.
    2. NO DICTIONARY: Use professional terms (Project, Ownership, Sales, Holding cost) naturally. Do NOT explain them.
    3. LEGAL ACCURACY: 
       - Land Law 2024, Housing Law 2023, RE Business Law 2023: All effective from 01/08/2024 (Standard for 21 months).
       - NQ 171/2024/QH15: The primary tool for Land Acquisition.
    
    REPORT STRUCTURE:
    - EXECUTIVE SUMMARY: Identify the most critical project risk/opportunity from news.
    - STRATEGIC ANALYSIS (IRAC): 
        + Issue: Locate the bottleneck in the Project lifecycle (Survey to Sales).
        + Rule & Reality: Interlink NQ 171 with Land Law 2024 and Decree 102/2024.
        + Application: Analyze the impact on cost and timeline at HCMC departments (Sở Nông nghiệp và Môi trường, Sở Tài chính).
    - 1:1 ACTION PLAN: Precise steps for Vũ Quang Phát to execute (e.g., specific negotiation points, land-split tactics).
    
    INPUT DATA: {news_data}
    """

    try:
        # Tự động quét chọn model cao cấp nhất sẵn có
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        best_model = next((m for m in models if "pro" in m), models[0])
        
        model = genai.GenerativeModel(best_model)
        response = model.generate_content(prompt)
        report = response.text
                
        # Firewall Python cưỡng chế thuật ngữ hành chính hậu 2025
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "tỉnh Bình Dương": "TP.HCM", "tỉnh Bà Rịa": "TP.HCM"
        }
        for old, new in replacements.items():
            report = re.compile(re.escape(old), re.IGNORECASE).sub(new, report)
        return report
    except Exception as e: return f"Error: {str(e)}"

def send_email(markdown_content):
    """Email Executive Style: Tinh gọn và Quyền lực"""
    sender = "phat.clover@gmail.com"
    msg = MIMEMultipart()
    msg["Subject"] = f"[TOP PRIORITY] LEGAL STRATEGY REPORT #{datetime.now().strftime('%d%m')}"
    msg["From"] = f"Senior Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'tables'])
    full_html = f"""
    <div style="font-family: 'Times New Roman', serif; max-width: 850px; margin: auto; border-top: 8px solid #002D62; padding: 40px; color: #1a1a1a;">
        <h1 style="color: #002D62; text-align: center;">MEMO: CHIẾN LƯỢC DỰ ÁN BĐS</h1>
        <p style="text-align: center; border-bottom: 1px solid #eee; padding-bottom: 20px;">Strictly Confidential | For: Vũ Quang Phát</p>
        <div style="line-height: 1.8; text-align: justify;">{html_body}</div>
        <div style="margin-top: 50px; text-align: center; font-size: 11px; color: #888;">AI Strategic Advisor System | Gemini Pro Core</div>
    </div>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, os.environ.get('GMAIL_PASSWORD'))
            server.sendmail(sender, sender, msg.as_string())
        print("Báo cáo tham mưu đã được gửi trực tiếp.")
    except Exception as e: print(f"Email Error: {e}")

if __name__ == "__main__":
    news = get_real_estate_news()
    report = get_ai_report(news)
    send_email(report)
