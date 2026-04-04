import os
import smtplib
import feedparser
import markdown
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_ma_esg_news():
    """Thu thập tin tức từ các nguồn RSS"""
    sources = {
        "Reuters Business": "https://www.reutersagency.com/feed/?best-topics=business&format=xml",
        "FT Corporate": "https://www.ft.com/corporate-governance?format=rss",
        "VnExpress Biz": "https://vnexpress.net/rss/kinh-doanh.rss",
        "ESG News": "https://esgnews.com/feed/",
        "Tuổi Trẻ Luật": "https://tuoitre.vn/rss/phap-luat.rss"
    }
    summary = ""
    for cat, url in sources.items():
        try:
            feed = feedparser.parse(url)
            summary += f"\n--- SOURCE: {cat.upper()} ---\n"
            for entry in feed.entries[:6]: 
                desc = entry.get('summary', entry.get('description', ''))
                summary += f"Title: {entry.title}\nContent: {desc}\nLink: {entry.link}\n\n"
        except:
            continue
    return summary

def get_ai_report(news_data):
    """Gửi dữ liệu cho Gemini để phân tích và soạn báo cáo"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return "Error: Missing GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    prompt = f"""
Bạn là chuyên gia phân tích chiến lược M&A và ESG phục vụ Vũ Quang Phát (10 năm kinh nghiệm Pháp lý, ULAW).
Dữ liệu đầu vào: {news_data}

YÊU CẦU HÌNH THỨC:
1. Định dạng: Markdown, KHÔNG dùng Emoji.
2. Ngôn ngữ: UK English cho toàn báo cáo.
3. NGOẠI LỆ SONG NGỮ: Mục 5 và Mục 7 BẮT BUỘC phải có tiếng Việt (Giải nghĩa và Dịch ví dụ).

CẤU TRÚC BÁO CÁO:
## 1. TỔNG QUAN M&A (DEAL FLOWS)
## 2. ESG COMPLIANCE & GOVERNANCE (Dạng bảng: Lĩnh vực | Tình trạng | Chi tiết)
## 3. PHÂN TÍCH PHÁP LÝ (IRAC METHOD)
## 4. KỸ NĂNG LẬP LUẬN (LOGIC)
## 5. UK IDIOM OF THE DAY (LEVEL B2)
- **Thành ngữ:** "[Idiom]"
- **Nghĩa:** [English definition] - ([Nghĩa tiếng Việt])
- **Ví dụ:** [English example] - ([Dịch ví dụ sang tiếng Việt])
## 6. TƯ DUY PHẢN BIỆN (RISK & OPPORTUNITY)
## 7. TỪ VỰNG CHUYÊN NGÀNH (UK B2)
- Bảng: **Từ vựng** | /IPA/ | Nghĩa (Anh-Việt) | Ví dụ (Anh-Việt)
## 8. TRÍCH DẪN NGUỒN
"""

    try:
        # GIẢI PHÁP SỬA LỖI 404: Tự động liệt kê và chọn model khả dụng
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Ưu tiên Flash -> Pro -> các bản khác
        models_to_try = sorted(available_models, key=lambda x: (0 if 'flash' in x else (1 if 'pro' in x else 2)))
        
        if not models_to_try:
            return "Error: No supported AI models found in your account."

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception:
                continue
        
        return "AI Generation Failed after trying multiple models."
    except Exception as e:
        return f"System Error: {str(e)}"

def send_email(markdown_content):
    """Gửi email định dạng HTML chuyên nghiệp"""
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[STRATEGIC] M&A & ESG REPORT #{run_num}"
    msg["From"] = f"Strategic AI Assistant <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'tables'])
    
    full_html = f"""
    <html>
      <head>
        <style>
            body {{ font-family: 'Times New Roman', serif; background-color: #f4f7f6; padding: 20px; color: #1a1a1a; line-height: 1.6; }}
            .container {{ max-width: 800px; margin: 0 auto; background: #fff; padding: 40px; border-top: 8px solid #002b5e; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
            h1 {{ color: #002b5e; text-align: center; text-transform: uppercase; font-size: 20px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
            h2 {{ color: #002b5e; border-bottom: 2px solid #002b5e; padding-bottom: 5px; margin-top: 30px; font-size: 18px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 15px; }}
            table, th, td {{ border: 1px solid #ccc; padding: 10px; text-align: left; }}
            th {{ background-color: #f8f9fa; color: #002b5e; }}
            .footer {{ text-align: center; font-size: 11px; color: #999; margin-top: 40px; border-top: 1px solid #eee; padding-top: 10px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>M&A & ESG STRATEGIC ANALYSIS</h1>
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
        print(f"Success! Report #{run_num} sent.")
    except Exception as e:
        print(f"Email Error: {e}")

if __name__ == "__main__":
    news = get_ma_esg_news()
    report = get_ai_report(news)
    send_email(report)
