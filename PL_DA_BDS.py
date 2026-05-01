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
    """Phân tích dữ liệu bằng AI: Mức độ chuyên sâu chiến lược, giải pháp thực chiến"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là Trợ lý AI cấp cao chuyên về Pháp lý Bất động sản, hỗ trợ trực tiếp cho Chuyên viên pháp lý dự án BĐS: Vũ Quang Phát.
Nhiệm vụ của bạn là lập báo cáo phân tích CHUYÊN SÂU CHIẾN LƯỢC từ dữ liệu tin tức, tuân thủ nghiêm ngặt quy trình ISO (PDCA) và bám sát khung pháp lý hiện hành.

THỜI GIAN LẬP BÁO CÁO HIỆN TẠI: {current_time}

LƯU Ý CỐT LÕI (BẮT BUỘC TUÂN THỦ MỆNH LỆNH 100%):
1. VỀ NGHỊ QUYẾT 171/2024/QH15: 
   - Tên chính xác: "Nghị quyết về thí điểm thực hiện dự án nhà ở thương mại thông qua thỏa thuận về nhận quyền sử dụng đất hoặc đang có quyền sử dụng đất".
   - Phân tích chuyên sâu vào bài toán thực tiễn: Giải pháp khi đàm phán nhận QSDĐ bế tắc ("đất da báo"), rủi ro trượt giá đền bù, và vướng mắc khi xác định tiền sử dụng đất.
2. VỀ LUẬT VÀ THUẬT NGỮ CHUYÊN MÔN: 
   - Chỉ dùng: Luật Đầu tư 143/2025/QH15; Luật Xây dựng 135/2025/QH15; Luật KDBĐS 29/2023/QH15; Luật Đất đai 31/2024/QH15.
   - Khi phân tích dự án tổng quát: Phải làm rõ các ngã rẽ lựa chọn nhà đầu tư (Điều 23 LĐT 143/2025) và các trường hợp áp dụng thủ tục đầu tư đặc biệt (Điều 28 LĐT 143/2025).
   - Thuật ngữ chuẩn: "Chấp thuận chủ trương đầu tư" (CTCTĐT), "Giao đất, cho thuê đất, cho phép chuyển mục đích sử dụng đất". Nghiêm cấm dùng từ "chấp thuận nhu cầu sử dụng đất".
3. VỀ TÊN GỌI SỞ BAN NGÀNH (SAU 01/07/2025):
   - KHÔNG dùng "Sở Tài nguyên và Môi trường" -> Bắt buộc dùng "Sở Nông nghiệp và Môi trường".
   - KHÔNG dùng "Sở Kế hoạch và Đầu tư" -> Bắt buộc dùng "Sở Tài chính".
   - KHÔNG dùng "Sở Quy hoạch - Kiến trúc" -> Bắt buộc dùng "Sở Xây dựng".

Dữ liệu thô từ báo chí hôm nay: {news_data}

YÊU CẦU TRÌNH BÀY: Markdown, KHÔNG EMOJI. Văn phong tham mưu chiến lược, bóc tách rủi ro cực kỳ sắc bén. KHÔNG đánh số cứng (1, 2, 3...) cho tiêu đề chính. Tùy biến tiêu đề cho linh hoạt, tuân thủ luồng phân tích 5 bước sau:

CẤU TRÚC BÁO CÁO DỰ KIẾN:
* [Bắt buộc ở dòng đầu tiên] "Thời gian lập báo cáo: {current_time}"

* TIÊU ĐỀ BƯỚC CHECK (Nhận diện & Đánh giá Tác động chính sách 24h): 
  - Tổng hợp tin tức, cảnh báo hiệu lực văn bản. ĐÁNH GIÁ SÂU: Tin tức này tác động thế nào đến rủi ro thời gian và chi phí của Chủ đầu tư? Nêu rõ thẩm quyền rà soát.

* TIÊU ĐỀ BƯỚC PLAN (Chiến lược pháp lý DA ĐT BĐS TỔNG QUÁT): 
  - Đánh giá chiến lược tiếp cận dự án theo Điều 23, 24, 25, 28 Luật Đầu tư 143/2025/QH15. Phân tích ưu/nhược điểm giữa việc tham gia đấu thầu/đấu giá so với xin chấp thuận nhà đầu tư.
  - Thẩm quyền thực hiện: Quốc hội, Thủ tướng, UBND cấp tỉnh, Sở Tài chính.

* TIÊU ĐỀ BƯỚC DO (Phân tích chuyên sâu DA ĐT THÍ ĐIỂM THEO NQ 171/2024/QH15): 
  - Trình bày thành 3 tiểu mục mang tính tham mưu cao:
    + 1. Nút thắt Quy trình & Thẩm quyền: Phân tích khoảng hở thời gian từ lúc HĐND cấp tỉnh duyệt danh mục đến khi UBND cấp tỉnh ra Thông báo. Cơ quan nào (Sở NN&MT hay Sở Tài chính) sẽ nắm quyền chi phối tiến độ ở giai đoạn này?
    + 2. Cơ hội tối ưu hóa chi phí: Việc được chủ động thỏa thuận QSDĐ giúp CĐT chủ động dòng tiền ra sao so với chờ Nhà nước thu hồi đất?
    + 3. Quản trị rủi ro "Đất da báo": Đề xuất giải pháp dự phòng pháp lý cho CĐT nếu quá trình thỏa thuận với dân kéo dài, hoặc không đạt 100% diện tích (áp dụng luật dân sự kết hợp chính sách địa phương).

* TIÊU ĐỀ BƯỚC ACT (Giải pháp tình huống IRAC trình Ban Giám đốc): 
  - Xử lý 1 vướng mắc từ tin tức. 
  - Cấu trúc: Issue (Vấn đề) - Rule (Luật áp dụng) - Application (Phân tích áp dụng) - Conclusion (Phải là một ACTION PLAN/Giải pháp hành động cụ thể cho CĐT).
  - Nêu rõ Thẩm quyền phê duyệt của cơ quan nhà nước (dùng đúng tên Sở mới).

* TIÊU ĐỀ BƯỚC 5: TỪ VỰNG TIẾNG ANH PHÁP LÝ BĐS & UK IDIOM: Bảng từ vựng cao cấp (C1/C2) và 1 thành ngữ đàm phán hợp đồng.
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
