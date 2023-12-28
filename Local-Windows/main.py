import requests
import json
import os
import subprocess
import time
import whisper
import spacy
import re
from faster_whisper import WhisperModel
from langdetect import detect


# 初始化 Faster Whisper 模型
model = WhisperModel("large-v2", device="cuda", compute_type="int8")  

#從api_key.txt取得api
def get_api_key_from_file(file_path='api_key.txt'):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print("未找到 API 密鑰文件。")
        return None

#從deepl_api_key.txt取得api
def get_deepl_api_key_from_file(file_path='deepl_api_key.txt'):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print("未找到 DeepL API 密鑰文件。")
        return None

# 呼叫DeepL API的函數(備案，當Gemini不能翻譯色色內容時)
def call_deepl_api(input_text, deepL_auth_key, target_lang='ZH'):
    deepL_url = 'https://api-free.deepl.com/v2/translate'
    headers = {
        'Authorization': f'DeepL-Auth-Key {deepL_auth_key}'
    }
    data = {
        'text': input_text,
        'target_lang': target_lang
    }
    response = requests.post(deepL_url, headers=headers, data=data)
    if response.status_code == 200:
        response_data = response.json()
        if 'translations' in response_data and response_data['translations']:
            return response_data['translations'][0]['text']
        else:
            print("DeepL 翻譯失敗：無翻譯結果。")
            return None
    else:
        print(f"DeepL API 調用發生錯誤: {response.status_code}")
        return None

# 呼叫Gemini的函數
def call_gemini_api(input_text):
    # 获取 DeepL API KEY
    deepl_auth_key = get_deepl_api_key_from_file()
    if not deepl_auth_key:
        print("无法获取 DeepL API KEY。")
        return None

    # 先使用 DeepL API 翻译为简体中文
    simplified_chinese_text = call_deepl_api(input_text, deepl_auth_key, target_lang='ZH')
    if not simplified_chinese_text:
        print("DeepL 翻译失败。")
        return None

    # 从文件中取得 Gemini API KEY
    api_key = get_api_key_from_file()
    if not api_key:
        print("Gemini API KEY 无效")
        return None

    # Gemini API URL 请求头
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={}".format(api_key)
    headers = {'Content-Type': 'application/json'}

    # 格式化输入文本，准备发送给 Gemini API
    formatted_input = f"請你翻譯成繁體中文並修正任何語句與文法問題使其流暢: \n{simplified_chinese_text}"
    data = json.dumps({"contents": [{"parts": [{"text": formatted_input}]}]})

    # 发送请求到 Gemini API
    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()

     # 检查响应并处理
    if response.status_code == 200:
        if 'blockReason' in response_data and response_data['blockReason'] == 'SAFETY':
            # 如果 Gemini API 返回 blockReason 为 SAFETY，直接使用 DeepL 翻译结果
            return simplified_chinese_text
        elif 'candidates' in response_data:
            return response_data['candidates'][0]['content']['parts'][0]['text']
        else:
            print("KeyError: 'candidates' not found in response.")
            # 可以选择直接使用 DeepL API 的翻译结果
            return simplified_chinese_text
    else:
        print(f"错误: {response.status_code}")
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
        # 使用 Faster Whisper 进行转录
        segments, info = model.transcribe(file_path, vad_filter=True)
        # 合并段落以形成完整文本
        text = " ".join([seg.text for seg in segments])

        # 保存转录文本到文件
        save_transcription(file_path, text)

        return text
    except Exception as e:
        print(f"錯誤: 無法轉錄聲音。詳情：{e}")
        return None

# 新增的保存轉錄文的函數
def save_transcription(file_path, text, is_api_response=False):
    raw_data_dir = 'RawData' if not is_api_response else 'APIResponses'
    if not os.path.exists(raw_data_dir):
        os.makedirs(raw_data_dir)
    
    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    suffix = '.txt' if not is_api_response else '_response.json'
    filename = os.path.join(raw_data_dir, f'{base_filename}{suffix}')

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)

# 新增的保存轉錄文本經過NLP出來的函數
def save_nlp_segments(file_path, segments):
    nlp_data_dir = 'RawData_NLP'
    if not os.path.exists(nlp_data_dir):
        os.makedirs(nlp_data_dir)

    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    nlp_filename = os.path.join(nlp_data_dir, f'{base_filename}_nlp_segments.txt')

    with open(nlp_filename, 'w', encoding='utf-8') as file:
        for segment in segments:
            file.write(segment + "\n\n")

# 新增語言檢測機制並加載模型
def detect_and_split_text(text, max_length=500):
    language = detect(text)  
    nlp = None
    if language == "en":
        nlp = spacy.load("en_core_web_sm")
    elif language == "ja":
        nlp = spacy.load("ja_core_news_sm")
    elif language in ["zh-cn", "zh-tw"]:
        nlp = spacy.load("zh_core_web_sm")
    else:
        # 如果无法识别语言，则根据标点符号分段
        return split_text_on_punctuation(text, max_length)
    
    return split_text_natural(nlp, text, max_length)

# 根據傳入的NLP對象來處理語句
def split_text_natural(nlp, text, max_length):
    doc = nlp(text)
    segments = []
    current_segment = ""
    for sent in doc.sents:
        if len(current_segment + sent.text) <= max_length:
            current_segment += sent.text + " "
        else:
            if current_segment:  # 非空字符串
                segments.append(current_segment.strip())
            current_segment = sent.text + " "
    if current_segment:
        segments.append(current_segment.strip())
    return segments

# 不是中英日文? 就用標點符號來分類
def split_text_on_punctuation(text, max_length):
    punctuations = ".!?\n"
    pattern = f"[{re.escape(punctuations)}]"
    segments = []
    current_segment = ""
    for word in re.split(pattern, text):
        if len(current_segment) + len(word) <= max_length:
            current_segment += word
        else:
            if current_segment:
                segments.append(current_segment.strip())
            current_segment = word
    if current_segment:
        segments.append(current_segment.strip())
    return segments

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
                # 儲存
                segments = detect_and_split_text(text, max_length=500)
                save_nlp_segments(filename, segments)
                
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
SEGMENT_DURATION = 15  # 每一段錄製的長度，單位是秒
TOTAL_DURATION = 6000   # 總錄製時間，單位是秒

if __name__ == "__main__":
    main(SEGMENT_DURATION, TOTAL_DURATION)
