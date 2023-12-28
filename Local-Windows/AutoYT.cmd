@echo off

pip install -U pip setuptools wheel
pip install -r requirements.txt
pip install -U 'spacy[cuda110]'
python -m spacy download zh_core_web_sm
python -m spacy download en_core_web_sm
python -m spacy download ja_core_news_sm


python main.py
