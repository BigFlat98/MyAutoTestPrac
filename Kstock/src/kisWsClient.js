import { EventEmitter } from 'events'
import WebSocket from 'ws'

const KIS_APP_KEY    = process.env.KIS_APP_KEY
const KIS_APP_SECRET = process.env.KIS_APP_SECRET
const BACKEND_URL    = process.env.BACKEND_URL || 'http://backend:8000'

// 모의투자: KIS_MOCK=true (default), 실전: KIS_MOCK=false
const IS_MOCK   = process.env.KIS_MOCK !== 'false'
const REST_BASE = IS_MOCK
  ? 'https://openapivts.koreainvestment.com:29443'
  : 'https://openapi.koreainvestment.com:9443'
const WS_URL    = IS_MOCK
  ? 'ws://ops.koreainvestment.com:31000'
  : 'ws://ops.koreainvestment.com:21000'

const SYMBOLS = [
  // 사용자 지정 우선 종목
  { code: '005930', name: '삼성전자'              },
  { code: '000660', name: 'SK하이닉스'            },
  { code: '005380', name: '현대차'                },
  { code: '012450', name: '한화에어로스페이스'    },
  { code: '079550', name: 'LIG넥스원'             },
  { code: '272210', name: '한화시스템'            },
  { code: '034020', name: '두산에너빌리티'        },
  { code: '360750', name: 'TIGER 미국S&P500'      },
  { code: '261220', name: 'KODEX WTI원유선물(H)'  },
  // 인기 대형주
  { code: '035420', name: 'NAVER'                 },
  { code: '035720', name: '카카오'                },
  { code: '373220', name: 'LG에너지솔루션'        },
  { code: '006400', name: '삼성SDI'               },
  { code: '051910', name: 'LG화학'                },
  { code: '068270', name: '셀트리온'              },
  { code: '000270', name: '기아'                  },
  { code: '005490', name: 'POSCO홀딩스'           },
  { code: '105560', name: 'KB금융'                },
  { code: '055550', name: '신한지주'              },
  { code: '086790', name: '하나금융지주'          },
  { code: '017670', name: 'SK텔레콤'              },
  { code: '030200', name: 'KT'                    },
  { code: '066570', name: 'LG전자'                },
  { code: '028260', name: '삼성물산'              },
  { code: '012330', name: '현대모비스'            },
  { code: '096770', name: 'SK이노베이션'          },
  { code: '034730', name: 'SK'                    },
  { code: '032830', name: '삼성생명'              },
  { code: '323410', name: '카카오뱅크'            },
  { code: '259960', name: '크래프톤'              },
  { code: '247540', name: '에코프로비엠'          },
  { code: '086520', name: '에코프로'              },
  { code: '003670', name: '포스코퓨처엠'          },
  { code: '329180', name: 'HD현대중공업'          },
  { code: '015760', name: '한국전력'              },
  { code: '241560', name: '두산밥캣'              },
  { code: '009150', name: '삼성전기'              },
  { code: '000720', name: '현대건설'              },
  { code: '003550', name: 'LG'                    },
  { code: '069500', name: 'KODEX 200'             },
]

class KisWsClient extends EventEmitter {
  constructor() {
    super()
    this.ws              = null
    this.approvalKey     = null
    this.latestPrices    = new Map()   // symbol -> { price, change }
    this.reconnectTimer  = null
    this.dbSyncStarted   = false       // DB 동기화 루프 중복 실행 방지 플래그
    this.dbSyncTimer     = null        // 재시도 setTimeout 참조
    this.dbSyncInterval  = null        // 성공 후 setInterval 참조
  }

  // KIS WebSocket 접속키(approval_key) 발급
  async getApprovalKey() {
    const res = await fetch(`${REST_BASE}/oauth2/Approval`, {
      method:  'POST',
      headers: { 'content-type': 'application/json' },
      body:    JSON.stringify({
        grant_type: 'client_credentials',
        appkey:     KIS_APP_KEY,
        secretkey:  KIS_APP_SECRET,
      }),
    })
    if (!res.ok) throw new Error(`KIS Approval 실패: ${res.status} ${await res.text()}`)
    const data = await res.json()
    return data.approval_key
  }

