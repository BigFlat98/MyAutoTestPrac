<script setup>
import { ref, onMounted, watch } from 'vue';
import { api } from '@/api/index.js';

const activeTab = ref('kospi');
const stocks = ref([]);
const loading = ref(false);

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

watch(activeTab, () => {
  stocks.value = []; // Clear list on switch
  fetchStocks();
});

onMounted(() => {
  fetchStocks();
});

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
      <h3 class="text-sm uppercase tracking-widest text-gray-500">Market Leaders</h3>
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
          <tr v-for="stock in stocks" :key="stock.symbol" class="border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors group">
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
