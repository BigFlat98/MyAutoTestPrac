<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from '@/api';

const score = ref(0);
const rating = ref('');
const timestamp = ref('');

const fetchData = async () => {
  try {
    // Fetch data from our backend
    const response = await api.get("/dashboard/fear-greed");
    
    if (response.data) {
      score.value = response.data.score;
      rating.value = response.data.rating;
      timestamp.value = response.data.timestamp;
    }
  } catch (error) {
    console.error("Failed to fetch Fear & Greed Index:", error);
    // Fallback or error state could be handled here
  }
};

onMounted(() => {
  fetchData();
});

const status = computed(() => {
  // Use API rating if available, otherwise fallback to score-based logic
  if (rating.value) return rating.value;
  
  if (score.value <= 25) return 'Extreme Fear';
  if (score.value <= 45) return 'Fear';
  if (score.value <= 55) return 'Neutral';
  if (score.value <= 75) return 'Greed';
  return 'Extreme Greed';
});

const rotation = computed(() => {
  // Map 0-100 to -90deg to 90deg
  return (score.value / 100) * 180 - 90;
});

const colorClass = computed(() => {
  if (score.value <= 25) return 'text-green-700';      // Extreme Fear -> Green (Opportunity)
  if (score.value <= 45) return 'text-emerald-500';    // Fear -> Emerald
  if (score.value <= 55) return 'text-gray-500';       // Neutral
  if (score.value <= 75) return 'text-orange-500';     // Greed -> Orange
  return 'text-red-600';                               // Extreme Greed -> Red (Danger)
});
</script>

<template>
  <div class="h-full flex flex-col p-6 border border-gray-200 bg-white hover:border-luxury-gold transition-colors duration-300 relative overflow-hidden group">
    <div class="absolute top-0 right-0 p-4 opacity-10 font-[Pinyon_Script] text-6xl pointer-events-none select-none">
      F&G
    </div>
    
    <h3 class="text-xs uppercase tracking-[0.2em] text-gray-400 mb-1">Market Sentiment</h3>
    <h2 class="text-xl font-light mb-8">Fear & Greed Index</h2>
    
    <div class="flex-1 flex flex-col items-center pt-8 relative">
      <!-- Semi-Circle Gauge -->
      <div class="relative w-64 h-32 overflow-hidden mb-2">
        <div class="absolute w-64 h-64 rounded-full border-[12px] border-gray-100 box-border"></div>
        <div 
          class="absolute w-64 h-64 rounded-full border-[12px] border-transparent border-t-emerald-500 box-border transition-transform duration-1000 ease-out origin-center"
          :style="{ transform: `rotate(${rotation}deg)` }"
          :class="[
            score <= 25 ? '!border-t-green-700' : 
            score <= 45 ? '!border-t-emerald-500' : 
            score <= 55 ? '!border-t-gray-400' : 
            score <= 75 ? '!border-t-orange-500' : '!border-t-red-600'
          ]"
        ></div>
        <!-- Needle Base -->
        <div class="absolute bottom-0 left-1/2 -translate-x-1/2 w-full h-1 bg-white z-10"></div>
      </div>
      
      <!-- Score Text -->
      <div class="flex flex-col items-center mt-2">
        <span class="text-4xl font-light font-mono tracking-tighter" :class="colorClass">{{ score }}</span>
        <span class="text-sm uppercase tracking-widest mt-1 font-medium" :class="colorClass">{{ status }}</span>
      </div>
      
      <p class="text-[0.6rem] text-gray-300 mt-auto mb-0 font-light font-mono">
        Last updated: {{ timestamp ? new Date(timestamp).toLocaleDateString() : 'Loading...' }}
      </p>
    </div>
  </div>
</template>