  // DB에 저장된 최신 종가를 불러와 초기 스냅샷으로 설정
  // 성공 시 true, 실패 시 false 반환
  async initFromDb() {
    try {
      const res = await fetch(`${BACKEND_URL}/dashboard/stocks/kospi`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      const stocks = data.stocks ?? []
      if (stocks.length === 0) throw new Error('DB에 데이터 없음')
      for (const stock of stocks) {
        this.latestPrices.set(stock.symbol, { price: stock.price, change: stock.change })
      }
      console.log(`[KIS] DB 종가 스냅샷 로드 완료 (${stocks.length}개 종목)`)
      this.emit('priceUpdate', this.getSnapshot())
      return true
    } catch (err) {
      console.warn('[KIS] DB 초기화 실패:', err.message)
      return false
    }
  }

  // DB 종가 동기화 루프
  // - 성공할 때까지 10초마다 재시도 (backend 기동 지연 대응)
  // - 성공 후에는 10분마다 갱신 (스케줄러 주기와 동기화)
  // - connect() 재연결 시 중복 실행 방지
  startDbSync() {
    if (this.dbSyncStarted) return
    this.dbSyncStarted = true

    const tryLoad = async () => {
      const ok = await this.initFromDb()
      if (!ok) {
        this.dbSyncTimer = setTimeout(tryLoad, 10_000)
      } else {
        // 기존 interval이 있으면 정리 후 새로 등록
        if (this.dbSyncInterval) clearInterval(this.dbSyncInterval)
        this.dbSyncInterval = setInterval(() => this.initFromDb(), 10 * 60 * 1_000)
      }
    }
    tryLoad()
  }

  async connect() {
    // DB 종가 동기화 시작 (WebSocket과 독립적으로 병렬 실행)
    this.startDbSync()

    try {
      this.approvalKey = await this.getApprovalKey()
      console.log('[KIS] approval_key 발급 완료')
    } catch (err) {
      console.error('[KIS] approval_key 발급 실패:', err.message)
      this.scheduleReconnect()
      return
    }

    this.ws = new WebSocket(WS_URL)

    this.ws.on('open', () => {
      console.log(`[KIS] WebSocket 연결 완료 (${WS_URL})`)
      for (const sym of SYMBOLS) {
        this.subscribe(sym.code)
      }
      console.log(`[KIS] ${SYMBOLS.length}개 종목 구독 요청 완료`)
    })

    this.ws.on('message', (raw) => {
      const msg = raw.toString()
      if (msg === 'PINGPONG') {
        this.ws.send('PINGPONG')
        return
      }
      this.parseMessage(msg)
    })

    this.ws.on('error', (err) => {
      console.error('[KIS] WebSocket 오류:', err.message)
    })

    this.ws.on('close', () => {
      console.log('[KIS] 연결 종료 → 5초 후 재연결')
      this.scheduleReconnect()
    })
  }

  subscribe(symbol) {
    const payload = JSON.stringify({
      header: {
        approval_key:   this.approvalKey,
        custtype:       'P',
        tr_type:        '1',
        'content-type': 'utf-8',
      },
      body: {
        input: { tr_id: 'H0STCNT0', tr_key: symbol },
      },
    })
    this.ws.send(payload)
  }

  parseMessage(msg) {
    // 구독 응답(JSON) 스킵
    if (msg.startsWith('{')) return

    const parts = msg.split('|')
    if (parts.length < 4) return

    const [encrypted, trId, , rawData] = parts
    if (encrypted === '1') return   // 암호화 데이터 미지원
    if (trId !== 'H0STCNT0')  return

    const f = rawData.split('^')
    // H0STCNT0 필드 순서
    // [0] MKSC_SHRN_ISCD  종목코드
    // [2] STCK_PRPR        현재가
    // [3] PRDY_VRSS_SIGN   전일대비 부호 (1:상한 2:상승 3:보합 4:하한 5:하락)
    // [5] PRDY_CTRT        전일대비율 (절대값)
    const symbol    = f[0]
    const price     = parseFloat(f[2])
    const signCode  = f[3]
    const rateAbs   = parseFloat(f[5])
    const change    = (signCode === '4' || signCode === '5')
      ? -Math.abs(rateAbs)
      :  Math.abs(rateAbs)

    if (!symbol || isNaN(price)) return

    this.latestPrices.set(symbol, { price, change })
    this.emit('priceUpdate', this.getSnapshot())
  }

  // 현재 보유 중인 전 종목 스냅샷 반환
  getSnapshot() {
    return SYMBOLS.map((sym, i) => {
      const d = this.latestPrices.get(sym.code)
      return {
        rank:   i + 1,
        symbol: sym.code,
        name:   sym.name,
        price:  d?.price  ?? 0,
        change: d?.change ?? 0,
      }
    })
  }

  scheduleReconnect() {
    if (this.reconnectTimer) return
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      this.connect()
    }, 5000)
  }
}

export default KisWsClient
