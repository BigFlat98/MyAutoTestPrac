# File: Front/Dockerfile
# --- Stage 1: Build ---
FROM node:22-alpine as build-stage
WORKDIR /app
# 패키지 매니저 파일 복사 및 설치
COPY package*.json ./
RUN npm install -g npm@11.13.0 && npm install
# 소스 코드 복사 및 빌드
COPY . .
RUN npm run build
# --- Stage 2: Serve (Nginx) ---
FROM nginxinc/nginx-unprivileged:stable-alpine as production-stage
# 빌드된 결과물(dist)을 Nginx가 서빙하는 경로로 복사
COPY --from=build-stage /app/dist /usr/share/nginx/html
# SPA 라우팅 설정을 위한 Nginx 설정 파일 복사
COPY nginx.default.conf /etc/nginx/conf.d/default.conf
# Nginx 기본 포트 노출
EXPOSE 8080
# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]