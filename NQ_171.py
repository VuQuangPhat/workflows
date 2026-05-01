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
    """Trợ lý AI chuyên sâu: Bóc tách chi tiết quy trình NQ 171 và Lộ trình thực chiến"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    # PROMPT TẬP TRUNG TRỌNG TÂM VÀO NQ 171
    prompt = f"""
Bạn là Trợ lý Cố vấn Pháp lý BĐS cấp cao. Nhiệm vụ trọng tâm: Phân tích chi tiết quy trình thí điểm theo **NGHỊ QUYẾT 171**.

THỜI GIAN LẬP BÁO CÁO: {current_time}

BỘ QUY TẮC NỘI DUNG (TUÂN THỦ TUYỆT ĐỐI):

1. TRỌNG TÂM NQ 171 (THỎA THUẬN GOM ĐẤT):
   - Phân tích chi tiết điều kiện áp dụng NQ 171: Loại đất (không chỉ đất ở), quy hoạch, phù hợp chương trình nhà ở.
   - Làm rõ quy trình "Thỏa thuận nhận quyền sử dụng đất": Cách xác lập văn bản thỏa thuận, thời điểm đặt cọc (Deposit) và rủi ro pháp lý khi dân "quay xe".

2. LỘ TRÌNH 11 BƯỚC MỞ BÁN THEO NQ 171:
   Mô tả chi tiết quá trình từ "Thỏa thuận" đến "Văn bản đủ điều kiện bán hàng":
   - Bước 1-3: Chấp thuận chủ trương đầu tư (Sở Tài chính thẩm định năng lực) & Công nhận Chủ đầu tư.
   - Bước 4-7: Quy hoạch 1/500, Chuyển mục đích sử dụng đất, thẩm định giá đất (Valuation) tại Sở Tài chính.
   - Bước 8-11: Hoàn thành nghĩa vụ tài chính, Giấy phép xây dựng (Permit), Nghiệm thu hạ tầng và thông báo mở bán.

3. ĐIỂM NGHẼN SỞ NGÀNH:
   - Nút thắt cực đại tại **Sở Tài chính**: Thẩm định giá đất cụ thể hậu sáp nhập NQ 202.
   - Vai trò rà soát nguồn gốc đất của **Sở Nông nghiệp và Môi trường** để khớp với tiêu chuẩn NQ 171.

4. YÊU CẦU TRÌNH BÀY:
   - Sử dụng BẢNG SO SÁNH/TIẾN ĐỘ cho quy trình 11 bước.
   - Phân tích IRAC cho rủi ro: "Dự án tắc nghẽn do không đạt thỏa thuận 100% diện tích đất (vùng da báo)".
   - Ngôn ngữ: 5 từ vựng B1 (Procedure, Contract, Compliance, Lease, Regulation) và 1 UK Idiom (ví dụ: 'The devil is in the detail').

5. ĐỊA GIỚI: Bình Dương, BR-VT đã vào TP.HCM. Tuyệt đối không dùng từ "tỉnh", không dùng "Quận".

Dữ liệu thô: {news_data}
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
            except Exception:
                continue
                
        # --- BỘ LỌC CƯỠNG CHẾ THUẬT NGỮ PHÁP LÝ ---
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở TN&MT": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "Sở KH&ĐT": "Sở Tài chính",
            "UBND quận": "UBND TP.HCM/Thành phố trực thuộc",
            "tỉnh Bình Dương": "TP.HCM",
            "tỉnh Bà Rịa": "TP.HCM",
            "tỉnh BR-VT": "TP.HCM"
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
            .container {{ max-width: 950px; margin: 0 auto; background: #fff; padding: 50px; border-top: 10px solid #1a237e; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-radius: 4px; }}
            h1 {{ color: #1a237e; text-align: center; text-transform: uppercase; font-size: 24px; border-bottom: 2px solid #eee; padding-bottom: 20px; }}
            h2 {{ color: #1a237e; border-left: 5px solid #1a237e; padding-left: 15px; margin-top: 40px; font-size: 20px; text-transform: uppercase; }}
            h3 {{ color: #b71c1c; font-size: 18px; margin-top: 25px; font-weight: bold; }}
            p, li {{ text-align: justify; margin-bottom: 15px; font-size: 16px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 25px 0; }}
            table, th, td {{ border: 1px solid #cfd8dc; padding: 15px; text-align: left; }}
            th {{ background-color: #f5f5f5; color: #1a237e; font-weight: bold; }}
            .footer {{ text-align: center; font-size: 12px; color: #7f8c8d; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>BÁO CÁO CHIẾN LƯỢC: QUY TRÌNH NQ 171 & LỘ TRÌNH THỰC CHIẾN</h1>
            <p style="text-align: center; font-weight: bold;">Người phụ trách chuyên môn: Vũ Quang Phát (ULAW)</p>
            <div class="content">{html_body}</div>
            <div class="footer">Báo cáo tự động hóa | Vận hành bởi Gemini AI cho mục đích Pháp lý BĐS chuyên sâu</div>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, pwd)
            server.sendmail(sender, sender, msg.as_string())
        print("Trợ lý đã gửi báo cáo chiến lược NQ 171 thành công!")
    except Exception as e:
        print(f"Lỗi gửi mail: {e}")

if __name__ == "__main__":
    news = get_real_estate_news()
    report = get_ai_report(news)
    send_email(report)
