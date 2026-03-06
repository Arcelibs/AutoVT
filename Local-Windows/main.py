import os
import subprocess
import time
import threading
import queue
from openai import OpenAI
from faster_whisper import WhisperModel


# 初始化 Faster Whisper 模型
model = WhisperModel("Systran/faster-distil-whisper-large-v3", device="cuda", compute_type="int8")

OPENAI_MODEL = "gpt-5-mini"
SEGMENT_DURATION = 10    # 每段錄音秒數
TOTAL_DURATION = 6000    # 總錄製秒數
URL_REFRESH_INTERVAL = 1800  # 每 30 分鐘刷新串流 URL

# Whisper 常見日語雜訊黑名單
NOISE_PATTERNS = ["[音楽]", "[拍手]", "(音楽)", "ご視聴ありがとうございました", "字幕"]

LOG_FILE = f"autovt_{time.strftime('%Y%m%d_%H%M%S')}.txt"


def load_api_key():
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    try:
        with open("api_key.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("錯誤：找不到 API key。請設定環境變數 OPENAI_API_KEY 或建立 api_key.txt。")
        raise


client = OpenAI(api_key=load_api_key())


def translate(text):
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": f"Translate the following to Traditional Chinese. Output only the translation:\n{text}"}],
            timeout=30,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"翻譯失敗: {e}")
        return None


def get_stream_url(youtube_url):
    command = ["yt-dlp", "-g", youtube_url]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if process.returncode != 0:
        print(f"錯誤: 無法取得直播流。詳情：{process.stderr}")
        return None
    return process.stdout.strip()


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


def is_noise(text):
    stripped = text.strip()
    if not stripped:
        return True
    return any(pattern in stripped for pattern in NOISE_PATTERNS)


def transcribe_audio(file_path):
    try:
        segments, info = model.transcribe(file_path, language="ja", vad_filter=True)
        return " ".join([seg.text for seg in segments])
    except Exception as e:
        print(f"錯誤: 無法轉錄聲音。詳情：{e}")
        return None


def save_log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")


def worker(audio_queue):
    """轉錄 + 翻譯 worker，與錄音主執行緒並行執行"""
    while True:
        item = audio_queue.get()
        if item is None:  # 結束信號
            break
        filename, segment_idx = item
        try:
            text = transcribe_audio(filename)
            if text and not is_noise(text):
                translated_text = translate(text)
                if translated_text:
                    output = f"[{time.strftime('%H:%M:%S')}] {translated_text}"
                    print(output)
                    save_log(output)
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] 無法翻譯片段 {segment_idx}。")
        finally:
            if os.path.exists(filename):
                os.remove(filename)
            audio_queue.task_done()


def main(segment_duration, total_duration):
    youtube_url = input("請輸入 YouTube URL: ")
    stream_url = get_stream_url(youtube_url)
    if not stream_url:
        print("無法取得 YouTube 直播流地址。")
        return

    print(f"開始翻譯，紀錄檔：{LOG_FILE}")

    audio_queue = queue.Queue()
    worker_thread = threading.Thread(target=worker, args=(audio_queue,), daemon=True)
    worker_thread.start()

    last_url_refresh = time.time()

    for segment in range(0, total_duration, segment_duration):
        # 定期刷新串流 URL
        if time.time() - last_url_refresh >= URL_REFRESH_INTERVAL:
            print("刷新串流 URL...")
            new_url = get_stream_url(youtube_url)
            if new_url:
                stream_url = new_url
                last_url_refresh = time.time()
            else:
                print("警告：刷新失敗，繼續使用舊 URL。")

        filename = f"output_{segment}.wav"
        if record_audio(stream_url, segment_duration, filename):
            audio_queue.put((filename, segment))  # 錄音完畢，交給 worker 並行處理
        else:
            print(f"錄製段落 {segment} 失敗。")

    # 等待所有片段處理完畢
    audio_queue.join()
    audio_queue.put(None)
    worker_thread.join()


if __name__ == "__main__":
    main(SEGMENT_DURATION, TOTAL_DURATION)
