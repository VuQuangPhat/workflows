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
            for entry in feed.entries[:5]:
                desc = entry.get('summary', entry.get('description', ''))
                clean_desc = re.sub('<[^<]+>', '', desc) 
                short_desc = (clean_desc[:350] + '...') if len(clean_desc) > 350 else clean_desc
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {short_desc}\nLink: {entry.link}\n\n"
        except Exception as e:
            print(f"Lỗi khi tải nguồn {cat}: {e}")
            continue
    return summary

def get_ai_report(news_data):
    """Phân tích dữ liệu bằng AI: Tầm nhìn Cố vấn Vĩ mô & Vi mô, bóc tách điểm nghẽn quy trình"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là Chuyên gia Cố vấn Pháp lý Bất động sản vĩ mô và vi mô, tham mưu chiến lược cho Chuyên viên pháp lý dự án BĐS: Vũ Quang Phát.
Nhiệm vụ: Lập báo cáo phân tích SẮC BÉN, ĐỘC LẬP, từ bức tranh VĨ MÔ đến điểm nghẽn VI MÔ trong quy trình ISO (PDCA).

THỜI GIAN LẬP BÁO CÁO: {current_time}

BỘ QUY TẮC CỐT LÕI (BẮT BUỘC TUÂN THỦ 100%):

1. TƯ DUY CỐ VẤN VĨ MÔ & VI MÔ:
   - Vĩ mô: Đánh giá bức tranh toàn cảnh (luật pháp mới, hạ tầng, sự lúng túng của bộ máy quản lý nhà nước) đang tạo ra rào cản hệ thống nào.
   - Vi mô (Quy trình): Khi phân tích thủ tục, phải chỉ rõ điểm nghẽn nằm ở khâu nào. (Ví dụ: Luật Đất đai 31/2024 cho phép, nhưng quy trình thực tế lại đang tắc ở khâu Sở Tài chính thẩm định giá, hoặc tắc ở Sở Nông nghiệp và Môi trường khi rà soát nguồn gốc đất). Đề xuất giải pháp khơi thông.

2. MÔ HÌNH CHÍNH QUYỀN ĐÔ THỊ (KHÔNG CÒN UBND QUẬN):
   - CẤM TUYỆT ĐỐI dùng "UBND quận". Mọi thẩm quyền cấp cơ sở đô thị thuộc "UBND cấp Thành phố trực thuộc" (như TP. Thủ Đức, TP. Thủ Dầu Một) hoặc UBND TP.HCM.

3. ĐỊA GIỚI HÀNH CHÍNH & TÊN CƠ QUAN CHUYÊN MÔN (SAU 01/07/2025):
   - Bình Dương và Bà Rịa - Vũng Tàu đã sáp nhập vào TP.HCM. (Đồng Nai, Long An là tỉnh độc lập).
   - Chỉ sử dụng tên Sở mới: "Sở Nông nghiệp và Môi trường", "Sở Tài chính", "Sở Xây dựng".

4. BẢN CHẤT NGHỊ QUYẾT 171/2024/QH15:
   - TUYỆT ĐỐI KHÔNG lấy ví dụ cải tạo chung cư cũ. 
   - CHỈ dùng Case Study đi gom quỹ "đất nông nghiệp" hoặc "đất cơ sở sản xuất kinh doanh" vùng ven để làm khu đô thị mới.

5. HÌNH THỨC & VĂN PHONG:
   - Góc nhìn chuyên gia độc lập. Không nhận vơ dự án. Không dùng định dạng thư tín (TO, FROM).

Dữ liệu thô từ báo chí hôm nay: {news_data}

CẤU TRÚC BÁO CÁO DỰ KIẾN (Markdown, Tùy biến tiêu đề linh hoạt theo tin tức):
* [Dòng 1] "Thời gian lập báo cáo: {current_time}"
* TIÊU ĐỀ BƯỚC CHECK (Vĩ mô - Nhận diện Điểm nghẽn hệ thống 24h): Đánh giá bức tranh pháp lý, hạ tầng từ tin tức. Rủi ro hệ thống và cơ hội tổng quan.
* TIÊU ĐỀ BƯỚC PLAN (Vi mô - Nút thắt thủ tục CTCTĐT & Hạ tầng): Case Study dự án ăn theo hạ tầng tại phía Nam. Phân tích tiến độ xin CTCTĐT (Điều 24, 25 Luật Đầu tư 143/2025). Chỉ đích danh điểm nghẽn quy trình nằm ở cơ quan nào (Sở Tài chính hay UBND).
* TIÊU ĐỀ BƯỚC DO (Vĩ mô & Vi mô - Thực chiến NQ 171/2024/QH15): Case Study gom quỹ đất phi nông nghiệp/nông nghiệp. Vĩ mô: NQ 171 tháo gỡ cơ chế gì? Vi mô: Điểm nghẽn thực tế khi đàm phán với dân hoặc khi Sở Nông nghiệp và Môi trường thẩm định chuyển mục đích. Giải pháp gỡ rối.
* TIÊU ĐỀ BƯỚC ACT (Giải pháp Cố vấn - IRAC Plan): Chọn 1 vướng mắc cốt lõi. Phân tích IRAC. Conclusion là Action Plan gỡ rối quy trình cụ thể cho CĐT.
* TIÊU ĐỀ BƯỚC 5: TỪ VỰNG TIẾNG ANH (B1-B2) & UK IDIOM: 5 từ vựng pháp lý B1-B2 (Bảng) & 1 thành ngữ kinh doanh.
"""

    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models_to_try = sorted(available_models, key=lambda x: (0 if 'flash' in x else (1 if 'pro' in x else 2)))
        
        raw_report = "AI Generation Failed."
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                raw_report = response.text
                break
            except:
                continue
                
        # --- BỘ LỌC CƯỠNG CHẾ BẰNG PYTHON ---
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở TN&MT": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "Sở KH&ĐT": "Sở Tài chính",
            "Sở Kế hoạch Đầu tư": "Sở Tài chính",
            "Sở Quy hoạch - Kiến trúc": "Sở Xây dựng",
            "Sở Quy hoạch và Kiến trúc": "Sở Xây dựng",
            "Sở QH-KT": "Sở Xây dựng",
            "UBND quận": "UBND cấp Thành phố trực thuộc",
            "Ủy ban nhân dân quận": "Ủy ban nhân dân cấp Thành phố trực thuộc",
            "UBND Quận": "UBND cấp Thành phố trực thuộc"
        }
        
        cleaned_report = raw_report
        for old_term, new_term in replacements.items():
            pattern = re.compile(re.escape(old_term), re.IGNORECASE)
            cleaned_report = pattern.sub(new_term, cleaned_report)
            
        return cleaned_report
        
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
            .container {{ max-width: 850px; margin: 0 auto; background: #fff; padding: 50px; border-top: 10px solid #004d40; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            h1 {{ color: #004d40; text-align: center; text-transform: uppercase; font-size: 22px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
            h2 {{ color: #004d40; border-bottom: 2px solid #004d40; padding-bottom: 5px; margin-top: 40px; font-size: 19px; text-transform: uppercase; }}
            h3 {{ color: #bf360c; font-size: 17px; margin-top: 20px; }}
            p, li {{ text-align: justify; text-justify: inter-word; margin-bottom: 15px; font-size: 16px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            table, th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #e0f2f1; color: #004d40; }}
            .time-stamp {{ text-align: right; font-style: italic; color: #555; margin-bottom: 30px; font-weight: bold; }}
            .footer {{ text-align: center; font-size: 11px; color: #888; margin-top: 50px; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>BÁO CÁO CỐ VẤN PHÁP LÝ DỰ ÁN BẤT ĐỘNG SẢN</h1>
            <p style="text-align: center;">Tham mưu chuyên môn: <b>Vũ Quang Phát</b></p>
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
