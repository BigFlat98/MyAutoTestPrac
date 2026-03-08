<script setup>
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import zoomPlugin from 'chartjs-plugin-zoom'
import { Line } from 'vue-chartjs'
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { api } from '@/api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  zoomPlugin
)

// Coin Configurations
const coins = {
    BTC: { name: 'Bitcoin', symbol: 'BTC', color: '#F7931A' },
    ETH: { name: 'Ethereum', symbol: 'ETH', color: '#627EEA' },
    XRP: { name: 'Ripple', symbol: 'XRP', color: '#23292F' }
}

const selectedCoinKey = ref('BTC');
const isDropdownOpen = ref(false);
const isLoading = ref(false);

const toggleDropdown = () => {
    isDropdownOpen.value = !isDropdownOpen.value;
}

const selectCoin = (key) => {
    selectedCoinKey.value = key;
    isDropdownOpen.value = false;
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
    const dropdown = document.querySelector('.custom-dropdown-container');
    if (dropdown && !dropdown.contains(event.target)) {
        isDropdownOpen.value = false;
    }
}

// Reactive Data
const chartData = ref({ labels: [], datasets: [] });
const coinData = ref({
    krwPrice: '-',
    usdPrice: '-',
    changeRate: 0,
    kimchiPremium: 0,
});

// Fetch Real Data
const updateChart = async () => {
    const coinKey = selectedCoinKey.value;
    const coinConfig = coins[coinKey];
    
    isLoading.value = true;
    
    try {
        const response = await api.get(`/dashboard/crypto/${coinKey}`);
        const data = response.data;
        console.log(`[CryptoWidget] Fetched data for ${coinKey}:`, data);
        
        // Update Coin Info
        coinData.value = {
            krwPrice: new Intl.NumberFormat('ko-KR').format(data.krwPrice),
            usdPrice: new Intl.NumberFormat('en-US').format(data.usdPrice),
            changeRate: data.changeRate, // Percentage
            kimchiPremium: data.kimchiPremium
        };

        const labels = data.history.labels;
        const upbitPrices = data.history.upbit;
        const binancePrices = data.history.binance; 

        // Add padding (3 empty points)
        for (let i = 0; i < 3; i++) {
            labels.push('');
            upbitPrices.push(null);
            binancePrices.push(null);
        }

        chartData.value = {
            labels: labels,
            datasets: [
                {
                    label: `Upbit (KRW)`,
                    borderColor: coinConfig.color,
                    backgroundColor: `${coinConfig.color}1A`, // 10% opacity
                    data: upbitPrices,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    pointHoverRadius: 4
                },
                {
                    label: `Binance (KRW)`,
                    borderColor: '#9CA3AF',
                    backgroundColor: 'transparent',
                    data: binancePrices,
                    borderWidth: 1,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.3,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }
            ]
        };

    } catch (error) {
        console.error("Failed to fetch crypto data:", error);
    } finally {
        isLoading.value = false;
    }
}

// Watch for selection change
watch(selectedCoinKey, () => {
    updateChart();
});

onMounted(() => {
    updateChart();
    document.addEventListener('click', handleClickOutside);
})

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside);
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  layout: {
    padding: {
        right: 40 // Space for latest value visibility
    }
  },
  plugins: {
    legend: { 
        display: true,
        align: 'end',
        labels: {
            boxWidth: 8,
            usePointStyle: true,
            font: { size: 10 }
        }
    },
    tooltip: {
      mode: 'index',
      intersect: false,
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      titleColor: '#111827',
      bodyColor: '#4b5563',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      padding: 10,
      callbacks: {
        label: (context) => {
           if (context.raw === null) return null;
           return `${context.dataset.label}: ` + new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' }).format(context.raw);
        }
      }
    },
    zoom: {
        zoom: {
            wheel: { enabled: true },
            pinch: { enabled: true },
            mode: 'x',
        },
        pan: {
            enabled: true,
            mode: 'x',
        },
        limits: {
            x: { min: 0, max: 'original' }
        }
    }
  },
  scales: {
    x: {
      display: true,
      grid: { display: false },
       ticks: {
        font: { size: 10, family: 'monospace' },
        color: '#9ca3af',
        maxTicksLimit: 10 // Show fewer ticks to avoid clutter
      },
      min: (ctx) => {
          const total = ctx.chart.data.labels.length;
          return total > 35 ? total - 35 : 0;
      }
    },
    y: {
      display: false, // Hide Y axis for cleaner look like stock cards
    }
  },
  interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
  }
}
</script>

