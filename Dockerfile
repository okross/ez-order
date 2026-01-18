FROM python:3.11-slim

WORKDIR /app

# 安裝基礎依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# --- 強力安裝指令開始 ---
# 1. 升級 pip
# 2. 強制使用 IPv4 避免連線錯誤
# 3. 手動指定信任的主機地址
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir \
    --trusted-host pypi.python.org \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt
# --- 強力安裝指令結束 ---

COPY . .

CMD gunicorn --bind 0.0.0.0:$PORT app:application
