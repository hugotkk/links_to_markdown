FROM python:latest

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /app

COPY app .

RUN pip install celery

CMD ["celery", "-A", "app.tasks", "worker", "--beat", "--loglevel=info"]