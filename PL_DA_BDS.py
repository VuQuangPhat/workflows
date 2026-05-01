import os
import re
import smtplib
import feedparser
import markdown
import pytz
from datetime import datetime
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_real_estate_news():
    """Thu thập dữ liệu đầu vào từ các trang tin pháp luật & kinh tế"""
    sources = {
        "Chính phủ": "https://baochinhphu.vn/rss/phap-luat.rss",
        "Kinh tế (Tuổi Trẻ)": "https://tuoitre.vn/rss/kinh-doanh.rss",
        "Báo Đấu Thầu": "https://baodauthau.vn/rss/phap-luat-16.rss", 
        "Đại Biểu Nhân Dân": "https://daibieunhandan.vn/rss/phap-luat-kinh-te.rss",
        "VN Business Law": "https://vietnam-business-law.info/feed", 
        "Công Báo Chính Phủ": "https://congbao.chinhphu.vn/rss" 
    }
    
    summary = ""
    for cat, url in sources.items():
        try:
            feed = feedparser.parse(url)
            summary += f"\n--- NGUỒN: {cat.upper()} ---\n"
            for entry in feed.entries[:5]:
                desc = entry.get('summary', entry.get('description', ''))
                clean_desc = re.sub('<[^<]+>', '', desc) 
                short_desc = (clean_desc[:350] + '...') if len(clean_desc) > 350 else clean_desc
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {short_desc}\nLink: {entry.link}\n\n"
        except Exception as e:
            print(f"Lỗi tải nguồn {cat}: {e}")
            continue
    return summary

def get_ai_report(news_data):
    """Trợ lý AI xử lý dữ liệu: Thẩm định nội dung chuyên môn, So sánh NQ 171 và Lộ trình thực chiến"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là Trợ lý Cố vấn Pháp lý BĐS chuyên nghiệp. Nhiệm vụ: Lập báo cáo TỔNG HỢP & THAM MƯU CHIẾN LƯỢC.

THỜI GIAN LẬP BÁO CÁO: {current_time}

BỘ QUY TẮC NỘI DUNG (TUÂN THỦ TUYỆT ĐỐI):

1. BỘ LỌC CHUYÊN MÔN (HÀNG RÀO NỘI DUNG):
   - LOẠI BỎ các tin vĩ mô không liên quan đến BĐS (Hormuz, du lịch, vận tải...).
   - CHỈ PHÂN TÍCH tin tức ảnh hưởng đến: Pháp lý dự án, giá vốn đất, đền bù, quy hoạch[cite: 6].

2. TÁCH BẠCH CƠ CHẾ ĐẦU TƯ (YÊU CẦU MỚI):
   - Phân tích ƯU và KHUYẾT ĐIỂM của cơ chế NQ 171 (Thỏa thuận gom đất) so với:
     + Hình thức Thông thường (Đấu giá/Đấu thầu quyền sử dụng đất).
     + Thủ tục Đặc biệt (Dự án quy mô lớn, công nghệ cao theo Điều 28 Luật Đầu tư 143)[cite: 3, 7].

3. LỘ TRÌNH THỰC CHIẾN & NÚT THẮT:
   - Làm rõ lộ trình 11 bước "về đích mở bán" (từ gom đất đến khi có văn bản đủ điều kiện bán hàng).
   - Chỉ đích danh nút thắt tại: Sở Tài chính (định giá đất chậm hậu sáp nhập NQ 202) và Sở Nông nghiệp và Môi trường (rà soát nguồn gốc đất)[cite: 4, 7].

4. ĐỊA GIỚI & NGOẠI NGỮ (B1):
   - Bình Dương, BR-VT đã vào TP.HCM. Cấm dùng "UBND Quận"[cite: 5].
   - Tiếng Anh: Chỉ dùng mức độ B1 (Deposit, Lease, Permit...) và 1 UK Idiom[cite: 7].

Dữ liệu thô từ báo chí: {news_data}

YÊU CẦU CẤU TRÚC:
Linh động chia tiêu đề, không cố định các bước. Tuy nhiên phải có:
- Bảng so sánh Ưu/Khuyết điểm các ngả rẽ đầu tư (Thông thường - NQ 171 - Đặc biệt)[cite: 3, 7].
- Bảng/Sơ đồ lộ trình 11 bước mở bán và điểm nghẽn Sở ngành[cite: 7].
- Phân tích IRAC cho rủi ro trọng tâm (Ưu tiên rủi ro định giá đất chậm)[cite: 7].
- 5 từ vựng B1 & 1 UK Idiom[cite: 7].
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash") # Ưu tiên Flash để tốc độ ổn định
        response = model.generate_content(prompt)
        raw_report = response.text
                
        # --- BỘ LỌC CƯỠNG CHẾ PYTHON ---
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở TN&MT": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "Sở KH&ĐT": "Sở Tài chính",
            "UBND quận": "UBND TP.HCM/Thành phố trực thuộc",
            "tỉnh Bình Dương": "TP.HCM",
            "tỉnh Bà Rịa": "TP.HCM"
        }
        
        cleaned_report = raw_report
        for old_term, new_term in replacements.items():
            pattern = re.compile(re.escape(old_term), re.IGNORECASE)
            cleaned_report = pattern.sub(new_term, cleaned_report)
            
        return cleaned_report
        
    except Exception as e:
        return f"System Error: {str(e)}"

def send_email(markdown_content):
    """Biên dịch Markdown sang HTML và Gửi Email nội bộ"""
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[PHÁP LÝ BĐS] CHIẾN LƯỢC NQ 171 & LỘ TRÌNH MỞ BÁN #{run_num}"
    msg["From"] = f"Real Estate Legal Assistant <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'tables'])
    
    full_html = f"""
    <html>
      <head>
        <style>
            body {{ font-family: 'Times New Roman', serif; background-color: #f4f7f6; padding: 30px; line-height: 1.8; color: #1a1a1a; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #fff; padding: 50px; border-top: 10px solid #004d40; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-radius: 4px; }}
            h1 {{ color: #004d40; text-align: center; text-transform: uppercase; font-size: 22px; border-bottom: 2px solid #eee; padding-bottom: 20px; }}
            h2 {{ color: #004d40; border-bottom: 2px solid #004d40; padding-bottom: 5px; margin-top: 40px; font-size: 19px; text-transform: uppercase; }}
            h3 {{ color: #bf360c; font-size: 17px; margin-top: 20px; font-weight: bold; }}
            p, li {{ text-align: justify; margin-bottom: 15px; font-size: 16px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #fafafa; }}
            table, th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #e0f2f1; color: #004d40; font-weight: bold; }}
            .time-stamp {{ text-align: right; font-style: italic; color: #555; margin-bottom: 30px; font-weight: bold; }}
            .footer {{ text-align: center; font-size: 11px; color: #888; margin-top: 50px; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>BÁO CÁO CHIẾN LƯỢC DỰ ÁN ĐẦU TƯ BĐS</h1>
            <p style="text-align: center;">Phê duyệt chuyên môn: <strong>Vũ Quang Phát</strong></p>
            <div class="content">{html_body}</div>
            <div class="footer">Hệ thống Trợ lý Báo cáo Tự động | Vận hành bởi Gemini AI & GitHub Actions</div>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, pwd)
            server.sendmail(sender, sender, msg.as_string())
        print("Trợ lý đã gửi báo cáo thành công!")
    except Exception as e:
        print(f"Lỗi gửi mail: {e}")

if __name__ == "__main__":
    news = get_real_estate_news()
    report = get_ai_report(news)
    send_email(report)
