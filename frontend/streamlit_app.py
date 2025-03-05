import requests
import streamlit as st

# URL của API FastAPI
API_URL = "http://localhost:8000/query"

def fetch_data(question):
    """
    Gửi câu hỏi đến API FastAPI và nhận câu trả lời
    """
    response = requests.post(API_URL, json={"query": question})
    if response.status_code == 200:
        return response.json().get("response", "Không nhận được phản hồi từ API.")
    return "Lỗi khi kết nối đến API."

def main():
    st.set_page_config(page_title="Chatbot AI")
    st.title("🤖 Chatbot AI - Hỗ trợ thông tin")
    st.subheader("Nhập câu hỏi của bạn vào ô bên dưới")
    
    # Khởi tạo session state nếu chưa có
    if 'text' not in st.session_state:
        st.session_state['text'] = ""
    
    question = st.text_area("Nhập câu hỏi:", key='text', height=100)
    
    if st.button("Gửi câu hỏi"):
        if question.strip():
            response = fetch_data(question)
            st.subheader("📢 Câu trả lời:")
            st.write(response)
        else:
            st.warning("Vui lòng nhập câu hỏi trước khi gửi.")

if __name__ == "__main__":
    main()
