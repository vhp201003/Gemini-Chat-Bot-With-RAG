import google.generativeai as genai
import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config/config.yaml")

# Load config
with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)
# Tải cấu hình từ tệp config.yaml
with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

# Thiết lập API key cho Google Gemini
genai.configure(api_key=config["gemini"]["api_key"])

# Khởi tạo model Gemini
model = genai.GenerativeModel(config["gemini"]["model"])

# System prompt hướng dẫn Gemini
SYSTEM_PROMPT = """
Bạn là một trợ lý AI chuyên nghiệp. 
Nếu có thông tin cần thiết, vui lòng cung cấp một câu trả lời rõ ràng.
Nếu không có dữ liệu phù hợp, hãy phản hồi rằng không có đủ thông tin.
"""

def generate_response(context, query):
    """Sinh phản hồi từ Gemini với format cố định"""
    if not context:
        return "Xin lỗi, tôi không có thông tin để trả lời câu hỏi này."

    # Tạo prompt với format yêu cầu
    prompt = f"{SYSTEM_PROMPT}\n\nThông tin có sẵn:\n{context}\n\nCâu hỏi: {query}\nTrả lời ngắn gọn:"

    try:
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"Lỗi khi gọi API Gemini: {e}")
        return "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn."
