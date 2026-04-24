# 주가 상세 팝업 패널 — 구현 계획서

작성일: 2026-04-24  
상태: 계획 완료 / 구현 대기

---

## 1. 개요

대시보드 `StockTopList`에서 종목 클릭 시 **페이지 전환 없이** 현재 화면 위에 글래스모피즘 모달 패널로 상세 정보를 표시한다.

---

## 2. UI 방식

### Vue `<Teleport to="body">` 모달
- `body` 최상단에 독립 렌더링 → z-index / overflow / backdrop-filter 충돌 없음
- `<Transition>` 으로 페이드+슬라이드 애니메이션 적용
- 바깥 클릭 또는 `Esc` 키로 닫힘
- **디자인은 기존 `glassmorphism.scss`의 `.glass-card`, `.glass-header` 클래스 그대로 적용**

### 레이아웃 스케치
```
┌─────────────────────────────────────────────────────────┐
│                   대시보드 (흐림 처리)                     │
│                                                         │
│    ┌───────────────────────────────────────────┐        │
│    │  🔷 삼성전자  005930  KOSPI      [✕ 닫기] │        │
│    │─────────────────────────────────────────── │        │
│    │  ₩ 78,500  ▲ +1,200 (+1.55%)              │        │
│    │─────────────────────────────────────────── │        │
│    │  📊 재무 지표                               │        │
│    │  PER 14.2 | PBR 1.1 | EPS 5,520           │        │
│    │  시가총액 468조 | 52주 최고 88,800          │        │
│    │─────────────────────────────────────────── │        │
│    │  👥 투자자 현황                             │        │
│    │  외국인 보유 지분율 ────────────── 52.3%   │        │
│    │  오늘 순매수 동향                           │        │
│    │    개인  +125,000주                        │        │
│    │    기관    -48,000주                       │        │
│    │    외국인  +23,000주                       │        │
│    │─────────────────────────────────────────── │        │
│    │  📰 관련 뉴스                               │        │
│    │  · 삼성전자, HBM 수율 개선...  한경  2시간전 │        │
│    │  · 반도체 업황 회복 신호...    매경  5시간전 │        │
│    │─────────────────────────────────────────── │        │
│    │  [네이버 증권] [TradingView]               │        │
│    └───────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 데이터 항목 및 출처

### 섹션 1: 현재가 헤더
| 항목 | 출처 | 비고 |
|------|------|------|
| 현재가 | **기존 KIS WebSocket** | 추가 작업 없음 |
| 전일 대비 등락 (금액/비율) | **기존 KIS WebSocket** | 추가 작업 없음 |
| 종목명, 종목코드, 시장구분 | kisWsClient.js SYMBOLS 목록 | 이미 보유 |

---

### 섹션 2: 재무 지표
**출처: KIS REST API `FHKST01010100`** (기존 앱키/시크릿 재사용)

| 필드명 | 항목 | 비고 |
|--------|------|------|
| `per` | PER (주가수익비율) | 직접 제공 |
| `pbr` | PBR (주가순자산비율) | 직접 제공 |
| `eps` | EPS (주당순이익) | 직접 제공 |
| `hts_avls` | 시가총액 | 직접 제공 |
| `w52_hgpr` | 52주 최고가 | 직접 제공 |
| `w52_lwpr` | 52주 최저가 | 직접 제공 |
| `frgn_hld_vol_rate` | 외국인 보유 지분율(%) | 직접 제공 |

> ⚠️ ROE는 이 API에서 제공되지 않음 → **미노출 처리**

**정확도 원칙:** 값이 null / 0 / API 실패 시 해당 카드 전체 숨김 처리

---

### 섹션 3: 투자자 현황 (옵션 B 확정)
**두 가지 데이터를 함께 표시**

#### 3-1. 외국인 보유 지분율 (정확한 값)
- `FHKST01010100` 응답의 `frgn_hld_vol_rate` 필드
- 섹션 2 호출 시 동시에 획득 가능 (추가 API 호출 없음)

#### 3-2. 당일 순매수 동향 (개인 / 기관 / 외국인)
- **출처: KIS REST API `FHKST01010900`** (종목별 투자자 매매동향)
- 개인 순매수량, 기관 순매수량, 외국인 순매수량
- 장중: 실시간 누적 / 장 종료 후: 확정치

```
외국인 보유 지분율   ━━━━━━━━━━━━━━━━━  52.3%

오늘 순매수 동향
  개인    +125,000주  ▲
  기관     -48,000주  ▼
  외국인   +23,000주  ▲
