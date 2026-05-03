import os, re, smtplib, feedparser, markdown, pytz
from datetime import datetime
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_real_estate_news():
    """Lọc nguồn tin tinh hoa: Chỉ lấy tin Chính phủ và Pháp lý dự án"""
    sources = {
        "Chính phủ - Pháp luật": "https://baochinhphu.vn/rss/phap-luat.rss",
        "Báo Đấu Thầu - Dự án": "https://baodauthau.vn/rss/phap-luat-16.rss",
        "Công Báo": "https://congbao.chinhphu.vn/rss"
    }
    summary = ""
    for cat, url in sources.items():
        try:
            feed = feedparser.parse(url)
            summary += f"\n--- {cat.upper()} ---\n"
            for entry in feed.entries[:6]: # Chỉ lấy top 6 tin nóng nhất
                desc = re.sub('<[^<]+>', '', entry.get('summary', ''))
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {desc[:350]}...\nLink: {entry.link}\n\n"
        except: continue
    return summary

def get_ai_report(news_data):
    """LÕI TƯ DUY: SENIOR LEGAL ADVISOR (BẢN TỐI ƯU CHO FREE TIER)"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Thiếu API Key. Vui lòng set biến môi trường GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    # --- PROMPT CHIẾN LƯỢC DÀNH CHO BẢN KHÔNG CÓ SEARCH ---
    prompt = f"""
    CONTEXT: Today is {current_time}. 
    
    1. Vai trò và Bản sắc:
    Bạn là một Cố vấn Pháp lý cao cấp với tư duy phân tích sắc bén, hỗ trợ trực tiếp cho chuyên gia pháp lý Vũ Quang Phát. Nhiệm vụ của bạn là cung cấp các giải pháp pháp lý chính xác, thực tế và có tính ứng dụng cao dựa vào dữ liệu được cung cấp.
    
    2. Nguyên tắc cốt lõi về Nội dung:
    - Văn bản hiện hành: Phân tích dựa trên các văn bản quy phạm pháp luật cập nhật nhất trong kiến thức của bạn. Nếu có sự chuyển tiếp (như Luật Đất đai 2024, Luật Nhà ở 2023, Luật Kinh doanh BĐS 2023), phải phân tích rõ sự khác biệt giữa quy định cũ và mới.
    - Độ sâu chuyên môn: Không dừng lại ở việc trích dẫn điều khoản. Phải giải thích được "bản chất pháp lý", "ý đồ của nhà lập pháp" và "hệ quả thực tế" của quy định đó đối với dự án.
    - NQ 171 và Pháp lý BĐS: Đặc biệt chú trọng quy trình gỡ vướng dự án, cơ chế thỏa thuận nhận quyền sử dụng đất (NQ 171) và các thủ tục hành chính tại TP.HCM.
    
    3. Quy tắc phản hồi:
    - Ngắn gọn & Tinh gọn: Đi thẳng vào vấn đề. Sử dụng Bullet points và Bảng so sánh để tối ưu hóa việc đọc nhanh.
    - Ngôn ngữ: Sử dụng tiếng Việt chuyên ngành pháp lý chuẩn xác. Thuật ngữ tiếng Anh giới hạn ở trình độ B1.
    - Phân tích rủi ro: Luôn kèm theo một phần đánh giá về rủi ro pháp lý hoặc các điểm "mờ" trong quy định có thể gây khó khăn khi triển khai thực tế.
    
    4. Cấu trúc phản hồi mặc định:
    - Căn cứ pháp lý: Danh mục các văn bản liên quan.
    - Nội dung phân tích chuyên sâu: Tổng hợp và đánh giá thông tin từ INPUT DATA.
    - Lưu ý thực thi/Rủi ro: Các điểm cần đặc biệt cẩn trọng tại các Sở/Ngành.
    - Gợi ý bước tiếp theo (1:1 Action Plan): Chiến thuật hành động cụ thể cho dự án.
    
    5. Điều khoản cấm:
    - Không được Hallucination (ảo giác): Chỉ phân tích dựa trên sự kiện có thật trong INPUT DATA và kiến thức luật đã được huấn luyện. Tuyệt đối không tự bịa ra văn bản hay số liệu.
    - Không giải thích từ vựng chuyên ngành cơ bản (GPMB, CTĐT, QH 1/500...).
    
    INPUT DATA (DỮ LIỆU TIN TỨC MỚI NHẤT): 
    {news_data}
    """

    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Xếp thứ tự ưu tiên: flash hoạt động tốt và nhanh trên Free Tier
        models_to_try = sorted(available_models, key=lambda x: (0 if 'flash' in x else (1 if 'pro' in x else 2)))
        
        report = "AI Generation Failed."
        
        for model_name in models_to_try:
            try:
                if "1.0" in model_name: continue 
                
                print(f"[*] Đang thử chạy model: {model_name}...")
                
                # KHỞI TẠO MODEL CƠ BẢN - KHÔNG GỌI TOOL ĐỂ TRÁNH LỖI FREE TIER
                model = genai.GenerativeModel(model_name=model_name)
                response = model.generate_content(prompt)
                
                if not response.parts:
                    print(f"[!] Model {model_name} bị chặn do Safety Settings: {response.prompt_feedback}")
                    continue
                    
                report = response.text
                print("[+] Xử lý thành công!")
                break
            except Exception as inner_e:
                print(f"[-] Lỗi ở model {model_name}: {str(inner_e)}")
                continue
                
        return report
    except Exception as e: 
        return f"Lỗi hệ thống AI nghiêm trọng: {str(e)}"

def send_email(markdown_content):
    """Email Executive Style: Tinh gọn và Quyền lực"""
    sender = "phat.clover@gmail.com"
    msg = MIMEMultipart()
    
    msg["Subject"] = f"[TOP PRIORITY] THAM MƯU PHÁP LÝ DỰ ÁN & NQ 171 - #{datetime.now().strftime('%d%m')}"
    msg["From"] = f"Senior Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'tables'])
    full_html = f"""
    <div style="font-family: 'Times New Roman', serif; max-width: 850px; margin: auto; border-top: 8px solid #002D62; padding: 40px; color: #1a1a1a;">
        <h1 style="color: #002D62; text-align: center;">BÁO CÁO THAM MƯU PHÁP LÝ</h1>
        <p style="text-align: center; border-bottom: 1px solid #eee; padding-bottom: 20px;">Strictly Confidential | Dành riêng cho chuyên gia Vũ Quang Phát</p>
        <div style="line-height: 1.8; text-align: justify;">{html_body}</div>
        <div style="margin-top: 50px; text-align: center; font-size: 11px; color: #888;">AI Strategic Advisor System | API Free Tier Edition</div>
    </div>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, os.environ.get('GMAIL_PASSWORD'))
            server.sendmail(sender, sender, msg.as_string())
        print("[+] Báo cáo tham mưu đã được gửi trực tiếp qua Email.")
    except Exception as e: 
        print(f"[-] Email Error: {e}")

if __name__ == "__main__":
    print("[*] Đang cào dữ liệu tin tức pháp lý...")
    news = get_real_estate_news()
    print("[*] Bắt đầu phân tích AI...")
    report = get_ai_report(news)
    print("[*] Đang gửi báo cáo qua Email...")
    send_email(report)
    print("[+] Hoàn tất quy trình!")
