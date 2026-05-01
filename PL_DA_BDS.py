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
            for entry in feed.entries[:4]:
                desc = entry.get('summary', entry.get('description', ''))
                clean_desc = re.sub('<[^<]+>', '', desc) 
                short_desc = (clean_desc[:350] + '...') if len(clean_desc) > 350 else clean_desc
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {short_desc}\nLink: {entry.link}\n\n"
        except Exception as e:
            print(f"Lỗi khi tải nguồn {cat}: {e}")
            continue
    return summary

def get_ai_report(news_data):
    """Phân tích dữ liệu bằng AI: Chuẩn hóa bộ máy sau 1/7/2025 & Nêu rõ thẩm quyền từng bước ISO"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là Trợ lý AI cấp cao chuyên về Pháp lý Bất động sản, hỗ trợ trực tiếp cho Chuyên viên pháp lý dự án BĐS: Vũ Quang Phát.
Nhiệm vụ của bạn là lập báo cáo phân tích chuyên sâu từ dữ liệu tin tức, tuân thủ nghiêm ngặt quy trình ISO (PDCA) và bám sát khung pháp lý hiện hành.

THỜI GIAN LẬP BÁO CÁO HIỆN TẠI: {current_time}

LƯU Ý CỐT LÕI (BẮT BUỘC TUÂN THỦ MỆNH LỆNH 100%):
1. VỀ LUẬT VÀ THUẬT NGỮ CHUYÊN MÔN: 
   - CHỈ ĐƯỢC PHÉP dùng cấu trúc của Luật Đầu tư 143/2025/QH15 (Điều 24: Dự án thuộc diện CTCTĐT; Điều 25: Thẩm quyền CTCTĐT).
   - Luật Xây dựng 135/2025/QH15; Luật KDBĐS 29/2023/QH15; Luật Đất đai 31/2024/QH15.
   - Thuật ngữ chuẩn: "Chấp thuận chủ trương đầu tư" (CTCTĐT), "Giao đất, cho thuê đất, cho phép chuyển mục đích sử dụng đất". Nghiêm cấm dùng từ "chấp thuận nhu cầu sử dụng đất".
2. VỀ TÊN GỌI SỞ BAN NGÀNH SAU 1/7/2025:
   - Hệ thống tổ chức các Sở, Ban, Ngành đã thay đổi toàn bộ từ 1/7/2025. Bắt buộc phải rà soát, kiểm chứng và sử dụng ĐÚNG danh xưng của các cơ quan có thẩm quyền MỚI NHẤT. Nếu dữ liệu báo chí dùng tên cũ, bạn phải tự động hiệu chỉnh lại cho đúng cơ cấu hiện hành.
3. VỀ NGHỊ QUYẾT 171/2024/QH15 & THẨM QUYỀN TỪNG BƯỚC ISO:
   - Trong mỗi bước phân tích (Plan - Do - Check - Act), BẮT BUỘC phải làm rõ: THẨM QUYỀN thuộc về ai? (Quốc hội, Thủ tướng, HĐND cấp tỉnh, UBND cấp tỉnh, hay các cơ quan chuyên môn tương ứng).
   - Với NQ 171/2024/QH15: Phân tích sâu vướng mắc về thời điểm xin văn bản chấp thuận của UBND cấp tỉnh. Thẩm quyền quyết định danh mục là của HĐND, thẩm quyền ra Thông báo chấp thuận là của UBND. Trình tự thực hiện thế nào?

Dữ liệu thô từ báo chí hôm nay: {news_data}

YÊU CẦU TRÌNH BÀY: Markdown, KHÔNG EMOJI. Văn phong sắc bén, thực chiến. KHÔNG đánh số cứng (1, 2, 3...) cho tiêu đề chính. Tùy biến tiêu đề cho linh hoạt và đúng trọng tâm tin tức, nhưng phải tuân thủ 5 phần sau:

CẤU TRÚC BÁO CÁO DỰ KIẾN:
* [Bắt buộc ở dòng đầu tiên] "Thời gian lập báo cáo: {current_time}"
* TIÊU ĐỀ BƯỚC CHECK (Nhận diện & Cảnh báo pháp lý 24h): Tổng hợp tin tức. Chỉ rõ văn bản nào sắp ban hành, vừa có hiệu lực hoặc vừa bị bãi bỏ. Nêu rõ thẩm quyền rà soát, theo dõi của CĐT/Chuyên viên pháp lý ở bước này.
* TIÊU ĐỀ BƯỚC PLAN (Hoạch định - Chuyên đề NQ 171/2024/QH15): Đưa ra góc nhìn sâu về thủ tục triển khai NQ 171. CHỈ RÕ THẨM QUYỀN của HĐND và UBND cấp tỉnh trong việc đưa dự án vào danh mục và ra văn bản chấp thuận. Nếu không có tin mới, lập Checklist phòng rủi ro cho CĐT khi thỏa thuận quỹ đất.
* TIÊU ĐỀ BƯỚC DO (Thực thi - Cơ chế CTCTĐT hiện hành): Phân tích quy trình theo Điều 24 Luật Đầu tư 143/2025/QH15. CHỈ RÕ THẨM QUYỀN quyết định CTCTĐT theo Điều 25 Luật Đầu tư 143/2025/QH15 (Chỉ rõ dự án nào thuộc Quốc hội, Thủ tướng, UBND cấp tỉnh...).
* TIÊU ĐỀ BƯỚC ACT (Đánh giá tình huống - IRAC): Xử lý 1 vướng mắc từ tin (Giao đất, chuyển mục đích, bồi thường...). Nêu rõ THẨM QUYỀN giải quyết tình huống này thuộc về cơ quan quản lý nhà nước nào (sử dụng tên gọi cơ quan mới nhất sau 1/7/2025).
* TIÊU ĐỀ BƯỚC 5: TỪ VỰNG TIẾNG ANH PHÁP LÝ & UK IDIOM: Bảng từ vựng và 1 câu thành ngữ.
"""

    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models_to_try = sorted(available_models, key=lambda x: (0 if 'flash' in x else (1 if 'pro' in x else 2)))
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text
            except:
                continue
        return "AI Generation Failed."
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
