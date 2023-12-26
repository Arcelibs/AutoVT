# 使用pythpm 3.10鏡像檔
FROM python:3.10

# 設定工作目錄
WORKDIR /usr/src/app

# 複製到容器
COPY . .

# 安裝 requirements.txt 
RUN pip install --no-cache-dir -r requirements.txt

# 啟動容器時執行py
CMD ["python", "./main.py"]
