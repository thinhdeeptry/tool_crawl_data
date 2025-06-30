# Sử dụng một base image Python chính thức, gọn nhẹ
FROM python:3.11-slim

# Thiết lập biến môi trường để Python chạy tốt hơn trong Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Tạo và đặt thư mục làm việc trong container là /app
WORKDIR /app

# Sao chép file requirements.txt vào trước để tận dụng cơ chế cache của Docker
# Nếu file này không đổi, Docker sẽ không cần cài lại thư viện ở những lần build sau
COPY requirements.txt .

# Chạy lệnh pip để cài đặt các thư viện từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ code của project từ máy thật vào thư mục /app trong container
COPY . .