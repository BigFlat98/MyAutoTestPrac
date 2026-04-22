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

const currentKR = ref(null);
const currentUS = ref(null);

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
    const res = await api.get('/dashboard/interest-rates');
    totalLabels.value = res.data.dates.length;
    
    if (res.data.dates.length > 0) {
        const lastDate = new Date(res.data.dates[res.data.dates.length - 1]);
        for (let i = 1; i <= 5; i++) {
            const nextDate = new Date(lastDate);
            nextDate.setMonth(lastDate.getMonth() + i);
            res.data.dates.push(nextDate.toISOString().split('T')[0]);
        }
    }
    
    const validKR = res.data.kr.filter(r => r !== null);
    const validUS = res.data.us.filter(r => r !== null);
    if (validKR.length) currentKR.value = validKR[validKR.length - 1];
    if (validUS.length) currentUS.value = validUS[validUS.length - 1];

    const allRates = [...res.data.kr, ...res.data.us].filter(r => r !== null);
    const minVal = Math.min(...allRates);
    const maxVal = Math.max(...allRates);
    
    yMin.value = Math.max(0, minVal - 0.25);
    yMax.value = maxVal + 0.25;

    mainChartOptions.value.scales.y.min = yMin.value;
    mainChartOptions.value.scales.y.max = yMax.value;
    
    const datasets = [
      {
        label: 'Korea (Base Rate)',
        backgroundColor: '#38bdf8', // Sky Blue
        borderColor: '#38bdf8',
        data: res.data.kr,
        borderWidth: 1.5
      },
      {
        label: 'USA (Fed Funds)',
        backgroundColor: '#f8fafc', // White
        borderColor: '#f8fafc',
        data: res.data.us,
        borderWidth: 1.5,
        borderDash: [5, 5]
      }
    ];

    chartData.value = { labels: res.data.dates, datasets };

    setTimeout(() => {
        if (chartContainer.value) {
            chartContainer.value.scrollLeft = chartContainer.value.scrollWidth;
        }
    }, 100);

  } catch (e) {
    console.error("Failed to load rates", e);
  }
};

onMounted(fetchData);
</script>

<template>
  <div class="glass-card h-full flex flex-col">
    <!-- Header -->
    <div class="flex justify-between items-start mb-4">
      <div>
        <h3 class="text-xs uppercase tracking-widest text-slate-400 mb-1">Base Interest Rate</h3>
        <div class="flex items-baseline gap-3">
          <!-- Korea -->
          <div class="flex items-baseline gap-1">
            <span class="text-[10px] font-mono text-slate-500 uppercase">KR</span>
            <span class="text-2xl font-light text-sky-400 tracking-tight font-mono">
              {{ currentKR !== null ? currentKR.toFixed(2) : '—' }}
            </span>
            <span class="text-xs text-slate-500">%</span>
          </div>
          <span class="text-white/20 text-sm">|</span>
          <!-- USA -->
          <div class="flex items-baseline gap-1">
            <span class="text-[10px] font-mono text-slate-500 uppercase">US</span>
            <span class="text-2xl font-light text-slate-100 tracking-tight font-mono">
              {{ currentUS !== null ? currentUS.toFixed(2) : '—' }}
            </span>
            <span class="text-xs text-slate-500">%</span>
          </div>
        </div>
      </div>
      <!-- Legend -->
      <div class="flex gap-3 text-[10px] font-mono text-slate-400 mt-1">
        <div class="flex items-center gap-1">
          <span class="w-3 h-[2px] bg-sky-400 inline-block"></span>
          <span>Korea</span>
        </div>
        <div class="flex items-center gap-1">
          <span class="w-3 h-[2px] bg-slate-100 inline-block border-t border-dashed border-slate-100"></span>
          <span>USA</span>
        </div>
      </div>
    </div>
    
    <!-- Chart Body -->
    <div class="flex-1 min-h-0 flex relative">
      <div ref="chartContainer" class="flex-1 overflow-x-auto overflow-y-hidden custom-scrollbar relative z-10">
        <div :style="{ width: Math.max(100, (totalLabels / 500) * 100) + '%' }" class="h-full min-w-full">
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