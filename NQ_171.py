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
    """Thu thập dữ liệu đầu vào - Tập trung 100% vào Đầu tư & Pháp lý dự án"""
    sources = {
        "Chính phủ - Pháp luật": "https://baochinhphu.vn/rss/phap-luat.rss",
        "Báo Đấu Thầu - Dự án": "https://baodauthau.vn/rss/phap-luat-16.rss",
        "Kinh tế (Tuổi Trẻ)": "https://tuoitre.vn/rss/kinh-doanh.rss",
        "VN Business Law": "https://vietnam-business-law.info/feed",
        "Công Báo": "https://congbao.chinhphu.vn/rss"
    }
    
    summary = ""
    for cat, url in sources.items():
        try:
            feed = feedparser.parse(url)
            summary += f"\n--- NGUỒN: {cat.upper()} ---\n"
            # Chỉ lấy tin trong 48h để tránh lỗi 'tiên tri' tin tức
            for entry in feed.entries[:8]: 
                desc = entry.get('summary', entry.get('description', ''))
                clean_desc = re.sub('<[^<]+>', '', desc) 
                short_desc = (clean_desc[:400] + '...') if len(clean_desc) > 400 else clean_desc
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {short_desc}\nLink: {entry.link}\n\n"
        except Exception as e:
            print(f"Lỗi tải nguồn {cat}: {e}")
    return summary

def get_ai_report(news_data):
    """Trợ lý AI Cố vấn Pháp lý Cao cấp - Mastermind Edition"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    # --- BỘ LỆNH CƯỠNG CHẾ (THE CONSTITUTION) ---
    prompt = f"""
QUY TRÌNH XỬ LÝ ƯU TIÊN: Xác thực hiệu lực văn bản trước khi viết.
THỜI GIAN HIỆN TẠI: {current_time}

1. DANH MỤC CSPL BẮT BUỘC (CẤM SAI LỆCH):
- Luật Đất đai 2024 (31/2024/QH15): Hiệu lực 01/08/2024.
- Nghị quyết 171/2024/QH15: Cơ chế thí điểm gom đất thực hiện dự án nhà ở thương mại.
- Luật Kinh doanh BĐS 2023 (29/2023/QH15): Hiệu lực 01/08/2024.
- Luật Nhà ở 2023 (27/2023/QH15): Hiệu lực 01/08/2024.

2. VAI TRÒ & PHẠM VI:
Bạn là Cố vấn cấp cao tham mưu cho Chuyên gia Vũ Quang Phát. 
PHẠM VI: Chỉ tập trung vòng đời đầu tư dự án (Survey, Land Acquisition, NQ 171, Approval, 1/500, Valuation, Permit, Sales).
CẤM TUYỆT ĐỐI: Tin tức vận hành (điện, nước, nhà trọ), nông sản, du lịch. Nếu dữ liệu thô có tin này, PHẢI LOẠI BỎ NGAY.

3. NGUYÊN TẮC PHẢN HỒI:
- Không giải thích luật dông dài kiểu hàn lâm. Đi thẳng vào CHIẾN THUẬT tháo gỡ điểm nghẽn.
- Sử dụng mô hình IRAC (Issue - Rule - Application - Conclusion) cho mọi nút thắt.
- Conclusion (Kết luận) PHẢI là một Action Plan (Kế hoạch hành động) 1:1 cho chuyên gia.
- Ngôn ngữ: Tiếng Việt chuyên ngành + Tiếng Anh trình độ B1 (Project, Permit, Deposit, Ownership).

4. ĐỊA GIỚI HÀNH CHÍNH (HẬU 2025):
Bình Dương, BR-VT thuộc TP.HCM. Dùng đúng tên: Sở Nông nghiệp và Môi trường (Đất đai), Sở Tài chính (Định giá đất), Sở Xây dựng.

DỮ LIỆU ĐẦU VÀO: {news_data}
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
                
        # Bộ lọc Firewall Python cưỡng chế thuật ngữ
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
        for old, new in replacements.items():
            cleaned_report = re.compile(re.escape(old), re.IGNORECASE).sub(new, cleaned_report)
            
        return cleaned_report
    except Exception as e:
        return f"System Error: {str(e)}"

def send_email(markdown_content):
    """Gửi Email với phong cách Executive tham mưu cao cấp"""
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[THAM MƯU CHIẾN LƯỢC] DỰ ÁN & MỞ BÁN #{run_num}"
    msg["From"] = f"Senior Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'tables'])
    
    full_html = f"""
    <html>
      <head>
        <style>
            body {{ font-family: 'Times New Roman', Times, serif; background-color: #f4f4f4; padding: 20px; line-height: 1.6; color: #1a1a1a; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #fff; padding: 40px; border-top: 10px solid #002D62; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #002D62; text-align: center; text-transform: uppercase; border-bottom: 2px solid #eee; padding-bottom: 15px; font-size: 24px; }}
            h2 {{ color: #002D62; border-left: 5px solid #002D62; padding-left: 10px; margin-top: 30px; font-size: 19px; background: #f9f9f9; }}
            h3 {{ color: #8B0000; font-size: 17px; font-weight: bold; }}
            p, li {{ text-align: justify; font-size: 16px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            table, th, td {{ border: 1px solid #ccc; padding: 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .footer {{ text-align: center; font-size: 11px; color: #777; margin-top: 40px; border-top: 1px solid #eee; padding-top: 10px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>BÁO CÁO THAM MƯU PHÁP LÝ DỰ ÁN BĐS</h1>
            <p style="text-align: center;">Thực hiện riêng cho chuyên gia: <strong>Vũ Quang Phát</strong></p>
            <div class="content">{html_body}</div>
            <div class="footer">Tài liệu lưu hành nội bộ - Bảo mật cao | Vận hành bởi Gemini API</div>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, pwd)
            server.sendmail(sender, sender, msg.as_string())
        print("Báo cáo tham mưu cao cấp đã được gửi!")
    except Exception as e:
        print(f"Lỗi gửi email: {e}")

if __name__ == "__main__":
    news = get_real_estate_news()
    report = get_ai_report(news)
    send_email(report)