```

---

### 섹션 4: 관련 뉴스
**출처: 네이버 검색 OpenAPI**
```
GET https://openapi.naver.com/v1/search/news.json
    ?query={종목명}+주가&display=5&sort=date
```
- 무료 25,000건/일
- `Back/.env`에 `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` 추가 필요
- 제목, 언론사, 게시일, 원문링크 표시

---

### 섹션 5: 외부 차트 링크 (구현 없음)
| 버튼명 | 이동 URL |
|--------|---------|
| 네이버 증권 | `https://finance.naver.com/item/main.naver?code={symbol}` |
| TradingView | `https://kr.tradingview.com/chart/?symbol=KRX:{symbol}` |

---

## 4. 백엔드 구현

### 신규 파일: `Back/router/stock.py`

```
GET /stock/{symbol}/overview    → KIS FHKST01010100
                                  (재무지표 + 외국인 지분율)

GET /stock/{symbol}/investors   → KIS FHKST01010900
                                  (개인/기관/외국인 순매수량)

GET /stock/{symbol}/news        → 네이버 검색 API
                                  (뉴스 5건)
```

### DB 캐싱 전략
| 데이터 | 캐시 여부 | 갱신 주기 |
|--------|---------|---------|
| 재무지표 (`market_stock_fundamental` 신규 테이블) | ✅ 캐시 | 장 마감 후 1회 |
| 외국인 지분율 | ✅ 재무지표와 동일 테이블 | 장 마감 후 1회 |
| 투자자 매매동향 | ❌ 캐시 없음 | 요청마다 실시간 |
| 뉴스 | ❌ 캐시 없음 | 요청마다 실시간 |

### 신규 DB 테이블
```sql
CREATE TABLE market_stock_fundamental (
    id          SERIAL PRIMARY KEY,
    symbol      VARCHAR(20) UNIQUE NOT NULL,
    per         NUMERIC(8,2),
    pbr         NUMERIC(8,2),
    eps         NUMERIC(12,2),
    market_cap  NUMERIC(20,2),
    w52_high    NUMERIC(15,2),
    w52_low     NUMERIC(15,2),
    frgn_ratio  NUMERIC(6,2),   -- 외국인 보유 지분율(%)
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. 프론트엔드 구현

### 신규 컴포넌트 구조
```
components/stock/
├── StockDetailModal.vue      ← <Teleport to="body"> + <Transition> 래퍼
├── StockModalHeader.vue      ← 종목명, 현재가, 등락
├── StockModalFundamental.vue ← PER/PBR/EPS/시가총액/52주
├── StockModalInvestors.vue   ← 외국인 지분율 + 순매수 동향
├── StockModalNews.vue        ← 뉴스 리스트
└── StockModalLinks.vue       ← 외부 차트 링크 버튼
```

### HomeView.vue 수정
```vue
<script setup>
const selectedSymbol = ref(null)
</script>

<template>
  <StockTopList @select="selectedSymbol = $event" />
  <StockDetailModal
    v-if="selectedSymbol"
    :symbol="selectedSymbol"
    @close="selectedSymbol = null"
  />
</template>
```

### StockTopList.vue 수정
- 종목 행에 `@click="$emit('select', stock.symbol)"` 추가 (1줄 수정)

---

## 6. 구현 순서 (권장)

| 순서 | 항목 | 예상 난이도 |
|------|------|-----------|
| 1 | `Back/.env`에 네이버 API 키 추가 | ⭐ |
| 2 | DB 테이블 `market_stock_fundamental` 추가 | ⭐ |
| 3 | `Back/router/stock.py` 라우터 작성 | ⭐⭐ |
| 4 | KIS REST API 서비스 로직 작성 (access_token 발급 포함) | ⭐⭐⭐ |
| 5 | 네이버 뉴스 서비스 로직 작성 | ⭐⭐ |
| 6 | `StockDetailModal.vue` Teleport/Transition 골격 작성 | ⭐⭐ |
| 7 | 각 섹션 컴포넌트 작성 (glassmorphism 스타일 적용) | ⭐⭐ |
| 8 | `StockTopList.vue` 클릭 이벤트 연결 | ⭐ |

---

## 7. 사전 준비 사항

- [ ] **네이버 Developers 앱 등록** → Client ID / Client Secret 발급
  - https://developers.naver.com → 애플리케이션 등록 → 검색 API 선택
- [ ] **KIS API 모의투자 환경 확인** → `FHKST01010100`, `FHKST01010900` 모의환경 동작 여부 확인
  - 미지원 시 실전 환경 전용으로 분기 처리 필요
