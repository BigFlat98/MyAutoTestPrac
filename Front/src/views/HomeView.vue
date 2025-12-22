<script setup>
import FearGreedIndex from '../components/dashboard/FearGreedIndex.vue'
import StockTopList from '../components/dashboard/StockTopList.vue'
import InterestRateChart from '../components/dashboard/InterestRateChart.vue'
import ExchangeRateChart from '../components/dashboard/ExchangeRateChart.vue'
</script>

<template>
  <div class="w-full max-w-[1400px] mx-auto px-6 pb-20">
    <header class="mb-12 text-left">
      <h1 class="text-4xl font-light tracking-tight text-black mb-2">
        Financial Overview
      </h1>
      <p class="text-gray-500 font-mono text-sm">
        Real-time market insights
      </p>
    </header>

    <!-- Dashboard Layout -->
    <div class="flex flex-col gap-6 h-[800px]">
      
      <!-- Top Row: 1:2 Ratio -->
      <div class="grid grid-cols-1 md:grid-cols-[1fr_2fr] gap-6 flex-1">
        <!-- Quadrant 1: Fear & Greed Index (Narrower) -->
        <FearGreedIndex />
        
        <!-- Quadrant 2: Stock Top 10 (Wider) -->
        <StockTopList />
      </div>

      <!-- Bottom Row: 1:1 Ratio -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1">
        <!-- Quadrant 3: Exchange Rate (Left) -->
        <ExchangeRateChart />
        
        <!-- Quadrant 4: Interest Rates (Right) -->
        <InterestRateChart />
      </div>
      
    </div>
  </div>
</template>