<template>
  <div class="bg-white p-8 border border-gray-100 shadow-sm hover:shadow-md transition-shadow duration-300 h-full flex flex-col relative group">
    <!-- Header -->
    <div class="flex justify-between items-start mb-6 z-20 w-full">
      <div class="flex-1 relative custom-dropdown-container">
        <h2 class="text-sm font-bold text-gray-400 tracking-widest uppercase mb-1">Crypto Asset</h2>
        
        <!-- Custom Dropdown Trigger -->
        <div 
            @click="toggleDropdown"
            class="flex items-center gap-2 cursor-pointer group w-fit"
        >
            <h3 class="text-3xl font-light text-gray-900 tracking-tight group-hover:text-gray-600 transition-colors">
                {{ coins[selectedCoinKey].name }}
            </h3>
            <span class="text-base text-gray-400 font-normal mt-2">{{ coins[selectedCoinKey].symbol }}</span>
            <svg 
                class="w-4 h-4 text-gray-400 mt-2 transition-transform duration-300" 
                :class="{ 'rotate-180': isDropdownOpen }"
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
        </div>

        <!-- Dropdown Menu -->
        <transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="transform scale-95 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-75 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-95 opacity-0"
        >
            <div 
                v-if="isDropdownOpen"
                class="absolute top-full left-0 mt-2 w-48 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50"
            >
                <ul>
                    <li 
                        v-for="(coin, key) in coins" 
                        :key="key"
                        @click="selectCoin(key)"
                        class="px-4 py-3 hover:bg-gray-50 cursor-pointer flex items-center justify-between group transition-colors"
                        :class="{ 'bg-gray-50': selectedCoinKey === key }"
                    >
                        <span class="font-light text-gray-800" :class="{ 'font-medium': selectedCoinKey === key }">{{ coin.name }}</span>
                        <span class="text-xs text-gray-400 font-mono group-hover:text-gray-600">{{ coin.symbol }}</span>
                    </li>
                </ul>
            </div>
        </transition>

      </div>
      <!-- Icon -->
      <div 
        class="w-10 h-10 rounded-full flex items-center justify-center transition-colors duration-300"
        :style="{ backgroundColor: `${coins[selectedCoinKey].color}1A`, color: coins[selectedCoinKey].color }"
      >
         <span class="font-bold text-xs tracking-tighter">{{ selectedCoinKey }}</span>
      </div>
    </div>

    <!-- Main Price Info -->
    <div class="flex items-end gap-4 mb-8 z-10">
        <span class="text-4xl font-extralight text-black tracking-tighter">
            ₩{{ coinData.krwPrice }}
        </span>
        <div class="flex flex-col mb-1">
            <span :class="coinData.changeRate >= 0 ? 'text-red-500' : 'text-blue-500'" class="text-sm font-medium flex items-center">
                {{ coinData.changeRate >= 0 ? '▲' : '▼' }} {{ Math.abs(coinData.changeRate) }}%
            </span>
             <span class="text-xs text-gray-400">vs yesterday</span>
        </div>
    </div>

    <!-- Kimchi Premium Badge -->
    <div class="absolute top-8 right-24 bg-gray-50 px-3 py-1 rounded-full border border-gray-100 flex items-center gap-2">
        <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Kimchi Prem.</span>
        <span :class="coinData.kimchiPremium >= 0 ? 'text-red-500' : 'text-blue-500'" class="text-xs font-bold font-mono">
            {{ coinData.kimchiPremium > 0 ? '+' : ''}}{{ coinData.kimchiPremium }}%
        </span>
    </div>

    <!-- Chart Area -->
    <div class="flex-1 w-full min-h-[200px] relative">
      <Line :data="chartData" :options="chartOptions" />
    </div>

  </div>
</template>
