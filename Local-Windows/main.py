import requests
import json
import os
import subprocess
import time
import whisper
from faster_whisper import WhisperModel


# 初始化 Faster Whisper 模型
model = WhisperModel("large-v2", device="cuda", compute_type="int8")  # 使用适合您硬件的模型大小和设备

def get_api_key_from_file(file_path='api_key.txt'):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print("未找到 API 密鑰文件。")
        return None

def call_gemini_api(input_text):
    # 從文件中獲取 API 密鑰
    api_key = get_api_key_from_file()
    if not api_key:
        print("無效的 API 密鑰。")
        return None
    
    url = f"https://palm-proxy.arcelibs.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    formatted_input = f"請你必須將下列語句翻譯成流暢的繁體中文:\n{input_text}"
    data = json.dumps({"contents":[{"parts":[{"text": formatted_input}]}]})

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        response_data = response.json()
        #print("Response Data:", response_data)  # 调试：打印响应数据
        try:
            return response_data['candidates'][0]['content']['parts'][0]['text']
        except KeyError:
            print("KeyError: 'candidates' not found in response.")
            return None
    else:
        print(f"錯誤: {response.status_code}")
        return None


# 使用 yt-dlp 獲取 YouTube 直播媒體位置
def get_stream_url(youtube_url):
    command = ["yt-dlp", "-g", youtube_url]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if process.returncode != 0:
        print(f"錯誤: 無法取得直播流。詳情：{process.stderr}")
        return None
    return process.stdout.strip()

# 錄製聲音的函數
def record_audio(stream_url, duration, output_filename):
    try:
        command = [
            "ffmpeg", "-i", stream_url, "-t", str(duration),
            "-ac", "1", "-ar", "16000", "-y", output_filename
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        print(f"錯誤: 無法錄製聲音。詳情：{e.stderr.decode()}")
        return False
    return True

# 轉寫聲音函數
def transcribe_audio(file_path, language="japanese"):
    try:
        # 使用 Faster Whisper 進行轉錄
        segments, info = model.transcribe(file_path)
        # 合併段落
        text = " ".join([seg.text for seg in segments])
        return text
    except Exception as e:
        print(f"錯誤: 無法轉錄聲音。詳情：{e}")
        return None



# 主流程
def main(segment_duration, total_duration):
    youtube_url = input("請輸入 YouTube URL: ")  # 讓用戶輸入 YouTube URL
    stream_url = get_stream_url(youtube_url)
    if not stream_url:
        print("無法取得 YouTube 直播流地址。")
        return

    for segment in range(0, total_duration, segment_duration):
        filename = f"output{segment}.wav"
        if record_audio(stream_url, segment_duration, filename):
            text = transcribe_audio(filename)
            if text:
                translated_text = call_gemini_api(text)
                if translated_text:
                    #print(f"Segment {segment}: {translated_text}")
                    print(f"{translated_text}")
                else:
                    print(f"無法翻譯 {segment}。")
            else:
                print(f"無法轉錄片段 {segment}。")
            os.remove(filename)  # 清理：聲音檔案
        else:
            print(f"錄製段落 {segment} 失敗。")
        time.sleep(segment_duration)

# 配置參數
SEGMENT_DURATION = 10  # 每一段錄製的長度，單位是秒
TOTAL_DURATION = 6000   # 總錄製時間，單位是秒

if __name__ == "__main__":
    main(SEGMENT_DURATION, TOTAL_DURATION)
