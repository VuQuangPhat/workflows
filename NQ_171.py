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
    """Thu thập dữ liệu đầu vào từ các nguồn tin tức pháp luật & kinh tế trọng điểm"""
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
    """Trợ lý AI Cố vấn Pháp lý - Phiên bản Mở rộng & Linh hoạt"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    prompt = f"""
QUY TRÌNH XỬ LÝ ƯU TIÊN: Đối với mọi truy vấn liên quan đến văn bản pháp luật, địa danh hành chính hoặc quy trình thủ tục, bạn PHẢI quét xác thực trạng thái hiệu lực hiện hành và các thay đổi mới nhất trước khi soạn thảo phản hồi. Tuyệt đối không sử dụng kiến thức cũ nếu có thông tin mới hơn.   

THỜI GIAN CẬP NHẬT: {current_time}

1. Vai trò và Bản sắc:
Bạn là một Cố vấn Pháp lý cao cấp với tư duy phân tích sắc bén, làm việc trực tiếp với tôi. Nhiệm vụ của bạn là cung cấp các giải pháp pháp lý chính xác, thực tế và có tính ứng dụng cao. Bỏ qua các định nghĩa cơ bản, đi thẳng vào chiến thuật tháo gỡ.

2. Nguyên tắc cốt lõi về Nội dung:
- Ma trận pháp lý mở rộng: Không chỉ bó hẹp ở Luật Đất đai. Bắt buộc rà soát liên thông các văn bản liên quan (Luật Đầu tư, Xây dựng, Quy hoạch, Kinh doanh BĐS, Môi trường) để tìm hướng mở.
- Văn bản hiện hành: Luôn kiểm tra và chỉ sử dụng các văn bản đang có hiệu lực tại thời điểm truy vấn. Nếu văn bản đã hết hiệu lực hoặc đang trong giai đoạn chuyển tiếp, phải phân tích rõ sự khác biệt giữa quy định cũ và mới.
- Độ sâu chuyên môn: Không dừng lại ở việc trích dẫn điều khoản. Phải giải thích được "bản chất pháp lý", "ý đồ của nhà lập pháp" và "hệ quả thực tế" của quy định đó.
- NQ 171 và Pháp lý BĐS: Đặc biệt am hiểu về quy trình gỡ vướng dự án từ lúc gom đất đến khi ra sản phẩm, các nghị quyết về điều phối phát triển vùng (như NQ 171) và các thủ tục hành chính tại khu vực phía Nam.

3. Quy tắc phản hồi:
- Ngắn gọn & Tinh gọn: Đi thẳng vào vấn đề. Sử dụng Bullet points và Bảng so sánh để tối ưu hóa việc đọc nhanh. Tránh các câu dẫn rườm rà.
- Ngôn ngữ: Sử dụng tiếng Việt chuyên ngành pháp lý chuẩn xác. Đối với các thuật ngữ tiếng Anh, GIỚI HẠN TUYỆT ĐỐI ở trình độ B1 (Ví dụ: Project, Permit, Deposit, Lease, Ownership).
- Phân tích rủi ro: Luôn kèm theo một phần đánh giá ngắn về rủi ro pháp lý hoặc các điểm "mờ" trong quy định có thể gây khó khăn khi triển khai thực tế.

4. Cấu trúc phản hồi linh hoạt (Dynamic Structure):
- KHÔNG sử dụng cấu trúc cố định. Hãy tự động đánh giá dữ liệu đầu vào để chia nội dung thành các bước xử lý, giai đoạn dự án hoặc nhóm vấn đề trọng tâm cho phù hợp.
- BẮT BUỘC áp dụng mô hình IRAC (Issue - Rule - Application - Conclusion) cho các phân tích điểm nghẽn (ví dụ: vướng mắc thỏa thuận đất theo NQ 171). Phần Conclusion phải là giải pháp thực chiến 1:1, không đề xuất chung chung.
- Đảm bảo có phần liệt kê nhanh Căn cứ pháp lý (Số hiệu, Ngày ban hành, Trạng thái hiệu lực) ở đầu báo cáo.

5. Điều khoản cấm:
- Không được Hallucination (ảo giác): Nếu không tìm thấy văn bản hoặc quy định chưa rõ ràng, phải nêu rõ là "chưa có quy định cụ thể" thay vì tự suy diễn.
- Không sử dụng ngôn ngữ quá thân mật hoặc quá sáo rỗng.
- CẤM sai lệch địa giới hành chính (Hậu 01/07/2025): Bình Dương, BR-VT thuộc TP.HCM. Bắt buộc dùng: UBND TP.HCM, Sở Nông nghiệp và Môi trường, Sở Tài chính, Sở Xây dựng.

DỮ LIỆU ĐẦU VÀO TỪ BÁO CHÍ HÔM NAY:
{news_data}
"""

    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Ưu tiên model Pro cho tư duy pháp lý phức tạp
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
                
        # --- BỘ LỌC TỪ KHÓA ÉP BUỘC ĐỊA GIỚI/CƠ QUAN ---
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
            "tỉnh Bà Rịa": "TP.HCM",
            "tỉnh Bà Rịa - Vũng Tàu": "TP.HCM"
        }
        
        cleaned_report = raw_report
        for old_term, new_term in replacements.items():
            pattern = re.compile(re.escape(old_term), re.IGNORECASE)
            cleaned_report = pattern.sub(new_term, cleaned_report)
            
        return cleaned_report
        
    except Exception as e:
        return f"System Error: {str(e)}"

def send_email(markdown_content):
    """Gửi Email Báo cáo Tham mưu Pháp lý Nội bộ"""
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
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6f9; padding: 20px; line-height: 1.6; color: #2c3e50; }}
            .container {{ max-width: 920px; margin: 0 auto; background: #ffffff; padding: 40px; border-top: 6px solid #1a5276; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-radius: 6px; }}
            h1 {{ color: #1a5276; text-align: left; font-size: 22px; border-bottom: 2px solid #ecf0f1; padding-bottom: 12px; margin-bottom: 20px; text-transform: uppercase; }}
            h2 {{ color: #2471a3; border-left: 4px solid #2980b9; padding-left: 10px; margin-top: 30px; font-size: 18px; }}
            h3 {{ color: #c0392b; font-size: 16px; margin-top: 15px; font-weight: bold; }}
            p, li {{ text-align: justify; margin-bottom: 10px; font-size: 15px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            table, th, td {{ border: 1px solid #bdc3c7; padding: 12px; text-align: left; font-size: 14px; }}
            th {{ background-color: #ecf0f1; color: #2c3e50; font-weight: bold; text-transform: uppercase; }}
            .footer {{ text-align: left; font-size: 12px; color: #7f8c8d; margin-top: 40px; border-top: 1px solid #ecf0f1; padding-top: 15px; font-style: italic; }}
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
