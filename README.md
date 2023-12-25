# AutoVT
GPT流派的Youtube直播流切片翻譯(半即時)

## 這是什麼?
因為我日文程度N87，又很喜歡看那些小小軟軟可愛的V

苦於聽不懂市面上又沒有人做翻譯插件，只好自己搓一個直播流切片翻譯

然後我自己也不是Python專業，只好求助GPT-4幫幫忙

## 技術說明
運用Youtube DL去下載影片，運用FFmepeg去分割影片存成mp3

最後用Whisper去讀取wav轉文字印出，印出的文字再翻譯

## 操作環境
Google Colab With T4 GPU(Free)

顯卡也不是不行，但是方便多裝置連網使用

## 版本差異
### V1版本使用DeepL翻譯

翻譯速度:最快 / 翻譯語意:接近 / 翻譯語言:簡體中文

(需要用到DeepL的API，自己想辦法取得，不建議再翻譯)

### V2版本使用OpenAI GPT3.5翻譯

翻譯速度:中 / 翻譯語意:接近 / 翻譯語言:繁體中文

不建議使用，因為OpenAI API太貴了，看五分鐘要0.01美金

### V30版本使用Google Gemini Pro翻譯

翻譯速度:快 / 翻譯語意:接近 / 翻譯語言:繁體中文

改用large-V2模型

改用Faster-Whisper框架，大幅降低VRAM需求

改用Google LLM Gemini Pro API，優點就是不用錢又快


## 相關api取得方法
DeepL API: 需要海外的信用卡才能拿到免費API，免費額度500000字母/月

OpenAI GPT3.5: 註冊OpenAI帳號申請，免費額度用完需要儲值

Gemini Pro API: 免費申請，但僅限美國地區使用，美國以外需要代理

代理方法:

使用CF Worker: https://zhile.io/2023/12/24/gemini-pro-proxy.html

使用Vercel: https://simonmy.com/posts/%E4%BD%BF%E7%94%A8vercel%E5%8F%8D%E5%90%91%E4%BB%A3%E7%90%86google-palm-api.html




