<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/index.js';

const props = defineProps({
  symbol: {
    type: String,
    required: true
  }
});

const fundamental = ref(null);
const loading = ref(true);

const fetchFundamental = async () => {
  loading.value = true;
  try {
    const res = await api.get(`/stock/${props.symbol}/overview`);
    fundamental.value = res.data;
  } catch (error) {
    console.error("Failed to fetch fundamental data:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchFundamental);

const formatNumber = (num, digits = 2) => {
  if (num === null || num === undefined) return '-';
  return Number(num).toLocaleString('ko-KR', { minimumFractionDigits: digits, maximumFractionDigits: digits });
};

const formatMarketCap = (num) => {
  if (!num) return '-';
  return Math.round(num).toLocaleString('ko-KR') + ' 억';
};
</script>

<template>
  <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm relative overflow-hidden">
    <!-- background glow -->
    <div class="absolute -top-10 -right-10 w-32 h-32 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none"></div>

    <h3 class="text-sm uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      재무 지표
    </h3>
    
    <div v-if="loading" class="animate-pulse flex flex-col gap-3">
      <div class="h-4 bg-white/10 rounded w-3/4"></div>
      <div class="h-4 bg-white/10 rounded w-1/2"></div>
      <div class="h-4 bg-white/10 rounded w-5/6"></div>
    </div>
    
    <div v-else-if="fundamental" class="grid grid-cols-2 sm:grid-cols-3 gap-4">
      <div class="flex flex-col">
        <span class="text-xs text-slate-500 mb-1">PER</span>
        <span class="font-mono text-slate-200">{{ formatNumber(fundamental.per) }} 배</span>
      </div>
      <div class="flex flex-col">
        <span class="text-xs text-slate-500 mb-1">PBR</span>
        <span class="font-mono text-slate-200">{{ formatNumber(fundamental.pbr) }} 배</span>
      </div>
      <div class="flex flex-col">
        <span class="text-xs text-slate-500 mb-1">EPS</span>
        <span class="font-mono text-slate-200">{{ formatNumber(fundamental.eps, 0) }} 원</span>
      </div>
      <div class="flex flex-col">
        <span class="text-xs text-slate-500 mb-1">시가총액</span>
        <span class="font-mono text-slate-200">{{ formatMarketCap(fundamental.market_cap) }}</span>
      </div>
      <div class="flex flex-col">
        <span class="text-xs text-slate-500 mb-1">52주 최고</span>
        <span class="font-mono text-slate-200">{{ formatNumber(fundamental.w52_high, 0) }} 원</span>
      </div>
      <div class="flex flex-col">
        <span class="text-xs text-slate-500 mb-1">52주 최저</span>
        <span class="font-mono text-slate-200">{{ formatNumber(fundamental.w52_low, 0) }} 원</span>
      </div>
      <!-- 추가된 필드 -->
      <div class="flex flex-col">
        <span class="text-xs text-slate-500 mb-1">영업이익</span>
        <span class="font-mono text-slate-200">{{ fundamental.operating_profit > 0 ? formatMarketCap(fundamental.operating_profit) : '-' }}</span>
      </div>
      <div class="flex flex-col">
        <span class="text-xs text-slate-500 mb-1">부채비율</span>
        <span class="font-mono text-slate-200">{{ fundamental.debt_ratio > 0 ? formatNumber(fundamental.debt_ratio) + ' %' : '-' }}</span>
      </div>
    </div>
    
    <div v-else class="text-sm text-slate-500">데이터를 불러오지 못했습니다.</div>
  </div>
</template>
