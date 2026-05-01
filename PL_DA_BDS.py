def get_ai_report(news_data):
    """Phân tích dữ liệu bằng AI tập trung vào NQ 171 và pháp lý BĐS"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    prompt = f"""
Bạn là Luật sư cấp cao chuyên ngành Bất động sản phục vụ Vũ Quang Phát (10 năm kinh nghiệm, học ULAW).
Nhiệm vụ của bạn là đọc tin tức hôm nay và soạn thảo báo cáo cập nhật chuyên sâu.

Dữ liệu thô từ báo chí hôm nay: {news_data}

HÃY SOẠN: "BÁO CÁO PHÁP LÝ BẤT ĐỘNG SẢN & DỰ ÁN".
Yêu cầu: Markdown, KHÔNG EMOJI. Ngôn ngữ chính: TIẾNG VIỆT. Văn phong chuẩn mực, logic pháp lý chặt chẽ.

CẤU TRÚC BẮT BUỘC:
## 1. NHẬN ĐỊNH THỊ TRƯỜNG & HIỆU LỰC CHÍNH SÁCH TRONG 24H QUA
- Tóm tắt các sự kiện, chính sách BĐS đáng chú ý. 
- Cảnh báo hiệu lực: Chỉ rõ văn bản pháp luật nào sắp ban hành, vừa có hiệu lực (ví dụ Luật Đầu tư 143/2025/QH15), hoặc vừa hết hiệu lực/bị bãi bỏ dựa trên tin tức (nếu có).

## 2. CHUYÊN ĐỀ ĐẶC BIỆT: NGHỊ QUYẾT 171 & NĐ 75/2025 (MỤC TIÊU CÔNG VIỆC)
- Lọc mọi tin tức liên quan đến việc triển khai Nghị quyết 171 (Thí điểm thực hiện dự án nhà ở thương mại thông qua thỏa thuận về nhận quyền sử dụng đất hoặc đang có quyền sử dụng đất).
- Đánh giá tiến độ tháo gỡ điểm nghẽn thủ tục tại các địa phương (ví dụ: vướng mắc thủ tục xin văn bản chấp thuận của UBND cấp tỉnh trước hay sau khi HĐND thông qua danh mục).
- LƯU Ý: Nếu hôm nay không có tin tức mới về NQ 171, hãy tự động phân tích một rủi ro pháp lý hoặc đưa ra một lời khuyên thực chiến cho CĐT khi thực hiện thỏa thuận nhận quyền sử dụng đất theo cơ chế thí điểm này.

## 3. CƠ CHẾ PHÁP LÝ CHUNG VỀ CHẤP THUẬN CHỦ TRƯƠNG ĐẦU TƯ
- Phân tích bình luận chuyên sâu về quy trình, thủ tục dự án dựa trên khung pháp luật hiện hành mới nhất (Luật Đất đai 2024, Luật Đầu tư 2025).

## 4. PHÂN TÍCH TÌNH HUỐNG BĐS (IRAC METHOD)
- Trích xuất một tình huống thực tiễn từ tin tức (ưu tiên vướng mắc bồi thường, giao đất) và giải quyết theo cấu trúc IRAC (Issue - Rule - Application - Conclusion). Áp dụng luật hiện hành.

## 5. TỪ VỰNG TIẾNG ANH PHÁP LÝ BĐS (UK B2)
- Bảng (Từ vựng | IPA | Nghĩa tiếng Việt | Ví dụ áp dụng).

## 6. UK IDIOM OF THE DAY (LEVEL B2)
- Một thành ngữ Anh (UK) dùng trong đàm phán thương mại.
"""

    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models_to_try = sorted(available_models, key=lambda x: (0 if 'flash' in x else (1 if 'pro' in x else 2)))
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text
            except:
                continue
        return "AI Generation Failed."
    except Exception as e:
        return f"System Error: {str(e)}"
