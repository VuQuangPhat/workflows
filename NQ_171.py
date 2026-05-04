import os, re, smtplib, feedparser, markdown, pytz, requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from google import genai

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
            print(f"[-] Lỗi đọc RSS {cat}: {e}")
            continue
    return summary

def get_admin_notices(url):
    """Trích xuất thông báo, văn bản vi mô từ Sở ban ngành"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
            
        return extracted_data if extracted_data else "Không có thông báo mới sát với từ khóa NQ 171."
    except Exception as e:
        return f"[-] Lỗi quét Cổng thông tin: {str(e)}"

def get_ai_report(news_data, admin_data, project_status):
    """LÕI TƯ DUY: CỐ VẤN PHÁP LÝ CAO CẤP"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu API Key."
    
    client = genai.Client(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    prompt = f"""
    CONTEXT: Today is {current_time}. Bạn là một Cố vấn Pháp lý cao cấp với tư duy phân tích sắc bén, hỗ trợ trực tiếp cho Vũ Quang Phát.

    LUẬT ĐỊNH HIỆN HÀNH (TRUTH DATA):
    - Cơ sở pháp lý: NQ 171/2024/QH15 và NĐ 75/2025/NĐ-CP (Thí điểm thỏa thuận nhận quyền SDĐ).
    - Thẩm quyền: Tại TP.HCM năm 2026, quy trình lập Danh mục khu đất thí điểm do Sở Nông nghiệp và Môi trường rà soát, trình UBND để HĐND thông qua. Sở Tài chính chủ trì định giá thặng dư.

    DỮ LIỆU ĐẦU VÀO:
    [TIN TỨC BÁO CHÍ]: {news_data}
    [THÔNG BÁO HÀNH CHÍNH]: {admin_data}
    [THỰC TRẠNG DỰ ÁN]: {project_status}

    QUY TẮC PHẢN HỒI (BẮT BUỘC TUÂN THỦ):
    - Ngắn gọn, tinh gọn, đi thẳng vấn đề bằng Bullet points.
    - CẤM ảo giác (Hallucination): Quy định nào chưa rõ phải ghi chú rõ ràng.
    - Từ ngữ: Tiếng Việt chuyên ngành pháp lý chuẩn xác, không sáo rỗng.

    CẤU TRÚC BÁO CÁO MẶC ĐỊNH (Phải sử dụng chính xác các Heading này):
    ### Căn cứ pháp lý
    (Liệt kê văn bản hiện hành, số hiệu, ngày ban hành).
    
    ### Nội dung phân tích chuyên sâu
    (Giải thích bản chất pháp lý, ý đồ nhà lập pháp và hệ quả thực tế. Soi chiếu trực tiếp với vướng mắc của DA Saigonres và DA Hưng Thịnh từ Dữ liệu đầu vào).
    
    ### Lưu ý thực thi / Rủi ro
    (Đánh giá các rủi ro, điểm mờ pháp lý - đặc biệt tập trung vào rủi ro đàm phán giá đất với dân theo Điều 6 NĐ 75).
    
    ### Gợi ý bước tiếp theo
    (Giải pháp 1:1, thực tế, kèm deadline).
    """

    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
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
            Automated Legal Intelligence | Compliance Framework 2026
        </div>
    </div>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, os.environ.get('GMAIL_PASSWORD'))
            server.sendmail(sender, sender, msg.as_string())
        print("[+] Báo cáo pháp lý đã được mã hóa và gửi thành công.")
    except Exception as e: 
        print(f"[-] Email Error: {e}")

if __name__ == "__main__":
    TARGET_URL = "https://donvi.tphcm.gov.vn/thong-bao" 
    
    REAL_PROJECT_STATUS = """
    - DA Hung Thinh: Nghẽn thẩm định giá (thặng dư) tại Sở Tài chính TP.HCM.
    - DA Saigonres: Vướng chuyển đổi đất nông nghiệp theo NQ 171/2024/QH15. Chưa chốt được giá đền bù với 15% hộ dân còn lại.
    - DA Hoa Sen: Khảo sát đấu giá tại Long An, Tiền Giang.
    """
    
    print("[INFO] Initiating Data Scraping Sequence...")
    news = get_real_estate_news()
    admin_notices = get_admin_notices(TARGET_URL)
    
    print("[INFO] AI Legal Advisor Analyzing...")
    report = get_ai_report(news, admin_notices, REAL_PROJECT_STATUS)
    
    print("[INFO] Transmitting Report...")
    send_email(report)
