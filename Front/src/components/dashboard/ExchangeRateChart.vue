<script setup>
import { ref, onMounted } from 'vue';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Line } from 'vue-chartjs';
import { api } from '@/api/index.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const chartData = ref({ labels: [], datasets: [] });
const chartContainer = ref(null);
const totalLabels = ref(0);

const yMin = ref(0);
const yMax = ref(1500);

const currentRate = ref(null);
const changeRate = ref(null);

const mainChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  elements: { point: { radius: 0, hitRadius: 10 }, line: { tension: 0.1 } },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      titleColor: '#f8fafc',
      bodyColor: '#cbd5e1',
      borderColor: 'rgba(255,255,255,0.1)',
      borderWidth: 1,
      callbacks: { label: (ctx) => ` ₩${ctx.parsed.y.toLocaleString()}` }
    }
  },
  scales: {
    x: { 
      display: true,
      offset: true,
      grid: { display: false },
      ticks: {
        maxTicksLimit: 60,
        maxRotation: 0,
        color: '#94a3b8',
        callback: function(val) {
          const dateStr = this.getLabelForValue(val);
          const date = new Date(dateStr);
          return `${date.getFullYear().toString().slice(2)}.${(date.getMonth() + 1).toString().padStart(2, '0')}`;
        },
        font: { family: 'monospace', size: 10 }
      }
    }, 
    y: { 
      display: true,
      position: 'right', 
      min: 0, 
      max: 1500,
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
      ticks: { color: '#94a3b8', font: { family: 'monospace', size: 10 } }
    } 
  }
});

const fetchData = async () => {
  try {
    const res = await api.get('/dashboard/exchange-rate');
    totalLabels.value = res.data.dates.length;

    if (res.data.dates.length > 0) {
        const lastDate = new Date(res.data.dates[res.data.dates.length - 1]);
        for (let i = 1; i <= 5; i++) {
            const nextDate = new Date(lastDate);
            nextDate.setMonth(lastDate.getMonth() + i);
            res.data.dates.push(nextDate.toISOString().split('T')[0]);
        }
    }

    const validRates = res.data.rates.filter(r => r !== null);
    if (validRates.length >= 2) {
      currentRate.value = validRates[validRates.length - 1];
      const prev = validRates[validRates.length - 2];
      changeRate.value = parseFloat(((currentRate.value - prev) / prev * 100).toFixed(2));
    } else if (validRates.length === 1) {
      currentRate.value = validRates[0];
    }

    const rates = res.data.rates.filter(r => r !== null);
    const minVal = Math.min(...rates);
    const maxVal = Math.max(...rates);
    const padding = (maxVal - minVal) * 0.1;

    yMin.value = Math.floor(minVal - padding);
    yMax.value = Math.ceil(maxVal + padding);

    mainChartOptions.value.scales.y.min = yMin.value;
    mainChartOptions.value.scales.y.max = yMax.value;

    chartData.value = {
      labels: res.data.dates,
      datasets: [
        {
          label: 'USD/KRW',
          backgroundColor: '#34d399', 
          borderColor: '#34d399',
          data: res.data.rates, 
          borderWidth: 1.5,
          fill: false
        }
      ]
    };
    
    setTimeout(() => {
        if (chartContainer.value) {
            chartContainer.value.scrollLeft = chartContainer.value.scrollWidth;
        }
    }, 100);

  } catch (e) {
    console.error("Failed to load exchange rates", e);
  }
};

onMounted(fetchData);
</script>

<template>
  <div class="glass-card h-full flex flex-col">
    <div class="flex justify-between items-start mb-4">
      <div>
        <h3 class="text-xs uppercase tracking-widest text-slate-400 mb-1">Exchange Rate</h3>
        <div class="flex items-baseline gap-2">
          <span class="text-2xl font-light text-slate-100 tracking-tight font-mono">
            {{ currentRate ? currentRate.toLocaleString('ko-KR') : '—' }}
          </span>
          <span class="text-xs text-slate-400">KRW</span>
        </div>
        <div v-if="changeRate !== null" class="flex items-center gap-1 mt-0.5">
          <span :class="changeRate >= 0 ? 'text-red-400' : 'text-blue-400'" class="text-xs font-mono font-medium">
            {{ changeRate >= 0 ? '▲' : '▼' }} {{ Math.abs(changeRate) }}%
          </span>
          <span class="text-[10px] text-slate-500">vs prev day</span>
        </div>
      </div>
      <div class="flex items-center gap-1 text-[10px] font-mono text-slate-400 mt-1">
        <span class="w-3 h-[2px] bg-[#34d399] inline-block"></span>
        <span>USD / KRW</span>
      </div>
    </div>
    
    <div class="flex-1 min-h-0 flex relative">
      <div ref="chartContainer" class="flex-1 overflow-x-auto overflow-y-hidden custom-scrollbar relative z-10">
         <div :style="{ width: Math.max(100, (totalLabels / 500) * 100) + '%' }" class="h-full min-w-full">
            <Line v-if="chartData.datasets.length > 0" :data="chartData" :options="mainChartOptions" />
            <div v-else class="h-full flex items-center justify-center text-slate-500">Loading Data...</div>
         </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { height: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.3); }
</style>
