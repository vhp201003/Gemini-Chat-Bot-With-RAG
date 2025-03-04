# Sử dụng Python 3.10
FROM python:3.10

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép tất cả các file vào container
COPY . .

# Tạo virtual environment và cài đặt thư viện
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Thiết lập biến môi trường để sử dụng venv
ENV PATH="/opt/venv/bin:$PATH"

# Mặc định chạy API FastAPI
CMD ["uvicorn", "retrieval_system.chatbot_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
