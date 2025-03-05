FROM python:3.10

# Đặt thư mục làm việc giống Local
WORKDIR /app

# Copy toàn bộ project vào container
COPY . /app

# Cài đặt thư viện
RUN pip install --no-cache-dir -r requirements.txt

# Thiết lập biến môi trường để nhận diện môi trường Docker
ENV DOCKERIZED=true

# Chạy lệnh mặc định
CMD ["bash"]
