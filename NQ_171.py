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
            for entry in feed.entries[:6]:
                desc = re.sub('<[^<]+>', '', entry.get('summary', ''))
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {desc[:350]}...\nLink: {entry.link}\n\n"
        except: continue
    return summary

def get_ai_report(news_data):
    """LÕI TƯ DUY: SENIOR LEGAL ADVISOR (V6 - HYBRID SEARCH & FALLBACK)"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Thiếu API Key."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    prompt = f"""
    CONTEXT: Today is {current_time}. Bạn là Senior Legal Advisor cho chuyên gia Vũ Quang Phát.
    MỤC TIÊU: Sử dụng GOOGLE SEARCH để báo cáo về điểm nóng pháp lý BĐS.

    NHIỆM VỤ TRA CỨU (GOOGLE SEARCH):
    1. Xác thực tên các đơn vị hành chính hậu sáp nhập tại TP.HCM năm 2026 (VD: Sở Nông nghiệp và Môi trường, Sở Tài chính).
    2. Check hiệu lực thực tế của các Nghị định/Thông tư hướng dẫn Luật Đất đai 2024 mới nhất. KHÔNG gán cứng mốc 01/08/2024.
    3. Tìm điểm nóng NQ 171/2024/QH15 tại TP.HCM trong 24h qua.

    BÁO CÁO THEO MÔ HÌNH IRAC:
    - [I] ISSUE: Điểm nóng thị trường. Ảnh hưởng thế nào đến DA ĐT theo NQ 171 (Thỏa thuận nhận quyền SDĐ)?
    - [R] RULE & REALITY: Dẫn luật chính xác + Phân tích "Ý đồ nhà lập pháp" & "Hệ quả thực tế".
    - [A] APPLICATION: Quy trình tại các Sở hậu sáp nhập. So sánh với quy trình đấu giá "bình thường".
    - [C] CONCLUSION: Action Plan 1:1 cho Vũ Quang Phát.
    
    - GLOSSARY: 05 từ vựng pháp lý B1 (English - Vietnamese).

    INPUT DATA: {news_data}
    """

    # Biến lưu trữ kết quả cuối cùng
    final_report = "AI Generation Failed."

    try:
        # THỬ LẦN 1: Chạy có Google Search (Đã sửa thụt đầu dòng)
        try:
            print("[*] Đang thử chạy Gemini 1.5 Flash với Google Search...")
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                tools=[{"google_search_retrieval": {}}] 
            )
            response = model.generate_content(prompt)
            final_report = response.text
        except Exception as search_error:
            # THỬ LẦN 2: Nếu Search lỗi, chạy chế độ thường để đảm bảo luôn có báo cáo
            print(f"[!] Lỗi Search ({search_error}). Đang chuyển sang chế độ thường...")
            model = genai.GenerativeModel(model_name='gemini-1.5-flash')
            response = model.generate_content(prompt)
            final_report = response.text + "\n\n*(Lưu ý: Báo cáo không dùng Search do giới hạn bản Free)*"

        # Firewall thuật ngữ cưỡng chế (Dùng final_report đã thống nhất tên biến)
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính"
        }
        for old, new in replacements.items():
            final_report = re.compile(re.escape(old), re.IGNORECASE).sub(new, final_report)
            
        return final_report
        
    except Exception as e: 
        return f"Lỗi hệ thống nghiêm trọng: {str(e)}"

def send_email(markdown_content):
    """Email Executive Style: Tinh gọn và Quyền lực"""
    sender = "phat.clover@gmail.com"
    msg = MIMEMultipart()
    msg["Subject"] = f"[TOP PRIORITY] THAM MƯU PHÁP LÝ & NQ 171 - #{datetime.now().strftime('%d%m')}"
    msg["From"] = f"Senior Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'tables'])
    full_html = f"""
    <div style="font-family: 'Times New Roman', serif; max-width: 850px; margin: auto; border-top: 8px solid #002D62; padding: 40px; color: #1a1a1a;">
        <h1 style="color: #002D62; text-align: center;">BÁO CÁO: THUẬN LỢI VÀ KHÓ KHĂN NQ 171</h1>
        <p style="text-align: center; border-bottom: 1px solid #eee; padding-bottom: 20px;">Strictly Confidential | For: Vũ Quang Phát</p>
        <div style="line-height: 1.8; text-align: justify;">{html_body}</div>
        <div style="margin-top: 50px; text-align: center; font-size: 11px; color: #888;">AI Strategic Advisor System | Gemini Hybrid Logic</div>
    </div>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, os.environ.get('GMAIL_PASSWORD'))
            server.sendmail(sender, sender, msg.as_string())
        print("[+] Báo cáo đã gửi thành công.")
    except Exception as e: print(f"[-] Email Error: {e}")

if __name__ == "__main__":
    news = get_real_estate_news()
    report = get_ai_report(news)
    send_email(report)
