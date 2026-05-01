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
    """Phân tích dữ liệu bằng AI: Tích hợp Bộ lọc Cưỡng chế Tên Cơ quan"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là Trợ lý AI cấp cao chuyên về Pháp lý Bất động sản, hỗ trợ trực tiếp cho Chuyên viên pháp lý dự án BĐS: Vũ Quang Phát.
Nhiệm vụ: Lập báo cáo THỰC CHIẾN, KHÔNG LÝ THUYẾT, tuân thủ ISO (PDCA), bám sát pháp lý và địa lý mới nhất.

THỜI GIAN LẬP BÁO CÁO: {current_time}

LƯU Ý CỐT LÕI (BẮT BUỘC TUÂN THỦ MỆNH LỆNH 100%):
1. CƠ CẤU TỔ CHỨC MỚI (BẮT BUỘC DÙNG CÁC TÊN NÀY CHO THẨM QUYỀN):
   - Phụ trách Đất đai, Bồi thường, Giao đất, Môi trường: Gọi là "Sở Nông nghiệp và Môi trường".
   - Phụ trách Đầu tư, Thẩm định CTCTĐT, Đấu thầu: Gọi là "Sở Tài chính".
   - Phụ trách Quy hoạch, Kiến trúc, Cấp phép: Gọi là "Sở Xây dựng".
   - (Tuyệt đối chỉ dùng 3 tên Sở trên khi nhắc đến cơ quan chuyên môn cấp tỉnh).

2. ĐỊA GIỚI HÀNH CHÍNH (NGHỊ QUYẾT 202/2025/QH15):
   - Toàn bộ Bình Dương và Bà Rịa - Vũng Tàu đã thuộc TP.HCM. Thẩm quyền cấp tỉnh cao nhất nay là UBND TP.HCM. Không gọi là tỉnh Bình Dương. (Ví dụ: TP. Thủ Dầu Một trực thuộc TP.HCM). Đồng Nai và Long An vẫn là tỉnh độc lập.

3. KHÔNG VĂN MẪU LÝ THUYẾT: Đi thẳng vào VẤN ĐỀ THỰC TẾ của CĐT và HƯỚNG GIẢI QUYẾT.

4. ĐIỂM NÓNG HẠ TẦNG & LUẬT MỚI: 
   - Phân tích ảnh hưởng của Sân bay Long Thành, Vành đai 3, 4 đến các dự án đang xin CTCTĐT theo Luật Đầu tư 143/2025/QH15.
   - NQ 171/2024/QH15: Phân tích thực tế gom đất thỏa thuận làm Nhà ở thương mại.
   - Các luật: Luật Xây dựng 135/2025/QH15; Luật KDBĐS 29/2023/QH15; Luật Đất đai 31/2024/QH15.

5. TIẾNG ANH CHUYÊN NGÀNH: CHỈ dùng từ vựng B1 - B2, thông dụng (Tenant, Landlord, Deposit, Contract, Permit...).

Dữ liệu thô từ báo chí: {news_data}

CẤU TRÚC BÁO CÁO DỰ KIẾN (Markdown, Tùy biến tiêu đề linh hoạt):
* [Dòng 1] "Thời gian lập báo cáo: {current_time}"
* TIÊU ĐỀ BƯỚC CHECK (Cảnh báo Pháp lý 24h): Tin tức trọng tâm. Thẩm quyền rà soát thuộc về ai.
* TIÊU ĐỀ BƯỚC PLAN (Tiến độ CTCTĐT & Hạ tầng): Case Study thực tế tại TP.HCM (vùng Bình Dương/BR-VT cũ), Đồng Nai hoặc Long An xin CTCTĐT theo Luật Đầu tư 143/2025. Thẩm quyền giải quyết của Sở Tài chính và UBND.
* TIÊU ĐỀ BƯỚC DO (Thực chiến NQ 171/2024/QH15): Bài toán thỏa thuận đền bù quỹ đất. Vướng mắc & Quy trình gỡ rối của Sở Nông nghiệp và Môi trường.
* TIÊU ĐỀ BƯỚC ACT (IRAC Plan trình Ban Giám đốc): Xử lý 1 vướng mắc. Cấu trúc IRAC. Conclusion là Action Plan cụ thể.
* TIÊU ĐỀ BƯỚC 5: TỪ VỰNG TIẾNG ANH (B1-B2) & UK IDIOM: 5 từ vựng (Bảng) & 1 thành ngữ.
"""

    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models_to_try = sorted(available_models, key=lambda x: (0 if 'flash' in x else (1 if 'pro' in x else 2)))
        
        raw_report = "AI Generation Failed."
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                raw_report = response.text
                break
            except:
                continue
                
        # --- BỘ LỌC CƯỠNG CHẾ BẰNG PYTHON (Đảm bảo 100% không sót tên Sở cũ) ---
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở TN&MT": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "Sở KH&ĐT": "Sở Tài chính",
            "Sở Kế hoạch Đầu tư": "Sở Tài chính",
            "Sở Quy hoạch - Kiến trúc": "Sở Xây dựng",
            "Sở Quy hoạch và Kiến trúc": "Sở Xây dựng",
            "Sở QH-KT": "Sở Xây dựng"
        }
        
        cleaned_report = raw_report
        for old_term, new_term in replacements.items():
            cleaned_report = cleaned_report.replace(old_term, new_term)
            
        return cleaned_report
        
    except Exception as e:
        return f"System Error: {str(e)}"

def send_email(markdown_content):
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[PHÁP LÝ BĐS] BÁO CÁO CẬP NHẬT DỰ ÁN #{run_num}"
    msg["From"] = f"Real Estate Legal AI <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'tables'])
    
    full_html = f"""
    <html>
      <head>
        <style>
            body {{ font-family: 'Times New Roman', serif; background-color: #f4f7f6; padding: 30px; line-height: 1.8; color: #1a1a1a; }}
            .container {{ max-width: 850px; margin: 0 auto; background: #fff; padding: 50px; border-top: 10px solid #8b0000; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            h1 {{ color: #8b0000; text-align: center; text-transform: uppercase; font-size: 22px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
            h2 {{ color: #8b0000; border-bottom: 2px solid #8b0000; padding-bottom: 5px; margin-top: 40px; font-size: 19px; text-transform: uppercase; }}
            h3 {{ color: #002b5e; font-size: 17px; margin-top: 20px; }}
            p, li {{ text-align: justify; text-justify: inter-word; margin-bottom: 15px; font-size: 16px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            table, th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #f8f9fa; color: #8b0000; }}
            .time-stamp {{ text-align: right; font-style: italic; color: #555; margin-bottom: 30px; font-weight: bold; }}
            .footer {{ text-align: center; font-size: 11px; color: #888; margin-top: 50px; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>BÁO CÁO PHÁP LÝ BẤT ĐỘNG SẢN & DỰ ÁN</h1>
            <p style="text-align: center;">Kính gửi Chuyên viên pháp lý: <b>Vũ Quang Phát</b></p>
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
