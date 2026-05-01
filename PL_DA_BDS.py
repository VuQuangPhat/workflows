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
    """Thu thập tin tức chuyên sâu về Pháp lý, Chính sách và Bất động sản"""
    sources = {
        "Chính phủ": "https://baochinhphu.vn/rss/phap-luat.rss",
        "Thư viện Pháp luật": "https://thuvienphapluat.vn/rss/tin-tuc.rss",
        "Pháp luật (PLO)": "https://plo.vn/rss/phap-luat.rss",
        "Bất động sản (PLO)": "https://plo.vn/rss/bat-dong-san.rss",
        "BĐS (VnExpress)": "https://vnexpress.net/rss/bat-dong-san.rss",
        "Kinh tế (Tuổi Trẻ)": "https://tuoitre.vn/rss/kinh-doanh.rss"
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
            print(f"Lỗi khi tải nguồn {cat}: {e}")
            continue
    return summary

def get_ai_report(news_data):
    """Phân tích AI: Cố vấn chiến lược từ CTCTĐT đến Mở bán (Sales Eligibility)"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là Chuyên gia Cố vấn Pháp lý BĐS cấp cao, tham mưu trực tiếp cho Vũ Quang Phát.
Nhiệm vụ: Lập báo cáo CHIẾN LƯỢC TOÀN DIỆN từ khâu CTCTĐT đến khâu ĐỦ ĐIỀU KIỆN MỞ BÁN sản phẩm.

BỘ QUY TẮC CỐT LÕI (TUÂN THỦ 100%):

1. LỘ TRÌNH VỀ ĐÍCH (MỞ BÁN DỰ ÁN):
   - Phân tích xuyên suốt: CTCTĐT -> Giao đất/CMĐSDĐ -> Nộp tiền sử dụng đất -> Có sổ hồng tổng -> Giấy phép xây dựng -> Văn bản đủ điều kiện mở bán của Sở Xây dựng.
   - So sánh trực diện: Bảng đối chiếu lợi ích/rủi ro giữa DA theo Luật Đầu tư (đấu thầu/đấu giá) và NQ 171 (thỏa thuận nhận quyền).

2. CHẤN CHỈNH TƯ DUY CMĐSDĐ & NQ 171/2024/QH15:
   - NQ 171 là công cụ CMĐ từ đất nông nghiệp/phi nông nghiệp sang ĐẤT Ở để bán nhà ở thương mại. Tuyệt đối không lấy ví dụ chung cư cũ.
   - Rủi ro & Khắc phục: Xử lý bài toán "đất da báo" và biến động giá đất tại Sở Tài chính hậu sáp nhập địa giới.

3. ĐỊA GIỚI & BỘ MÁY (SAU 01/07/2025):
   - Tuyệt đối không dùng "UBND quận", "tỉnh Bình Dương", "tỉnh Bà Rịa - Vũng Tàu".
   - Thẩm quyền: UBND TP.HCM/Thành phố trực thuộc; Sở Nông nghiệp và Môi trường (Đất đai); Sở Tài chính (Đầu tư/Giá đất); Sở Xây dựng (Quy hoạch/Bán hàng).

4. CHIẾN LƯỢC VI MÔ: Chỉ rõ điểm nghẽn tại bàn chuyên viên Sở ngành đang làm chậm lộ trình bán hàng.

Dữ liệu thô từ báo chí: {news_data}

CẤU TRÚC BÁO CÁO (Markdown):
* [Dòng 1] "Thời gian lập báo cáo: {current_time}"
* TIÊU ĐỀ BƯỚC CHECK (Vĩ mô - Hạ tầng & Sức mua miền Nam): Tác động đến thanh khoản và giá bán dự án.
* TIÊU ĐỀ BƯỚC PLAN (So sánh Chiến lược & Nút thắt quy trình): Bảng so sánh LĐT vs NQ 171. Lộ trình từ CTCTĐT đến Mở bán kẹt ở khâu nào?
* TIÊU ĐỀ BƯỚC DO (Thực chiến NQ 171 - Gom đất & CMĐSDĐ): Giải pháp gỡ nút thắt tại Sở Nông nghiệp và Môi trường để có "Sổ hồng dự án".
* TIÊU ĐỀ BƯỚC ACT (Giải pháp Cố vấn - Quản trị rủi ro Về đích): Phân tích IRAC cho rủi ro chậm nộp tiền sử dụng đất ảnh hưởng điều kiện mở bán. Action Plan 3 bước cụ thể.
* TIÊU ĐỀ BƯỚC 5: TỪ VỰNG TIẾNG ANH (B1-B2) & UK IDIOM: 5 từ vựng bán hàng & 1 thành ngữ.
"""

    try:
        # --- KHẮC PHỤC LỖI 404: Tự động chọn model khả dụng ---
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models_to_try = sorted(available_models, key=lambda x: (0 if 'flash' in x else (1 if 'pro' in x else 2)))
        
        raw_report = "AI Generation Failed."
        for model_name in models_to_try:
            try:
                # Bỏ qua các model version 1.0 cũ không tương thích tốt
                if "1.0" in model_name: continue 
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                raw_report = response.text
                break
            except:
                continue
                
        # --- BỘ LỌC CƯỠNG CHẾ PYTHON (Bảo mật địa danh & cơ quan) ---
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở TN&MT": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "Sở KH&ĐT": "Sở Tài chính",
            "UBND quận": "UBND TP.HCM/Thành phố trực thuộc",
            "Ủy ban nhân dân quận": "UBND TP.HCM/Thành phố trực thuộc",
            "tỉnh Bình Dương": "TP.HCM",
            "tỉnh Bà Rịa": "TP.HCM",
            "UBND Quận": "UBND TP.HCM/Thành phố trực thuộc"
        }
        
        cleaned_report = raw_report
        for old, new in replacements.items():
            pattern = re.compile(re.escape(old), re.IGNORECASE)
            cleaned_report = pattern.sub(new, cleaned_report)
            
        return cleaned_report
        
    except Exception as e:
        return f"System Error: {str(e)}"

