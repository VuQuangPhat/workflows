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
    """Trợ lý AI xử lý dữ liệu: Áp dụng tư duy Cố vấn Chiến lược & Lọc từ khóa"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là Trợ lý Cố vấn Pháp lý BĐS chuyên nghiệp, làm việc dưới sự chỉ đạo của Chuyên viên pháp lý dự án Vũ Quang Phát.
Nhiệm vụ: Lập báo cáo TỔNG HỢP & THAM MƯU CHIẾN LƯỢC định kỳ, tập trung vào LỘ TRÌNH MỞ BÁN dự án.

THỜI GIAN LẬP BÁO CÁO: {current_time}

BỘ QUY TẮC CỐT LÕI (TUÂN THỦ TUYỆT ĐỐI 100%):

1. ĐỊA GIỚI & BỘ MÁY HÀNH CHÍNH (SAU 01/07/2025):
   - NQ 202/2025: Bình Dương, Bà Rịa - Vũng Tàu đã sáp nhập vào TP.HCM. 
   - CẤM TUYỆT ĐỐI dùng "UBND Quận", "Ủy ban nhân dân quận". Mọi thẩm quyền cấp cơ sở thuộc "UBND TP.HCM/Thành phố trực thuộc".
   - BẮT BUỘC dùng tên cơ quan chuyên môn mới: "Sở Nông nghiệp và Môi trường" (Đất đai/Bồi thường), "Sở Tài chính" (Đầu tư/Giá đất), "Sở Xây dựng" (Quy hoạch/Điều kiện bán hàng).

2. BẢN CHẤT NQ 171/2024/QH15 & CMĐSDĐ:
   - Cơ chế NQ 171 CHỈ dùng để chuyển mục đích từ ĐẤT KHÁC (nông nghiệp, phi nông nghiệp) sang ĐẤT Ở làm dự án nhà ở thương mại. Tuyệt đối không phân tích chung cư cũ.

3. TƯ DUY CỐ VẤN CHIẾN LƯỢC (VĨ MÔ & VI MÔ):
   - Mọi lộ trình phân tích phải hướng tới vạch đích: Đủ điều kiện MỞ BÁN sản phẩm.
   - Vi mô: Phải soi thấu điểm nghẽn (tắc ở khâu Sở Tài chính định giá, hay Sở Nông nghiệp & Môi trường rà soát nguồn gốc đất).
   - [Bắt buộc] So sánh hiệu quả tài chính và tiến độ: Đầu tư theo LĐT (Đấu thầu/đấu giá) vs Đầu tư theo NQ 171 (Thỏa thuận gom đất).

Dữ liệu thô từ báo chí hôm nay: {news_data}

CẤU TRÚC BÁO CÁO (Markdown chuyên nghiệp):
* [Dòng 1] "Thời gian lập báo cáo: {current_time}"
* TIÊU ĐỀ BƯỚC CHECK (Vĩ mô - Bức tranh Hạ tầng & Chính sách Miền Nam): Tác động của tin tức đến giá vốn, chi phí đền bù và sức mua của dự án.
* TIÊU ĐỀ BƯỚC PLAN (Vi mô - So sánh & Nút thắt quy trình): Bảng so sánh chiến lược LĐT vs NQ 171. Chỉ rõ lộ trình từ CTCTĐT đến Mở bán đang có nguy cơ kẹt ở khâu nào tại Sở chuyên môn.
* TIÊU ĐỀ BƯỚC DO (Thực chiến NQ 171 - Quản trị rủi ro gom đất & CMĐSDĐ): Giải pháp khắc phục rủi ro "Đất da báo" (không thỏa thuận được 100%) và cách gỡ nút thắt tại Sở Nông nghiệp và Môi trường để có "Sổ hồng tổng".
* TIÊU ĐỀ BƯỚC ACT (Giải pháp Cố vấn - Action Plan Về đích): Chọn 1 rủi ro vi mô (VD: Giá đất hậu sáp nhập tăng cao làm chậm nộp tiền sử dụng đất). Phân tích cấu trúc IRAC và đề xuất 3 bước hành động cụ thể cho CĐT.
* TIÊU ĐỀ BƯỚC 5: TỪ VỰNG TIẾNG ANH (B1-B2) & UK IDIOM: 5 từ vựng chuyên ngành Mở bán BĐS & 1 thành ngữ thương mại Anh Quốc.
"""

    try:
        # Lựa chọn model thông minh, ưu tiên Flash để có tốc độ và độ ổn định cao
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models_to_try = sorted(available_models, key=lambda x: (0 if 'flash' in x else (1 if 'pro' in x else 2)))
        
        raw_report = "AI Generation Failed."
        for model_name in models_to_try:
            try:
                # Bỏ qua các phiên bản 1.0 cũ
                if "1.0" in model_name: continue 
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                raw_report = response.text
                break
            except Exception as e:
                print(f"Lỗi khi thử model {model_name}: {e}")
                continue
                
        # --- BỘ LỌC CƯỠNG CHẾ PYTHON (BẢO VỆ TUYỆT ĐỐI) ---
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
    """Biên dịch Markdown sang HTML và Gửi Email nội bộ"""
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[PHÁP LÝ BĐS] BÁO CÁO CHIẾN LƯỢC MỞ BÁN #{run_num}"
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
            <h1>BÁO CÁO TỔNG HỢP & THAM MƯU CHIẾN LƯỢC</h1>
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
