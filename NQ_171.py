import os, re, smtplib, feedparser, markdown, pytz
from datetime import datetime
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_real_estate_news():
    """LỌC TIN TINH HOA: Chỉ lấy các nguồn tác động đến Pháp lý & Đầu tư dự án"""
    sources = {
        "Chính phủ - Pháp luật": "https://baochinhphu.vn/rss/phap-luat.rss",
        "Báo Đấu Thầu - Dự án": "https://baodauthau.vn/rss/phap-luat-16.rss",
        "Công Báo": "https://congbao.chinhphu.vn/rss"
    }
    summary = ""
    for cat, url in sources.items():
        try:
            feed = feedparser.parse(url)
            summary += f"\n--- NGUỒN: {cat.upper()} ---\n"
            for entry in feed.entries[:6]: # Lấy 6 tin nóng nhất
                desc = re.sub('<[^<]+>', '', entry.get('summary', ''))
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {desc[:400]}...\nLink: {entry.link}\n\n"
        except: continue
    return summary

def get_ai_report(news_data):
    """KHỐI TƯ DUY CỐ VẤN: Đã nạp NQ 171 và Quy trình 11 bước của Vũ Quang Phát"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Thiếu GEMINI_API_KEY trong Environment."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    # --- ĐỊNH NGHĨA 'BỘ NÃO' CỐ VẤN ---
    prompt = f"""
    CONTEXT: Today is {current_time}. You are the Senior Legal Advisor to expert Vũ Quang Phát.
    ROLE: A high-level legal peer. Your goal is to assess risks and provide strategic solutions.
    
    INTERNAL KNOWLEDGE (Mandatory Baseline):
    1. QUY TRÌNH 11 BƯỚC DỰ ÁN BĐS:
       - Step 1: Khảo sát dự án.
       - Step 2: Thỏa thuận nhận quyền sử dụng đất (Gom đất).
       - Step 3: Chấp thuận chủ trương đầu tư.
       - Step 4: Phê duyệt quy hoạch 1/500.
       - Step 5-10: Các bước định giá đất, GPXD, thi công hạ tầng.
       - Step 11: Thông báo đủ điều kiện bán hàng (Sales).
       *Nhiệm vụ: Định vị tin tức hôm nay đang ảnh hưởng trực tiếp đến Step nào.*
    
    2. NGHỊ QUYẾT 171/2024/QH15 (Chìa khóa chiến lược):
       - Cơ chế thí điểm cho phép nhận chuyển nhượng quyền sử dụng đất 'khác' (không phải đất ở) để làm dự án nhà ở thương mại.
       - Đây là ưu thế tuyệt đối để xử lý các dự án đang kẹt tại Step 2 và Step 3.

    STRICT GUIDELINES:
    - KHÔNG meta-talk: Không viết 'Tôi đã đọc', 'Tôi lọc tin'. Nhảy thẳng vào phân tích.
    - KHÔNG hàn lâm: Sử dụng thuật ngữ chuyên môn (Holding cost, Project, Sales, Ownership) tự nhiên, không giải thích.
    - PHÁP LÝ THỰC TẾ 2026: Luật Đất đai 2024, Kinh doanh BĐS 2023 đều đã vận hành từ 01/08/2024. Hãy tư vấn dựa trên trạng thái thực thi hiện hành.

    CẤU TRÚC BÁO CÁO:
    1. ĐÁNH GIÁ TRỌNG TÂM: Tin tức nào tác động mạnh nhất đến Step nào trong quy trình 11 bước?
    2. PHÂN TÍCH ƯU & KHUYẾT (NQ 171 Perspective): 
       - Ưu điểm để đẩy nhanh tiến độ dự án.
       - Khuyết điểm/Rủi ro về chi phí vốn (Holding cost) hoặc rào cản tại các Sở ban ngành.
    3. CHIẾN THUẬT THÁO GỠ (Action Plan 1:1): Các bước đi cụ thể cho Vũ Quang Phát để làm việc với đối tác hoặc cơ quan nhà nước.

    DATA: {news_data}
    """

    try:
        # Tự động chọn Model cao cấp nhất
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        best_model = next((m for m in models if "pro" in m), models[0])
        
        model = genai.GenerativeModel(best_model)
        response = model.generate_content(prompt)
        report = response.text
                
        # Firewall Python: Chuẩn hóa thuật ngữ hành chính TP.HCM 2025
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "tỉnh Bình Dương": "TP.HCM", "tỉnh Bà Rịa": "TP.HCM"
        }
        for old, new in replacements.items():
            report = re.compile(re.escape(old), re.IGNORECASE).sub(new, report)
        return report
    except Exception as e: return f"AI Error: {str(e)}"

def send_email(markdown_content):
    """GỬI EMAIL: Giao diện Memo mật của Cố vấn cấp cao"""
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[LEGAL STRATEGY] BÁO CÁO THAM MƯU #{datetime.now().strftime('%d%m')}"
    msg["From"] = f"Senior Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'tables', 'nl2br'])
    full_html = f"""
    <div style="font-family: 'Times New Roman', serif; max-width: 800px; margin: auto; border-top: 10px solid #002D62; padding: 45px; background: #fff; color: #1a1a1a;">
        <h1 style="color: #002D62; text-align: center; text-transform: uppercase; font-size: 24px;">Memo: Tham mưu chiến lược dự án</h1>
        <p style="text-align: center; font-style: italic; color: #666; border-bottom: 1px solid #eee; padding-bottom: 20px;">
            Strictly Confidential | Dành riêng cho chuyên gia Vũ Quang Phát
        </p>
        <div style="line-height: 1.8; text-align: justify; font-size: 16px;">{html_body}</div>
        <div style="margin-top: 50px; text-align: center; font-size: 11px; color: #aaa; border-top: 1px solid #eee; padding-top: 20px;">
            Hệ thống Cố vấn Chiến lược tự động | Cấu trúc bởi NQ 171 & Quy trình 11 bước của Chuyên gia.
        </div>
    </div>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, pwd)
            server.sendmail(sender, sender, msg.as_string())
        print("Báo cáo chiến lược đã được gửi thành công.")
    except Exception as e: print(f"Email Error: {e}")

if __name__ == "__main__":
    news = get_real_estate_news()
    report = get_ai_report(news)
    send_email(report)
