# File: Back/Dockerfile
# 1. Python 3.9 슬림 이미지 사용
FROM python:3.9-slim
# 2. 작업 디렉토리 설정
WORKDIR /app
# 3. 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 4. 소스 코드 복사
COPY . .
# 5. 사용자 추가 및 권한 설정
RUN useradd -m appuser \
    && mkdir -p /app/uploads /app/profile_uploads \
    && chown -R appuser:appuser /app
USER appuser
# 6. 포트 노출 (FastAPI 기본 포트)
EXPOSE 8000
# 6. 실행 명령어 (Uvicorn)
# --host 0.0.0.0 옵션은 외부(호스트/컨테이너 간) 접근을 허용하기 위해 필수입니다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]