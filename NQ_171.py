import os, re, smtplib, feedparser, markdown, pytz, requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

def get_real_estate_news():
    """Trích xuất tin tức pháp lý vĩ mô"""
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
            for entry in feed.entries[:3]: 
                desc = re.sub('<[^<]+>', '', entry.get('summary', ''))
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {desc[:200]}...\nLink: {entry.link}\n\n"
        except Exception as e:
            continue
    return summary

def get_admin_notices(url):
    """Trích xuất thông báo, văn bản vi mô từ Sở ban ngành"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = soup.find_all(['div', 'li'], class_=re.compile('article-item|news-item|list-item'))
        extracted_data = ""
        keywords = ["thí điểm", "nhà ở thương mại", "thỏa thuận nhận quyền", "chuyển mục đích", "danh mục khu đất", "trả hồ sơ"]
        
        count = 0
        for article in articles:
            title_tag = article.find('a')
            if not title_tag: continue
            
            title = title_tag.text.strip()
            link = title_tag.get('href', '')
            if not link.startswith('http'): 
                link = "https://donvi.tphcm.gov.vn" + link
                
            if any(kw.lower() in title.lower() for kw in keywords):
                extracted_data += f"- {title}\n  Link: {link}\n"
                count += 1
            if count >= 5: break
            
        return extracted_data if extracted_data else "Không có thông báo mới sát với từ khóa."
    except Exception as e:
        return f"[-] Lỗi quét Cổng thông tin: {str(e)}"

def get_ai_report(news_data, admin_data, project_status):
    """LÕI TƯ DUY: SYSTEM INSTRUCTION TÍCH HỢP GOOGLE SEARCH"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu API Key."
    
    client = genai.Client(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    sys_instruct = """
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
    ### Căn cứ pháp lý
    (Danh mục các văn bản hiện hành: Số hiệu, Ngày ban hành, Trạng thái hiệu lực).
    ### Nội dung phân tích chuyên sâu
    (Giải đáp trực tiếp yêu cầu của người dùng).
    ### Lưu ý thực thi / Rủi ro
    (Các điểm cần đặc biệt cẩn trọng).
    ### Gợi ý bước tiếp theo
    (Nếu cần thiết).
    
    5. Điều khoản cấm:
    - Không được Hallucination (ảo giác): Nếu không tìm thấy văn bản hoặc quy định chưa rõ ràng, phải nêu rõ là "chưa có quy định cụ thể" thay vì tự suy diễn.
    - Không sử dụng ngôn ngữ quá thân mật hoặc quá sáo rỗng.
    """

    user_prompt = f"""
    CONTEXT: Today is {current_time}.
    
    DỮ LIỆU ĐẦU VÀO CẬP NHẬT:
    [TIN TỨC BÁO CHÍ]: {news_data}
    [THÔNG BÁO HÀNH CHÍNH]: {admin_data}
    [THỰC TRẠNG DỰ ÁN]: {project_status}
    
    Hãy xuất báo cáo theo đúng cấu trúc và quy tắc đã được nạp. Nhớ xác thực trạng thái văn bản qua Search.
    """

    try:
        available_models = [m.name for m in client.models.list()]
        model_id = next((m for m in available_models if 'flash' in m), 'gemini-1.5-flash')
        
        response = client.models.generate_content(
            model=model_id,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct,
                temperature=0.1, 
                tools=[{"google_search": {}}] # BẬT CHỨC NĂNG TÌM KIẾM WEB CHO AI
            )
        )
        return response.text
    except Exception as e:
        if "429" in str(e): return "Lỗi 429: Đã vượt quá hạn mức API Free. Cần chờ reset quota."
        return f"Lỗi hệ thống AI: {str(e)}"

def send_email(markdown_content):
    """Gửi email format chuyên nghiệp"""
    sender = "phat.clover@gmail.com"
    msg = MIMEMultipart()
    msg["Subject"] = f"[TOP PRIORITY] LEGAL STRATEGY REPORT - #{datetime.now().strftime('%d%m')}"
    msg["From"] = f"Senior Legal Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'tables'])
    full_html = f"""
    <div style="font-family: 'Times New Roman', serif; max-width: 850px; margin: auto; border-top: 12px solid #002D62; padding: 50px; color: #1a1a1a; line-height: 1.8;">
        <h1 style="color: #002D62; text-align: center; font-size: 28px;">BÁO CÁO THAM MƯU PHÁP LÝ TUẦN</h1>
        <p style="text-align: center; border-bottom: 2px solid #eee; padding-bottom: 20px; font-style: italic;">Strictly Confidential | Prepared for: Vũ Quang Phát</p>
        <div style="font-size: 18px; text-align: justify;">{html_body}</div>
        <div style="margin-top: 60px; text-align: center; font-size: 11px; color: #888;">
            AI Flash Free Tier | Google Search Grounding Enabled | Compliance Framework 2026
        </div>
    </div>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, os.environ.get('GMAIL_PASSWORD'))
            server.sendmail(sender, sender, msg.as_string())
        print("[+] Báo cáo pháp lý đã được gửi thành công.")
    except Exception as e: 
        print(f"[-] Email Error: {e}")

if __name__ == "__main__":
    TARGET_URL = "https://donvi.tphcm.gov.vn/thong-bao" 
    
    # Đọc dữ liệu đầu vào linh hoạt từ file .txt
    project_file_path = "project_status.txt"
    if os.path.exists(project_file_path):
        with open(project_file_path, "r", encoding="utf-8") as file:
            REAL_PROJECT_STATUS = file.read().strip()
    else:
        REAL_PROJECT_STATUS = "Chưa có dữ liệu dự án cụ thể. Vui lòng phân tích tổng quan các điểm mới nhất về NQ 171."
    
    news = get_real_estate_news()
    admin_notices = get_admin_notices(TARGET_URL)
    report = get_ai_report(news, admin_notices, REAL_PROJECT_STATUS)
    send_email(report)
