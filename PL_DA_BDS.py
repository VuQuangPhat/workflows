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
    """Phân tích AI: Chuyên gia cố vấn vĩ mô & vi mô, từ CTCTĐT đến khâu mở bán dự án"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là Chuyên gia Cố vấn Pháp lý BĐS cấp cao, tham mưu trực tiếp cho Vũ Quang Phát.
Nhiệm vụ: Lập báo cáo CHIẾN LƯỢC TOÀN DIỆN từ khâu CTCTĐT đến khâu ĐỦ ĐIỀU KIỆN MỞ BÁN sản phẩm.

BỘ QUY TẮC CỐT LÕI (TUÂN THỦ 100%):

1. TẦM NHÌN CỐ VẤN VĨ MÔ & VI MÔ:
   - Vĩ mô: Đánh giá sự giao thoa giữa hạ tầng miền Nam và chính sách pháp luật mới (Luật Đất đai 31/2024, Luật Đầu tư 143/2025, NQ 171/2024).
   - Vi mô (Quy trình ISO): Chỉ rõ điểm nghẽn tại bàn chuyên viên Sở Tài chính (định giá), Sở Nông nghiệp và Môi trường (nguồn gốc đất), Sở Xây dựng (điều kiện bán hàng).

2. SO SÁNH CHIẾN LƯỢC: 
   - [Bắt buộc] Phải có bảng so sánh lợi thế/rủi ro giữa triển khai dự án theo Luật Đầu tư (đấu thầu/đấu giá) và Nghị quyết 171 (thỏa thuận nhận QSDĐ).

3. CHẤN CHỈNH TƯ DUY CMĐSDĐ & LỘ TRÌNH MỞ BÁN:
   - NQ 171 là công cụ CMĐ từ đất nông nghiệp/phi nông nghiệp sang ĐẤT Ở.
   - Lộ trình bán hàng: Phải qua bước: Có CTCTĐT -> Giao đất/CMĐSDĐ -> Nộp tiền sử dụng đất -> Có sổ hồng tổng -> Xong móng/hạ tầng -> Giấy phép bán hàng của Sở Xây dựng.

4. ĐỊA GIỚI & BỘ MÁY (SAU 01/07/2025):
   - Tuyệt đối không dùng "UBND quận", "tỉnh Bình Dương", "tỉnh Bà Rịa - Vũng Tàu".
   - Thẩm quyền: UBND TP.HCM/Thành phố trực thuộc; Sở Nông nghiệp và Môi trường; Sở Tài chính; Sở Xây dựng.

5. RỦI RO & KHẮC PHỤC:
   - Phân tích rủi ro "Đất da báo" (thỏa thuận bế tắc) và rủi ro trượt giá nghĩa vụ tài chính hậu sáp nhập. Đưa ra cách khắc phục cụ thể.

Dữ liệu thô từ báo chí: {news_data}

CẤU TRÚC BÁO CÁO (Markdown):
* [Dòng 1] "Thời gian lập báo cáo: {current_time}"
* TIÊU ĐỀ BƯỚC CHECK (Vĩ mô - Bức tranh hạ tầng & chính sách miền Nam): Đánh giá tác động đến giá bán và sức mua của dự án.
* TIÊU ĐỀ BƯỚC PLAN (So sánh Chiến lược & Nút thắt quy trình): Bảng so sánh LĐT vs NQ 171. Chỉ rõ lộ trình từ CTCTĐT đến Mở bán kẹt ở khâu nào.
* TIÊU ĐỀ BƯỚC DO (Thực chiến NQ 171 - Quản trị rủi ro gom đất & CMĐSDĐ): Phân tích Case Study gom đất nông nghiệp/phi nông nghiệp. Giải pháp gỡ nút thắt tại Sở Nông nghiệp và Môi trường để có "Sổ hồng dự án".
* TIÊU ĐỀ BƯỚC ACT (Giải pháp Cố vấn - Action Plan Mở bán): Chọn 1 rủi ro (Ví dụ: Chậm nộp tiền sử dụng đất). Phân tích IRAC và Action Plan gỡ rối.
* TIÊU ĐỀ BƯỚC 5: TỪ VỰNG TIẾNG ANH (B1-B2) & UK IDIOM: 5 từ vựng bán hàng & 1 thành ngữ kinh doanh.
"""

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        raw_report = response.text
                
        # --- BỘ LỌC CƯỠNG CHẾ PYTHON (Bảo mật tên địa phương & cơ quan) ---
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
    msg["Subject"] = f"[PHÁP LÝ BĐS] BÁO CÁO CHIẾN LƯỢC MỞ BÁN #{run_num}"
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
            <p style="text-align: center;">Cố vấn chuyên môn: <b>Vũ Quang Phát</b></p>
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
