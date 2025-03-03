import google.generativeai as genai
import yaml

# Tải cấu hình từ tệp config.yaml
with open(r"../config.yaml", "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

# Thiết lập API key cho Google Gemini
genai.configure(api_key=config["gemini"]["api_key"])

# Khởi tạo model Gemini
model = genai.GenerativeModel('gemini-2.0-flash')

# System prompt hướng dẫn Gemini
SYSTEM_PROMPT = """
Bạn là một trợ lý AI chuyên nghiệp. Trả lời theo đúng format sau:

Xin chào,  
Cảm ơn anh/chị đã có câu hỏi về chủ đề {chủ đề}.  
Câu trả lời của tôi là:  

<Trả lời ngắn gọn nội dung chính, có thể kèm LaTeX nếu cần để diễn đạt công thức toán học hoặc ký hiệu khoa học>  

Nếu cần thêm thông tin, anh/chị có thể đặt câu hỏi tiếp theo.
"""

def generate_response(context, query, topic="chủ đề chung"):
    """Sinh phản hồi từ Gemini với format cố định"""
    if not context:
        return "Xin lỗi, tôi không có thông tin để trả lời câu hỏi này."

    # Chèn chủ đề vào system prompt
    formatted_system_prompt = SYSTEM_PROMPT.replace("{chủ đề}", topic)

    # Tạo prompt với format yêu cầu
    prompt = f"{formatted_system_prompt}\n\nThông tin có sẵn:\n{context}\n\nCâu hỏi: {query}\nTrả lời theo format trên:"

    try:
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"Lỗi khi gọi API Gemini: {e}")
        return "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn."