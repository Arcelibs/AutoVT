# AutoVT
GPT流派的Youtube直播流切片翻譯(半即時)

## 這是什麼?
因為我日文程度N87，又很喜歡看那些小小軟軟可愛的V

苦於聽不懂市面上又沒有人做翻譯插件，只好自己搓一個直播流切片翻譯

然後我自己也不是Python專業，只好求助GPT-4幫幫忙

## 技術說明
運用Youtube DL去下載影片

運用FFmepeg去分割影片存成mp3

最後用Whisper去讀取mp3轉文字印出

## 操作環境
因為會用上Whisper，眾所皆知OpenAI Whisper模型是開源的

但是開源就需要用上GPU運算，所以建議在Colab上面跑

免費的T4 GPU跑中等模型是剛剛好，大型模型可能會顯存爆炸

## 設置說明
DeepL的KEY需要去搞一個，DeepL的翻譯品質很好





