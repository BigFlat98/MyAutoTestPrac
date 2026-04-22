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
  Legend,
  Filler
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
  Legend,
  Filler
);

const chartData = ref({ labels: [], datasets: [] });
const chartContainer = ref(null);
const totalLabels = ref(0);

const yMin = ref(0);
const yMax = ref(10);

const currentYield = ref(null);
const changeRate = ref(null);

const mainChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  elements: { point: { radius: 0, hitRadius: 10 }, line: { tension: 0.1 } },
  plugins: {
    legend: { display: false },
    tooltip: { 
      enabled: true,
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      titleColor: '#f8fafc',
      bodyColor: '#cbd5e1',
      borderColor: 'rgba(255,255,255,0.1)',
      borderWidth: 1
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
          if(!dateStr) return '';
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
      max: 10,
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
      ticks: { color: '#94a3b8', font: { family: 'monospace', size: 10 } }
    }
  }
});

const fetchData = async () => {
  try {
    const res = await api.get('/dashboard/treasury-yield');
    setupChart(res.data);
  } catch (e) {
    console.error("Failed to load treasury yields from API", e);
  }
};

const setupChart = (data) => {
    totalLabels.value = data.dates.length;
    
    if (data.dates.length > 0) {
        const lastDate = new Date(data.dates[data.dates.length - 1]);
        for (let i = 1; i <= 5; i++) {
            const nextDate = new Date(lastDate);
            nextDate.setDate(lastDate.getDate() + i * 7);
            data.dates.push(nextDate.toISOString().split('T')[0]);
        }
    }
    
    const validYields = data.yields.filter(r => r !== null);
    if (validYields.length > 0) {
        currentYield.value = validYields[validYields.length - 1];
    }
    
    if (validYields.length >= 2) {
        const lastVal = validYields[validYields.length - 1];
        const prevVal = validYields[validYields.length - 2];
        if (prevVal !== 0) {
            changeRate.value = ((lastVal - prevVal) / prevVal) * 100;
        } else {
            changeRate.value = 0;
        }
    }

    if (validYields.length > 0) {
      const minVal = Math.min(...validYields);
      const maxVal = Math.max(...validYields);
      
      yMin.value = Math.max(0, minVal - 0.2);
      yMax.value = maxVal + 0.2;

      mainChartOptions.value.scales.y.min = yMin.value;
      mainChartOptions.value.scales.y.max = yMax.value;
    }
    
    const datasets = [
      {
        label: 'US 10Y Treasury',
        backgroundColor: '#38bdf8', 
        borderColor: '#38bdf8',
        data: data.yields,
        borderWidth: 1.5,
        fill: {
            target: 'origin',
            above: 'rgba(56, 189, 248, 0.05)'
        }
      }
    ];

    chartData.value = { labels: data.dates, datasets };

    setTimeout(() => {
        if (chartContainer.value) {
            chartContainer.value.scrollLeft = chartContainer.value.scrollWidth;
        }
    }, 100);
}

onMounted(fetchData);
</script>

<template>
  <div class="glass-card h-full flex flex-col">
    <div class="flex justify-between items-start mb-4">
      <div>
        <h3 class="text-xs uppercase tracking-widest text-slate-400 mb-1">US 10-Year Treasury Yield</h3>
        <div class="flex items-baseline gap-3">
          <div class="flex items-baseline gap-1">
            <span class="text-2xl font-light text-sky-400 tracking-tight font-mono">
              {{ currentYield !== null ? currentYield.toFixed(3) : '—' }}
            </span>
            <span class="text-xs text-slate-500">%</span>
          </div>
          <div v-if="changeRate !== null" :class="[
            'text-sm font-mono flex items-center',
            changeRate > 0 ? 'text-red-400' : changeRate < 0 ? 'text-blue-400' : 'text-slate-500'
          ]">
            <span>{{ changeRate > 0 ? '▲ ' : changeRate < 0 ? '▼ ' : '' }}</span>
            <span>{{ Math.abs(changeRate).toFixed(2) }}%</span>
          </div>
        </div>
      </div>
      <div class="flex gap-3 text-[10px] font-mono text-slate-400 mt-1">
        <div class="flex items-center gap-1">
          <span class="w-3 h-[2px] bg-sky-400 inline-block"></span>
          <span>US 10Y</span>
        </div>
      </div>
    </div>
    
    <div class="flex-1 min-h-0 flex relative">
      <div ref="chartContainer" class="flex-1 overflow-x-auto overflow-y-hidden custom-scrollbar relative z-10">
        <div :style="{ width: Math.max(100, (totalLabels / 100) * 100) + '%' }" class="h-full min-w-full">
           <Line v-if="chartData.datasets.length > 0" :data="chartData" :options="mainChartOptions" />
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
