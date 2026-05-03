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
    """Thu thập dữ liệu đầu vào tập trung vào pháp lý dự án và đầu thầu"""
    sources = {
        "Chính phủ - Pháp luật": "https://baochinhphu.vn/rss/phap-luat.rss",
        "Báo Đấu Thầu - Pháp luật": "https://baodauthau.vn/rss/phap-luat-16.rss",
        "Kinh tế (Tuổi Trẻ)": "https://tuoitre.vn/rss/kinh-doanh.rss",
        "VN Business Law": "https://vietnam-business-law.info/feed",
        "Công Báo": "https://congbao.chinhphu.vn/rss"
    }
    
    summary = ""
    for cat, url in sources.items():
        try:
            feed = feedparser.parse(url)
            summary += f"\n--- NGUỒN: {cat.upper()} ---\n"
            for entry in feed.entries[:8]: 
                desc = entry.get('summary', entry.get('description', ''))
                clean_desc = re.sub('<[^<]+>', '', desc) 
                short_desc = (clean_desc[:400] + '...') if len(clean_desc) > 400 else clean_desc
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {short_desc}\nLink: {entry.link}\n\n"
        except Exception as e:
            print(f"Lỗi tải nguồn {cat}: {e}")
    return summary

def get_ai_report(news_data):
    """Trợ lý AI Cố vấn Pháp lý Cao cấp - Cơ chế tự chọn Model & IRAC thực chiến"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    # --- "HIẾN PHÁP" THAM MƯU (PROMPT) ---
    prompt = f"""
QUY TRÌNH XỬ LÝ ƯU TIÊN: Đối với mọi văn bản pháp luật hoặc quy trình thủ tục, bạn PHẢI xác thực trạng thái hiệu lực hiện hành. Không dùng kiến thức cũ nếu có thông tin mới hơn.

BỐI CẢNH & VAI TRÒ: 
Bạn là Cố vấn Pháp lý cao cấp, tham mưu trực tiếp cho chuyên gia Vũ Quang Phát. 
PHẠM VI TƯ VẤN ĐỘC QUYỀN: Chỉ tập trung vào vòng đời phát triển dự án BĐS (Khảo sát, Gom đất, NQ 171, Chấp thuận chủ trương, Quy hoạch 1/500, Định giá đất, GPXD đến khi MỞ BÁN). 
LOẠI BỎ HOÀN TOÀN: Tin tức về quản lý vận hành (điện, nước, nhà trọ), nông sản, du lịch hay kinh tế vĩ mô không tác động đến pháp lý dự án.

NGUYÊN TẮC NỘI DUNG:
1. Ma trận pháp lý mở rộng: Quét liên thông Luật Đất đai, Đầu tư, Xây dựng, Quy hoạch, Kinh doanh BĐS, Môi trường và các văn bản dưới luật.
2. Độ sâu chuyên môn: Giải thích "bản chất pháp lý", "ý đồ nhà lập pháp" và "hệ quả thực tế". Không trích dẫn suông.
3. Ngôn ngữ: Tiếng Việt chuyên ngành. Tiếng Anh trình độ B1 (VD: Project, Permit, Deposit, Lease, Ownership).
4. Địa giới (Hậu 01/07/2025): Bình Dương, BR-VT thuộc TP.HCM. Dùng đúng tên: Sở Nông nghiệp và Môi trường (Đất đai), Sở Tài chính (Định giá đất), Sở Xây dựng.

CẤU TRÚC PHẢN HỒI LINH HOẠT (DYNAMIC):
- Không dùng form cố định. Tự chia giai đoạn dự án hoặc nhóm rủi ro dựa trên tin tức nóng nhất.
- BẮT BUỘC dùng mô hình IRAC (Issue - Rule - Application - Conclusion) cho các nút thắt dự án (như gom đất NQ 171). Phần Conclusion phải là giải pháp thực chiến 1:1.
- Danh mục Căn cứ pháp lý (Số hiệu, Ngày ban hành, Hiệu lực) phải liệt kê ở đầu báo cáo.

DỮ LIỆU ĐẦU VÀO HÔM NAY: {news_data}
"""

    try:
        # --- CƠ CHẾ TỰ CHỌN MODEL (NHƯ BẢN 23/26) ---
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
                
        # --- BỘ LỌC CƯỠNG CHẾ PYTHON ---[cite: 3, 4]
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
    """Gửi Email với giao diện sang trọng, chuyên nghiệp"""
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[CỐ VẤN PHÁP LÝ] CHIẾN LƯỢC DỰ ÁN & MỞ BÁN #{run_num}"
    msg["From"] = f"Senior Legal Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'tables'])
    
    full_html = f"""
    <html>
      <head>
        <style>
            body {{ font-family: 'Times New Roman', Times, serif; background-color: #f2f4f7; padding: 20px; line-height: 1.8; color: #1c1e21; }}
            .container {{ max-width: 950px; margin: 0 auto; background: #ffffff; padding: 50px; border-top: 12px solid #002d5e; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-radius: 4px; }}
            h1 {{ color: #002d5e; text-align: center; font-size: 26px; border-bottom: 2px solid #eee; padding-bottom: 20px; text-transform: uppercase; }}
            h2 {{ color: #0056b3; border-left: 6px solid #002d5e; padding-left: 15px; margin-top: 40px; font-size: 20px; background: #f8f9fa; padding-top: 5px; padding-bottom: 5px; }}
            h3 {{ color: #a91e2c; font-size: 18px; margin-top: 25px; font-weight: bold; }}
            p, li {{ text-align: justify; margin-bottom: 12px; font-size: 16px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 25px 0; }}
            table, th, td {{ border: 1px solid #dee2e6; padding: 15px; text-align: left; }}
            th {{ background-color: #e9ecef; color: #002d5e; font-weight: bold; text-transform: uppercase; font-size: 14px; }}
            .footer {{ text-align: center; font-size: 12px; color: #6c757d; margin-top: 60px; border-top: 1px solid #eee; padding-top: 20px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>THÔNG TIN THAM MƯU PHÁP LÝ DỰ ÁN BĐS</h1>
            <p style="text-align: center;">Thực hiện riêng cho: <strong>Vũ Quang Phát</strong></p>
            <div class="content">{html_body}</div>
            <div class="footer">
                Tài liệu lưu hành nội bộ - Bảo mật cao<br>
                Hệ thống Cố vấn AI tự động | Vận hành bởi Gemini API
            </div>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, pwd)
            server.sendmail(sender, sender, msg.as_string())
        print("Đã gửi báo cáo tham mưu cao cấp thành công!")
    except Exception as e:
        print(f"Lỗi gửi mail: {e}")

if __name__ == "__main__":
    news = get_real_estate_news()
    report = get_ai_report(news)
    send_email(report)
