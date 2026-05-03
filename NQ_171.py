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
    LANGUAGE: Vietnamese (TOÀN BỘ BÁO CÁO PHẢI VIẾT BẰNG TIẾNG VIỆT CHUYÊN NGÀNH PHÁP LÝ TẠI VIỆT NAM).
    CORE FOCUS: NQ 171/2024/QH15 (Cơ chế thí điểm thực hiện dự án nhà ở thương mại thông qua thỏa thuận về nhận quyền sử dụng đất).
    
    STRICT GUIDELINES:
    1. NO META-TALK: Do NOT mention "I have filtered news", "Based on your rules", or "I checked the laws". Jump straight into the strategy.
    2. NO DICTIONARY: Use professional terms (Dự án, Sở hữu, Mở bán, Chi phí vốn, Giải phóng mặt bằng) naturally. Do NOT explain them.
    3. LEGAL ACCURACY: 
       - Xử lý hiệu lực pháp lý: KHÔNG mặc định mọi thứ đều có hiệu lực từ 01/08/2024. Phải phân tích dựa trên ngày có hiệu lực thực tế và ĐIỀU KHOẢN CHUYỂN TIẾP của từng văn bản (Luật Đất đai 2024, Luật Nhà ở 2023, Luật Kinh doanh BĐS 2023, và các Nghị định) áp dụng cho bối cảnh thực tế.
       - NQ 171/2024/QH15: Áp dụng sắc bén cơ chế thí điểm để giải quyết bài toán quỹ đất.
    
    REPORT STRUCTURE:
    - EXECUTIVE SUMMARY: Tóm tắt nhanh cục diện và tác động lớn nhất từ các tin tức mới nhất.
    - THUẬN LỢI TỪ NQ 171 & LUẬT MỚI: Chỉ ra các điểm gỡ vướng, lợi thế về thời gian, chi phí, cơ chế gom đất, thỏa thuận nhận chuyển nhượng quyền sử dụng đất.
    - KHÓ KHĂN & ĐIỂM NGHẼN: Phân tích rủi ro trong quá trình áp dụng, điểm nghẽn thủ tục hành chính, đặc biệt lưu ý tác động tại các Sở ban ngành TP.HCM (Sở Nông nghiệp và Môi trường, Sở Tài chính).
    - 1:1 ACTION PLAN: Các bước thực thi chính xác và chiến thuật cụ thể dành cho Vũ Quang Phát (ví dụ: điểm cốt lõi khi đàm phán, chiến thuật tách thửa, gom đất).
    
    INPUT DATA: {news_data}
    """

    try:
        # Cơ chế quét chọn model tự động để tránh lỗi 404
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models_to_try = sorted(available_models, key=lambda x: (0 if 'pro' in x else (1 if 'flash' in x else 2)))
        
        raw_report = "AI Generation Failed."
        for model_name in models_to_try:
            try:
                if "1.0" in model_name: continue 
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                raw_report = response.text
                break
            except: continue
                
        # Firewall Python cưỡng chế thuật ngữ hành chính hậu 2025
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "tỉnh Bình Dương": "TP.HCM", "tỉnh Bà Rịa": "TP.HCM"
        }
        
        # Gán biến report để tránh lỗi "referenced before assignment"
        report = raw_report 
        
        for old, new in replacements.items():
            report = re.compile(re.escape(old), re.IGNORECASE).sub(new, report)
        return report
    except Exception as e: return f"Lỗi hệ thống AI: {str(e)}"

def send_email(markdown_content):
    """Email Executive Style: Tinh gọn và Quyền lực"""
    sender = "phat.clover@gmail.com"
    msg = MIMEMultipart()
    
    # Cập nhật Tiêu đề Email
    msg["Subject"] = f"[TOP PRIORITY] THUẬN LỢI VÀ KHÓ KHĂN NQ 171 - #{datetime.now().strftime('%d%m')}"
    msg["From"] = f"Senior Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'tables'])
    full_html = f"""
    <div style="font-family: 'Times New Roman', serif; max-width: 850px; margin: auto; border-top: 8px solid #002D62; padding: 40px; color: #1a1a1a;">
        <h1 style="color: #002D62; text-align: center;">BÁO CÁO: THUẬN LỢI VÀ KHÓ KHĂN NQ 171</h1>
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
