import os, re, smtplib, feedparser, markdown, pytz, requests
from datetime import datetime
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

def get_real_estate_news():
    """Lọc nguồn tin tinh hoa pháp lý (Vĩ mô)"""
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
            for entry in feed.entries[:3]: # Giảm xuống 3 để tối ưu token
                desc = re.sub('<[^<]+>', '', entry.get('summary', ''))
                summary += f"Tiêu đề: {entry.title}\nTóm tắt: {desc[:200]}...\nLink: {entry.link}\n\n"
        except Exception as e:
            print(f"Lỗi đọc RSS {cat}: {e}")
            continue
    return summary

def get_admin_notices(url):
    """Cào dữ liệu vi mô từ Cổng thông tin (Sở NN&MT / UBND)"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # NOTE: Điều chỉnh class_ theo thực tế DOM của website Sở
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
                link = "https://[domain_cua_So]" + link
                
            if any(kw.lower() in title.lower() for kw in keywords):
                extracted_data += f"- {title}\n  Link: {link}\n"
                count += 1
            if count >= 5: break
            
        return extracted_data if extracted_data else "Không có thông báo mới sát với từ khóa NQ 171."
    except Exception as e:
        return f"Lỗi quét Cổng thông tin: {str(e)}"

def get_ai_report(news_data, admin_data, project_status):
    """LÕI TƯ DUY V14.1: XỬ LÝ CHÉO VĨ MÔ & VI MÔ"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Thiếu API Key."
    
    genai.configure(api_key=api_key)
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M - %d/%m/%Y")
    
    prompt = f"""
    CONTEXT: Today is {current_time}. Bạn là Senior Legal Advisor cho Vũ Quang Phát.
    
    LUẬT ĐỊNH HIỆN HÀNH (TRUTH DATA):
    - Cơ sở pháp lý: NQ 171/2024/QH15 và NĐ 75/2025/NĐ-CP (Thí điểm thỏa thuận nhận quyền SDĐ).
    - Thẩm quyền: Tại TP.HCM năm 2026, quy trình lập Danh mục khu đất thí điểm do Sở Nông nghiệp và Môi trường rà soát, trình UBND để HĐND thông qua. Sở Tài chính chủ trì định giá thặng dư.
    
    DỮ LIỆU ĐẦU VÀO:
    [TIN TỨC BÁO CHÍ]: {news_data}
    [THÔNG BÁO HÀNH CHÍNH]: {admin_data}
    [THỰC TRẠNG DỰ ÁN]: {project_status}

    YÊU CẦU BÁO CÁO (Cấu trúc IRAC):
    1. ISSUE: Soi chiếu dữ liệu đầu vào với vướng mắc của DA Saigonres và DA Hưng Thịnh.
    2. RULE & REALITY: Phân tích 'Ý đồ nhà lập pháp' vs 'Nút thắt thực tế' (đặc biệt lưu ý rủi ro đàm phán giá đất với dân theo Điều 6 NĐ 75).
    3. APPLICATION: Quy trình tích hợp hồ sơ tại Sở Nông nghiệp và Môi trường để lọt vào Danh mục dự án thí điểm.
    4. ACTION PLAN: Đề xuất hành động 1:1 cho anh Phát (Bullet points, ngắn gọn, có deadline).
    """

    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_id = next((m for m in available_models if 'flash' in m), "gemini-1.5-flash")
        
        model = genai.GenerativeModel(model_name=model_id)
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        if "429" in str(e): return "THÔNG BÁO: Hết hạn mức API. Vui lòng nâng cấp Key."
        return f"Lỗi hệ thống AI: {str(e)}"

def send_email(markdown_content):
    """UI/UX: Chuẩn Format Báo cáo Cấp cao"""
    sender = "phat.clover@gmail.com"
    msg = MIMEMultipart()
    msg["Subject"] = f"[TOP PRIORITY] LEGAL STRATEGY REPORT - #{datetime.now().strftime('%d%m')}"
    msg["From"] = f"Senior Advisor <{sender}>"
    msg["To"] = sender
    
    html_body = markdown.markdown(markdown_content, extensions=['extra', 'tables'])
    full_html = f"""
    <div style="font-family: 'Times New Roman', serif; max-width: 850px; margin: auto; border-top: 12px solid #002D62; padding: 50px; color: #1a1a1a; line-height: 1.8;">
        <h1 style="color: #002D62; text-align: center; font-size: 28px;">BÁO CÁO THAM MƯU PHÁP LÝ TUẦN</h1>
        <p style="text-align: center; border-bottom: 2px solid #eee; padding-bottom: 20px; font-style: italic;">Strictly Confidential | For: Vũ Quang Phát</p>
        <div style="font-size: 18px; text-align: justify;">{html_body}</div>
        <div style="margin-top: 60px; text-align: center; font-size: 11px; color: #888;">
            AI Strategic Advisor | V14.1 Micro-Data Enabled | 2026 Compliance Framework
        </div>
    </div>
    """
    msg.attach(MIMEText(full_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, os.environ.get('GMAIL_PASSWORD'))
            server.sendmail(sender, sender, msg.as_string())
        print("[+] Báo cáo đã gửi thành công.")
    except Exception as e: 
        print(f"[-] Email Error: {e}")

if __name__ == "__main__":
    # Thay URL dưới đây bằng link Cổng TTĐT thực tế cần theo dõi
    TARGET_URL = "https://[domain_cua_So]/thong-bao" 
    
    REAL_PROJECT_STATUS = """
    - DA Hung Thinh: Nghẽn thẩm định giá (thặng dư) tại Sở Tài chính TP.HCM.
    - DA Saigonres: Vướng chuyển đổi đất nông nghiệp theo NQ 171/2024/QH15. Chưa chốt được giá đền bù với 15% hộ dân còn lại.
    - DA Hoa Sen: Khảo sát đấu giá tại Long An, Tiền Giang.
    """
    
    print("[1] Đang quét tin vĩ mô...")
    news = get_real_estate_news()
    
    print("[2] Đang quét dữ liệu vi mô (Sở ban ngành)...")
    admin_notices = get_admin_notices(TARGET_URL)
    
    print("[3] AI Đang phân tích chiến lược...")
    report = get_ai_report(news, admin_notices, REAL_PROJECT_STATUS)
    
    print("[4] Đang gửi báo cáo...")
    send_email(report)
