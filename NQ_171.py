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
    """Thu thập dữ liệu đầu vào từ các trang tin pháp luật & kinh tế (Tần suất 2 lần/tuần)"""
    sources = {
        "Chính phủ": "https://baochinhphu.vn/rss/phap-luat.rss",
        "Kinh tế (Tuổi Trẻ)": "https://tuoitre.vn/rss/kinh-doanh.rss",
        "Báo Đấu Thầu": "https://baodauthau.vn/rss/phap-luat-16.rss", 
        "Đại Biểu Nhân Dân": "https://daibieunhandan.vn/rss/phap-luat-kinh-te.rss",
        "VN Business Law": "https://vietnam-business-law.info/feed", 
        "Công Báo Chính Phủ": "https://congbao.chinhphu.vn/rss" 
    }
    
    summary = ""
    for cat, url in sources.items():
        try:
            feed = feedparser.parse(url)
            summary += f"\n--- NGUỒN: {cat.upper()} ---\n"
            # Lấy nhiều tin hơn để đánh giá tính tức thời trong 3-4 ngày qua
            for entry in feed.entries[:7]: 
                desc = entry.get('summary', entry.get('description', ''))
                clean_desc = re.sub('<[^<]+>', '', desc) 
                short_desc = (clean_desc[:350] + '...') if len(clean_desc) > 350 else clean_desc
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {short_desc}\nLink: {entry.link}\n\n"
        except Exception as e:
            print(f"Lỗi tải nguồn {cat}: {e}")
            continue
    return summary

def get_ai_report(news_data):
    """Trợ lý AI xử lý dữ liệu: Phiên bản Tức thời & Linh hoạt"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là Cố vấn Pháp lý cao cấp với tư duy phân tích sắc bén, làm việc trực tiếp với tôi. Nhiệm vụ của bạn là cung cấp báo cáo pháp lý định kỳ chính xác, thực tế, phản ứng ngay lập tức với các biến động của thị trường.

THỜI GIAN LẬP BÁO CÁO: {current_time}

BỘ QUY TẮC CỐT LÕI (TUÂN THỦ TUYỆT ĐỐI):

1. TÍNH TỨC THỜI & VĂN BẢN HIỆN HÀNH:
   - Từ dữ liệu đầu vào, phải quét ngay lập tức các văn bản, dự thảo hoặc chính sách mới nhất. 
   - Luôn ghi rõ trạng thái hiệu lực (Đang hiệu lực, Chờ thi hành, Dự thảo) của mọi quy định được nhắc đến. Nếu có sự chuyển tiếp quy định cũ/mới, phải so sánh ngắn gọn hệ quả thực tế.
   - Không tự suy diễn quy định nếu dữ liệu đầu vào hoặc văn bản hiện hành chưa làm rõ.

2. CẤU TRÚC LINH HOẠT TÙY BIẾN DỮ LIỆU:
   - KHÔNG sử dụng cấu trúc quy trình cố định (như 11 bước).
   - Tùy thuộc vào tin tức và dữ liệu đầu vào của ngày hôm nay, hãy TỰ ĐỘNG CHIA LÀM CÁC BƯỚC/GIAI ĐOẠN trọng tâm đang gặp biến động. (Ví dụ: Nếu tin tức hằng tuần tập trung vào đền bù, hãy xoáy sâu phân tích các bước đền bù; nếu tin tức về tín dụng, xoáy sâu dòng tiền).

3. NQ 171 & GIẢI PHÁP 1:1:
   - Bất cứ khi nào nhận diện được một khó khăn/nút thắt liên quan đến việc thực thi NQ 171 (chuyển mục đích đất khác sang đất ở), BẮT BUỘC phải đi kèm ngay lập tức với một Giải pháp Cố vấn thực chiến cho nút thắt đó.

4. TỪ VỰNG & VĂN PHONG:
   - Ngắn gọn, tinh gọn, sử dụng Bullet points và Bảng biểu. Bỏ các câu dẫn rườm rà.
   - CHỈ SỬ DỤNG từ vựng tiếng Anh chuyên ngành ở trình độ B1 (Ví dụ: Deposit, Lease, Permit, Ownership, Project). Không dùng từ ngữ phức tạp hơn trừ khi là thuật ngữ luật quốc tế bắt buộc.

5. BỐI CẢNH HÀNH CHÍNH (SAU 01/07/2025):
   - NQ 202/2025: Bình Dương, BR-VT đã sáp nhập vào TP.HCM.
   - Chỉ dùng tên: UBND TP.HCM, Sở Nông nghiệp và Môi trường (Xử lý Đất đai), Sở Tài chính (Định giá đất), Sở Xây dựng.

Dữ liệu thô từ báo chí cập nhật: {news_data}

YÊU CẦU TRÌNH BÀY MARKDOWN:
* [Dòng 1] "Cập nhật dữ liệu lúc: {current_time}"
* PHẦN 1: RADAR PHÁP LÝ & TÍNH TỨC THỜI: Liệt kê các chính sách/văn bản mới nhất tác động ngay đến dự án trong tuần này (Kèm trạng thái hiệu lực và hệ quả).
* PHẦN 2: PHÂN TÍCH GIAI ĐOẠN TRỌNG ĐIỂM (Linh hoạt cấu trúc): Dựa vào dữ liệu, tự tạo các bước/giai đoạn đang gặp "điểm nóng" và phân tích bản chất pháp lý.
* PHẦN 3: GỠ VƯỚNG NQ 171 (Mô hình Khó khăn - Giải pháp): Lập bảng liệt kê các điểm nghẽn hiện tại và đề xuất giải pháp trực diện 1:1.
* PHẦN 4: RỦI RO & TỪ VỰNG: Đánh giá rủi ro ngắn gọn và cung cấp 5 từ vựng B1 + 1 Idiom.
"""

    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models_to_try = sorted(available_models, key=lambda x: (0 if 'pro' in x else (1 if 'flash' in x else 2)))
        
        raw_report = "AI Generation Failed."
        for model_name in models_to_try:
            try:
                if "1.0" in model_name: continue 
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                raw_report = response.text
                break
            except Exception as e:
                print(f"Lỗi khi thử model {model_name}: {e}")
                continue
                
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở TN&MT": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "Sở KH&ĐT": "Sở Tài chính",
            "Sở Kế hoạch Đầu tư": "Sở Tài chính",
            "UBND quận": "UBND TP.HCM/Thành phố trực thuộc",
            "Ủy ban nhân dân quận": "UBND TP.HCM/Thành phố trực thuộc",
            "UBND Quận": "UBND TP.HCM/Thành phố trực thuộc",
            "tỉnh Bình Dương": "TP.HCM",
            "tỉnh Bà Rịa": "TP.HCM"
        }
        
        cleaned_report = raw_report
        for old_term, new_term in replacements.items():
            pattern = re.compile(re.escape(old_term), re.IGNORECASE)
            cleaned_report = pattern.sub(new_term, cleaned_report)
            
        return cleaned_report
        
    except Exception as e:
        return f"System Error: {str(e)}"

