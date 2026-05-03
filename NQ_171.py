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
    """LÕI TƯ DUY: SENIOR LEGAL ADVISOR (V11 - REAL PROJECT FOCUS)"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Thiếu API Key."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    prompt = f"""
    CONTEXT: Today is {current_time}. Bạn là Senior Legal Advisor cho Vũ Quang Phát.
    
    MỤC TIÊU: Soi chiếu TIN TỨC MỚI và TÌNH HÌNH DỰ ÁN THỰC TẾ để đưa ra tham mưu chiến lược.

    PHẦN 1: TÌNH HÌNH DỰ ÁN THỰC TẾ CỦA CHỦ NHÂN:
    {project_status}

    YÊU CẦU PHÂN TÍCH (IRAC):
    - [I] ISSUE: Điểm nóng thị trường. PHẢI đối chiếu trực tiếp điểm nóng này ảnh hưởng thế nào đến các DA thực tế nêu trên (vd: DA tại Hung Thinh, Saigonres...).
    - [R] RULE & REALITY: Dẫn luật (Đất đai 2024, NQ 171). Phân tích "Ý đồ nhà lập pháp" & "Hệ quả thực tế" đối với danh mục dự án hiện hữu.
    - [A] APPLICATION: Quy trình cụ thể tại Sở Nông nghiệp và Môi trường, Sở Tài chính TP.HCM cho các DA này.
    - [C] CONCLUSION: Action Plan 1:1 cực kỳ chi tiết cho Vũ Quang Phát để xử lý các dự án đang nghẽn.
    
    - GLOSSARY: 05 từ vựng pháp lý B1 (English - Vietnamese).

    TIN TỨC ĐẦU VÀO: {news_data}
    """

    final_report = "AI Generation Failed."
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models_to_try = sorted(available_models, key=lambda x: (0 if 'flash' in x else (1 if 'pro' in x else 2)))
        
        for model_name in models_to_try:
            if "1.0" in model_name: continue
            try:
                # Thử chạy Flash với Search
                model = genai.GenerativeModel(model_name=model_name, tools=[{"google_search_retrieval": {}}])
                response = model.generate_content(prompt)
                final_report = response.text
                break
            except:
                try:
                    # Fallback chạy thường
                    model = genai.GenerativeModel(model_name=model_name)
                    response = model.generate_content(prompt)
                    final_report = response.text
                    break
                except: continue

        replacements = {"Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường", "Sở Kế hoạch và Đầu tư": "Sở Tài chính"}
        for old, new in replacements.items():
            final_report = re.compile(re.escape(old), re.IGNORECASE).sub(new, final_report)
        return final_report
    except Exception as e: return f"Lỗi hệ thống: {str(e)}"

def send_email(markdown_content):
    """Cập nhật giao diện: Chữ to rõ, Scannable cho Senior Executive"""
    sender = "phat.clover@gmail.com"
    msg = MIMEMultipart()
    msg["Subject"] = f"[TOP PRIORITY] THAM MƯU PHÁP LÝ & NQ 171 - #{datetime.now().strftime('%d%m')}"
    msg["From"] = f"Senior Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'tables'])
    
    # CSS Upgrade: Font-size 16px, Headers 24px, Line-height chuẩn UK
    full_html = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 900px; margin: auto; border-top: 10px solid #002D62; padding: 40px; color: #1a1a1a; line-height: 1.7;">
        <h1 style="color: #002D62; text-align: center; font-size: 28px; margin-bottom: 5px;">BÁO CÁO THAM MƯU PHÁP LÝ DỰ ÁN</h1>
        <p style="text-align: center; border-bottom: 2px solid #002D62; padding-bottom: 20px; font-weight: bold; color: #555;">Strictly Confidential | For: Vũ Quang Phát</p>
        
        <div style="font-size: 16px; text-align: justify;">
            {html_body}
        </div>
        
        <div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; font-size: 12px; color: #888;">
            AI Strategic Advisor System | Gemini V11 Hybrid Core | 2026 Compliance
        </div>
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
    # --- CẬP NHẬT TÌNH HÌNH DỰ ÁN THỰC TẾ TẠI ĐÂY ---
    REAL_PROJECT_STATUS = """
    1. DA Dự án tại Hung Thinh Corporation: Đang nghẽn khâu thẩm định giá đất theo phương pháp thặng dư tại TP.HCM.
    2. DA tại Saigonres Group: Đang vướng thủ tục chuyển đổi 2ha đất nông nghiệp sang đất ở thương mại theo cơ chế NQ 171.
    3. DA tại Hoa Sen Group: Đang khảo sát pháp lý để đấu giá quyền sử dụng đất tại các tỉnh miền Tây.
    """
    
    news = get_real_estate_news()
    report = get_ai_report(news, REAL_PROJECT_STATUS)
    send_email(report)
