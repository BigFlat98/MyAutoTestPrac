<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { api } from '@/api/index.js';

const activeTab  = ref('kospi');
const stocks     = ref([]);
const loading    = ref(false);
// 'disconnected' | 'connecting' | 'connected'
const wsStatus   = ref('disconnected');

let ws = null;

// ─── NASDAQ: 기존 REST 방식 그대로 유지 ───────────────────────────────────
const fetchStocks = async () => {
  loading.value = true;
  try {
    const response = await api.get(`/dashboard/stocks/${activeTab.value}`);
    if (response.data && response.data.stocks) {
      stocks.value = response.data.stocks;
    }
  } catch (error) {
    console.error(`Failed to fetch ${activeTab.value} stocks:`, error);
  } finally {
    loading.value = false;
  }
};

// ─── KOSPI: WebSocket 실시간 방식 ─────────────────────────────────────────
const connectKospiWs = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const url      = `${protocol}//${window.location.host}/kstock/ws`;

  wsStatus.value = 'connecting';
  ws = new WebSocket(url);

  ws.onopen = () => {
    wsStatus.value = 'connected';
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === 'price_update' && Array.isArray(data.stocks)) {
        stocks.value  = data.stocks;
        loading.value = false;
      }
    } catch (e) {
      console.error('[Kstock WS] 메시지 파싱 오류:', e);
    }
  };

  ws.onerror = () => {
    wsStatus.value = 'disconnected';
    loading.value  = false;
  };

  ws.onclose = () => {
    wsStatus.value = 'disconnected';
  };
};

const disconnectWs = () => {
  if (ws) {
    ws.close();
    ws = null;
  }
  wsStatus.value = 'disconnected';
};

// ─── 탭 전환 ──────────────────────────────────────────────────────────────
watch(activeTab, (newTab) => {
  stocks.value = [];
  disconnectWs();

  if (newTab === 'kospi') {
    loading.value = true;
    connectKospiWs();
  } else {
    fetchStocks();
  }
});

onMounted(() => {
  if (activeTab.value === 'kospi') {
    loading.value = true;
    connectKospiWs();
  } else {
    fetchStocks();
  }
});

onUnmounted(() => {
  disconnectWs();
});

// ─── 포맷 유틸 (기존 그대로) ──────────────────────────────────────────────
const formatPrice = (price, market) => {
  if (market === 'kospi') {
    return new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' }).format(price);
  }
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(price);
};
</script>

<template>
  <div class="h-full flex flex-col p-6 border border-gray-200 bg-white hover:border-luxury-gold transition-colors duration-300">
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center gap-3">
        <h3 class="text-sm uppercase tracking-widest text-gray-500">Market Leaders</h3>
        <!-- KOSPI 실시간 연결 상태 표시 -->
        <span v-if="activeTab === 'kospi'" class="flex items-center gap-1 text-xs font-mono">
          <span
            class="inline-block w-1.5 h-1.5 rounded-full"
            :class="wsStatus === 'connected' ? 'bg-green-400' : 'bg-gray-300'"
          ></span>
          <span :class="wsStatus === 'connected' ? 'text-green-500' : 'text-gray-400'">
            {{ wsStatus === 'connected' ? 'LIVE' : 'Connecting...' }}
          </span>
        </span>
      </div>

      <div class="flex gap-2 text-xs">
        <button
          @click="activeTab = 'kospi'"
          class="px-3 py-1 border transition-colors uppercase tracking-wider"
          :class="activeTab === 'kospi' ? 'bg-black text-white border-black' : 'bg-white text-gray-400 border-gray-200 hover:border-gray-400'"
        >KOSPI</button>
        <button
          @click="activeTab = 'nasdaq'"
          class="px-3 py-1 border transition-colors uppercase tracking-wider"
          :class="activeTab === 'nasdaq' ? 'bg-black text-white border-black' : 'bg-white text-gray-400 border-gray-200 hover:border-gray-400'"
        >NASDAQ</button>
      </div>
    </div>

    <div class="h-[340px] overflow-auto">
      <div v-if="loading" class="h-full flex items-center justify-center text-gray-400 text-sm font-light">
        Loading Market Data...
      </div>

      <table v-else class="w-full text-sm">
        <thead>
          <tr class="text-gray-400 border-b border-gray-100 text-xs uppercase tracking-wider">
            <th class="text-left font-light py-2">Rank</th>
            <th class="text-center font-light py-2">Name</th>
            <th class="text-right font-light py-2">Price</th>
            <th class="text-right font-light py-2">Change</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="stock in stocks"
            :key="stock.symbol"
            class="border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors group"
          >
            <td class="py-3 font-mono text-gray-400 group-hover:text-luxury-gold">{{ stock.rank }}</td>
            <td class="py-3 font-medium">{{ stock.name }} <span class="text-xs text-gray-300 block font-normal">{{ stock.symbol }}</span></td>
            <td class="py-3 text-right font-mono">{{ formatPrice(stock.price, activeTab) }}</td>
            <td class="py-3 text-right font-mono font-medium" :class="stock.change >= 0 ? 'text-red-500' : 'text-blue-500'">
              {{ stock.change > 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
