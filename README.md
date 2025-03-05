# Gemini-Chat-Bot-With-RAG

## 📌 Giới thiệu
Đây là một chatbot sử dụng **FastAPI**, **Qdrant** làm cơ sở dữ liệu vector và **Google Gemini** để sinh phản hồi dựa trên ngữ cảnh tìm kiếm được. Hệ thống bao gồm 3 thành phần chính:

- **Data Loader** (`data_ingestion/data_loader.py`): Xử lý dữ liệu đầu vào, nhúng embedding và lưu vào Qdrant.
- **Chatbot API** (`retrieval_system/chatbot_api.py`): API FastAPI xử lý truy vấn từ người dùng.
- **Pipeline** (`retrieval_system/pipeline.py`): Hệ thống pipeline giúp chatbot trả lời câu hỏi.

## 📂 Cấu trúc thư mục

### 📌 **Hỗ trợ định dạng dữ liệu**
Người dùng có thể thêm dữ liệu đầu vào dưới dạng **JSON, DOCX hoặc PDF** bằng cách đặt các tệp vào thư mục `/data`.

Dữ liệu sẽ tự động được xử lý và lưu vào Qdrant khi chạy `data_loader.py`.

---

## 📂 Cấu trúc thư mục
```
Gemini-Chat-Bot-With-RAG/
│── config/
│   └── config.yaml         # Cấu hình hệ thống
│── data/
│   └── data.json           # Dữ liệu đầu vào
│── data_ingestion/
│   ├── data_loader.py      # Xử lý dữ liệu và lưu vào Qdrant
│── retrieval_system/
│   ├── chatbot_api.py      # API xử lý truy vấn
│   ├── retrieval.py        # Xử lý tìm kiếm
│   ├── generator.py        # Sinh câu trả lời
│   ├── pipeline.py         # Pipeline chatbot
│── docker-compose.yaml     # Cấu hình Docker
│── Dockerfile              # Dockerfile để chạy hệ thống
│── requirements.txt        # Thư viện cần cài đặt
```

## 🛠 Cài đặt & Chạy hệ thống
### 1️⃣ **Chạy trên Local**
```sh
# Cài đặt thư viện cần thiết
pip install -r requirements.txt

# Chạy Data Loader
python data_ingestion/data_loader.py

# Chạy Chatbot API
uvicorn retrieval_system.chatbot_api:app --host 0.0.0.0 --port 8000 --reload
```

### 2️⃣ **Chạy bằng Docker**
```sh
# Build và chạy container
sudo docker-compose up --build
```

## 🔥 Sử dụng Chatbot API
### 📌 **Gửi câu hỏi đến API**
```sh
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Làm thế nào để cải thiện SEO?"}'
```
📌 **Phản hồi API:**
```json
{
    "query": "Làm thế nào để cải thiện SEO?",
    "response": "Để cải thiện SEO, bạn có thể tối ưu từ khóa, xây dựng liên kết, và tạo nội dung chất lượng."
}
```
