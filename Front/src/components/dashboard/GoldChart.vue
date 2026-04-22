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

const chartData = ref({ labels: [], datasets: [] })
const goldData = ref({ currentPrice: '-', changeRate: 0 })
const isLoading = ref(true);

const fetchGoldData = async () => {
    try {
        isLoading.value = true;
        const response = await api.get('/dashboard/gold');
        const data = response.data;
        
        goldData.value = {
            currentPrice: new Intl.NumberFormat('ko-KR').format(data.currentPrice),
            changeRate: data.changeRate
        };

        const labels = data.history.labels;
        const domesticData = data.history.domestic;

        for (let i = 0; i < 3; i++) {
            labels.push('');
            domesticData.push(null);
        }

        chartData.value = {
            labels: labels,
            datasets: [
                {
                    label: 'Domestic (KRW/g)',
                    borderColor: '#D4AF37',
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
  layout: { padding: { right: 40 } },
  plugins: {
    legend: {
      display: true,
      align: 'end',
      labels: { usePointStyle: true, boxWidth: 8, color: '#94a3b8', font: { size: 10 } }
    },
    tooltip: {
      mode: 'index',
      intersect: false,
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      titleColor: '#f8fafc',
      bodyColor: '#cbd5e1',
      borderColor: 'rgba(255,255,255,0.1)',
      borderWidth: 1,
      padding: 10,
      callbacks: {
        label: (context) => ` ${context.dataset.label}: ${new Intl.NumberFormat('ko-KR').format(context.raw)}`
      }
    },
    zoom: {
        zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' },
        pan: { enabled: true, mode: 'x' },
        limits: { x: { min: 0, max: 'original' } }
    }
  },
  scales: {
    x: {
      display: true,
      grid: { display: false, drawBorder: false },
      ticks: { font: { size: 10, family: 'monospace' }, color: '#94a3b8', maxTicksLimit: 10 },
      min: (ctx) => {
          const total = ctx.chart.data.labels.length;
          return total > 35 ? total - 35 : 0;
      }
    },
    y: {
      position: 'right',
      grid: { color: 'rgba(255, 255, 255, 0.05)', borderDash: [4, 4], drawBorder: false },
      ticks: {
        font: { size: 10, family: 'monospace' },
        color: '#94a3b8',
        callback: (value) => `₩${new Intl.NumberFormat('ko-KR', { notation: "compact" }).format(value)}`
      }
    }
  },
  interaction: { mode: 'nearest', axis: 'x', intersect: false }
}
</script>

<template>
  <div class="glass-card h-full flex flex-col">
    <div class="flex justify-between items-end mb-6">
      <div>
        <h2 class="text-sm font-bold text-slate-400 tracking-widest uppercase mb-1">Commodities</h2>
        <h3 class="text-2xl font-light text-slate-100 tracking-tight">Gold Futures</h3>
      </div>
      
      <div class="text-right">
          <div class="text-2xl font-light tracking-tight text-[#D4AF37]">
              ₩{{ goldData.currentPrice }}<span class="text-sm text-slate-400">/g</span>
          </div>
          <div :class="goldData.changeRate >= 0 ? 'text-red-400' : 'text-blue-400'" class="text-xs font-mono font-medium">
              {{ goldData.changeRate >= 0 ? '▲' : '▼' }} {{ Math.abs(goldData.changeRate) }}%
          </div>
      </div>
    </div>

    <div class="flex-1 w-full min-h-0">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>
