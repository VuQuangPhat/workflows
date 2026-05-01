def get_ai_report(news_data):
    """Trợ lý AI chuyên sâu: Bóc tách chi tiết quy trình NQ 171 và Lộ trình thực chiến"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key: return "Lỗi: Thiếu GEMINI_API_KEY."
    
    genai.configure(api_key=api_key)
    
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz_hcm).strftime("%H:%M:%S - Ngày %d/%m/%Y")
    
    # Prompt tập trung trọng tâm vào NQ 171
    prompt = f"""
Bạn là Trợ lý Cố vấn Pháp lý BĐS cấp cao. Nhiệm vụ trọng tâm: Phân tích chi tiết quy trình thí điểm theo **NGHỊ QUYẾT 171**.

THỜI GIAN LẬP BÁO CÁO: {current_time}

BỘ QUY TẮC NỘI DUNG (TUÂN THỦ TUYỆT ĐỐI):

1. TRỌNG TÂM NQ 171 (THỎA THUẬN GOM ĐẤT):
   - Phân tích chi tiết điều kiện để dự án được áp dụng NQ 171 (Loại đất, quy hoạch, sự phù hợp với chương trình phát triển nhà ở).
   - Làm rõ quy trình "Thỏa thuận nhận quyền sử dụng đất": Cách thức xác lập văn bản thỏa thuận, thời điểm đặt cọc (Deposit) và rủi ro khi người dân thay đổi ý định.

2. LỘ TRÌNH 11 BƯỚC MỞ BÁN THEO NQ 171:
   Yêu cầu mô tả chi tiết các bước chuyển tiếp từ "Thỏa thuận" sang "Giao đất/Cho thuê đất", bao gồm:
   - Bước 1-3: Chấp thuận chủ trương đầu tư & công nhận chủ đầu tư (Lưu ý thẩm quyền của TP.HCM).
   - Bước 4-7: Quy hoạch 1/500, Chuyển mục đích sử dụng đất, và thẩm định giá đất (Valuation).
   - Bước 8-11: Nghĩa vụ tài chính, Giấy phép xây dựng (Permit), nghiệm mưu và Thông báo đủ điều kiện bán hàng.

3. ĐIỂM NGHẼN HẬU SÁP NHẬP (NQ 202):
   - Phân tích sâu nút thắt tại **Sở Tài chính** trong việc thẩm định giá đất cụ thể.
   - Vai trò của **Sở Nông nghiệp và Môi trường** trong việc rà soát nguồn gốc đất nông nghiệp/đất phi nông nghiệp không phải đất ở để khớp với NQ 171.

4. YÊU CẦU TRÌNH BÀY:
   - Dùng Bảng biểu để liệt kê các mốc thời gian dự kiến và hồ sơ tương ứng của NQ 171.
   - Phân tích IRAC cho rủi ro: "Dự án bị đình trệ do không thỏa thuận được 100% diện tích đất".
   - Ngôn ngữ: Dùng 5 từ vựng B1 (ví dụ: Procedure, Contract, Compliance...) và 1 UK Idiom phù hợp với bối cảnh kinh doanh.

5. ĐỊA GIỚI: Tuyệt đối tuân thủ: Bình Dương, BR-VT đã sáp nhập vào TP.HCM. Không dùng "tỉnh", không dùng "Quận".

Dữ liệu thô từ báo chí: {news_data}
"""

    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models_to_try = sorted(available_models, key=lambda x: (0 if 'flash' in x else (1 if 'pro' in x else 2)))
        
        raw_report = "AI Generation Failed."
        for model_name in models_to_try:
            try:
                if "1.0" in model_name: continue 
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                raw_report = response.text
                break
            except Exception as e:
                continue
                
        # --- BỘ LỌC CƯỠNG CHẾ PYTHON (Giữ nguyên các quy tắc thay đổi thuật ngữ của bạn) ---
        replacements = {
            "Sở Tài nguyên và Môi trường": "Sở Nông nghiệp và Môi trường",
            "Sở TN&MT": "Sở Nông nghiệp và Môi trường",
            "Sở Kế hoạch và Đầu tư": "Sở Tài chính",
            "Sở KH&ĐT": "Sở Tài chính",
            "UBND quận": "UBND TP.HCM/Thành phố trực thuộc",
            "tỉnh Bình Dương": "TP.HCM",
            "tỉnh Bà Rịa": "TP.HCM",
            "tỉnh BR-VT": "TP.HCM"
        }
        
        cleaned_report = raw_report
        for old_term, new_term in replacements.items():
            pattern = re.compile(re.escape(old_term), re.IGNORECASE)
            cleaned_report = pattern.sub(new_term, cleaned_report)
            
        return cleaned_report
        
    except Exception as e:
        return f"System Error: {str(e)}"
