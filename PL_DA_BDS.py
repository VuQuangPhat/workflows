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
    
    # PROMPT ĐƯỢC NÂNG CẤP: LINH ĐỘNG CẤU TRÚC, ÉP ĐƯA BẢNG TIẾN ĐỘ & NÚT THẮT
    prompt = f"""
Bạn là Trợ lý Cố vấn Pháp lý BĐS chuyên nghiệp, làm việc dưới sự chỉ đạo của Chuyên viên pháp lý dự án Vũ Quang Phát.
Nhiệm vụ: Lập báo cáo TỔNG HỢP, CẬP NHẬT CHÍNH SÁCH & THAM MƯU CHIẾN LƯỢC định kỳ.

THỜI GIAN LẬP BÁO CÁO: {current_time}

BỘ QUY TẮC CỐT LÕI (TUÂN THỦ TUYỆT ĐỐI 100%):
1. ĐỊA GIỚI & BỘ MÁY (SAU 01/07/2025): NQ 202/2025 sáp nhập Bình Dương, BR-VT vào TP.HCM. Cấm dùng "UBND Quận". Bắt buộc dùng: "Sở Nông nghiệp và Môi trường" (Đất đai), "Sở Tài chính" (Giá đất), "Sở Xây dựng".
2. BẢN CHẤT NQ 171: Chỉ dùng để chuyển mục đích từ ĐẤT KHÁC sang ĐẤT Ở. Tuyệt đối không phân tích chung cư cũ.
3. LUẬT MỚI LIÊN THÔNG: Phân tích dựa trên sự đồng bộ của Luật Đầu tư 143, Luật Đất đai 31, Luật Xây dựng 135, Luật KDBĐS 29.
4. NGOẠI NGỮ B1: Chỉ sử dụng các từ vựng tiếng Anh chuyên ngành ở mức độ B1 (Ví dụ: Deposit, Lease, Permit...) và 1 UK Idiom. KHÔNG dùng từ C1/C2 phức tạp.

Dữ liệu thô từ báo chí hôm nay: {news_data}

YÊU CẦU CẤU TRÚC (LINH ĐỘNG VÀ THỰC CHIẾN):
Bạn được TOÀN QUYỀN TỰ QUYẾT ĐỊNH việc chia các tiêu đề (Heading) sao cho logic, mạch lạc và phù hợp nhất với luồng thông tin nhận được. KHÔNG CẦN phải chia theo kiểu "Bước 1, Bước 2". 
Tạo ra một báo cáo đọc tự nhiên như một chuyên gia đang trình bày. Tuy nhiên, TRONG BÁO CÁO BẮT BUỘC PHẢI CHỨA CÁC KHỐI NỘI DUNG SAU:

- Khối 1: Đánh giá Tác động Chính sách & Vĩ mô từ tin tức (Giá vốn, chi phí đền bù, sức mua).
- Khối 2 [QUAN TRỌNG NHẤT]: Bảng hoặc Sơ đồ phân tích LỘ TRÌNH, THẨM QUYỀN VÀ NÚT THẮT THỰC TẾ. Phân tích rõ các bước từ lúc gom đất, CTCTĐT đến khi Mở bán theo NQ 171. Chỉ đích danh quy trình đang hoặc sẽ bị kẹt ở khâu nào tại Sở Nông nghiệp và Môi trường (rà soát nguồn gốc) hay Sở Tài chính (định giá đất). Đề xuất ngay GIẢI PHÁP THỰC CHIẾN để gỡ nút thắt đó.
- Khối 3: Quản trị rủi ro "Đất da báo" (nếu có thông tin liên quan đến gom đất).
- Khối 4: Giải pháp tình huống IRAC cho một rủi ro cốt lõi nhất từ tin tức trong ngày.
- Khối 5: 5 từ vựng B1 & 1 UK Idiom.

Đầu báo cáo luôn bắt đầu bằng dòng: "Thời gian lập báo cáo: {current_time}"
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
    msg["Subject"] = f"[PHÁP LÝ BĐS] BÁO CÁO CẬP NHẬT CHÍNH SÁCH & CHIẾN LƯỢC MỞ BÁN #{run_num}"
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
