# 프로젝트 설계서

> 마지막 업데이트: 2026-03-23 (HTTPS 전환 완료)

---

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [전체 아키텍처](#2-전체-아키텍처)
3. [기술 스택](#3-기술-스택)
4. [환경 변수 (API 키)](#4-환경-변수-api-키)
5. [백엔드 (FastAPI)](#5-백엔드-fastapi)
6. [채팅 서버 (Rust / Axum)](#6-채팅-서버-rust--axum)
7. [KOSPI 실시간 서버 (Kstock / Node.js)](#7-kospi-실시간-서버-kstock--nodejs)
8. [프론트엔드 (Vue 3)](#8-프론트엔드-vue-3)
9. [페이지별 상세 설명](#9-페이지별-상세-설명)
10. [외부 API 연동 목록](#10-외부-api-연동-목록)
11. [데이터베이스 테이블 목록](#11-데이터베이스-테이블-목록)
12. [스케줄러 (자동 수집 주기)](#12-스케줄러-자동-수집-주기)
13. [추후 작업 예정](#13-추후-작업-예정)

---

## 1. 프로젝트 개요

개인 종합 대시보드 웹 애플리케이션. 금융 시장 데이터 모니터링, 게시판, 실시간 채팅, 영상 관리, 할 일 관리 기능을 통합 제공.

| 항목 | 내용 |
|------|------|
| 서비스 형태 | 개인용 풀스택 웹 애플리케이션 |
| 인증 방식 | 세션 기반 (서버 측 세션, max_age=7200초) |
| 데이터베이스 | PostgreSQL (asyncpg 비동기 드라이버) |
| 배포 환경 | 개인 서버 (iptime DDNS) + Cloudflare CDN + Caddy 리버스 프록시 |

---

## 2. 전체 아키텍처

```
[브라우저 (Vue 3)]
        │
        ▼ (HTTPS :443)
  [Cloudflare CDN]
  hadaboni.work
  (오렌지 클라우드 프록시)
        │
        ▼ (HTTPS :443)
  [Caddy hadaboni.work]
  Origin Certificate (TLS)
    │       │           │
    ▼       ▼           ▼
[Front]  [/chat/*]  [/kstock/*]
 nginx   Rust/Axum   Node.js
         WebSocket   Hono+ws
              │           │
              │      [KIS WebSocket]
              │      실시간 체결가
              ▼
         [FastAPI /api/*]
              │
              ▼
        [PostgreSQL DB]
```

- `/kstock/*` → Kstock 서버 (Node.js / Hono) — KOSPI 실시간 WebSocket 브로드캐스트
- `/chat/*` → Rust Axum 채팅 서버 (HTTP + WebSocket)
- `/api/*` → FastAPI (Python) 백엔드
- 프론트엔드는 Vite 빌드 후 nginx가 정적 파일로 서빙, Caddy가 리버스 프록시

---

## 3. 기술 스택

### 백엔드 (Back/)

| 분류 | 항목 | 버전/설명 |
|------|------|-----------|
| 프레임워크 | FastAPI | 비동기 REST API |
| ASGI 서버 | Uvicorn | FastAPI 구동 |
| DB 드라이버 | asyncpg | PostgreSQL 비동기 연결 |
| 스케줄러 | APScheduler | 시장 데이터 자동 수집 |
| 금융 데이터 | yfinance | 국제 금 선물, 환율 보조 |
| 금융 데이터 | ccxt | 업비트/바이낸스 암호화폐 |
| 금융 데이터 | fredapi | 미국 FRED 기준금리 |
| 인증 | bcrypt | 비밀번호 해싱 |
| 세션 | itsdangerous | 세션 서명/검증 |
| HTTP 요청 | requests | 외부 API 호출 |
| HTML 파싱 | beautifulsoup4 | YouTube 제목 파싱 |
| 데이터 처리 | pandas | 시계열 데이터 처리 |
| 유효성 검사 | pydantic | 요청/응답 스키마 |

### KOSPI 실시간 서버 (Kstock/)

| 분류 | 항목 | 버전/설명 |
|------|------|-----------|
| 프레임워크 | Hono | Node.js 경량 웹 프레임워크 |
| 런타임 | Node.js 20 | ESM 모듈 방식 |
| WebSocket (KIS) | ws | KIS WebSocket 클라이언트 |
| WebSocket (브라우저) | ws (WebSocketServer) | 브라우저 브로드캐스트 서버 |
| 환경변수 | dotenv | 로컬 개발용 |

### 채팅 서버 (Chat/)

| 분류 | 항목 | 설명 |
|------|------|------|
| 언어 | Rust | 고성능 WebSocket 서버 |
| 프레임워크 | Axum 0.7 | HTTP + WebSocket |
| 비동기 런타임 | Tokio (full) | 비동기 처리 |
| DB 연결 | sqlx 0.7 (postgres) | 비동기 PostgreSQL |
| 직렬화 | serde / serde_json | JSON 처리 |
| 브로드캐스트 | tokio::sync::broadcast | 전체 방 메시지 브로드캐스트 |
| 로깅 | tracing / tracing-subscriber | 구조화 로그 |

### 프론트엔드 (Front/)

| 분류 | 항목 | 버전 |
|------|------|------|
| 프레임워크 | Vue 3 | 3.5.24 |
| 빌드 도구 | Vite | - |
| 라우팅 | vue-router | 4.6.4 |
| 상태 관리 | Pinia | 3.0.4 |
| HTTP 클라이언트 | axios | 1.13.2 |
| 차트 | chart.js | 4.5.1 |
| 차트 래퍼 | vue-chartjs | 5.3.3 |
| 차트 줌 | chartjs-plugin-zoom | 2.2.0 |
| 캘린더 | @fullcalendar/vue3 외 4종 | 6.1.20 |
| 스타일 | Tailwind CSS 4 | PostCSS 기반 |

---

## 4. 환경 변수 (API 키)

`Back/.env` 파일에 관리.

| 키 이름 | 용도 |
|---------|------|
| `DB_HOST` | PostgreSQL 호스트 |
| `DB_NAME` | DB 이름 |
| `DB_USER` | DB 사용자 |
| `DB_PASSWORD` | DB 비밀번호 |
| `DB_PORT` | DB 포트 (기본 5432) |
| `ECOS_DATA_API_KEY` | 한국은행 ECOS API (기준금리, 환율) |
| `FRED_DATA_API_KEY` | 미국 FRED API (미국 기준금리) |
| `DATA_GO_KR_API_KEY` | 공공데이터포털 API (KRX 금 시세) |
| `KIS_APP_KEY` | 한국투자증권 API 앱 키 (KOSPI 주식) |
| `KIS_APP_SECRET` | 한국투자증권 API 앱 시크릿 |
| `KIS_ACCOUNT_NO` | 한국투자증권 계좌번호 |
| `TWELVE_DATA_API_KEY` | Twelve Data API (NASDAQ 주식) |
| `EIA_API_KEY` | 미국 에너지정보청 EIA API (유가 - 예정) |
| `SESSION_SECRET` | 세션 서명용 시크릿 키 |

---

## 5. 백엔드 (FastAPI)

### 5-1. 디렉토리 구조

```
Back/
├── main.py                        ← FastAPI 앱 진입점, 라우터 등록, 미들웨어 설정
├── database.py                    ← DB 연결 풀, 테이블 자동 생성
├── schemas.py                     ← Pydantic 공통 스키마
├── .env
├── requirements.txt
├── router/
│   ├── auth.py                    ← 인증 라우터
│   ├── board.py                   ← 게시판 라우터
│   ├── dashboard.py               ← 대시보드 라우터
│   ├── todo.py                    ← 할 일 라우터
│   └── video.py                   ← 영상 라우터
└── controller/
    ├── auth/
    │   └── auth_controller.py     ← 회원가입, 로그인, 세션 처리
    ├── post/
    │   └── post_controller.py     ← 게시글, 댓글 CRUD, 이미지 업로드
    ├── service/
    │   ├── market_scheduler.py    ← APScheduler 기반 자동 수집 엔진
    │   ├── interest_service.py    ← 기준금리 수집/조회 (ECOS + FRED)
    │   ├── exchange_service.py    ← 환율 수집/조회 (ECOS)
    │   ├── crypto_service.py      ← 암호화폐 수집/조회 (ccxt)
    │   ├── gold_service.py        ← 금 가격 수집/조회 (공공데이터 + yfinance)
    │   ├── stock_service.py       ← 주식 수집/조회 (KIS + Twelve Data)
    │   └── fng_crawler.py         ← 공포탐욕지수 수집 (CNN API)
    ├── todo/
    │   └── service.py             ← 할 일 CRUD
    └── video/
        └── service.py             ← 영상 등록/삭제, 댓글, YouTube 파싱
```

### 5-2. 미들웨어 설정

```python
# CORS
origins = ["http://localhost:5173", "http://{EC2_PUBLIC_IP}"]

# Session
SessionMiddleware(secret_key=SESSION_SECRET, max_age=7200)

# Static Files
/static → uploads/ 디렉토리 (이미지 업로드 파일 서빙)
```

### 5-3. 전체 API 엔드포인트

#### 인증 (`/auth`)

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| POST | `/auth/signup` | 회원가입 (bcrypt 해싱) | ❌ |
| POST | `/auth/login` | 로그인 (세션 생성) | ❌ |
| POST | `/auth/logout` | 로그아웃 (세션 삭제) | ✅ |
| GET | `/auth/me` | 현재 로그인 유저 조회 | ✅ |

#### 대시보드 (`/dashboard`)

| 메서드 | 경로 | 설명 | 데이터 소스 |
|--------|------|------|------------|
| GET | `/dashboard/interest-rates` | 한/미 기준금리 시계열 | DB (ECOS + FRED) |
| GET | `/dashboard/exchange-rate` | 원/달러 환율 시계열 | DB (ECOS) |
| GET | `/dashboard/fear-greed` | 공포탐욕지수 현재값 | DB (CNN API) |
| GET | `/dashboard/stocks/{market}` | KOSPI/NASDAQ 상위 주식 | DB (KIS + Twelve Data) |
| GET | `/dashboard/crypto/{coin}` | BTC/ETH/XRP 시세 + 히스토리 | DB (Upbit + Binance via ccxt) |
| GET | `/dashboard/gold` | 금 현재가 + 국내 히스토리 | DB (공공데이터 + yfinance) |

#### 게시판 (`/posts`)

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| GET | `/posts` | 게시글 목록 (페이지네이션) | ✅ |
| GET | `/posts/{post_id}` | 게시글 상세 + 조회수 증가 | ✅ |
| POST | `/posts` | 게시글 작성 (이미지 포함) | ✅ |
| POST | `/posts/image/upload` | 이미지 단독 업로드 | ✅ |
| PUT | `/posts/{post_id}` | 게시글 수정 | ✅ |
| DELETE | `/posts/{post_id}` | 게시글 삭제 | ✅ |
| GET | `/posts/{post_id}/comments` | 댓글 조회 (트리 구조) | ✅ |
| POST | `/posts/{post_id}/comments` | 댓글/대댓글 작성 | ✅ |
| DELETE | `/posts/comments/{comment_id}` | 댓글 삭제 | ✅ |

#### 할 일 (`/todos`)

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| GET | `/todos` | 내 할 일 목록 | ✅ |
| POST | `/todos` | 할 일 생성 | ✅ |
| PUT | `/todos/{todo_id}` | 할 일 수정 | ✅ |
| DELETE | `/todos/{todo_id}` | 할 일 삭제 | ✅ |

#### 영상 (`/videos`)

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| GET | `/videos` | 영상 목록 (페이지네이션, 태그 필터) | ✅ |
| POST | `/videos` | 영상 등록 (YouTube URL → 제목 자동 파싱) | ✅ |
| DELETE | `/videos/{video_id}` | 영상 삭제 | ✅ |
| GET | `/videos/tags` | 태그 목록 조회 | ✅ |
| POST | `/videos/{video_id}/comments` | 댓글 작성 | ✅ |
| POST | `/videos/{video_id}/view` | 조회수 증가 | ✅ |
| POST | `/videos/{video_id}/like` | 좋아요 증가 | ✅ |
| POST | `/videos/{video_id}/hate` | 싫어요 증가 | ✅ |
| POST | `/videos/{video_id}/report` | 신고 수 증가 | ✅ |

---

## 7. KOSPI 실시간 서버 (Kstock / Node.js)

### 구조

```
Kstock/
├── package.json        ← hono, @hono/node-server, ws, dotenv
├── Dockerfile          ← node:20-alpine
└── src/
    ├── index.js        ← Hono HTTP 서버 + 브라우저 WebSocket 브로드캐스트
    └── kisWsClient.js  ← KIS WebSocket 클라이언트 + EventEmitter
```

### 동작 방식

```
Kstock 시작
  ├─ startDbSync(): backend REST API에서 DB 종가 로드 (성공할 때까지 10초마다 재시도)
  │                 이후 10분마다 자동 갱신 (스케줄러 주기와 동기화)
  │
  ├─ KIS approval_key 발급 (POST /oauth2/Approval)
  ├─ KIS WebSocket 연결 (ws://ops.koreainvestment.com:31000 — 모의투자)
  └─ 40개 KOSPI 종목 H0STCNT0 구독

브라우저 연결 시:
  └─ /ws 엔드포인트 → 즉시 현재 스냅샷 전송 → 체결 발생 시마다 push
```

### API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 서버 상태 + 연결 클라이언트 수 + 현재 스냅샷 |
| GET | `/ws` | 브라우저 WebSocket 연결 (upgrade) |

### WebSocket 메시지 형식 (서버 → 브라우저)

```json
{
  "type": "price_update",
  "stocks": [
    { "rank": 1, "symbol": "005930", "name": "삼성전자", "price": 78000, "change": 1.23 },
    ...
  ]
}
```

### 구독 종목 (40개)

삼성전자, SK하이닉스, 현대차, 한화에어로스페이스, LIG넥스원, 한화시스템, 두산에너빌리티,
TIGER 미국S&P500, KODEX WTI원유선물(H), NAVER, 카카오, LG에너지솔루션, 삼성SDI, LG화학,
셀트리온, 기아, POSCO홀딩스, KB금융, 신한지주, 하나금융지주, SK텔레콤, KT, LG전자, 삼성물산,
현대모비스, SK이노베이션, SK, 삼성생명, 카카오뱅크, 크래프톤, 에코프로비엠, 에코프로,
포스코퓨처엠, HD현대중공업, 한국전력, 두산밥캣, 삼성전기, 현대건설, LG, KODEX 200

### 환경변수

| 키 | 기본값 | 설명 |
|----|--------|------|
| `KIS_APP_KEY` | - | KIS API 앱 키 (Back/.env 공유) |
| `KIS_APP_SECRET` | - | KIS API 앱 시크릿 (Back/.env 공유) |
| `KIS_MOCK` | `true` | `false`로 변경 시 실전투자 모드 |
| `KSTOCK_PORT` | `4000` | 서버 포트 |
| `BACKEND_URL` | `http://backend:8000` | FastAPI 내부 URL (DB 종가 조회용) |

---

## 6. 채팅 서버 (Rust / Axum)

### 구조

```
Chat/
├── Cargo.toml
└── src/
    ├── main.rs       ← 서버 진입점, 라우터 등록, DB 풀, broadcast 채널
    ├── handler.rs    ← HTTP 핸들러 + WebSocket 핸들러
    └── model.rs      ← 데이터 구조체 (Message, WsEvent 등)
```

### API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 헬스 체크 |
| GET | `/messages` | 채팅 기록 조회 (커서 기반 페이지네이션) |
| PATCH | `/messages/:id` | 메시지 수정 + 전체 브로드캐스트 |
| DELETE | `/messages/:id` | 메시지 soft delete + 전체 브로드캐스트 |
| GET | `/ws` | WebSocket 연결 업그레이드 |

### WebSocket 이벤트 구조

```json
// 새 메시지
{ "type": "new",    "data": { MessageDetail } }
// 메시지 수정
{ "type": "update", "data": { MessageDetail } }
// 메시지 삭제
{ "type": "delete", "data": { "id": 123 } }
```

- 기본 포트: `PORT` 환경변수 (기본값: 3000)
- DB: `DATABASE_URL` 또는 `POSTGRES_USER/PASSWORD/DB/DB_HOST` 조합으로 연결
- 채팅방: 기본 General 방 (id=1) 단일 운영

---

## 8. 프론트엔드 (Vue 3)

### 디렉토리 구조

```
Front/src/
├── App.vue                          ← 루트 컴포넌트 (NavBar + RouterView + Footer)
├── main.js                          ← Vue 앱 초기화, Pinia, Router 등록
├── api/
│   └── index.js                     ← Axios 인스턴스 2개 (api, chat)
├── router/
│   └── index.js                     ← 라우트 정의 + 네비게이션 가드
├── stores/
│   └── auth.js                      ← Pinia 인증 스토어
├── data/
│   └── dummyVideoData.js            ← 영상 더미 데이터
├── views/
│   ├── HomeView.vue                 ← 대시보드 메인
│   ├── MustDoView.vue               ← 할 일 + 캘린더
│   ├── auth/
│   │   ├── Login.vue                ← 로그인 페이지
│   │   └── Signup.vue               ← 회원가입 (보안 공지 + 동의 체크박스 포함)
│   ├── post/
│   │   ├── BoardListView.vue        ← 게시글 목록
│   │   ├── BoardWriteView.vue       ← 게시글 작성/수정 (공용)
│   │   ├── BoardDetailView.vue      ← 게시글 상세
│   │   └── CommentItem.vue          ← 재귀 댓글 컴포넌트
│   ├── chat/
│   │   └── ChatView.vue             ← 실시간 채팅
│   └── video/
│       └── VideoView.vue            ← 영상 목록 페이지
└── components/
    ├── NavBar.vue                   ← 상단 내비게이션 바
    ├── Footer.vue                   ← 하단 푸터
    ├── dashboard/
    │   ├── FearGreedIndex.vue       ← 공포탐욕지수 게이지
    │   ├── StockTopList.vue         ← KOSPI/NASDAQ 상위 종목 테이블
    │   ├── ExchangeRateChart.vue    ← 원/달러 환율 차트
    │   ├── InterestRateChart.vue    ← 한/미 기준금리 차트
    │   ├── BitcoinChart.vue         ← 암호화폐 차트 (BTC/ETH/XRP 선택)
    │   └── GoldChart.vue            ← 금 현물 차트
    └── video/
        ├── VideoItem.vue            ← 영상 카드 컴포넌트
        ├── VideoList.vue            ← 영상 그리드 목록
        ├── VideoComments.vue        ← 영상 댓글 목록
        └── VideoRegisterModal.vue   ← 영상 등록 모달
```

### Axios 인스턴스 설정

```javascript
// api: FastAPI 백엔드
api = axios.create({ baseURL: '/api', withCredentials: true })

// chat: Rust 채팅 서버
chat = axios.create({ baseURL: '/chat', withCredentials: true })
```

### 라우터 설정

| 경로 | 컴포넌트 | 인증 필요 |
|------|----------|-----------|
| `/` | HomeView | ✅ |
| `/mustdo` | MustDoView | ✅ |
| `/login` | Login | ❌ |
| `/signup` | Signup | ❌ |
| `/board` | BoardListView | ✅ |
| `/board/write` | BoardWriteView | ✅ |
| `/board/:id` | BoardDetailView | ✅ |
| `/board/edit/:id` | BoardWriteView (수정 모드) | ✅ |
| `/chat` | ChatView | ✅ |
| `/video` | VideoView | ✅ |

### 폰트

- **Pretendard Variable** (CDN, `index.html`) — 한/영 통합 웹 폰트
- fallback: Inter → system-ui → -apple-system → sans-serif
- 기존 한글 맑은 고딕 fallback 렌더링 개선

- 네비게이션 가드: `router.beforeEach` → `authStore.checkAuth()` → 미인증 시 `/login` 리다이렉트

---

## 9. 페이지별 상세 설명

### 8-1. 대시보드 (`/` → HomeView.vue)

금융 시장 데이터를 한눈에 확인하는 메인 페이지. 3행 2열 그리드 레이아웃.

#### 레이아웃 구조

```
┌─────────────┬──────────────────────┐  ← 행1 h-[460px]
│ Fear&Greed  │   Market Leaders     │
│ Index       │   (KOSPI / NASDAQ)   │
├─────────────┴──┬───────────────────┤  ← 행2 h-[300px]
│  Exchange Rate │  Base Interest    │
│  (USD/KRW)    │  Rate (KR / US)   │
├────────────────┴──────────────────┤  ← 행3 h-[460px]
│  Crypto Asset  │  Gold Futures     │
│  (BTC/ETH/XRP) │  (국내 KRW/g)     │
└────────────────┴──────────────────┘
```

#### 각 위젯 상세

**FearGreedIndex.vue** — 공포탐욕지수
- API: `GET /dashboard/fear-greed`
- 데이터 소스: CNN Fear & Greed API (`dataviz.cnn.io/index/fearandgreed/graphdata`)
- 표시 요소: 반원 게이지, 0~100 점수, 등급 텍스트 (Extreme Fear → Extreme Greed)
- 색상: 점수 구간별 (green → emerald → gray → orange → red)

**StockTopList.vue** — 시장 주요 종목
- KOSPI 탭: Kstock 서버 WebSocket (`ws://host/kstock/ws`) 실시간 연결
  - 연결 즉시 DB 종가 스냅샷 수신 → 장중 체결 발생 시 실시간 업데이트
  - 헤더에 ● LIVE (초록) / ○ Connecting... (회색) 연결 상태 표시
  - 40개 KOSPI 종목 표시
- NASDAQ 탭: 기존 REST API 방식 유지 (`GET /dashboard/stocks/nasdaq`)
  - NASDAQ: Twelve Data API (AAPL, NVDA, MSFT, AMZN, GOOGL)
- 표시 요소: 순위, 종목명/심볼, 현재가, 등락률 (등락 색상 표시)
- 탭 전환 시 WebSocket 자동 해제/연결

**ExchangeRateChart.vue** — 원/달러 환율
- API: `GET /dashboard/exchange-rate`
- 데이터 소스: 한국은행 ECOS API (통계표 `731Y001`)
- 표시 요소:
  - 헤더: 현재 환율 (₩ 원화 표시) + 전일 대비 등락률
  - 차트: 시계열 라인 차트 (좌우 스크롤 가능, 최신 날짜로 자동 스크롤)
  - 색상: #10b981 (에메랄드)
- 차트 라이브러리: Chart.js + vue-chartjs

**InterestRateChart.vue** — 한/미 기준금리
- API: `GET /dashboard/interest-rates`
- 데이터 소스:
  - 한국 기준금리: ECOS API (통계표 `722Y001`)
  - 미국 기준금리: FRED API (시리즈 `DFEDTARU` - 연준 목표금리 상단)
- 표시 요소:
  - 헤더: KR X.XX% | US X.XX% 현재 금리
  - 차트: 두 라인 (KR: 골드 #D4AF37, US: 블랙)
  - 좌우 스크롤 가능, 최신 날짜로 자동 스크롤

**BitcoinChart.vue** — 암호화폐
- API: `GET /dashboard/crypto/{coin}` (coin: `BTC` | `ETH` | `XRP`)
- 데이터 소스: ccxt 라이브러리 → Upbit (KRW 마켓) + Binance (USDT 마켓)
- 표시 요소:
  - 헤더: 코인 선택 드롭다운 (Bitcoin/Ethereum/Ripple)
  - 현재가 (₩ KRW 기준) + 전일 대비 등락률
  - 김치 프리미엄 = `(업비트가 - 바이낸스가×환율) / 바이낸스가×환율 × 100`
  - 차트: Upbit (실선) + Binance KRW 환산 (점선) 두 라인
  - 줌/팬 지원 (chartjs-plugin-zoom)

**GoldChart.vue** — 금 현물
- API: `GET /dashboard/gold`
- 데이터 소스:
  - 현재가/히스토리: 공공데이터포털 API (`apis.data.go.kr/1160100/.../getGoldPriceInfo`) - KRX 금 시장
  - 국제 금 선물 보조: yfinance `GC=F`
- 표시 요소:
  - 헤더: 현재 금 시세 (₩/g) + 등락률
  - 차트: 국내 금 가격 시계열 (골드 컬러 #D4AF37, 그라디언트 fill)
  - 줌/팬 지원 (chartjs-plugin-zoom)

---

### 8-2. 할 일 관리 (`/mustdo` → MustDoView.vue)

- 기능: 할 일 CRUD + FullCalendar 연동
- API: `GET/POST/PUT/DELETE /todos`
- 라이브러리: `@fullcalendar/vue3`, `@fullcalendar/daygrid`, `@fullcalendar/interaction` 등

---

### 8-3. 게시판 (`/board`)

- **목록** (`BoardListView.vue`): 페이지네이션, 게시글 미리보기
- **작성/수정** (`BoardWriteView.vue`): 공용 컴포넌트, 이미지 업로드 지원 (멀티파트)
- **상세** (`BoardDetailView.vue`): 조회수, 이미지 갤러리, 댓글/대댓글 트리
- **댓글** (`CommentItem.vue`): 재귀 렌더링 (무한 depth 대댓글)
- 이미지: 서버에 UUID 파일명으로 저장 → `/static/` 경로로 서빙

---

### 8-4. 실시간 채팅 (`/chat` → ChatView.vue)

- WebSocket: `ws://서버/ws` 연결
- 기능: 메시지 송수신, 수정, soft delete
- 채팅 기록: `GET /messages` (커서 기반 페이지네이션, 과거 메시지 무한 스크롤)
- 실시간 이벤트: `new` / `update` / `delete` 타입으로 브로드캐스트
- 단일 채팅방 (General, id=1)

---

### 8-5. 영상 관리 (`/video` → VideoView.vue)

- **등록**: YouTube URL 입력 → 서버에서 제목 자동 파싱 (`urllib.request` + 정규식)
- **목록**: 태그 필터링 (Music / Game / Humor 등 8종), 페이지네이션
- **영상 카드**: 조회수, 좋아요/싫어요/신고 버튼, 댓글
- 태그: `video_tags` 테이블에서 관리 (미리 정의된 8종)

---

### 9-6. 로그인 / 회원가입

- **로그인** (`Login.vue`): ID/PW 입력 → `POST /auth/login` → 세션 쿠키 발급
- **회원가입** (`Signup.vue`):
  - 보안 취약 공지 박스 (비밀번호 입력 위에 표시)
  - 공지 동의 체크박스 필수 체크 후에만 가입 버튼 활성화 (이중 유효성 검사)
  - `POST /auth/signup` → bcrypt 해싱 후 DB 저장
- 인증 상태: Pinia `auth.js` 스토어에서 `isAuthenticated` 관리
- 자동 로그인 유지: 앱 시작 시 `GET /auth/me` 호출로 세션 확인

---

## 10. 외부 API 연동 목록

| 서비스명 | API 주소 / 라이브러리 | 용도 | 인증 방식 | 키 이름 |
|---------|---------------------|------|-----------|---------|
| 한국은행 ECOS | `ecos.bok.or.kr/api/StatisticSearch` | 기준금리 (`722Y001`), 원/달러 환율 (`731Y001`) | API Key | `ECOS_DATA_API_KEY` |
| FRED (미 연준) | `fredapi` Python 라이브러리 | 미국 기준금리 (`DFEDTARU`) | API Key | `FRED_DATA_API_KEY` |
| CNN Fear & Greed | `production.dataviz.cnn.io/index/fearandgreed/graphdata` | 공포탐욕지수 | 없음 (public) | - |
| Upbit | `ccxt` 라이브러리 + REST fallback | BTC/ETH/XRP KRW 시세, OHLCV | 없음 (public) | - |
| Binance | `ccxt` 라이브러리 | BTC/ETH/XRP USDT 시세, OHLCV | 없음 (public) | - |
| yfinance | `yfinance` Python 라이브러리 | 국제 금 선물 (`GC=F`), 환율 보조 (`KRW=X`) | 없음 (Yahoo Finance) | - |
| 공공데이터포털 | `apis.data.go.kr/1160100/.../getGoldPriceInfo` | KRX 국내 금 시세 | API Key | `DATA_GO_KR_API_KEY` |
| 한국투자증권 KIS REST | `openapi.koreainvestment.com:9443` (실전) / `openapivts.koreainvestment.com:29443` (모의) | KOSPI 40종목 종가 DB 저장 (10분 스케줄러) | App Key/Secret | `KIS_APP_KEY`, `KIS_APP_SECRET` |
| 한국투자증권 KIS WebSocket | `ops.koreainvestment.com:21000` (실전) / `:31000` (모의) | KOSPI 40종목 실시간 체결가 (H0STCNT0) | approval_key (OAuth2) | `KIS_APP_KEY`, `KIS_APP_SECRET` |
| Twelve Data | `api.twelvedata.com/quote` | NASDAQ 주식 현재가 | API Key | `TWELVE_DATA_API_KEY` |
| EIA (미 에너지정보청) | `api.eia.gov/v2/petroleum` | 원유 가격 WTI/Brent **(예정)** | API Key | `EIA_API_KEY` |
| YouTube | HTML 파싱 (`urllib.request`) | 영상 제목 자동 수집 | 없음 | - |

---

## 11. 데이터베이스 테이블 목록

PostgreSQL. `database.py`에서 앱 시작 시 자동 CREATE TABLE IF NOT EXISTS.

| 테이블 | 용도 | 관련 서비스 |
|--------|------|------------|
| `users` | 회원 정보 (id, username, password_hash) | auth_controller |
| `todos` | 할 일 (user_id FK, title, date, done) | todo/service |
| `posts` | 게시글 (title, content, author, views) | post_controller |
| `post_images` | 게시글 첨부 이미지 (post_id FK, file_path) | post_controller |
| `post_replies` | 게시글 댓글/대댓글 (post_id FK, parent_id 자기참조) | post_controller |
| `chat_rooms` | 채팅방 (기본: General id=1) | Rust 채팅 서버 |
| `messages` | 채팅 메시지 (room_id FK, content, is_deleted soft delete) | Rust 채팅 서버 |
| `video_tags` | 영상 태그 8종 (Music, Game, Humor 등) | video/service |
| `videos` | 영상 (youtube_key, title, views, likes 등) | video/service |
| `video_comments` | 영상 댓글 | video/service |
| `market_fear_greed` | 공포탐욕지수 스냅샷 (score, rating, timestamp) | fng_crawler |
| `market_stocks` | 주식 현재가 스냅샷 (symbol, price, change, market) | stock_service |
| `market_exchange_rate` | 원/달러 환율 시계열 (date, rate) | exchange_service |
| `market_interest_rate` | 한/미 기준금리 시계열 (date, kr_rate, us_rate) | interest_service |
| `market_crypto_price` | 암호화폐 현재가 스냅샷 (symbol, krw_price, usd_price, kimchi_premium) | crypto_service |
| `market_crypto_history` | 암호화폐 90일 OHLCV 히스토리 | crypto_service |
| `market_gold_price` | 금 현재가 스냅샷 (domestic_krw, international_usd, change_rate) | gold_service |
| `market_gold_history` | 금 가격 시계열 (date, price_krw) | gold_service |

---

## 12. 스케줄러 (자동 수집 주기)

`market_scheduler.py` — APScheduler 기반. 앱 시작 시 1회 즉시 실행 후 주기 반복.

| 데이터 | 수집 주기 | 서비스 파일 | 비고 |
|--------|----------|------------|------|
| 공포탐욕지수 | 1시간 | `fng_crawler.py` | CNN API 실패 시 Mock 데이터 반환 |
| KOSPI 주식 (40종목) | 10분 | `stock_service.py` | 장외 종가 DB 저장 목적. sleep 1.5s 간격 (약 60초 소요). Kstock DB 폴백용 |
| NASDAQ 주식 (5종목) | 10분 | `stock_service.py` | Twelve Data API |
| 원/달러 환율 | 1시간 | `exchange_service.py` | ECOS API |
| 기준금리 (한/미) | 24시간 | `interest_service.py` | ECOS + FRED |
| 암호화폐 (BTC/ETH/XRP) | 5분 | `crypto_service.py` | Upbit + Binance via ccxt |
| 금 가격 | 1시간 | `gold_service.py` | 공공데이터 + yfinance |

---

## 13. 추후 작업 예정

| 항목 | 내용 | 우선순위 |
|------|------|---------|
| 유가 데이터 | EIA API 연동 (WTI/Brent 원유 가격) → 대시보드 새 위젯 추가 | 높음 |
| | 백엔드: `oil_service.py` 작성, `market_oil_price` 테이블 추가 | |
| | 스케줄러: 1시간 주기 수집 | |
| | 프론트: `OilChart.vue` 컴포넌트 추가 | |
| TradingView 위젯 대체 | 기존 TradingView 위젯 → DB 데이터 기반 자체 Chart.js 차트로 전환 | 중간 |
| 모바일 앱 + 위젯 | DB 데이터 활용 모바일 앱 (Capacitor 또는 Flutter), 홈 위젯 지원 | 낮음 |
| ✅ 실시간 주가 (KIS WebSocket) | Kstock 서비스 신설. KIS WebSocket(H0STCNT0)으로 KOSPI 40종목 실시간 체결가 수신 → 브라우저 브로드캐스트 | 완료 |
| initFromDb 재시도 안정화 | Kstock 시작 시 backend 미준비로 DB 폴백 실패 → 현재 10초 재시도 로직 적용 중. 추가 검증 필요 | 낮음 |
| ✅ HTTPS 전환 (Cloudflare + Caddy) | hadaboni.work 도메인 구매 → Cloudflare 오렌지 클라우드 프록시 ON → Origin Certificate 발급 → Caddy tls 지시어로 인증서 마운트. docker-compose 443 포트 개방 | 완료 |
| 마이페이지 | 로그인 유저 전용 마이페이지 (`/mypage`) 신설 | 중간 |
| | - 프로필 이미지 업로드/변경 (서버 저장 후 `/static/` 서빙, `users` 테이블에 profile_image 컬럼 추가) | |
| | - 내가 작성한 게시글 목록 조회 (`GET /posts?author_me=true`) | |
| | - 내가 등록한 영상 목록 조회 (`GET /videos?uploader_me=true`) | |
| 소셜 로그인 | Google / GitHub / KakaoTalk OAuth2 연동 | 중간 |
| | - 백엔드: OAuth2 콜백 처리, 소셜 계정 연결 정보 저장 (`user_social_accounts` 테이블) | |
| | - 프론트: 로그인/회원가입 페이지에 소셜 로그인 버튼 추가 | |
| | - 기존 세션 기반 인증과 통합 (소셜 로그인 후 동일 세션 쿠키 발급) | |
