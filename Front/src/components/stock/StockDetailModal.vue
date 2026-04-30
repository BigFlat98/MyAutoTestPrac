<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import StockModalFundamental from './StockModalFundamental.vue';
import StockModalInvestors from './StockModalInvestors.vue';
import StockModalNews from './StockModalNews.vue';

const props = defineProps({
  stockInfo: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close']);

const closeOnEsc = (e) => {
  if (e.key === 'Escape') {
    emit('close');
  }
};

onMounted(() => {
  window.addEventListener('keydown', closeOnEsc);
  document.body.style.overflow = 'hidden'; // prevent background scrolling
});

onUnmounted(() => {
  window.removeEventListener('keydown', closeOnEsc);
  document.body.style.overflow = '';
});

const formatPrice = (price) => {
  return new Intl.NumberFormat('ko-KR').format(price);
};
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div 
          class="absolute inset-0 bg-black/40 backdrop-blur-sm" 
          @click="emit('close')"
        ></div>

        <!-- Modal Wrapper -->
        <div class="relative w-full max-w-2xl">
          <!-- Modal Content -->
          <div 
            class="glass-card w-full max-h-[90vh] overflow-y-auto custom-scrollbar flex flex-col shadow-2xl border border-white/20 relative"
          >
          
          <!-- Header (Sticky) -->
          <div class="glass-header relative sticky top-0 z-10 p-6 border-b border-white/10 bg-black/50 backdrop-blur-md">
            <!-- 왼쪽: 제목 및 가격 정보 -->
            <div>
              <div class="flex items-center gap-3">
                <h2 class="text-2xl font-semibold text-slate-100">{{ stockInfo.name }}</h2>
                <span class="text-sm text-slate-400 font-mono">{{ stockInfo.symbol }}</span>
              </div>
              <div class="mt-2 flex items-baseline gap-3">
                <span class="text-3xl font-mono text-white">₩ {{ formatPrice(stockInfo.price) }}</span>
                <span 
                  class="font-mono text-lg" 
                  :class="stockInfo.change >= 0 ? 'text-red-400' : 'text-blue-400'"
                >
                  {{ stockInfo.change > 0 ? '▲' : '▼' }} {{ stockInfo.change > 0 ? '+' : '' }}{{ stockInfo.change.toFixed(2) }}%
                </span>
              </div>
            </div>

            <!-- 오른쪽: X 닫기 버튼 (헤더 내부 우측 상단 절대 위치 고정) -->
            <button 
              @click="emit('close')" 
              class="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-md bg-red-500/20 hover:bg-red-500/40 text-red-200 hover:text-white border border-red-500/30 transition-all backdrop-blur-md z-20"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Body -->
          <div class="p-6 flex flex-col gap-6">
            <StockModalFundamental :symbol="stockInfo.symbol" />
            <StockModalInvestors :symbol="stockInfo.symbol" />
            <StockModalNews :stockName="stockInfo.name" />
            
            <!-- Links Section -->
            <div class="mt-4 flex gap-3">
              <a 
                :href="`https://finance.naver.com/item/main.naver?code=${stockInfo.symbol}`" 
                target="_blank" 
                class="flex-1 py-3 text-center rounded-lg bg-green-500/20 text-green-400 border border-green-500/30 hover:bg-green-500/30 transition-colors font-medium text-sm"
              >
                네이버 증권 바로가기
              </a>
              <a 
                :href="`https://kr.tradingview.com/chart/?symbol=KRX:${stockInfo.symbol}`" 
                target="_blank" 
                class="flex-1 py-3 text-center rounded-lg bg-blue-500/20 text-blue-400 border border-blue-500/30 hover:bg-blue-500/30 transition-colors font-medium text-sm"
              >
                TradingView 차트 보기
              </a>
            </div>
          </div>
        </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.4); }
</style>
