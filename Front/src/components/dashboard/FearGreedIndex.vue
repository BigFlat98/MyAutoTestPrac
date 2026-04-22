<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from '@/api';

const score = ref(0);
const rating = ref('');
const timestamp = ref('');

const fetchData = async () => {
  try {
    const response = await api.get("/dashboard/fear-greed");
    if (response.data) {
      score.value = response.data.score;
      rating.value = response.data.rating;
      timestamp.value = response.data.timestamp;
    }
  } catch (error) {
    console.error("Failed to fetch Fear & Greed Index:", error);
  }
};

onMounted(() => {
  fetchData();
});

const status = computed(() => {
  if (rating.value) return rating.value;
  if (score.value <= 25) return 'Extreme Fear';
  if (score.value <= 45) return 'Fear';
  if (score.value <= 55) return 'Neutral';
  if (score.value <= 75) return 'Greed';
  return 'Extreme Greed';
});

const rotation = computed(() => {
  return (score.value / 100) * 180 - 90;
});

const colorClass = computed(() => {
  if (score.value <= 25) return 'text-sky-400';        
  if (score.value <= 45) return 'text-sky-300';    
  if (score.value <= 55) return 'text-slate-400';       
  if (score.value <= 75) return 'text-orange-400';     
  return 'text-red-500';                               
});
</script>

<template>
  <div class="glass-card h-full flex flex-col relative overflow-hidden group">
    <div class="absolute top-0 right-0 p-4 opacity-10 font-[Pinyon_Script] text-6xl pointer-events-none select-none text-white">
      F&G
    </div>
    
    <h3 class="text-xs uppercase tracking-[0.2em] text-slate-400 mb-1">Market Sentiment</h3>
    <h2 class="text-xl font-light text-slate-100 mb-8">Fear & Greed Index</h2>
    
    <div class="flex-1 flex flex-col items-center pt-8 relative">
      <!-- Semi-Circle Gauge -->
      <div class="relative w-64 h-32 overflow-hidden mb-2">
        <div class="absolute w-64 h-64 rounded-full border-[12px] border-white/5 box-border"></div>
        <div 
          class="absolute w-64 h-64 rounded-full border-[12px] border-transparent border-t-emerald-500 box-border transition-transform duration-1000 ease-out origin-center drop-shadow-[0_0_15px_rgba(52,211,153,0.5)]"
          :style="{ transform: `rotate(${rotation}deg)` }"
          :class="[
            score <= 25 ? '!border-t-sky-400 drop-shadow-[0_0_15px_rgba(56,189,248,0.5)]' : 
            score <= 45 ? '!border-t-sky-300' : 
            score <= 55 ? '!border-t-slate-400 drop-shadow-none' : 
            score <= 75 ? '!border-t-orange-400' : '!border-t-red-500 drop-shadow-[0_0_15px_rgba(239,68,68,0.5)]'
          ]"
        ></div>
        <!-- Needle Base -->
        <div class="absolute bottom-0 left-1/2 -translate-x-1/2 w-full h-1 bg-white/50 z-10"></div>
      </div>
      
      <!-- Score Text -->
      <div class="flex flex-col items-center mt-2">
        <span class="text-4xl font-light font-mono tracking-tighter drop-shadow-md" :class="colorClass">{{ score }}</span>
        <span class="text-sm uppercase tracking-widest mt-1 font-medium" :class="colorClass">{{ status }}</span>
      </div>
      
      <p class="text-[0.6rem] text-slate-500 mt-auto mb-0 font-light font-mono">
        Last updated: {{ timestamp ? new Date(timestamp).toLocaleDateString() : 'Loading...' }}
      </p>
    </div>
  </div>
</template>
