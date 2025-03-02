FROM python:3.11

WORKDIR /app

COPY ./app/requirements.txt /app/requirements.txt 

RUN pip install -r requirements.txt  # 只安裝套件，不COPY程式碼

EXPOSE 8000
