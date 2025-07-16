FROM python:3.12

WORKDIR /app

COPY requirements.txt ./

# 빌드 도구 설치 (Debian/Ubuntu 계열 기준)
RUN apt-get update && \
    apt-get install -y --no-install-recommends cmake build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir numpy
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY . .
COPY .env ./


EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]