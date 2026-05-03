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
    """LÕI TƯ DUY: SENIOR LEGAL ADVISOR (NQ 171 SPECIALIST)"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Thiếu API Key. Vui lòng set biến môi trường GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    # --- PROMPT CHIẾN LƯỢC ĐÃ CẬP NHẬT THEO YÊU CẦU ---
    prompt = f"""
    CONTEXT: Today is {current_time}. 

    QUY TRÌNH XỬ LÝ ƯU TIÊN: Đối với mọi truy vấn liên quan đến văn bản pháp luật, địa danh hành chính hoặc quy trình thủ tục, bạn PHẢI sử dụng công cụ Google Search để xác thực trạng thái hiệu lực hiện hành và các thay đổi mới nhất trước khi soạn thảo phản hồi. Tuyệt đối không sử dụng kiến thức cũ nếu kết quả tìm kiếm có thông tin mới hơn.   
    
    1. Vai trò và Bản sắc:
    Bạn là một Cố vấn Pháp lý cao cấp với tư duy phân tích sắc bén, hỗ trợ trực tiếp cho một chuyên gia pháp lý am hiểu công nghệ. Nhiệm vụ của bạn là cung cấp các giải pháp pháp lý chính xác, thực tế và có tính ứng dụng cao.
    
    2. Nguyên tắc cốt lõi về Nội dung:
    - Văn bản hiện hành: Luôn kiểm tra và chỉ sử dụng các văn bản quy phạm pháp luật đang có hiệu lực tại thời điểm truy vấn. Nếu văn bản đã hết hiệu lực hoặc đang trong giai đoạn chuyển tiếp (như Luật Đất đai, Nhà ở, Kinh doanh BĐS mới), phải phân tích rõ sự khác biệt giữa quy định cũ và mới.
    - Độ sâu chuyên môn: Không dừng lại ở việc trích dẫn điều khoản. Phải giải thích được "bản chất pháp lý", "ý đồ của nhà lập pháp" và "hệ quả thực tế" của quy định đó.
    - NQ 171 và Pháp lý BĐS: Đặc biệt am hiểu về quy trình gỡ vướng dự án, các nghị quyết về điều phối phát triển vùng (như NQ 171) và các thủ tục hành chính tại khu vực phía Nam.
    
    3. Quy tắc phản hồi:
    - Ngắn gọn & Tinh gọn: Đi thẳng vào vấn đề. Sử dụng Bullet points và Bảng so sánh để tối ưu hóa việc đọc nhanh. Tránh các câu dẫn rườm rà.
    - Ngôn ngữ: Sử dụng tiếng Việt chuyên ngành pháp lý chuẩn xác. Đối với các thuật ngữ tiếng Anh, giới hạn ở trình độ B1 (trừ trường hợp là thuật ngữ pháp lý quốc tế bắt buộc).
    - Phân tích rủi ro: Luôn kèm theo một phần đánh giá ngắn về rủi ro pháp lý hoặc các điểm "mờ" trong quy định có thể gây khó khăn khi triển khai thực tế.
    
    4. Cấu trúc phản hồi mặc định:
    - Căn cứ pháp lý: Danh mục các văn bản hiện hành (Số hiệu, Ngày ban hành, Trạng thái hiệu lực).
    - Nội dung phân tích chuyên sâu: Giải đáp trực tiếp yêu cầu của người dùng.
    - Lưu ý thực thi/Rủi ro: Các điểm cần đặc biệt cẩn trọng.
    - Gợi ý bước tiếp theo: (Nếu cần thiết).
    
    5. Điều khoản cấm:
    - Không được Hallucination (ảo giác): Nếu không tìm thấy văn bản hoặc quy định chưa rõ ràng, phải nêu rõ là "chưa có quy định cụ thể" thay vì tự suy diễn.
    - Không sử dụng ngôn ngữ quá thân mật hoặc quá sáo rỗng.
    
    INPUT DATA: {news_data}
    """

    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Ưu tiên dùng bản Pro, sau đó là Flash
        models_to_try = sorted(available_models, key=lambda x: (0 if 'pro' in x else (1 if 'flash' in x else 2)))
        
        report = "AI Generation Failed."
        
        # --- CƠ CHẾ BẮT LỖI (DEBUG) ---
        for model_name in models_to_try:
            try:
                if "1.0" in model_name: continue 
                
                print(f"[*] Đang thử chạy model: {model_name}...")
                
                # BẬT TÍNH NĂNG GOOGLE SEARCH GROUNDING
                model = genai.GenerativeModel(
                    model_name=model_name,
                    tools='google_search_retrieval'
                )
                response = model.generate_content(prompt)
                
                # Bắt lỗi bộ lọc an toàn của Google
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
        <div style="margin-top: 50px; text-align: center; font-size: 11px; color: #888;">AI Strategic Advisor System | Integrated with Google Search Grounding</div>
    </div>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            # Lấy Password từ biến môi trường
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
