<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/index.js';

const props = defineProps({
  symbol: {
    type: String,
    required: true
  }
});

const investors = ref(null);
const frgnRatio = ref(null);
const loading = ref(true);

const fetchInvestors = async () => {
  loading.value = true;
  try {
    // 병렬 호출 시 KIS API Rate Limit 충돌 방지를 위해 순차 호출 및 약간의 딜레이 추가
    const invRes = await api.get(`/stock/${props.symbol}/investors`);
    investors.value = invRes.data;
    
    // Fundamental 컴포넌트의 DB 캐싱이 완료되기를 기다림 (0.5초)
    await new Promise(resolve => setTimeout(resolve, 500));
    
    try {
      const overRes = await api.get(`/stock/${props.symbol}/overview`);
      frgnRatio.value = overRes.data?.frgn_ratio || 0;
    } catch (e) {
      console.error("Overview fetch skipped or failed", e);
      frgnRatio.value = 0;
    }
  } catch (error) {
    console.error("Failed to fetch investor data:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchInvestors);

const formatVolume = (vol) => {
  if (vol === null || vol === undefined) return '-';
  const num = Number(vol);
  const formatted = Math.abs(num).toLocaleString('ko-KR');
  return `${num > 0 ? '+' : num < 0 ? '-' : ''}${formatted} 주`;
};
</script>

<template>
  <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm relative overflow-hidden">
    <!-- background glow -->
    <div class="absolute -bottom-10 -left-10 w-32 h-32 bg-sky-500/20 rounded-full blur-3xl pointer-events-none"></div>

    <h3 class="text-sm uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
      투자자 현황
    </h3>

    <div v-if="loading" class="animate-pulse h-16 bg-white/10 rounded w-full"></div>
    
    <div v-else class="flex flex-col gap-4">
      <!-- 외국인 지분율 바 -->
      <div class="flex items-center gap-3">
        <span class="text-xs text-slate-400 w-24">외국인 지분율</span>
        <div class="flex-1 bg-white/10 h-2 rounded-full overflow-hidden">
          <div class="bg-sky-400 h-full rounded-full" :style="{ width: `${frgnRatio}%` }"></div>
        </div>
        <span class="font-mono text-sm text-slate-200">{{ frgnRatio }}%</span>
      </div>

      <div class="border-t border-white/10 pt-4">
        <div class="text-xs text-slate-400 mb-3">당일 순매수 동향 (단위: 주)</div>
        <div class="grid grid-cols-3 gap-2">
          <div class="flex flex-col items-center bg-white/5 p-2 rounded">
            <span class="text-xs text-slate-500 mb-1">개인</span>
            <span class="font-mono text-sm" :class="investors?.retail > 0 ? 'text-red-400' : investors?.retail < 0 ? 'text-blue-400' : 'text-slate-300'">
              {{ formatVolume(investors?.retail) }}
            </span>
          </div>
          <div class="flex flex-col items-center bg-white/5 p-2 rounded">
            <span class="text-xs text-slate-500 mb-1">기관</span>
            <span class="font-mono text-sm" :class="investors?.institutional > 0 ? 'text-red-400' : investors?.institutional < 0 ? 'text-blue-400' : 'text-slate-300'">
              {{ formatVolume(investors?.institutional) }}
            </span>
          </div>
          <div class="flex flex-col items-center bg-white/5 p-2 rounded">
            <span class="text-xs text-slate-500 mb-1">외국인</span>
            <span class="font-mono text-sm" :class="investors?.foreign > 0 ? 'text-red-400' : investors?.foreign < 0 ? 'text-blue-400' : 'text-slate-300'">
              {{ formatVolume(investors?.foreign) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
