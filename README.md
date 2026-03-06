# AutoVT

YouTube 日語直播即時翻譯工具（日語 → 繁體中文）

## 這是什麼？

因為日文程度 N87 又很喜歡看那些小小軟軟可愛的 V，苦於聽不懂、市面上又沒有翻譯插件，只好自己搓一個直播流切片翻譯。

## 運作原理

```
yt-dlp 取得串流 URL → FFmpeg 錄音（每 10 秒）→ Faster-Whisper 語音轉文字 → Ollama 翻譯 → 終端顯示
```

## 環境需求

- Windows 10/11
- NVIDIA GPU（建議 8GB VRAM）
- Python 3.10+
- [FFmpeg](https://ffmpeg.org/)（需加入 PATH）
- [Ollama](https://ollama.ai/)

## 使用模型

| 元件 | 模型 | VRAM 用量 |
|------|------|-----------|
| 語音轉文字 | distil-whisper-large-v3 | ~4-5 GB |
| 翻譯 | TranslateGemma 4B（via Ollama） | ~2.6 GB |

## 安裝步驟

**1. 安裝 Python 套件**

```bash
pip install -r requirements.txt
```

**2. 安裝 Ollama 並下載翻譯模型**

```bash
ollama pull translategemma
```

**3. 啟動 Ollama**

```bash
ollama serve
```

## 使用方式

```bash
python main.py
```

或直接執行 `AutoYT.cmd`，輸入 YouTube 直播網址即可開始翻譯。

不需要任何 API 金鑰。

## 備註

提交 issue 我看不懂的機率高達 99.8%
