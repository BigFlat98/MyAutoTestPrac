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

## 🗺 로드맵

- [x] **Phase 1: Foundation** (초기 설정, Echo 기능, 기본 UI)
- [ ] **Phase 2: Data Core** (PostgreSQL, CRUD, 일정/쇼핑몰 기능)
- [ ] **Phase 3: QA & Auto** (테스트 케이스 설계, Selenium/Playwright 자동화)
- [ ] **Phase 4: High Perf** (Rust 스트리밍 서버, 실시간 채팅)
- [ ] **Phase 5: Intelligence** (LangChain AI 챗봇 도입)

---
<div align="center">
  <sub>품질 보증(QA)을 향한 열정으로 제작됨</sub>
</div>
