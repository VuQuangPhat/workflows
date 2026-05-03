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
    """LÕI TƯ DUY V12: TRUY VẤN ĐA TẦNG & TỰ KIỂM CHỨNG LỖI"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Thiếu API Key."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    # MASTER PROMPT V12: ÉP AI TỰ ĐIỀU CHỈNH KIẾN THỨC SAI LỆCH
    prompt = f"""
    CONTEXT: Today is {current_time}. Bạn là Senior Legal Advisor cho Vũ Quang Phát.
    Nhiệm vụ: Cung cấp báo cáo tham mưu TUYỆT ĐỐI CHÍNH XÁC về pháp lý BĐS 2026.

    1. CẢNH BÁO KIẾN THỨC (MANDATORY):
    - Kiểm chứng ngay Luật số 43/2024/QH15: Xác nhận Luật Đất đai, Nhà ở, Kinh doanh BĐS đã có hiệu lực từ 01/08/2024. TUYỆT ĐỐI KHÔNG dùng mốc 01/01/2025.
    - Cập nhật bộ máy TP.HCM 2026: Ưu tiên dùng tên 'Sở Nông nghiệp và Môi trường' và 'Sở Tài chính' (thay cho Sở TN&MT và Sở KH&ĐT cũ).
    - NQ 171: Phải là NQ 171/2024/QH15 (Cơ chế thí điểm nhận quyền SDĐ), KHÔNG nhầm với bản 2022.

    2. DỮ LIỆU DỰ ÁN THỰC TẾ:
    {project_status}

    3. CẤU TRÚC BÁO CÁO (IRAC):
    - [I] ISSUE: Điểm nóng thị trường soi chiếu trực tiếp vào vướng mắc của Hung Thinh, Saigonres, Hoa Sen.
    - [R] RULE & REALITY: Dẫn luật (mốc 01/08/2024) + Phân tích 'Ý đồ nhà lập pháp' & 'Hệ quả thực tế'.
    - [A] APPLICATION: Quy trình cụ thể tại Sở Nông nghiệp và Môi trường & Sở Tài chính cho từng DA.
    - [C] CONCLUSION: Action Plan 1:1 với thời hạn thực thi (deadline) rõ ràng.
    
    - GLOSSARY: 05 từ vựng pháp lý B1.

    INPUT DATA: {news_data}
    """

    try:
        # Sử dụng Flash với Google Search để AI tự check lại mốc 01/08/2024
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[{"google_search_retrieval": {}}]
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Lỗi hệ thống: {str(e)}"

def send_email(markdown_content):
    """Cấu trúc Email Executive: Chữ to, Scannable, Đẳng cấp"""
    sender = "phat.clover@gmail.com"
    msg = MIMEMultipart()
    msg["Subject"] = f"[TOP PRIORITY] THAM MƯU PHÁP LÝ DỰ ÁN & NQ 171 - #{datetime.now().strftime('%d%m')}"
    msg["From"] = f"Senior Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'tables'])
    
    # CSS: Fix chữ nhỏ bằng font-size 18px cho body và 26px cho Header
    full_html = f"""
    <div style="font-family: 'Times New Roman', Times, serif; max-width: 850px; margin: auto; border-top: 12px solid #002D62; padding: 50px; color: #1a1a1a; line-height: 1.8;">
        <h1 style="color: #002D62; text-align: center; font-size: 28px; text-transform: uppercase;">Báo Cáo Tham Mưu Pháp Lý Tuần</h1>
        <p style="text-align: center; border-bottom: 2px solid #eee; padding-bottom: 20px; font-style: italic;">Srictly Confidential | For: Vũ Quang Phát</p>
        
        <div style="font-size: 18px; text-align: justify;">
            {html_body}
        </div>
        
        <div style="margin-top: 60px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; font-size: 12px; color: #777;">
            AI Strategic Advisor System | Gemini V12 Grounded | 2026 Legal Framework
        </div>
    </div>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, os.environ.get('GMAIL_PASSWORD'))
            server.sendmail(sender, sender, msg.as_string())
        print("[+] Báo cáo đã được gửi với định dạng chuẩn.")
    except Exception as e: print(f"[-] Email Error: {e}")

if __name__ == "__main__":
    # Danh mục dự án thực tế để AI soi chiếu
    REAL_PROJECT_STATUS = """
    - DA Hung Thinh: Đang nghẽn khâu thẩm định giá đất (phương pháp thặng dư) tại Sở Tài chính TP.HCM.
    - DA Saigonres: Vướng thủ tục chuyển đổi 2ha đất nông nghiệp sang đất ở theo NQ 171/2024/QH15.
    - DA Hoa Sen: Đang khảo sát pháp lý đấu giá tại Long An và Tiền Giang.
    """
    
    news = get_real_estate_news()
    report = get_ai_report(news, REAL_PROJECT_STATUS)
    send_email(report)
