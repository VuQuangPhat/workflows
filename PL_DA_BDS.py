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
    """Thu thập tình báo pháp lý từ các nguồn chuyên sâu"""
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
            if not feed.entries: continue
            summary += f"\n--- NGUỒN: {cat.upper()} ---\n"
            for entry in feed.entries[:3]: # Lấy 3 tin lõi để phân tích sâu
                desc = entry.get('summary', entry.get('description', ''))
                clean_desc = re.sub('<[^<]+>', '', desc) 
                short_desc = (clean_desc[:300] + '...') if len(clean_desc) > 300 else clean_desc
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {short_desc}\nLink: {entry.link}\n\n"
        except Exception as e:
            print(f"Lỗi tải nguồn {cat}: {e}")
            continue
    return summary

def get_ai_report(news_data):
    """Trợ lý AI tự động suy nghĩ và tham mưu trực tiếp cho Vũ Quang Phát"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là Trợ lý Tình báo Pháp lý BĐS cá nhân độc quyền của Vũ Quang Phát. Anh Phát là người quyết định cuối cùng, KHÔNG CẦN báo cáo cho ai khác.
Nhiệm vụ: Tự động tổng hợp tin tức, tự suy nghĩ, bóc tách rủi ro và cung cấp cho anh Phát những lời khuyên sắc bén, thực dụng nhất về LỘ TRÌNH MỞ BÁN dự án.

BỘ QUY TẮC CỐT LÕI (TUÂN THỦ TUYỆT ĐỐI 100%):

1. ĐỊA GIỚI & BỘ MÁY (Hậu NQ 202/2025):
   - Cấm dùng "UBND Quận". Dùng "UBND TP.HCM" hoặc "UBND Thành phố trực thuộc" (do Bình Dương, BR-VT đã sáp nhập).
   - Gọi tên chuẩn xác: "Sở Nông nghiệp và Môi trường" (Đất đai), "Sở Tài chính" (Giá đất), "Sở Xây dựng" (Quy hoạch/Mở bán).

2. TƯ DUY PHÂN TÍCH (Cho riêng anh Phát):
   - Nói thẳng vào sự thật: Phân tích định lượng (tốn bao nhiêu tiền, kẹt bao nhiêu tháng).
   - Bản chất NQ 171: Chỉ là công cụ biến ĐẤT KHÁC thành ĐẤT Ở. Tuyệt đối không xúi anh Phát đi xin "Nhà nước thu hồi đất" hay "giãn nộp tiền sử dụng đất" cho dự án nhà ở thương mại. Luật không cho phép.
   - Vạch đích duy nhất: Phải gỡ đến bước cầm được Văn bản đủ điều kiện mở bán. (Không có sổ hồng tổng = Không có mở bán).

3. VĂN PHONG TÌNH BÁO:
   - Viết dạng Bullet points sắc gọn. Không rào trước đón sau. KHÔNG viết kiểu "văn mẫu" hay "khuyên sếp". 
   - Tập trung vào kỹ thuật pháp lý (Ví dụ: lách ranh 1/500, áp dụng phương pháp thặng dư, tính hệ số K).

Dữ liệu thô hôm nay: {news_data}

CẤU TRÚC BÁN TIN (Markdown):
* [Dòng 1] "Thời gian lập báo cáo: {current_time}"
* GÓC NHÌN VĨ MÔ (Tác động thị trường & Luật): Đánh giá nhanh tin tức ảnh hưởng thế nào đến dòng tiền và quỹ đất của anh Phát tại Miền Nam. Bỏ qua các tin rác vi mô.
* ĐIỂM NGHẼN VI MÔ (Quy trình Sở ngành): Đặt lên bàn cân LĐT (Đấu thầu) vs NQ 171 (Gom đất). Chỉ đích danh hồ sơ của anh Phát đang kẹt ở Sở nào, rủi ro là gì?
* CHIẾN THUẬT GỠ RỐI (Thực chiến NQ 171): Anh Phát cần làm gì để vượt qua rủi ro "Đất da báo"? Làm sao để thúc Sở NN&MT cấp sổ hồng tổng nhanh nhất? 
* PHÂN TÍCH IRAC (Trọng tâm 1 Vấn đề lõi): Mổ xẻ 1 rủi ro lớn nhất từ tin tức (Ví dụ: Định giá đất tăng). Đưa ra Action Plan 3 bước kỹ thuật pháp lý cho anh Phát.
* TỪ VỰNG & IDIOM (B1-B2): 5 từ vựng pháp lý/kinh doanh BĐS & 1 thành ngữ Anh Quốc.
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
                continue
                
        # --- BỘ LỌC CƯỠNG CHẾ PYTHON (CHỐNG LẠI "ẢO GIÁC" CỦA AI) ---
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở TN&MT": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "Sở KH&ĐT": "Sở Tài chính",
            "Sở Kế hoạch Đầu tư": "Sở Tài chính",
            "UBND quận": "UBND TP.HCM/Thành phố trực thuộc",
            "Ủy ban nhân dân quận": "UBND TP.HCM/Thành phố trực thuộc",
            "UBND Quận": "UBND TP.HCM/Thành phố trực thuộc",
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
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[TÌNH BÁO PHÁP LÝ] NHẬN ĐỊNH THỊ TRƯỜNG & CHIẾN LƯỢC #{run_num}"
    msg["From"] = f"AI Personal Brain <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'tables'])
    
    full_html = f"""
    <html>
      <head>
        <style>
            body {{ font-family: 'Arial', sans-serif; background-color: #f0f2f5; padding: 20px; line-height: 1.6; color: #1a1a1a; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #fff; padding: 40px; border-top: 8px solid #002b5e; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-radius: 8px; }}
            h1 {{ color: #002b5e; text-align: left; text-transform: uppercase; font-size: 24px; border-bottom: 2px solid #eee; padding-bottom: 15px; margin-bottom: 20px; }}
            h2 {{ color: #002b5e; border-left: 5px solid #d32f2f; padding-left: 10px; margin-top: 35px; font-size: 18px; text-transform: uppercase; }}
            h3 {{ color: #d32f2f; font-size: 16px; margin-top: 20px; font-weight: bold; }}
            p, li {{ text-align: justify; margin-bottom: 12px; font-size: 15px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #fafafa; }}
            table, th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f4f6f8; color: #002b5e; font-weight: bold; }}
            .footer {{ text-align: center; font-size: 12px; color: #7f8c8d; margin-top: 40px; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>BẢN TIN TÌNH BÁO PHÁP LÝ ĐỘC QUYỀN</h1>
            <p style="color: #d32f2f; font-weight: bold;">[Chỉ dành riêng cho: Vũ Quang Phát]</p>
            <div class="content">{html_body}</div>
            <div class="footer">Hệ thống Tư duy Tự động | Vận hành bởi Gemini AI & GitHub Actions</div>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, pwd)
            server.sendmail(sender, sender, msg.as_string())
        print("Đã gửi bản tin tình báo cho sếp Phát!")
    except Exception as e:
        print(f"Lỗi gửi mail: {e}")

if __name__ == "__main__":
    news = get_real_estate_news()
    report = get_ai_report(news)
    send_email(report)
