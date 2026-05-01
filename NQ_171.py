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
    """Trợ lý AI xử lý dữ liệu: Thẩm định nội dung chuyên môn & Quy trình NQ 171"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là Trợ lý Cố vấn Pháp lý BĐS chuyên nghiệp. Nhiệm vụ của bạn là lập báo cáo chuyên sâu về QUY TRÌNH ĐẦU TƯ DỰ ÁN BẤT ĐỘNG SẢN.

THỜI GIAN LẬP BÁO CÁO: {current_time}

BỘ QUY TẮC THẨM ĐỊNH NỘI DUNG (TUÂN THỦ TUYỆT ĐỐI):

1. BỘ LỌC CHUYÊN MÔN (HÀNG RÀO NỘI DUNG):
   - CHỈ TRÍCH XUẤT tin tức có tác động trực tiếp đến: Pháp lý dự án, giá đất, quy hoạch xây dựng, hạ tầng kỹ thuật, bồi thường giải phóng mặt bằng.
   - LOẠI BỎ hoàn toàn các tin tức kinh tế vĩ mô chung chung không liên quan đến BĐS (Ví dụ: chính trị quốc tế, vận tải hàng không, du lịch, kinh doanh hàng tiêu dùng...) ngay cả khi chúng xuất hiện trong dữ liệu thô.
   - Tuyệt đối không đưa các tin về eo biển Hormuz, Vietjet hay du lịch Cô Tô vào báo cáo nếu nó không ảnh hưởng đến chi phí/pháp lý dự án cụ thể.

2. QUY TRÌNH NQ 171 & LỘ TRÌNH VỀ ĐÍCH MỞ BÁN:
   - Phải làm rõ lộ trình 11 bước từ: Thỏa thuận gom đất (Đất khác) -> Chấp thuận chủ trương (CTCTĐT) -> Quy hoạch 1/500 -> Quyết định CMDSDĐ (NQ 171) -> Định giá đất -> Sổ hồng tổng -> GPXD -> Thông báo đủ điều kiện mở bán.
   - CHỈ ĐÍCH DANH NÚT THẮT: Điểm nghẽn thường kẹt tại Sở Nông nghiệp và Môi trường (rà soát nguồn gốc đất phức tạp) và Sở Tài chính (định giá đất chậm trễ hậu sáp nhập NQ 202/2025).

3. ĐỊA GIỚI & BỘ MÁY (SAU 01/07/2025):
   - Bình Dương, BR-VT đã sáp nhập vào TP.HCM. Cấm dùng "UBND Quận". 
   - Bắt buộc dùng tên cơ quan mới: Sở Nông nghiệp và Môi trường, Sở Tài chính, Sở Xây dựng.

4. NGOẠI NGỮ B1: 
   - Sử dụng từ vựng tiếng Anh pháp lý cơ bản (B1): Deposit, Lease, Permit, Ownership, Project. KHÔNG dùng từ C1/C2 phức tạp.
   - 1 UK Idiom thương mại.

Dữ liệu thô từ báo chí: {news_data}

YÊU CẦU CẤU TRÚC:
Tự do chia tiêu đề nhưng phải đảm bảo:
- Khối 1: Phân tích tin tức chuyên môn (tác động đến giá vốn, đền bù).
- Khối 2: Bảng chi tiết Lộ trình NQ 171, điểm nghẽn tại các Sở và giải pháp gỡ vướng thực chiến.
- Khối 3: Phân tích IRAC cho rủi ro pháp lý/tài chính trọng tâm nhất.
- Khối 4: 5 Từ vựng B1 & 1 UK Idiom.
"""

    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models_to_try = sorted(available_models, key=lambda x: (0 if 'flash' in x else (1 if 'pro' in x else 2)))
        
        raw_report = "AI Generation Failed."
        for model_name in models_to_try:
            try:
                if "1.0" in model_name: continue 
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                raw_report = response.text
                break
            except Exception as e:
                print(f"Lỗi khi thử model {model_name}: {e}")
                continue
                
        # --- BỘ LỌC CƯỠNG CHẾ PYTHON ---
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở TN&MT": "Sold Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "Sở KH&ĐT": "Sở Tài chính",
            "UBND quận": "UBND TP.HCM/Thành phố trực thuộc",
            "Ủy ban nhân dân quận": "UBND TP.HCM/Thành phố trực thuộc",
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
    msg["Subject"] = f"[PHÁP LÝ BĐS] BÁO CÁO CHIẾN LƯỢC DỰ ÁN & MỞ BÁN #{run_num}"
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
            <p style="text-align: center;">Thực hiện bởi: <strong>Trợ lý AI</strong> | Phê duyệt chuyên môn: <strong>Vũ Quang Phát</strong></p>
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
