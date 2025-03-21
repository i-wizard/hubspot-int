FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=run.py
ENV FLASK_DEBUG=1

COPY ./entrypoint.sh /src/entrypoint.sh
RUN chmod +x /src/entrypoint.sh

ENTRYPOINT ["/bin/sh", "/src/entrypoint.sh"]
