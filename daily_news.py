import os
import smtplib
import feedparser
import markdown
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_comprehensive_news():
    """Thu thập và cắt ngắn nội dung để tiết kiệm Quota/Token"""
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
        try:
            feed = feedparser.parse(url)
            summary += f"\n--- NGUỒN: {cat.upper()} ---\n"
            # Giảm xuống 6 tin để tránh prompt quá dài gây lỗi quota
            for entry in feed.entries[:6]:
                desc = entry.get('summary', entry.get('description', ''))
                # Cắt ngắn mô tả (tránh gửi quá nhiều text thô lên AI)
                short_desc = (desc[:300] + '...') if len(desc) > 300 else desc
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {short_desc}\nLink: {entry.link}\n\n"
        except:
            continue
    return summary

def get_ai_report(news_data):
    """Phân tích dữ liệu bằng AI với xử lý lỗi Quota"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    prompt = f"""
Bạn là chuyên gia phân tích chiến lược và pháp lý phục vụ Vũ Quang Phát (10 năm kinh nghiệm, học ULAW).
Dữ liệu thô: {news_data}

HÃY SOẠN: "BÁO CÁO PHÂN TÍCH TỔNG HỢP".
Yêu cầu: Markdown, KHÔNG EMOJI. Ngôn ngữ chính: TIẾNG VIỆT.

CẤU TRÚC:
## 1. ĐỊA CHÍNH TRỊ & KINH TẾ THẾ GIỚI
## 2. CHÍNH TRỊ & KINH TẾ VIỆT NAM
## 3. PHÂN TÍCH TÌNH HUỐNG (IRAC METHOD)
## 4. KỸ NĂNG LẬP LUẬN (LOGIC)
## 5. UK IDIOM OF THE DAY (LEVEL B2)
## 6. TƯ DUY PHẢN BIỆN (RISK & OPPORTUNITY)
## 7. TỪ VỰNG TIẾNG ANH CHUYÊN NGÀNH (UK B2) - Trình bày bảng (Từ vựng | IPA | Nghĩa | Ví dụ).
## 8. TRÍCH DẪN NGUỒN
"""

try:
        # Tự động tìm kiếm model khả dụng để tránh lỗi 404
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models_to_try = sorted(available_models, key=lambda x: (0 if 'flash' in x else (1 if 'pro' in x else 2)))
        
        for model_name in models_to_try:try:
        # Tự động tìm kiếm model khả dụng để tránh lỗi 404
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
    """Gửi email với định dạng CSS chuẩn pháp lý và canh lề đều"""
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[CHIẾN LƯỢC] BÁO CÁO TỔNG HỢP #{run_num}"
    msg["From"] = f"Strategic AI Assistant <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'tables'])
    
    full_html = f"""
    <html>
      <head>
        <style>
            body {{ 
                font-family: 'Times New Roman', serif; 
                background-color: #f4f7f6; 
                padding: 30px; 
                line-height: 1.8; 
                color: #1a1a1a;
            }}
            .container {{ 
                max-width: 850px; 
                margin: 0 auto; 
                background: #fff; 
                padding: 50px; 
                border-top: 10px solid #002b5e; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
            }}
            h1 {{ color: #002b5e; text-align: center; text-transform: uppercase; font-size: 22px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
            h2 {{ color: #002b5e; border-bottom: 2px solid #002b5e; padding-bottom: 5px; margin-top: 40px; font-size: 19px; text-transform: uppercase; }}
            
            /* Canh lề đều hai bên chuẩn văn bản pháp luật */
            p, li {{ 
                text-align: justify; 
                text-justify: inter-word; 
                margin-bottom: 15px; 
                font-size: 16px; 
            }}
            
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            table, th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #f8f9fa; }}
            .footer {{ text-align: center; font-size: 11px; color: #888; margin-top: 50px; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>BÁO CÁO PHÂN TÍCH TỔNG HỢP</h1>
            <p style="text-align: center;">Kính gửi chuyên gia: <b>Vũ Quang Phát</b></p>
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
    news = get_comprehensive_news()
    report = get_ai_report(news)
    send_email(report)
