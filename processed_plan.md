# 금일(Today) 진행 내역 요약

## 1. 프로젝트 초기 설정

- **Front (`/Front`)**:
  - Vite를 사용하여 Vue.js 3 프로젝트 생성.
  - 백엔드 통신을 위한 `axios` 라이브러리 설치.
- **Back (`/Back`)**:
  - Python 가상환경(`venv`) 생성 및 활성화.
  - `FastAPI`, `Uvicorn` 등 필수 의존성 설치 (`requirements.txt` 작성).

## 2. API 및 기능 구현

- **기본 통신 확인**:
  - GET `/`: 루트 경로 접속 테스트.
  - GET `/health`: 서버 상태 확인용 엔드포인트 구현.
  - 프론트엔드(`App.vue`)에서 앱 시작 시 자동으로 위 API들을 호출하여 연결 확인하도록 구성.
- **Echo 기능 구현**:
  - POST `/echo`: 클라이언트로부터 메시지를 받아 그대로 반환하는 기능 추가.
  - 프론트엔드에 입력창(Input)과 전송 버튼(Button)을 만들어 사용자가 직접 데이터를 보내고 응답을 화면에서 확인할 수 있도록 구현.

## 3. CORS 설정

- 개발 편의를 위해 백엔드에서 `localhost:5173` (Vue 기본 포트)의 요청을 허용하도록 `CORSMiddleware` 설정 완료.

---

**다음 예정 작업**: PostgreSQL 데이터베이스 연동 및 도커(Docker) 배포 실습.

## 4. 디자인 시스템 (Design System)

- **Concept**: Modern Luxury (Clean, Sharp, Elegant).
- **Colors**:
  - Background: `White (#ffffff)`
  - Text/Border: `Black (#000000)` - Thin 1px lines.
  - Accent: `Dark Gold (#996515)` - Used for Hover, Active states, Highlights.
- **UI Rules**:
  - **Square Edges**: 모든 버튼과 입력창의 `border-radius`는 `0`.
  - **Micro-Interactions**: Hover 시 부드러운 이동(Translate), 그림자(Shadow), 색상 전환(Transition) 필수.
  - **Sizing**: Input과 Button의 높이를 정확히 맞출 것. (현재 `3.2rem`으로 통일)
