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
            for entry in feed.entries[:5]: # Tăng lên 5 tin để gom nhiều dữ liệu dự án hơn
                desc = entry.get('summary', entry.get('description', ''))
                clean_desc = re.sub('<[^<]+>', '', desc) 
                short_desc = (clean_desc[:350] + '...') if len(clean_desc) > 350 else clean_desc
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {short_desc}\nLink: {entry.link}\n\n"
        except Exception as e:
            print(f"Lỗi khi tải nguồn {cat}: {e}")
            continue
    return summary

def get_ai_report(news_data):
    """Phân tích dữ liệu bằng AI: Thực chiến dự án, bám sát miền Nam & NQ 171"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là Trợ lý AI cấp cao chuyên về Pháp lý Bất động sản, hỗ trợ trực tiếp cho Chuyên viên pháp lý dự án BĐS: Vũ Quang Phát.
Nhiệm vụ của bạn là lập báo cáo THỰC CHIẾN, KHÔNG LÝ THUYẾT SUÔNG, tuân thủ nghiêm ngặt quy trình ISO (PDCA) và bám sát khung pháp lý hiện hành.

THỜI GIAN LẬP BÁO CÁO HIỆN TẠI: {current_time}

LƯU Ý CỐT LÕI (BẮT BUỘC TUÂN THỦ MỆNH LỆNH 100%):
1. CHỐNG BỆNH "LÝ THUYẾT SUÔNG": Tuyệt đối KHÔNG viết các đoạn văn định nghĩa, giải thích ưu/nhược điểm chung chung của luật. Mọi phân tích phải đi thẳng vào TÊN DỰ ÁN, ĐỊA PHƯƠNG, CON SỐ thực tế.
2. TRỌNG TÂM DỰ ÁN MIỀN NAM & ĐẦU TƯ CÔNG: Phải có mục phân tích sự cộng hưởng giữa làn sóng đầu tư công (Cao tốc, Vành đai 3, 4, Sân bay Long Thành...) tác động đến tiến độ phê duyệt, giao đất của các dự án BĐS quanh khu vực phía Nam (TP.HCM, Bình Dương, Đồng Nai, Long An...).
3. VỀ NGHỊ QUYẾT 171/2024/QH15: "Nghị quyết về thí điểm thực hiện dự án nhà ở thương mại thông qua thỏa thuận về nhận quyền sử dụng đất hoặc đang có quyền sử dụng đất". Phân tích thẳng vào vướng mắc quy trình thực tế tại địa phương hiện nay.
4. LUẬT & TÊN CƠ QUAN MỚI NHẤT (SAU 01/07/2025): 
   - Luật Đầu tư 143/2025/QH15; Luật Xây dựng 135/2025/QH15; Luật KDBĐS 29/2023/QH15; Luật Đất đai 31/2024/QH15. 
   - Tên Sở mới: "Sở Nông nghiệp và Môi trường", "Sở Tài chính", "Sở Xây dựng".
5. TIẾNG ANH CHUYÊN NGÀNH: CHỈ dùng từ vựng mức độ B1 - B2. Tuyệt đối KHÔNG dùng từ C1/C2 phức tạp.

Dữ liệu thô từ báo chí hôm nay: {news_data}

YÊU CẦU TRÌNH BÀY: Markdown. Văn phong đi thẳng vào vấn đề của nhà đầu tư. Tùy biến tiêu đề cho linh hoạt, tuân thủ 5 bước sau:

CẤU TRÚC BÁO CÁO DỰ KIẾN:
* [Bắt buộc ở dòng đầu tiên] "Thời gian lập báo cáo: {current_time}"

* TIÊU ĐỀ BƯỚC CHECK (Nhận diện & Cảnh báo pháp lý 24h): 
  - Điểm mặt đặt tên các dự án/chính sách vừa lên mặt báo. Tác động "tiền tươi thóc thật" đến rủi ro của CĐT.
  - Thẩm quyền rà soát: Nêu rõ ai chịu trách nhiệm báo cáo.

* TIÊU ĐỀ BƯỚC PLAN (Điểm nóng Miền Nam & Tiến độ CTCTĐT - Luật ĐT 143/2025/QH15): 
  - Phân tích sự cộng hưởng của đầu tư công phía Nam đến các dự án BĐS. Nêu tên các khu vực/dự án đang được hưởng lợi hoặc sắp được duyệt CTCTĐT (theo Điều 24, 25 LĐT 143/2025).
  - Thẩm quyền: UBND cấp tỉnh nào, Sở Tài chính địa phương nào đang đẩy nhanh thủ tục?

* TIÊU ĐỀ BƯỚC DO (Thực chiến DA ĐT THÍ ĐIỂM THEO NQ 171/2024/QH15): 
  - Phân tích 1 Case Study/Tình huống có thật (hoặc giả định sát thực tế nhất ở miền Nam). 
  - Cách tiếp cận quỹ đất, lập danh mục để HĐND tỉnh duyệt.
  - Xử lý bài toán đền bù, thỏa thuận giá đất với dân. Nếu bế tắc thì làm gì?
  - Thẩm quyền: HĐND, UBND, Sở Nông nghiệp và Môi trường xử lý ra sao.

* TIÊU ĐỀ BƯỚC ACT (Giải quyết Vướng mắc - IRAC Plan): 
  - Chọn 1 vướng mắc đang tồn đọng (Giao đất, chuyển mục đích...). 
  - Cấu trúc: Issue - Rule - Application - Conclusion (Conclusion phải là 1 Action Plan tham mưu từng bước cụ thể trình Ban Giám đốc).

* TIÊU ĐỀ BƯỚC 5: TỪ VỰNG TIẾNG ANH PHÁP LÝ (LEVEL B1-B2) & UK IDIOM:
  - Cung cấp 5-7 từ vựng B1/B2 chuyên dùng trong hợp đồng mua bán/thuê BĐS (Bảng: Từ vựng | IPA | Nghĩa tiếng Việt | Ví dụ).
  - 1 thành ngữ tiếng Anh thông dụng trong kinh doanh.
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
