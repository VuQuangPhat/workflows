import requests
from bs4 import BeautifulSoup
import re

def get_admin_notices(url):
    """
    Module cào dữ liệu từ Cổng thông tin điện tử (Sở Nông nghiệp và Môi trường / UBND).
    Tập trung vào các keyword phản ánh nút thắt của NQ 171.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # LƯU Ý: Cần inspect phần tử web thực tế để đổi class_ cho phù hợp với website của Sở
        articles = soup.find_all(['div', 'li'], class_=re.compile('article-item|news-item|list-item'))
        
        extracted_data = ""
        # Các keyword lõi liên quan đến vướng mắc dự án thí điểm NQ 171
        keywords = ["thí điểm", "nhà ở thương mại", "thỏa thuận nhận quyền", "chuyển mục đích", "danh mục khu đất", "trả hồ sơ"]
        
        count = 0
        for article in articles:
            title_tag = article.find('a')
            if not title_tag: continue
            
            title = title_tag.text.strip()
            link = title_tag.get('href', '')
            if not link.startswith('http'): 
                link = "https://[domain_của_Sở]" + link
                
            # Lọc tin tức rác, chỉ giữ tin có keyword pháp lý trọng điểm
            if any(kw.lower() in title.lower() for kw in keywords):
                extracted_data += f"- CẬP NHẬT MỚI: {title}\n  Link đối chiếu: {link}\n\n"
                count += 1
                
            if count >= 5: break # Giới hạn lấy 5 tin sát sườn nhất
            
        return extracted_data if extracted_data else "Không phát hiện thông báo mới liên quan đến vướng mắc NQ 171."
        
    except requests.exceptions.RequestException as e:
        return f"[-] Lỗi kết nối Cổng thông tin: {str(e)}"
