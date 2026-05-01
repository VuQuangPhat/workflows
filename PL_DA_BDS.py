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
    """Phân tích bằng AI: Lộ trình từ CTCTĐT đến Mở bán (Sales Eligibility)"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
Bạn là Chuyên gia Cố vấn Pháp lý BĐS chiến lược, tham mưu cho Chuyên viên pháp lý dự án Vũ Quang Phát.
Nhiệm vụ: Lập báo cáo CHIẾN LƯỢC xuyên suốt từ CTCTĐT đến khâu ĐỦ ĐIỀU KIỆN MỞ BÁN.

THỜI GIAN LẬP BÁO CÁO: {current_time}

BỘ QUY TẮC CỐT LÕI (TUÂN THỦ 100%):

1. LỘ TRÌNH VỀ ĐÍCH (MỞ BÁN DỰ ÁN):
   - Không chỉ dừng ở CTCTĐT. Phải phân tích các nhịp tiếp theo: 
     + Nhịp 1 (Đất đai): Quyết định giao đất/cho thuê đất -> Thẩm định giá đất (Sở Tài chính) -> Hoàn thành nghĩa vụ tài chính -> Cấp GCN QSDĐ dự án[cite: 1].
     + Nhịp 2 (Xây dựng): Phê duyệt quy hoạch 1/500 -> Thiết kế cơ sở/Kỹ thuật -> Giấy phép xây dựng (Sở Xây dựng).
     + Nhịp 3 (Bán hàng): Hoàn thành phần móng (đối với chung cư) hoặc hạ tầng kỹ thuật (đối với đất nền) -> Văn bản thông báo đủ điều kiện bán của Sở Xây dựng -> Bảo lãnh ngân hàng.

2. TƯ DUY NQ 171/2024/QH15 & CMĐSDĐ:
   - Bản chất: CMĐ từ đất nông nghiệp/phi nông nghiệp sang ĐẤT Ở. 
   - Điểm nghẽn bán hàng: Dự án thí điểm NQ 171 phải hoàn thành CMĐSDĐ và nộp tiền sử dụng đất mới được phép kinh doanh. Phân tích rủi ro trượt giá đất làm ảnh hưởng đến giá bán dự kiến.

3. CHUẨN HÓA BỘ MÁY (SAU 01/07/2025):
   - TUYỆT ĐỐI KHÔNG DÙNG: "UBND quận", "Tỉnh Bình Dương", "Tỉnh Bà Rịa - Vũng Tàu"[cite: 3, 5].
   - THẨM QUYỀN MỚI: UBND TP.HCM/Thành phố trực thuộc; Sở Nông nghiệp và Môi trường (Đất đai); Sở Tài chính (Đầu tư/Giá đất); Sở Xây dựng (Quy hoạch/Bán hàng)[cite: 5].

Dữ liệu thô từ báo chí: {news_data}

CẤU TRÚC BÁO CÁO (Markdown, Sắc bén, Tham mưu vĩ mô & vi mô):
* [Dòng 1] "Thời gian lập báo cáo: {current_time}"
* TIÊU ĐỀ BƯỚC CHECK (Vĩ mô - Nhận diện tác động chính sách đến lộ trình mở bán): Đánh giá tin tức ảnh hưởng thế nào đến "đầu ra" của dự án (sức mua, lãi suất, thủ tục xác định giá đất).
* TIÊU ĐỀ BƯỚC PLAN (Vi mô - Nút thắt quy trình ISO từ CTCTĐT đến Giấy phép xây dựng): Case Study hạ tầng miền Nam. Chỉ rõ điểm nghẽn kẹt tại khâu nào của Sở Tài chính (định giá) hay Sở Xây dựng (thẩm định thiết kế).
* TIÊU ĐỀ BƯỚC DO (Thực chiến NQ 171/2024/QH15 - Chiến thuật "về đích" cho dự án gom đất): Cách xử lý vướng mắc CMĐSDĐ để sớm có "Sổ hồng dự án" làm điều kiện mở bán. Giải pháp đối phó với tình trạng giá đất biến động hậu sáp nhập TP.HCM.
* TIÊU ĐỀ BƯỚC ACT (IRAC Plan - Điều kiện Mở bán dự án): Chọn 1 vướng mắc (Ví dụ: Chưa nộp xong tiền sử dụng đất nhưng muốn ký Hợp đồng đặt cọc). Phân tích rủi ro theo Luật KDBĐS 2023 và Action Plan cho CĐT.
* TIÊU ĐỀ BƯỚC 5: TỪ VỰNG TIẾNG ANH (B1-B2) & UK IDIOM: 5 từ vựng về điều kiện bán hàng & 1 thành ngữ.
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
                
        # --- BỘ LỌC CƯỠNG CHẾ BẰNG PYTHON (Triệt để lỗi thời) ---
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở TN&MT": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "Sở KH&ĐT": "Sở Tài chính",
            "UBND quận": "UBND cấp Thành phố trực thuộc/UBND TP.HCM",
            "Ủy ban nhân dân quận": "UBND TP.HCM/Thành phố trực thuộc",
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
    sender = "phat.clover@gmail.com"
    pwd = os.environ.get('GMAIL_PASSWORD')
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')
    
    msg = MIMEMultipart()
    msg["Subject"] = f"[PHÁP LÝ BĐS] BÁO CÁO CHIẾN LƯỢC MỞ BÁN #{run_num}"
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