def send_email(markdown_content):
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[PHÁP LÝ BĐS] LỘ TRÌNH CHIẾN LƯỢC MỞ BÁN #{run_num}"
    msg["From"] = f"Real Estate Legal Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'tables'])
    
    full_html = f"""
    <html>
      <head>
        <style>
            body {{ font-family: 'Times New Roman', serif; background-color: #f4f7f6; padding: 30px; line-height: 1.8; color: #1a1a1a; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #fff; padding: 50px; border-top: 10px solid #004d40; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            h1 {{ color: #004d40; text-align: center; text-transform: uppercase; font-size: 22px; border-bottom: 2px solid #eee; padding-bottom: 20px; }}
            h2 {{ color: #004d40; border-bottom: 2px solid #004d40; padding-bottom: 5px; margin-top: 40px; font-size: 19px; text-transform: uppercase; }}
            h3 {{ color: #bf360c; font-size: 17px; margin-top: 20px; font-weight: bold; }}
            p, li {{ text-align: justify; margin-bottom: 15px; font-size: 16px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #fafafa; }}
            table, th, td {{ border: 1px solid #ccc; padding: 12px; text-align: left; }}
            th {{ background-color: #e0f2f1; color: #004d40; }}
            .footer {{ text-align: center; font-size: 11px; color: #888; margin-top: 50px; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>BÁO CÁO CHIẾN LƯỢC PHÁP LÝ & LỘ TRÌNH MỞ BÁN</h1>
            <p style="text-align: center;">Cố vấn chiến lược: <b>Vũ Quang Phát</b></p>
            <div class="content">{html_body}</div>
            <div class="footer">Hệ thống phân tích tự động | Gemini AI & GitHub Actions</div>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, pwd)
            server.sendmail(sender, sender, msg.as_string())
        print("Gửi email thành công!")
    except Exception as e:
        print(f"Lỗi gửi mail: {e}")

if __name__ == "__main__":
    news = get_real_estate_news()
    report = get_ai_report(news)
    send_email(report)
