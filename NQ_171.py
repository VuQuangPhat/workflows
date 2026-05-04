import os, re, smtplib, feedparser, markdown, pytz, requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from google import genai
from google.genai import types # Import module types để cấu hình System Instruction

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
    """LÕI TƯ DUY: SYSTEM INSTRUCTION CHO BẢN FREE FLASH"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu API Key."
    
    client = genai.Client(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    # 1. TẦNG NÃO BỘ (SYSTEM INSTRUCTION): Chứa toàn bộ bản sắc và quy tắc
    sys_instruct = """
    QUY TRÌNH XỬ LÝ ƯU TIÊN: Bạn là một Cố vấn Pháp lý cao cấp, hỗ trợ trực tiếp cho chuyên gia Vũ Quang Phát. Nhiệm vụ của bạn là phân tích dữ liệu đầu vào để đưa ra giải pháp pháp lý chính xác, thực tiễn và ứng dụng cao cho các dự án bất động sản.
    1. Nguyên tắc cốt lõi về Nội dung (ANTI-HALLUCINATION):
    - Dữ liệu tối thượng: CHỈ được phép đánh giá và trích dẫn dựa trên [TIN TỨC BÁO CHÍ], [THÔNG BÁO HÀNH CHÍNH] và [TRUTH DATA] được cung cấp.
    - Giới hạn kiến thức: KHÔNG tự ý suy diễn hoặc viện dẫn các văn bản pháp luật không có trong dữ liệu đầu vào hoặc đã hết hiệu lực (như Luật Đất đai 2013, NĐ 43, 44, 47...). 
    - Nếu thông tin đầu vào không đủ để kết luận, BẮT BUỘC phải ghi rõ: "Chưa có quy định/thông tin cụ thể để xác định".
    - Đặc biệt am hiểu thủ tục hành chính tại TP.HCM, quy trình gỡ vướng pháp lý và cơ chế thí điểm theo NQ 171/2024/QH15 và NĐ 75/2025/NĐ-CP.

    2. Độ sâu chuyên môn:
    - Không chỉ liệt kê văn bản. Phải giải thích rõ "bản chất pháp lý", "ý đồ nhà lập pháp" và "hệ quả thực tế" tác động trực tiếp đến hiện trạng dự án.

    3. Quy tắc phản hồi:
    - Ngắn gọn & Tinh gọn: Đi thẳng vấn đề. Sử dụng Bullet points để tối ưu hóa việc đọc nhanh (scannable).
    - Ngôn ngữ: Sử dụng tiếng Việt chuyên ngành pháp lý sắc bén, khách quan. Đối với thuật ngữ tiếng Anh, giới hạn ở mức B1. Tuyệt đối KHÔNG dùng từ ngữ sáo rỗng, hô khẩu hào.

    4. Cấu trúc phản hồi BẮT BUỘC (Phải dùng chính xác các Heading này):
    ### Căn cứ pháp lý
    (Liệt kê văn bản hiện hành: Số hiệu, Ngày ban hành. Chỉ lấy từ Truth Data).
    ### Nội dung phân tích chuyên sâu
    (Giải đáp trực tiếp, soi chiếu luật vào vướng mắc thực tế của dự án).
    ### Lưu ý thực thi / Rủi ro
    (Đánh giá các rủi ro pháp lý, điểm "mờ", đặc biệt là rủi ro đàm phán giải phóng mặt bằng, nghĩa vụ tài chính).
    ### Gợi ý bước tiếp theo
    (Đề xuất hành động 1:1, ngắn gọn, có mốc thời gian/deadline nếu cần).
    """

    # 2. TẦNG DỮ LIỆU (USER PROMPT): Chỉ chứa context thay đổi hàng ngày
    user_prompt = f"""
    CONTEXT: Today is {current_time}.
    
    DỮ LIỆU ĐẦU VÀO CẬP NHẬT:
    [TIN TỨC BÁO CHÍ]: {news_data}
    [THÔNG BÁO HÀNH CHÍNH]: {admin_data}
    [THỰC TRẠNG DỰ ÁN]: {project_status}
    
    Hãy xuất báo cáo theo đúng cấu trúc và quy tắc đã được nạp.
    """

    try:
        # Tự động fetch model flash free mới nhất
        available_models = [m.name for m in client.models.list()]
        model_id = next((m for m in available_models if 'flash' in m), 'gemini-1.5-flash')
        
        # Cấu hình tham số kiểm soát ảo giác
        response = client.models.generate_content(
            model=model_id,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct,
                temperature=0.1, # Ép model trả lời logic, khô khan, chuẩn pháp lý thay vì sáng tạo
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
            AI Flash Free Tier | Strict Mode Enabled | Compliance Framework 2026
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
    REAL_PROJECT_STATUS = """
    - DA Hung Thinh: Nghẽn thẩm định giá (thặng dư) tại Sở Tài chính TP.HCM.
    - DA Saigonres: Vướng chuyển đổi đất nông nghiệp theo NQ 171/2024/QH15. Chưa chốt được giá đền bù với 15% hộ dân còn lại.
    - DA Hoa Sen: Khảo sát đấu giá tại Long An, Tiền Giang.
    """
    
    news = get_real_estate_news()
    admin_notices = get_admin_notices(TARGET_URL)
    report = get_ai_report(news, admin_notices, REAL_PROJECT_STATUS)
    send_email(report)
