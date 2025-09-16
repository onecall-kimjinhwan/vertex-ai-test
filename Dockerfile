# Python 3.12 slim 이미지 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 도구 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일들 복사
COPY train.py .
COPY gcp_utils.py .
COPY gcp_auth.json .

# data 디렉토리 생성 (GCS에서 다운로드한 파일 저장용)
RUN mkdir -p data

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1

# 실행 명령어
CMD ["python", "train.py"]