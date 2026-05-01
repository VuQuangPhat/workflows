import os
import re
import smtplib
import feedparser
import markdown
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_real_estate_news():
    """Thu thập tin tức chuyên sâu về Pháp lý, Chính sách và Bất động sản"""
    sources = {
        # Nguồn tin chính thống & Văn bản pháp luật
        "Chính sách - Pháp luật (Báo Chính phủ)": "https://baochinhphu.vn/rss/phap-luat.rss",
        "Tin tức (Thư viện Pháp luật)": "https://thuvienphapluat.vn/rss/tin-tuc.rss",
        
        # Nguồn chuyên ngành Pháp luật
        "Pháp luật (PLO)": "https://plo.vn/rss/phap-luat.rss",
        "Bất động sản (PLO)": "https://plo.vn/rss/bat-dong-san.rss",
        
        # Nguồn tin thị trường BĐS truyền thống
        "BĐS (VnExpress)": "https://vnexpress.net/rss/bat-dong-san.rss",
        "Pháp luật (VnExpress)": "https://vnexpress.net/rss/phap-luat.rss",
        "BĐS (CafeF)": "https://cafef.vn/bat-dong-san.rss"
    }
    
    summary = ""
    for cat, url in sources.items():
        try:
            feed = feedparser.parse(url)
            summary += f"\n--- NGUỒN: {cat.upper()} ---\n"
            
            # Lấy 4 tin mỗi nguồn để đảm bảo không vượt quá giới hạn Context Window của AI
            for entry in feed.entries[:4]:
                desc = entry.get('summary', entry.get('description', ''))
                # Lọc bỏ các thẻ HTML rác
                clean_desc = re.sub('<[^<]+>', '', desc) 
                
                short_desc = (clean_desc[:350] + '...') if len(clean_desc) > 350 else clean_desc
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {short_desc}\nLink: {entry.link}\n\n"
        except Exception as e:
            print(f"Lỗi khi tải nguồn {cat}: {e}")
            continue
            
    return summary

def get_ai_report(news_data):
    """Phân tích dữ liệu bằng AI tập trung vào Pháp lý dự án & NQ 171"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    prompt = f"""
Bạn là Luật sư cấp cao chuyên ngành Bất động sản phục vụ Vũ Quang Phát (10 năm kinh nghiệm, học ULAW).
Nhiệm vụ của bạn là đọc các tin tức thị trường/pháp luật dưới đây và soạn thảo một báo cáo cập nhật chuyên sâu.

Dữ liệu thô từ báo chí hôm nay: {news_data}

HÃY SOẠN: "BÁO CÁO PHÁP LÝ BẤT ĐỘNG SẢN & DỰ ÁN".
Yêu cầu: Markdown, KHÔNG EMOJI. Ngôn ngữ chính: TIẾNG VIỆT. Hành văn chuẩn mực, sắc bén của dân luật.

CẤU TRÚC BẮT BUỘC:
## 1. CẬP NHẬT THAY ĐỔI HÀNG NGÀY (THỊ TRƯỜNG & CHÍNH SÁCH)
- Lọc từ 'Dữ liệu thô', tóm tắt các sự kiện, chính sách, hoặc diễn biến thị trường BĐS đáng chú ý nhất trong 24h qua. Nếu không có tin liên quan, hãy phân tích xu hướng chung.

## 2. CHUYÊN ĐỀ: CHẤP THUẬN CHỦ TRƯƠNG ĐẦU TƯ & NGHỊ QUYẾT 171 (QUYỀN SỬ DỤNG ĐẤT)
- Phân tích bình luận chuyên sâu về nội dung, quy trình thủ tục chấp thuận chủ trương đầu tư đối với nhà đầu tư đang có quyền sử dụng đất (hoặc nhận chuyển nhượng QSDĐ).
- Đánh giá nút thắt pháp lý hiện tại (đặc biệt liên quan đến đất không phải là đất ở) và hướng tháo gỡ theo tinh thần Nghị quyết mới nhất/Luật Đất đai 2024.

## 3. PHÂN TÍCH TÌNH HUỐNG BĐS (IRAC METHOD)
- Tự tạo hoặc trích xuất một tình huống thực tiễn từ tin tức về tranh chấp hoặc vướng mắc thủ tục dự án BĐS.
- Giải quyết chặt chẽ theo cấu trúc IRAC (Issue - Rule - Application - Conclusion).

## 4. TƯ DUY PHẢN BIỆN (RISK & OPPORTUNITY TRONG LẬP DỰ ÁN)
- Đánh giá rủi ro pháp lý và cơ hội cho Chủ đầu tư dựa trên bối cảnh pháp luật hiện hành.

## 5. TỪ VỰNG TIẾNG ANH PHÁP LÝ BĐS (UK B2)
- Trình bày bảng (Từ vựng | IPA | Nghĩa tiếng Việt | Ví dụ áp dụng trong Hợp đồng/Dự án BĐS).

## 6. UK IDIOM OF THE DAY (LEVEL B2)
- Một thành ngữ Anh (UK) kèm ngữ cảnh sử dụng trong đàm phán thương mại.
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
    """Gửi email với định dạng CSS chuẩn pháp lý"""
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
                border-top: 10px solid #8b0000; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
            }}
            h1 {{ color: #8b0000; text-align: center; text-transform: uppercase; font-size: 22px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
            h2 {{ color: #8b0000; border-bottom: 2px solid #8b0000; padding-bottom: 5px; margin-top: 40px; font-size: 19px; text-transform: uppercase; }}
            
            p, li {{ 
                text-align: justify; 
                text-justify: inter-word; 
                margin-bottom: 15px; 
                font-size: 16px; 
            }}
            
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            table, th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #f8f9fa; color: #8b0000; }}
            .footer {{ text-align: center; font-size: 11px; color: #888; margin-top: 50px; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>BÁO CÁO PHÁP LÝ BẤT ĐỘNG SẢN & DỰ ÁN</h1>
            <p style="text-align: center;">Kính gửi Luật sư: <b>Vũ Quang Phát</b></p>
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
