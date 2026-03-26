<script setup>
import FearGreedIndex from '../components/dashboard/FearGreedIndex.vue'
import StockTopList from '../components/dashboard/StockTopList.vue'
import InterestRateChart from '../components/dashboard/InterestRateChart.vue'
import ExchangeRateChart from '../components/dashboard/ExchangeRateChart.vue'
import BitcoinChart from '../components/dashboard/BitcoinChart.vue'
import GoldChart from '../components/dashboard/GoldChart.vue'
import OilChart from '../components/dashboard/OilChart.vue'
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
    <div class="flex flex-col gap-6">
      
      <!-- Top Row: 1:2 Ratio -->
      <div class="grid grid-cols-1 md:grid-cols-[1fr_2fr] gap-6 h-[460px]">
        <FearGreedIndex />
        <StockTopList />
      </div>

      <!-- Middle Row: 1:1 Ratio -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 h-[300px]">
        <ExchangeRateChart />
        <InterestRateChart />
      </div>

      <!-- Bottom Row: Oil & Gold -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 h-[460px]">
        <OilChart />
        <GoldChart />
      </div>

      <!-- Crypto Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 h-[460px]">
        <BitcoinChart />
      </div>
      
    </div>
  </div>
</template>