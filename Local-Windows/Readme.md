## 使用環境

### 需安裝Python 3.10

### Windows執行環境，你應該要安裝Cuda11 Toolkit

### 需要Api_Key.txt

這個指的是Google MakerSuite 裡面的Gemini Pro API

如何申請要麻煩自己Google，將Key放在txt裡面後擺在跟EXE同一層即可

### 需要DeepL_API_KEY.txt

目前第一次翻譯會使用DeepL協助翻譯成簡體中文

這是因為有一些語句(工口)無法被Gemini API翻譯，會被阻擋

### 需要ffmpeg

看網路教學安裝好後加入系統環境變數

### 會下載3GB的Large-V2語音模型

模型大小與精準度掛勾 XDD

## DEV版本
同目錄下會有三個資料夾
debug:出現無法解析(可能是阻擋)時，將API回應句存下來
RawData:從Whisper聽取後轉出的第一次語意文本
RawData_NLP:從第一次語意文本經過NLP分析後的文本
(對照兩者資訊可以找出NLP是否有效?)
****

## 使用說明

記得要先執行pip install -r requirements.txt !!

僅支援Yotube完整連結，不支援短連結!
![image](https://github.com/Arcelibs/AutoVT/assets/49543451/e0732b8c-9fb3-493a-9e1b-787b9e50c084)

## 備註
當環境音BGM太大聲時可能會辨識錯誤

當說話的聲音不是標準日文口音時可能會降低辨識效果

某些Vtuber說話很像外星人或者有莫名其妙的高音不太適合用(例如三毛貓)

模型優先設計給日語為主，可嘗試用於台V或者EN台，不保證效果
