# 1. 使用官方已經包好的 Python 3.11 環境（這就是我們的虛擬電腦）
FROM python:3.11-slim

# 2. 設定這台虛擬電腦的工作目錄
WORKDIR /app

# 3. 安裝系統必要的編譯工具 (確保解密套件能順利安裝)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. 複製你的套件清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 把你的 app.py 和 HTML 全部搬進去
COPY . .

# 6. 啟動程式 (Render 會自動給 PORT，我們用 $PORT 接收)
CMD gunicorn --bind 0.0.0.0:$PORT app:application