def send_email(markdown_content):
    """Gửi Email với giao diện báo cáo chuyên biệt, tinh gọn"""
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[RADAR PHÁP LÝ] BÁO CÁO CẬP NHẬT DỰ ÁN NQ 171 #{run_num}"
    msg["From"] = f"Senior Legal Assistant <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'tables'])
    
    full_html = f"""
    <html>
      <head>
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f8f9fa; padding: 20px; line-height: 1.6; color: #333; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #ffffff; padding: 40px; border-top: 6px solid #d93025; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-radius: 4px; }}
            h1 {{ color: #d93025; text-align: left; font-size: 22px; border-bottom: 2px solid #eee; padding-bottom: 15px; margin-bottom: 20px; }}
            h2 {{ color: #1a73e8; border-left: 4px solid #1a73e8; padding-left: 10px; margin-top: 30px; font-size: 18px; text-transform: uppercase; }}
            h3 {{ color: #202124; font-size: 16px; margin-top: 15px; font-weight: 600; }}
            p, li {{ text-align: left; margin-bottom: 12px; font-size: 15px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            table, th, td {{ border: 1px solid #dadce0; padding: 12px; text-align: left; font-size: 14px; }}
            th {{ background-color: #f1f3f4; color: #202124; font-weight: bold; }}
            .footer {{ text-align: left; font-size: 12px; color: #5f6368; margin-top: 40px; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>BÁO CÁO CỐ VẤN PHÁP LÝ ĐỊNH KỲ</h1>
            <div class="content">{html_body}</div>
            <div class="footer">
                Tài liệu tham mưu chuyên môn trực tiếp cho đ/c Vũ Quang Phát.<br>
                Hệ thống cập nhật theo thời gian thực | Vận hành bởi Gemini AI.
            </div>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, pwd)
            server.sendmail(sender, sender, msg.as_string())
        print("Đã gửi báo cáo tức thời thành công!")
    except Exception as e:
        print(f"Lỗi gửi mail: {e}")

if __name__ == "__main__":
    news = get_real_estate_news()
    report = get_ai_report(news)
    send_email(report)
