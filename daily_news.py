import os
import smtplib
import feedparser
import markdown
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_comprehensive_news():
    sources = {
        "World (BBC)": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "World (NYT)": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "Business (VnExpress)": "https://vnexpress.net/rss/kinh-doanh.rss",
        "Business (Tuổi Trẻ)": "https://tuoitre.vn/rss/kinh-doanh.rss",
        "Politics (VnExpress)": "https://vnexpress.net/rss/thoi-su.rss",
        "Law (Tuổi Trẻ)": "https://tuoitre.vn/rss/phap-luat.rss"
    }
    summary = ""
    for cat, url in sources.items():
        feed = feedparser.parse(url)
        summary += f"\n--- NGUỒN: {cat.upper()} ---\n"
        # Lấy tối đa 10 tin mỗi nguồn để AI có nhiều dữ liệu lựa chọn
        for entry in feed.entries[:10]:
            description = entry.get('summary', entry.get('description', ''))
            summary += f"Tiêu đề: {entry.title}\nTóm tắt: {description}\nLink: {entry.link}\n\n"
    return summary

def get_ai_report(news_data):
    api_key = os.environ.get('GEMINI_API_KEY')
    genai.configure(api_key=api_key)
    
    prompt = f"""
Bạn là chuyên gia phân tích chiến lược và pháp lý vĩ mô phục vụ Vũ Quang Phát (10 năm kinh nghiệm, học ULAW).
Dữ liệu thô: {news_data}

HÃY SOẠN: "BÁO CÁO PHÂN TÍCH TÌNH HÌNH THẾ GIỚI VÀ VN".
Yêu cầu: Markdown, KHÔNG EMOJI, KHÔNG XƯNG HÔ 'Luật sư'.

QUY TẮC NỘI DUNG ĐỘNG:
- KHÔNG cố định số lượng tin tức. Hãy lọc từ dữ liệu thô những sự kiện THỰC SỰ QUAN TRỌNG, có tác động pháp lý hoặc kinh tế lớn để đưa vào.
- Nếu ngày hôm đó có nhiều sự kiện lớn, báo cáo có thể dài. Nếu ít sự kiện, báo cáo cần súc tích.

CẤU TRÚC TRÌNH BÀY:
## 1. ĐỊA CHÍNH TRỊ & KINH TẾ THẾ GIỚI
## 2. CHÍNH TRỊ & KINH TẾ VIỆT NAM
## 3. PHÂN TÍCH TÌNH HUỐNG (IRAC)
## 4. KỸ NĂNG LẬP LUẬN (ARGUMENTATION SKILLS)
## 5. UK IDIOM OF THE DAY
## 6. TƯ DUY PHẢN BIỆN & CHIẾN LƯỢC

## 7. TỪ VỰNG TIẾNG ANH (UK B2)
Yêu cầu trình bày mục này theo bảng hoặc danh sách có: **Từ vựng** | /Phiên âm IPA/ | Nghĩa | Ví dụ.

## 8. TRÍCH DẪN NGUỒN
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
    except Exception as e:
        return f"Lỗi: {str(e)}"

def send_email(markdown_content):
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"BÁO CÁO CHIẾN LƯỢC | LẦN CHẠY #{run_num}"
    msg["From"] = f"Strategic AI Assistant <{sender}>"
    msg["To"] = sender
    
    # Sử dụng các extension để tối ưu hiển thị Markdown sang HTML
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'sane_lists', 'tables'])
    
    full_html = f"""
    <html>
      <head>
        <style>
            body {{ 
                font-family: 'Times New Roman', Times, serif; 
                background-color: #f0f2f5; 
                padding: 30px; 
                color: #1a1a1a; 
                line-height: 1.8;
            }}
            .container {{ 
                max-width: 850px; 
                margin: 0 auto; 
                background: #ffffff; 
                padding: 50px; 
                border-radius: 2px; 
                border-top: 10px solid #002b5e;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }}
            h1 {{ color: #002b5e; text-align: center; text-transform: uppercase; font-size: 24px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
            h2 {{ color: #002b5e; border-bottom: 2px solid #002b5e; padding-bottom: 8px; margin-top: 45px; text-transform: uppercase; font-size: 19px; }}
            p, li {{ text-align: justify; margin-bottom: 15px; font-size: 16px; }}
            strong {{ color: #000; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            table, th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f8f9fa; color: #002b5e; }}
            .footer {{ text-align: center; font-size: 12px; color: #888; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>Báo Cáo Phân Tích Tổng Hợp</h1>
            <p style="text-align: center;">Kính gửi chuyên gia: <b>Vũ Quang Phát</b></p>
            <div class="content">{html_body}</div>
            <div class="footer">Hệ thống phân tích tự động | Gemini AI & GitHub Actions</div>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(full_html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, pwd)
        server.sendmail(sender, sender, msg.as_string())

if __name__ == "__main__":
    news = get_comprehensive_news()
    report = get_ai_report(news)
    send_email(report)
