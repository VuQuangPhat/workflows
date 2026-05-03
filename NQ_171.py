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
            # Lấy tin trong vòng 48h để đảm bảo tính tức thời
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
    
    # --- "HIẾN PHÁP" THAM MƯU CHO CHUYÊN GIA VŨ QUANG PHÁT ---
    prompt = f"""
QUY TRÌNH XỬ LÝ ƯU TIÊN: Bạn PHẢI xác thực trạng thái hiệu lực hiện hành của văn bản. 
LƯU Ý ĐẶC BIỆT: Luật Đất đai 2024, Luật Nhà ở 2023, Luật Kinh doanh BĐS 2023 đều đã có hiệu lực từ ngày 01/08/2024.

1. Vai trò và Bản sắc:
Bạn là Cố vấn Pháp lý cao cấp, tham mưu trực tiếp cho chuyên gia Vũ Quang Phát. 
PHẠM VI TƯ VẤN ĐỘC QUYỀN: Vòng đời dự án đầu tư BĐS (Khảo sát, Gom đất, NQ 171, Chủ trương đầu tư, 1/500, Định giá đất, GPXD đến khi MỞ BÁN).
LOẠI BỎ HOÀN TOÀN: Tin tức quản lý vận hành (nhà trọ, điện nước), nông sản, du lịch. Chỉ giữ lại tin tác động đến CHI PHÍ, TIẾN ĐỘ và RỦI RO pháp lý dự án.

2. Nguyên tắc nội dung:
- Ma trận liên thông: Lấy NQ 171 làm lõi nhưng PHẢI liên kết với Luật Đất đai, Đầu tư, Xây dựng, Quy hoạch để tìm hướng mở.
- Độ sâu chuyên môn: Giải thích "bản chất pháp lý", "ý đồ nhà lập pháp" và "hệ quả thực tế". Không trích dẫn suông.
- Ngôn ngữ: Tiếng Việt chuyên ngành. Tiếng Anh trình độ B1 (Project, Permit, Deposit, Lease, Ownership, Sales, Cash Flow).
- Địa giới (Hậu 01/07/2025): Bình Dương, BR-VT thuộc TP.HCM. Dùng đúng tên: Sở Nông nghiệp và Môi trường (Đất đai), Sở Tài chính (Định giá đất), Sở Xây dựng (Quy hoạch/Mở bán).

3. Cấu trúc phản hồi linh hoạt (Dynamic Structure):
- Không dùng form cố định. Tự chia vấn đề trọng tâm dựa trên tin tức nóng nhất.
- BẮT BUỘC dùng mô hình IRAC (Issue - Rule - Application - Conclusion) cho các nút thắt dự án. Phần Conclusion phải là chiến thuật tháo gỡ 1:1, thực chiến.
- Danh mục Căn cứ pháp lý (Số hiệu, Ngày ban hành, Hiệu lực) phải liệt kê rõ ràng ở đầu báo cáo.

DỮ LIỆU ĐẦU VÀO HÔM NAY: {news_data}
"""

    try:
        # Cơ chế tự chọn model khả dụng để tránh lỗi 404
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
            except Exception as e:
                continue
                
        # Bộ lọc Python cưỡng chế tên cơ quan và địa giới
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
    """Gửi Email với giao diện Báo cáo Tham mưu Cao cấp"""
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[CỐ VẤN CHIẾN LƯỢC] BÁO CÁO DỰ ÁN & MỞ BÁN #{run_num}"
    msg["From"] = f"Senior Legal Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'tables'])
    
    full_html = f"""
    <html>
      <head>
        <style>
            body {{ font-family: 'Times New Roman', Times, serif; background-color: #f4f7f9; padding: 25px; line-height: 1.8; color: #1a1a1a; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #ffffff; padding: 50px; border-top: 12px solid #1a5276; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-radius: 4px; }}
            h1 {{ color: #1a5276; text-align: center; font-size: 26px; border-bottom: 2px solid #eee; padding-bottom: 20px; text-transform: uppercase; }}
            h2 {{ color: #1a5276; border-left: 6px solid #1a5276; padding-left: 15px; margin-top: 40px; font-size: 20px; background: #f9f9f9; padding-top: 5px; padding-bottom: 5px; }}
            h3 {{ color: #c0392b; font-size: 18px; margin-top: 25px; font-weight: bold; }}
            p, li {{ text-align: justify; margin-bottom: 12px; font-size: 16px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 25px 0; }}
            table, th, td {{ border: 1px solid #dee2e6; padding: 15px; text-align: left; }}
            th {{ background-color: #ecf0f1; color: #1a5276; font-weight: bold; text-transform: uppercase; }}
            .footer {{ text-align: center; font-size: 12px; color: #7f8c8d; margin-top: 60px; border-top: 1px solid #eee; padding-top: 20px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>THÔNG TIN THAM MƯU CHIẾN LƯỢC DỰ ÁN BĐS</h1>
            <p style="text-align: center;">Thực hiện riêng cho chuyên gia: <strong>Vũ Quang Phát</strong></p>
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
        print("Đã gửi báo cáo chiến lược cao cấp thành công!")
    except Exception as e:
        print(f"Lỗi gửi mail: {e}")

if __name__ == "__main__":
    news = get_real_estate_news()
    report = get_ai_report(news)
    send_email(report)
