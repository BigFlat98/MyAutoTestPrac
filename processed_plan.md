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
  - 로그인 기능 개발 완료. (JWT 기반 인증)
- **인프라 및 배포**:
  - AWS EC2 인스턴스 생성 및 설정.
  - 도커(Docker) 도입: Front, Back, DB를 `docker-compose`로 컨테이너화.
  - Nginx 리버스 프록시 설정으로 보안 강화 및 CORS 문제 해결.

12/29
## 8. Rust 채팅 서버 구축 및 UI 개선

- **Rust 채팅 서버 (`/Chat`)**:
  - `Axum` 프레임워크와 `Tokio`를 사용하여 고성능 비동기 채팅 서버 구축.
  - `SQLx`를 사용한 PostgreSQL 연동 (기존 DB와 `chat_rooms`, `messages` 테이블 공유).
  - WebSocket 핸들러 구현: 클라이언트 연결 관리 및 실시간 메시지 브로드캐스팅.
- **프론트엔드 개선**:
  - **이미지 업로드**: 게시판 글 작성 시 인라인 이미지 붙여넣기 및 미리보기 기능 구현 (DC Inside 스타일).
  - **모바일 반응형**: 모바일 환경에서도 네비게이션 및 레이아웃이 깨지지 않도록 CSS 최적화.

1/3
## 9. 채팅 기능 고도화 (수정/삭제)

- **기능 확장**:
  - **Backend (Rust)**:
    - `PATCH /messages/:id`, `DELETE /messages/:id` API 구현.
    - WebSocket 이벤트(`update`, `delete`) 브로드캐스팅 로직 추가.
  - **Frontend**:
    - 본인 메시지에만 수정/삭제 버튼 노출.
    - 실시간 수정/삭제 반영 및 시각적 피드백(수정됨 배지 등) 구현.

1/4
## 10. 로그인 오류 수정 및 에러 처리 개선

- **문제 해결 (Bug Fix)**:
  - **증상**: EC2 배포 환경에서 로그인 시 422 Unprocessable Entity 오류 발생 및 화면에 Raw JSON 에러 노출.
  - **원인**:
    1. 백엔드 `UserLogin` 스키마에 불필요한 `nick_name` 필드가 포함되어 있어, 로그인 요청 시 유효성 검사 실패.
    2. 프론트엔드에서 API 에러 응답(`detail`)을 가공 없이 그대로 출력하여, JSON 배열 형태의 시스템 에러가 사용자에게 노출됨.
  - **해결**:
    - **Backend**: `schemas.py`의 `UserLogin` 모델에서 `nick_name` 필드 제거.
    - **Frontend**: `auth.js` 스토어에서 에러 `detail`이 배열인 경우 "입력 정보 형식이 올바르지 않습니다."라는 안내 메시지로 변환하여 표시.

## 11. 향후 로드맵 (Roadmap)

- **진행 중 (In Progress)**:
  - **이커머스 페이지 (E-commerce)** 구현.
  - 배포 자동화(CI/CD) 실습.
- **장기 목표 (Future)**:
  - **소셜 로그인 (Social Login)** 연동.
  - **스트리밍 서버 (Streaming Server)** 구축.
  - **챗봇 (Chatbot)** 기능 추가.

1/25
## 12. 동영상 페이지 기획 (Video Page Planning)

- **기획 (Planning)**:
  - fow.tv 스타일의 동영상 상세 페이지 구현 결정.
  - **DB 설계**: 동영상 댓글용 `PostReply` 재사용 vs 신규 테이블 생성 검토 결과, **`VideoReply` 신규 테이블 생성**으로 결정 (리그레션 방지 및 유지보수 용이성).
  - `implementation_plan.md` 작성 완료 (한글).
