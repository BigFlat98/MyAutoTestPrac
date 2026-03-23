import 'dotenv/config'
import { Hono } from 'hono'
import { serve } from '@hono/node-server'
import { WebSocketServer } from 'ws'
import KisWsClient from './kisWsClient.js'

const PORT = parseInt(process.env.KSTOCK_PORT ?? '4000')

const app = new Hono()

// 연결된 브라우저 WebSocket 세트
const clients = new Set()

// KIS 실시간 클라이언트 시작
const kisClient = new KisWsClient()
kisClient.connect()

// 가격 업데이트 → 연결된 모든 브라우저에 브로드캐스트
kisClient.on('priceUpdate', (stocks) => {
  if (clients.size === 0) return
  const msg = JSON.stringify({ type: 'price_update', stocks })
  for (const ws of clients) {
    if (ws.readyState === 1 /* OPEN */) {
      ws.send(msg)
    } else {
      clients.delete(ws)
    }
  }
})

// 헬스 체크
app.get('/health', (c) =>
  c.json({ status: 'ok', clients: clients.size, stocks: kisClient.getSnapshot() })
)

// HTTP 서버 시작 (serve()가 Node http.Server를 반환)
const server = serve({ fetch: app.fetch, port: PORT }, () => {
  console.log(`[Kstock] 서버 시작 → http://localhost:${PORT}`)
})

// 같은 HTTP 서버에 WebSocket 서버 연결 (/ws 경로)
const wss = new WebSocketServer({ server, path: '/ws' })

wss.on('connection', (ws) => {
  clients.add(ws)
  console.log(`[WS] 클라이언트 연결 (현재 ${clients.size}명)`)

  // 접속 즉시 현재 스냅샷 전송
  ws.send(JSON.stringify({ type: 'price_update', stocks: kisClient.getSnapshot() }))

  ws.on('close', () => {
    clients.delete(ws)
    console.log(`[WS] 클라이언트 종료 (현재 ${clients.size}명)`)
  })

  ws.on('error', (err) => {
    console.error('[WS] 클라이언트 오류:', err.message)
    clients.delete(ws)
  })
})
