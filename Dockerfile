FROM python:latest

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /app

COPY app .

CMD ["/usr/local/bin/python", "manage.py", "runserver", "0:8000"]
