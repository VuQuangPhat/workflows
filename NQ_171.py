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
    """Thu thập dữ liệu đầu vào (Cập nhật liên tục)"""
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
            for entry in feed.entries[:6]: 
                desc = entry.get('summary', entry.get('description', ''))
                clean_desc = re.sub('<[^<]+>', '', desc) 
                short_desc = (clean_desc[:350] + '...') if len(clean_desc) > 350 else clean_desc
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {short_desc}\nLink: {entry.link}\n\n"
        except Exception as e:
            print(f"Lỗi tải nguồn {cat}: {e}")
            continue
    return summary

def get_ai_report(news_data):
    """Trợ lý AI Cố vấn Pháp lý Cao cấp - Tích hợp IRAC & Tư duy linh hoạt"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là một Cố vấn Pháp lý cao cấp với tư duy phân tích sắc bén, hỗ trợ trực tiếp cho chuyên gia pháp lý Vũ Quang Phát. Nhiệm vụ của bạn là cung cấp các giải pháp pháp lý chính xác, thực tế và có tính ứng dụng cao.

THỜI GIAN LẬP BÁO CÁO: {current_time}

QUY TRÌNH XỬ LÝ & NGUYÊN TẮC CỐT LÕI (TUÂN THỦ 100%):
1. BỘ LỌC TIN TỨC: Tuyệt đối bỏ qua các tin tức vĩ mô không liên quan trực tiếp đến BĐS (ví dụ: xuất khẩu gạo, thuế vãng lai nhỏ lẻ). Chỉ giữ lại tin tác động đến quy hoạch, đền bù, giá đất, thủ tục đầu tư.
2. SỰ LINH HOẠT TỰ CHỦ: Không dùng một quy trình cố định. Hãy tự do chia nội dung phân tích thành các "bước" hoặc "vấn đề trọng tâm" tùy thuộc vào luồng dữ liệu đầu vào của ngày hôm nay.
3. ĐỘ SÂU CHUYÊN MÔN: Không chỉ trích dẫn điều khoản. Phải giải thích "bản chất pháp lý", "ý đồ nhà lập pháp" và "hệ quả thực tế". Không tự suy diễn (hallucination) nếu văn bản chưa rõ ràng.
4. NGÔN NGỮ: Tiếng Việt chuyên ngành tinh gọn (dùng Bullet points/Bảng). Thuật ngữ tiếng Anh GIỚI HẠN NGHIÊM NGẶT ở trình độ B1 (VD: Deposit, Lease, Permit, Ownership, Project). Không dùng từ C1/C2.
5. BỐI CẢNH ĐỊA LÝ & HÀNH CHÍNH (Sau sáp nhập NQ 202/2025): Bình Dương, BR-VT thuộc TP.HCM. Bắt buộc dùng: UBND TP.HCM, Sở Nông nghiệp và Môi trường (phụ trách đất đai/nguồn gốc), Sở Tài chính (định giá đất).

DỮ LIỆU ĐẦU VÀO TỪ BÁO CHÍ HÔM NAY:
{news_data}

CẤU TRÚC PHẢN HỒI MẶC ĐỊNH (Sử dụng Markdown chuyên nghiệp):
* [Dòng 1] "Cập nhật dữ liệu lúc: {current_time}"

### 1. CĂN CỨ PHÁP LÝ HIỆN HÀNH
- Danh mục văn bản đang có hiệu lực (hoặc dự thảo) liên quan trực tiếp đến tin tức (Số hiệu, Ngày ban hành, Trạng thái hiệu lực). Phân tích rõ khác biệt nếu đang trong giai đoạn chuyển tiếp.

### 2. NỘI DUNG PHÂN TÍCH CHUYÊN SÂU (TỰ ĐỘNG CHIA NHÓM VẤN ĐỀ)
- Lựa chọn các điểm nóng nhất từ dữ liệu và tự đặt tiêu đề phân tích.
- [BẮT BUỘC ĐỐI VỚI VƯỚNG MẮC NQ 171]: Trình bày theo mô hình IRAC:
  + I - Issue (Vấn đề)
  + R - Rule (Quy định)
  + A - Application (Áp dụng/Hệ quả thực tế)
  + C - Conclusion (Kết luận & Giải pháp Cố vấn 1:1)

### 3. LƯU Ý THỰC THI & RỦI RO PHÁP LÝ
- Đánh giá ngắn gọn rủi ro hoặc các điểm "mờ" trong quy định có thể làm đình trệ dự án.

### 4. GỢI Ý BƯỚC TIẾP THEO & TỪ VỰNG B1
- Đề xuất hành động lập tức cho bộ phận pháp lý.
- Cung cấp 5 từ vựng B1 + 1 Idiom thương mại.
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
                
        # --- BỘ LỌC TỪ KHÓA BẮT BUỘC ---
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở TN&MT": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "Sở KH&ĐT": "Sở Tài chính",
            "Sở Kế hoạch Đầu tư": "Sở Tài chính",
            "UBND quận": "UBND TP.HCM",
            "Ủy ban nhân dân quận": "UBND TP.HCM",
            "UBND Quận": "UBND TP.HCM",
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
    """Gửi Email với giao diện Báo cáo Tham mưu"""
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[CỐ VẤN PHÁP LÝ] BÁO CÁO CẬP NHẬT DỰ ÁN #{run_num}"
    msg["From"] = f"Senior Legal Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'nl2br', 'tables'])
    
    full_html = f"""
    <html>
      <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; padding: 25px; line-height: 1.6; color: #1c1e21; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #ffffff; padding: 45px; border-top: 8px solid #0056b3; box-shadow: 0 5px 15px rgba(0,0,0,0.08); border-radius: 8px; }}
            h1 {{ color: #0056b3; text-align: left; font-size: 24px; border-bottom: 2px solid #e4e6eb; padding-bottom: 15px; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 0.5px; }}
            h2 {{ color: #004085; border-left: 5px solid #0056b3; padding-left: 12px; margin-top: 35px; font-size: 19px; background-color: #eef3f8; padding-top: 8px; padding-bottom: 8px; }}
            h3 {{ color: #b02a37; font-size: 17px; margin-top: 20px; font-weight: 600; }}
            p, li {{ text-align: left; margin-bottom: 12px; font-size: 15px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 25px 0; }}
            table, th, td {{ border: 1px solid #ced4da; padding: 14px; text-align: left; font-size: 14.5px; }}
            th {{ background-color: #e9ecef; color: #212529; font-weight: 700; text-transform: uppercase; font-size: 13px; }}
            .footer {{ text-align: left; font-size: 13px; color: #6c757d; margin-top: 45px; border-top: 1px solid #dee2e6; padding-top: 20px; font-weight: 500; }}
        </style>
      </head>
      <body>
        <div class="container">
            <h1>THÔNG TIN THAM MƯU PHÁP LÝ DỰ ÁN</h1>
            <div class="content">{html_body}</div>
            <div class="footer">
                Tài liệu lưu hành nội bộ - Thực hiện riêng cho đ/c Vũ Quang Phát.<br>
                Hệ thống Cố vấn AI tự động | Vận hành bởi Gemini API.
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
        print("Đã gửi báo cáo tham mưu thành công!")
    except Exception as e:
        print(f"Lỗi gửi mail: {e}")

if __name__ == "__main__":
    news = get_real_estate_news()
    report = get_ai_report(news)
    send_email(report)
