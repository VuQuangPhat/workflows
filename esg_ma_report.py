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
            for entry in feed.entries[:6]: # Lấy 6 tin mỗi nguồn để tránh quá tải token
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
    
    # Prompt được thiết kế để khớp 100% với mẫu báo cáo bạn mong muốn
    prompt = f"""
Bạn là chuyên gia phân tích chiến lược M&A và ESG phục vụ Vũ Quang Phát (10 năm kinh nghiệm Pháp lý, ULAW).
Dữ liệu đầu vào: {news_data}

YÊU CẦU HÌNH THỨC:
1. Định dạng: Markdown, KHÔNG dùng Emoji.
2. Ngôn ngữ: UK English cho toàn báo cáo.
3. NGOẠI LỆ SONG NGỮ: Mục 5 và Mục 7 BẮT BUỘC phải có tiếng Việt (Giải nghĩa và Dịch ví dụ).

CẤU TRÚC BÁO CÁO (TUÂN THỦ TUYỆT ĐỐI):

## 1. TỔNG QUAN M&A (DEAL FLOWS)
(Phân tích các dòng vốn, thương vụ hoặc biến động kinh tế vĩ mô từ dữ liệu)

## 2. ESG COMPLIANCE & GOVERNANCE
(Trình bày dưới dạng BẢNG gồm các cột: Lĩnh vực | Tình trạng | Chi tiết chiến lược)

## 3. PHÂN TÍCH PHÁP LÝ (IRAC METHOD)
(Chọn 1 tình huống pháp lý tiêu biểu từ dữ liệu để phân tích theo: Issue, Rule, Analysis, Conclusion)

## 4. KỸ NĂNG LẬP LUẬN (LOGIC)
(Sử dụng một kỹ thuật logic như 'Refutation by Counter-example' hoặc 'Syllogism' để phản biện một vấn đề trong tin tức)

## 5. UK IDIOM OF THE DAY (LEVEL B2)
- **Thành ngữ:** "[Idiom]"
- **Nghĩa:** [English definition] - ([Nghĩa tiếng Việt])
- **Ví dụ:** [English example] - ([Dịch ví dụ sang tiếng Việt])

## 6. TƯ DUY PHẢN BIỆN (RISK & OPPORTUNITY)
(Đưa ra góc nhìn sâu về rủi ro tiềm ẩn hoặc cơ hội chiến lược, ví dụ về Greenwashing hoặc tâm lý đầu tư)

## 7. TỪ VỰNG CHUYÊN NGÀNH (UK B2)
- Trình bày dạng BẢNG: **Từ vựng** | /IPA/ | Nghĩa (Anh-Việt) | Ví dụ (Anh-Việt)
(Lưu ý: Cột Nghĩa và Ví dụ PHẢI có tiếng Việt)

## 8. TRÍCH DẪN NGUỒN
(Liệt kê các nguồn tin đã sử dụng)
"""

    try:
        # Tự động chọn model Flash để có tốc độ nhanh nhất hoặc Pro nếu cần sâu hơn
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Generation Error: {str(e)}"

def send_email(markdown_content):
    """Gửi email định dạng HTML chuyên nghiệp"""
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[STRATEGIC] M&A & ESG REPORT #{run_num}"
    msg["From"] = f"Strategic AI Assistant <{sender}>"
    msg["To"] = sender
    
    # Chuyển đổi Markdown sang HTML (hỗ trợ bảng và xuống dòng)
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'tables'])
    
    # Giao diện Email chuẩn CSS (Times New Roman, Blue Header)
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
    
    # QUAN TRỌNG: Thiết lập utf-8 để không lỗi font tiếng Việt
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, pwd)
            server.sendmail(sender, sender, msg.as_string())
        print(f"Báo cáo #{run_num} đã được gửi thành công!")
    except Exception as e:
        print(f"Lỗi gửi mail: {e}")

if __name__ == "__main__":
    # Quy trình thực thi
    print("Đang lấy tin tức...")
    news = get_ma_esg_news()
    
    print("Đang phân tích dữ liệu bằng AI...")
    report = get_ai_report(news)
    
    print("Đang gửi email báo cáo...")
    send_email(report)
