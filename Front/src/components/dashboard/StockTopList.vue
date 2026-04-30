<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { api } from '@/api/index.js';

const activeTab  = ref('kospi');
const stocks     = ref([]);
const loading    = ref(false);
const wsStatus   = ref('disconnected');

let ws = null;

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

const connectKospiWs = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const url      = `${protocol}//${window.location.host}/kstock/ws`;

  wsStatus.value = 'connecting';
  ws = new WebSocket(url);

  ws.onopen = () => { wsStatus.value = 'connected'; };
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
  ws.onerror = () => { wsStatus.value = 'disconnected'; loading.value  = false; };
  ws.onclose = () => { wsStatus.value = 'disconnected'; };
};

const disconnectWs = () => {
  if (ws) {
    ws.close();
    ws = null;
  }
  wsStatus.value = 'disconnected';
};

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

const formatPrice = (price, market) => {
  if (market === 'kospi') {
    return new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' }).format(price);
  }
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(price);
};
</script>

<template>
  <div class="glass-card h-full flex flex-col">
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center gap-3">
        <h3 class="text-sm uppercase tracking-widest text-slate-400">Market Leaders</h3>
        <span v-if="activeTab === 'kospi'" class="flex items-center gap-1 text-xs font-mono">
          <span
            class="inline-block w-1.5 h-1.5 rounded-full"
            :class="wsStatus === 'connected' ? 'bg-emerald-400' : 'bg-slate-500'"
          ></span>
          <span :class="wsStatus === 'connected' ? 'text-emerald-400' : 'text-slate-500'">
            {{ wsStatus === 'connected' ? 'LIVE' : 'Connecting...' }}
          </span>
        </span>
      </div>

      <div class="flex gap-2 text-xs">
        <button
          @click="activeTab = 'kospi'"
          class="px-3 py-1 border transition-colors uppercase tracking-wider rounded backdrop-blur-sm"
          :class="activeTab === 'kospi' ? 'bg-white/20 text-white border-white/30' : 'bg-transparent text-slate-400 border-white/10 hover:border-white/30'"
        >KOSPI</button>
        <button
          @click="activeTab = 'nasdaq'"
          class="px-3 py-1 border transition-colors uppercase tracking-wider rounded backdrop-blur-sm"
          :class="activeTab === 'nasdaq' ? 'bg-white/20 text-white border-white/30' : 'bg-transparent text-slate-400 border-white/10 hover:border-white/30'"
        >NASDAQ</button>
      </div>
    </div>

    <div class="h-[340px] overflow-auto custom-scrollbar">
      <div v-if="loading" class="h-full flex items-center justify-center text-slate-400 text-sm font-light">
        Loading Market Data...
      </div>

      <table v-else class="w-full text-sm">
        <thead>
          <tr class="text-slate-400 border-b border-white/10 text-xs uppercase tracking-wider">
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
            @click="$emit('select', stock)"
            class="border-b border-white/5 last:border-0 hover:bg-white/10 transition-colors group cursor-pointer"
          >
            <td class="py-3 font-mono text-slate-400 group-hover:text-sky-300 px-2">{{ stock.rank }}</td>
            <td class="py-3 font-medium text-slate-100">{{ stock.name }} <span class="text-xs text-slate-500 block font-normal">{{ stock.symbol }}</span></td>
            <td class="py-3 text-right font-mono text-slate-200">{{ formatPrice(stock.price, activeTab) }}</td>
            <td class="py-3 text-right font-mono font-medium px-2" :class="stock.change >= 0 ? 'text-red-400' : 'text-blue-400'">
              {{ stock.change > 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.3); }
</style>
