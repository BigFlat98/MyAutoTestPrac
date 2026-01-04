# 🧪 QA 자동화 플레이그라운드 (QA Automation Playground)

<div align="center">

![Vue.js](https://img.shields.io/badge/vue.js-%2335495e.svg?style=for-the-badge&logo=vuedotjs&logoColor=%234FC08D)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)

**풀스택 개발 & QA 자동화 실습 워크스페이스**  
*기초 REST API부터 Rust 스트리밍 & AI 연동까지*

[주요 기능](#-주요-기능) • [기술 스택](#-기술-스택) • [시작하기](#-시작하기) • [로드맵](#-로드맵)

</div>

---

## 📝 소개

이 프로젝트는 **QA 자동화**와 **풀스택 개발**을 마스터하기 위한 샌드박스입니다.  
탄탄한 `Vue.js` + `FastAPI` 기반에서 시작하여, 향후 **Rust** 스트리밍 서버, **Spring Boot** 아키텍처, 그리고 **LangChain** AI 파이프라인을 포함한 복합적인 시스템 테스트 환경으로 진화할 예정입니다.

> "모든 코드는 테스트를 위해 존재한다."

## ✨ 주요 기능

- **Modern UI/UX**: "Modern Luxury" 디자인 시스템 (White/Black/Dark Gold).
- **Interactive Echo**: 실시간 양방향 데이터 통신 테스트 기능.
- **Health Check**: 자동화된 시스템 상태 모니터링.
- **REST API**: 확장 가능한 견고한 API 구조.

## 🛠 기술 스택

### 현재 (Current)
- **Frontend**: Vue 3, Vite, Axios
- **Backend**: Python, FastAPI, Uvicorn
- **Design**: 커스텀 CSS (Modern Luxury 테마)

### 향후 확장 (Future)
- **Backend Extensions**: Rust (Axum/Actix), Spring Boot
- **AI/ML**: LangChain, LLM 연동
- **Infrastructure**: Docker, PostgreSQL, CI/CD 파이프라인

## 🚀 시작하기

### 필수 요구사항
- Node.js & npm
- Python 3.8 이상

### 설치 및 실행

#### 1. 백엔드 (FastAPI)
```bash
cd Back
python -m venv venv
# 가상환경 활성화 (Windows: venv\Scripts\activate, Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload
```

#### 2. 프론트엔드 (Vue.js)
```bash
cd Front
npm install
npm run dev
```

브라우저에서 `http://localhost:5173` 으로 접속하여 확인하세요! ✨

### 🐳 Docker로 실행 (권장)

필요한 환경(Node.js, Python, DB)을 설치할 필요 없이 한 번에 실행합니다.

```bash
docker-compose up --build
```
- **Frontend**: http://localhost
- **Backend**: http://localhost:8000
- **Database**: Port 5432 (User/PW: `postgres`/`1971601745` from .env.docker)



## ☁️ EC2 배포 초기 설정 가이드 (Swap, Docker, Git)

EC2 프리 티어(t2.micro, t3.micro)는 RAM이 1GB로 제한적이어서, **스왑(Swap) 메모리 설정**이 필수적입니다.

### 0. 시스템 업데이트 (최초 접속 시 권장)
```bash
# Ubuntu
sudo apt update && sudo apt upgrade -y

# Amazon Linux 2023
sudo dnf update -y
```

### 1. 스왑(Swap) 메모리 설정 (RAM 부족 해결)
```bash
# 1. 2GB 스왑 파일 생성
sudo dd if=/dev/zero of=/swapfile bs=128M count=16
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 2. 재부팅 후 유지 설정
echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab
```

### 2. Git 설치
```bash
# Ubuntu
sudo apt install git -y

# Amazon Linux 2023
sudo dnf install git -y
```

### 3. Docker & Compose 설치 (Ubuntu 기준)
```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker

# Docker Compose (최신 버전은 플러그인으로 포함됨)
docker compose version
```

## 🗺 로드맵

- [x] **Phase 1: Foundation** (초기 설정, Echo 기능, 기본 UI)
- [x] **Phase 2: Data Core** (PostgreSQL, CRUD, 일정/쇼핑몰 기능)
- [ ] **Phase 3: QA & Auto** (테스트 케이스 설계, Selenium/Playwright 자동화)
- [ ] **Phase 4: High Perf** (Rust 스트리밍 서버, 실시간 채팅)
- [ ] **Phase 5: Intelligence** (LangChain AI 챗봇 도입)

---
<div align="center">
  <sub>품질 보증(QA)을 향한 열정으로 제작됨</sub>
</div>
