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
        "Chính sách (Báo Chính phủ)": "https://baochinhphu.vn/rss/phap-luat.rss",
        "Tin tức (Thư viện Pháp luật)": "https://thuvienphapluat.vn/rss/tin-tuc.rss",
        "Pháp luật (PLO)": "https://plo.vn/rss/phap-luat.rss",
        "Bất động sản (PLO)": "https://plo.vn/rss/bat-dong-san.rss",
        "BĐS (VnExpress)": "https://vnexpress.net/rss/bat-dong-san.rss",
        "Pháp luật (VnExpress)": "https://vnexpress.net/rss/phap-luat.rss",
        "BĐS (CafeF)": "https://cafef.vn/bat-dong-san.rss"
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
    """Phân tích dữ liệu bằng AI bám sát quy trình chuẩn và NQ 171/2024/QH15"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    prompt = f"""
Bạn là Trợ lý AI chuyên môn cao hỗ trợ trực tiếp cho Chuyên viên pháp lý dự án BĐS: Vũ Quang Phát.
Nhiệm vụ của bạn là đọc tin tức hôm nay và soạn thảo báo cáo cập nhật chuyên sâu, tuân thủ tư duy kiểm soát rủi ro pháp lý chuẩn.

LƯU Ý CỐT LÕI VỀ VĂN BẢN PHÁP LUẬT: 
- Tuyệt đối không viện dẫn các văn bản đã hết hiệu lực hoặc bị nhầm lẫn ký hiệu cơ quan ban hành.
- ĐẶC BIỆT CHÚ Ý: Chuyên đề cốt lõi hiện tại là "Nghị quyết số 171/2024/QH15 của Quốc hội về thí điểm thực hiện dự án nhà ở thương mại thông qua thỏa thuận về nhận quyền sử dụng đất hoặc đang có quyền sử dụng đất". Tuyệt đối KHÔNG nhầm lẫn thành NQ 171/NQ-CP của Chính phủ.

Dữ liệu thô từ báo chí hôm nay: {news_data}

HÃY SOẠN: "BÁO CÁO PHÁP LÝ BẤT ĐỘNG SẢN & DỰ ÁN".
Yêu cầu: Markdown, KHÔNG EMOJI. Ngôn ngữ chính: TIẾNG VIỆT. Văn phong chuẩn mực, logic pháp lý chặt chẽ.

CẤU TRÚC BẮT BUỘC:
## 1. TỔNG HỢP & CẢNH BÁO HIỆU LỰC CHÍNH SÁCH 24H QUA (CHECK)
- Tóm tắt các sự kiện, chính sách BĐS đáng chú ý. 
- Cảnh báo hiệu lực: Chỉ rõ văn bản pháp luật nào sắp ban hành, vừa có hiệu lực (ví dụ Luật Đầu tư 143/2025/QH15), hoặc vừa hết hiệu lực.

## 2. CHUYÊN ĐỀ MỤC TIÊU: NGHỊ QUYẾT 171/2024/QH15 & NGHỊ ĐỊNH HƯỚNG DẪN (PLAN)
- Lọc mọi tin tức liên quan đến việc triển khai Nghị quyết 171/2024/QH15 và các thủ tục đi kèm.
- Đánh giá tiến độ tháo gỡ điểm nghẽn thủ tục tại các địa phương (ví dụ: các Thông báo chấp thuận cho tổ chức thực hiện dự án thí điểm của UBND cấp tỉnh).
- LƯU Ý: Nếu hôm nay không có tin tức mới, hãy tự động thiết lập một Check-list quy trình rủi ro thực chiến hoặc lời khuyên pháp lý cho Chủ đầu tư khi thực hiện thỏa thuận nhận quyền sử dụng đất theo cơ chế thí điểm của Nghị quyết 171/2024/QH15.

## 3. CƠ CHẾ PHÁP LÝ CHUNG VỀ CHẤP THUẬN CHỦ TRƯƠNG ĐẦU TƯ (DO)
- Phân tích bình luận chuyên sâu về quy trình, thủ tục dự án dựa trên khung pháp luật hiện hành (Luật Đất đai 2024, Luật Đầu tư 2025).

## 4. PHÂN TÍCH TÌNH HUỐNG THỰC TIỄN (IRAC METHOD - ACT)
- Trích xuất một tình huống thực tiễn từ tin tức (ưu tiên vướng mắc bồi thường, giao đất, chuyển mục đích sử dụng đất) và giải quyết theo cấu trúc IRAC (Issue - Rule - Application - Conclusion).

## 5. TỪ VỰNG TIẾNG ANH PHÁP LÝ BĐS (UK B2)
- Trình bày bảng (Từ vựng | IPA | Nghĩa tiếng Việt | Ví dụ áp dụng).

## 6. UK IDIOM OF THE DAY (LEVEL B2)
- Một thành ngữ Anh (UK) dùng trong đàm phán thương mại.
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
