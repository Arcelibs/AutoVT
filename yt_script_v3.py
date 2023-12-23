import os
import subprocess
import time
import whisper
import deepl

# 您的DeepL API密鑰
deepl_api_key = "73a3c938-6d7a-a458-2c28-a5134161e1d4:fx"

# 初始化DeepL翻譯客戶端
translator = deepl.Translator(deepl_api_key)

# 使用 yt-dlp 獲取 YouTube 媒體流地址
def get_stream_url(youtube_url):
    command = ["yt-dlp", "-g", youtube_url]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if process.returncode != 0:
        return None, f"錯誤: 無法獲取流地址。詳情：{process.stderr}"
    return process.stdout.strip(), None

# 錄製音頻的函數
def record_audio(stream_url, duration, output_filename):
    try:
        command = [
            "ffmpeg", "-i", stream_url, "-t", str(duration),
            "-ac", "1", "-ar", "16000", "-y", output_filename
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        return False, f"錯誤: 無法錄製音頻。詳情：{e.stderr.decode()}"
    return True, None

# 載入 Whisper 模型
model = whisper.load_model("large-v3")

# 轉寫音頻的函數
def transcribe_audio(file_path, language="japanese"):
    try:
        result = model.transcribe(file_path, language=language)
        return result["text"], None
    except RuntimeError as e:
        return None, f"錯誤: 無法轉寫音頻。詳情：{e}"

# 翻譯文本的函數
def translate_text(text, target_language="ZH"):
    try:
        result = translator.translate_text(text, target_lang=target_language)
        return result.text, None
    except Exception as e:
        return None, f"翻譯時出錯: {e}"

# 主流程
def main(youtube_url, segment_duration, total_duration):
    output = []
    stream_url, error = get_stream_url(youtube_url)
    if error:
        return [error]

    for segment in range(0, total_duration, segment_duration):
        filename = f"output{segment}.wav"
        success, error = record_audio(stream_url, segment_duration, filename)
        if success:
            text, error = transcribe_audio(filename)
            if text:
                translated_text, error = translate_text(text)
                if translated_text:
                    output.append(f"Segment {segment}: {translated_text}")
                else:
                    output.append(error)
            else:
                output.append(error)
            os.remove(filename)  # 清理：刪除音頻文件
        else:
            output.append(error)
        time.sleep(segment_duration)
    
    return output

# 配置參數
YOUTUBE_URL = "https://www.youtube.com/watch?v=x5c_N6f5NEI" # YouTube 直播頁面 URL
SEGMENT_DURATION = 5  # 每個音頻片段的長度，單位：秒
TOTAL_DURATION = 6000   # 總錄製時間，單位：秒

# 假如直接執行此腳本，則執行主流程
if __name__ == "__main__":
    results = main(YOUTUBE_URL, SEGMENT_DURATION, TOTAL_DURATION)
    for res in results:
        print(res)
