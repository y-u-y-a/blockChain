FROM python:3.7

RUN mkdir code

WORKDIR /code

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt
# コンテナ側で解放するポート
EXPOSE 80
