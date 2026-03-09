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
import { ref, onMounted } from 'vue'
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

// Reactive Data
const chartData = ref({ labels: [], datasets: [] })
const goldData = ref({
    currentPrice: '-',
    changeRate: 0
})
const isLoading = ref(true);

const fetchGoldData = async () => {
    try {
        isLoading.value = true;
        const response = await api.get('/dashboard/gold');
        const data = response.data;
        console.log('[GoldWidget] Fetched data:', data);
        
        goldData.value = {
            currentPrice: new Intl.NumberFormat('ko-KR').format(data.currentPrice),
            changeRate: data.changeRate
        };

        const labels = data.history.labels;
        const domesticData = data.history.domestic;

        // Add padding (3 empty points) to show latest data point without cutoff
        for (let i = 0; i < 3; i++) {
            labels.push('');
            domesticData.push(null);
        }

        chartData.value = {
            labels: labels,
            datasets: [
                {
                    label: 'Domestic (KRW/g)',
                    borderColor: '#D4AF37', // Gold Color
                    backgroundColor: (context) => {
                        const ctx = context.chart.ctx;
                        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
                        gradient.addColorStop(0, 'rgba(212, 175, 55, 0.2)');
                        gradient.addColorStop(1, 'rgba(212, 175, 55, 0.0)');
                        return gradient;
                    },
                    data: domesticData,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                }
            ]
        }
    } catch (error) {
        console.error("Failed to fetch gold data:", error);
    } finally {
        isLoading.value = false;
    }
}

onMounted(() => {
    fetchGoldData();
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
        usePointStyle: true,
        boxWidth: 8, 
        color: '#9ca3af', 
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
        label: (context) => ` ${context.dataset.label}: ${new Intl.NumberFormat('ko-KR').format(context.raw)}`
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
      grid: {
        display: false,
        drawBorder: false
      },
      ticks: {
        font: { size: 10, family: 'monospace' },
        color: '#9ca3af',
        maxTicksLimit: 10
      },
      // Ensure min is calculated safely even if data is empty initially
      min: (ctx) => {
          const total = ctx.chart.data.labels.length;
          return total > 35 ? total - 35 : 0;
      }
    },
    y: {
      position: 'right', // Right side axis like Interest Chart
      grid: {
        color: '#f3f4f6',
        borderDash: [4, 4],
        drawBorder: false
      },
      ticks: {
        font: { size: 10, family: 'monospace' },
        color: '#9ca3af',
        callback: (value) => `₩${new Intl.NumberFormat('ko-KR', { notation: "compact" }).format(value)}`
      }
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
}

onMounted(() => {
    // Logic to fetch real gold data will go here
})

</script>

<template>
  <div class="h-full flex flex-col p-6 border border-gray-200 bg-white hover:border-luxury-gold transition-colors duration-300">
    <!-- Header -->
    <div class="flex justify-between items-end mb-6">
      <div>
        <h2 class="text-sm font-bold text-gray-400 tracking-widest uppercase mb-1">Commodities</h2>
        <h3 class="text-2xl font-light text-gray-900 tracking-tight">Gold Futures</h3>
      </div>
      
      <!-- Current Price Badge -->
      <!-- Current Price Badge -->
      <div class="text-right">
          <div class="text-2xl font-light tracking-tight text-[#D4AF37]">
              ₩{{ goldData.currentPrice }}<span class="text-sm text-gray-400">/g</span>
          </div>
          <div :class="goldData.changeRate >= 0 ? 'text-red-500' : 'text-blue-500'" class="text-xs font-mono font-medium">
              {{ goldData.changeRate >= 0 ? '▲' : '▼' }} {{ Math.abs(goldData.changeRate) }}%
          </div>
      </div>
    </div>

    <!-- Chart -->
    <div class="flex-1 w-full min-h-0">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>
