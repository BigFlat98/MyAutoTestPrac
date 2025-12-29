# 진행 내역 요약

12/18
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


12/20
## 5. 데이터베이스 연동 (PostgreSQL)

- **DB 선택 및 설정**:
  - SQLite에서 PostgreSQL로 전환.
  - `python-dotenv`를 도입하여 DB 접속 정보를 `.env` 파일로 관리.
  - Windows 환경에서의 `asyncpg` 호환성 문제를 위해 `asyncio` 이벤트 루프 정책(`WindowsSelectorEventLoopPolicy`) 적용.
- **백엔드 구현**:
  - `asyncpg`를 사용한 비동기 DB 커넥션 풀(`db_pool`) 구현.
  - `database.py`로 DB 연결 로직 모듈화 (싱글톤 패턴).
  - `schemas.py` 생성하여 Pydantic 모델(DTO) 분리 (`ItemRequest`, `ItemResponse`).
  - `controller` 폴더 생성 및 `APIRouter`를 사용하여 라우팅 로직 분리 (`include_router` 사용).
  - CRUD 기능 구현: 데이터 저장(`POST /items`) 및 조회(`GET /items`).
- **프론트엔드 연동**:
  - `App.vue`에 데이터 저장 및 목록 조회 기능 추가.
  - API 응답 형식(`List` vs `Dict`) 불일치로 인한 타입 에러 디버깅 및 해결.
  - CORS 설정을 `*` (전체 허용)으로 변경하여 개발 환경 통신 문제 해결.

12/24
## 6. 금리 및 환율 대시보드 구현

- **데이터 수집 (Backend)**:
  - `InterestRateService`: ECOS(한국은행) 및 FRED(미 연준) API 연동. (미 금리는 `DFEDTARU` 목표 금리 사용)
  - `ExchangeRateService`: ECOS API 연동 (원/달러 환율).
  - 10년치 데이터를 5000건 제한으로 조회하여 2015~현재 데이터 확보.
- **차트 구현 (Frontend)**:
  - `chart.js`, `vue-chartjs` 도입.
  - 10년치 데이터를 가로 스크롤로 확인 가능하도록 구현 (최근 데이터 자동 스크롤).
  - 디자인: 한국 금리(Bright Gold), 환율(Emerald Green) 등 테마 적용.
- **구조 개선**:
  - `src/api/index.js` 생성하여 Axios 인스턴스 중앙 관리.
  - `.env` 및 `Soft Coding` 적용으로 배포 환경(Nginx) 대응 준비 완료.

12/26
## 7. 로그인 구현 및 AWS EC2 배포

- **기능 구현**:
  - 로그인 기능 개발 완료.
- **인프라 및 배포**:
  - AWS EC2 인스턴스 생성 및 설정.
  - 어플리케이션 배포 및 CORS 문제 해결.

## 8. 향후 로드맵 (Roadmap)

- **단기 목표 (Next Steps)**:
  - **게시판 페이지 (Bulletin Board)** 구현.
  - **이커머스 페이지 (E-commerce)** 구현.
  - 위 기능들의 EC2 배포 및 배포 자동화(Automation) 실습.
- **장기 목표 (Future)**:
  - **소셜 로그인 (Social Login)** 연동.
  - **스트리밍 서버 (Streaming Server)** 구축.
  - **챗봇 (Chatbot)** 기능 추가.
