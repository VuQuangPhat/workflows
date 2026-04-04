import os
import smtplib
import feedparser
import markdown
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_ma_esg_news():
    # Nguồn tin tập trung vào M&A và ESG
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
            for entry in feed.entries[:8]:
                desc = entry.get('summary', entry.get('description', ''))
                summary += f"Title: {entry.title}\nContent: {desc}\nLink: {entry.link}\n\n"
        except:
            continue
    return summary

def get_ai_report(news_data):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return "Error: Missing GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    # Prompt đã được tối ưu để đảm bảo nội dung song ngữ ở Mục 5 & 7
    prompt = f"""
Bạn là chuyên gia phân tích chiến lược M&A và ESG phục vụ Vũ Quang Phát (10 năm kinh nghiệm Pháp lý, ULAW).
Dữ liệu: {news_data}

HÃY SOẠN BÁO CÁO: Markdown, NO EMOJI.
NGÔN NGỮ CHÍNH: UK English. 
RIÊNG MỤC 5 VÀ 7: Bắt buộc trình bày SONG NGỮ (Anh - Việt).

CẤU TRÚC BÁO CÁO:
## 1. TỔNG QUAN M&A (DEAL FLOWS)
## 2. ESG COMPLIANCE & GOVERNANCE (Kèm bảng tóm tắt)
## 3. PHÂN TÍCH PHÁP LÝ (IRAC METHOD)
## 4. KỸ NĂNG LẬP LUẬN (LOGIC)
## 5. UK IDIOM OF THE DAY (LEVEL B2)
- **Thành ngữ:** "[Idiom]"
- **Nghĩa:** [English definition] - ([Nghĩa tiếng Việt])
- **Ví dụ:** [English example] - ([Dịch ví dụ sang tiếng Việt])
## 6. TƯ DUY PHẢN BIỆN (RISK & OPPORTUNITY)
## 7. TỪ VỰNG CHUYÊN NGÀNH (UK B2)
- Trình bày bảng: **Từ vựng** | /IPA/ | Nghĩa (Anh-Việt) | Ví dụ (Anh-Việt). 
(Lưu ý: Cột Nghĩa và Ví dụ PHẢI có tiếng Việt).
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
        return "AI Generation Failed."
    except Exception as e:
        return f"System Error: {str(e)}"

def send_email(markdown_content):
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[STRATEGIC] M&A & ESG REPORT #{run_num}"
    msg["From"] = sender
    msg["To"] = sender
    
    # Render Markdown sang HTML
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'tables'])
    
    full_html = f"""
    <html>
      <head>
        <style>
            body {{ font-family: 'Times New Roman', serif; background-color: #f4f7f6; padding: 30px; color: #1a1a1a; line-height: 1.8; }}
            .container {{ max-width: 850px; margin: 0 auto; background: #fff; padding: 50px; border-radius: 4px; border-top: 10px solid #002b5e; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            h1 {{ color: #002b5e; text-align: center; text-transform: uppercase; font-size: 22px; border-bottom: 2px solid #eee; padding-bottom: 20px; }}
            h2 {{ color: #002b5e; border-bottom: 2px solid #002b5e; padding-bottom: 5px; margin-top: 40px; font-size: 19px; }}
            p, li {{ text-align: justify; margin-bottom: 15px; font-size: 16px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            table, th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #f8f9fa; }}
            .footer {{ text-align: center; font-size: 11px; color: #888; margin-top: 50px; border-top: 1px solid #eee; padding-top: 15px; }}
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
    
    # QUAN TRỌNG: Thêm "utf-8" để hiển thị tiếng Việt chuẩn xác
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, pwd)
            server.sendmail(sender, sender, msg.as_string())
        print("Success! Email sent with UTF-8 encoding.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    news = get_ma_esg_news()
    report = get_ai_report(news)
    send_email(report)
