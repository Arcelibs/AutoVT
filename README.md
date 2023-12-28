# AutoVT
GPT流派的Youtube直播流切片翻譯(半即時)

## 這是什麼?
因為我日文程度N87又很喜歡看那些小小軟軟可愛的V

苦於聽不懂市面上又沒有人做翻譯插件，只好自己搓一個直播流切片翻譯

然後我自己也不是Python專業，只好求助GPT-4幫幫忙

## 技術說明
運用Youtube DL去下載影片，運用FFmepeg去分割影片存成mp3

最後用Whisper去讀取wav轉文字印出，印出的文字再翻譯

## Colab版本(Cuda)，不建議使用(太舊了)
運用於Google Colab使用，其他ipynb環境無測試

## Local-Windows版本(Cuda/CPU)
運用於Windows環境使用

## Docker版本(Cuda)，沒測試過
> docker pull arcelibs/autovt

## 版本更新說明

AutoVT v1.0.1  (穩定版): 使用基礎Gemini Pro API 進行翻譯

AutoVT v1.0.2  (測試版): 先使用NLP做語意分析，再用DeepL API進行翻譯，最後使用Gemini Pro API 進行翻譯



## 備註
提交issue我看不懂的機率高達99.8%



