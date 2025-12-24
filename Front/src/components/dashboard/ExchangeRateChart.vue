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
import api from '@/api/index.js';

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

// 1. Main Chart (Scrollable)
const mainChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  elements: { point: { radius: 0, hitRadius: 10 }, line: { tension: 0.1 } },
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: { label: (ctx) => ` ₩${ctx.parsed.y.toLocaleString()}` }
    }
  },
  scales: {
    x: { 
      display: true,
      grid: { display: false },
      ticks: {
        maxTicksLimit: 60,
        maxRotation: 0,
        callback: function(val) {
          const dateStr = this.getLabelForValue(val);
          const date = new Date(dateStr);
          return `${date.getFullYear().toString().slice(2)}.${(date.getMonth() + 1).toString().padStart(2, '0')}`;
        },
        font: { family: 'monospace', size: 10 }
      }
    }, 
    y: { 
      display: true, // Re-enable Y-axis
      position: 'right', 
      min: 0, 
      max: 1500,
      grid: { color: '#f3f4f6' },
      ticks: { font: { family: 'monospace', size: 10 } }
    } 
  }
});

const fetchData = async () => {
  try {
    const res = await api.get('/dashboard/exchange-rate');
    totalLabels.value = res.data.dates.length;

    // Calculate Min/Max (Keep logic same)
    const rates = res.data.rates.filter(r => r !== null);
    const minVal = Math.min(...rates);
    const maxVal = Math.max(...rates);
    const padding = (maxVal - minVal) * 0.1;

    yMin.value = Math.floor(minVal - padding);
    yMax.value = Math.ceil(maxVal + padding);

    // Apply scaling
    mainChartOptions.value.scales.y.min = yMin.value;
    mainChartOptions.value.scales.y.max = yMax.value;

    chartData.value = {
      labels: res.data.dates,
      datasets: [
        {
          label: 'USD/KRW',
          backgroundColor: '#10b981', 
          borderColor: '#10b981',
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
  <div class="h-full flex flex-col p-6 border border-gray-200 bg-white hover:border-luxury-gold transition-colors duration-300">
    <!-- Header: Title & Custom Legend -->
    <div class="flex justify-between items-start mb-4">
      <h3 class="text-xs uppercase tracking-widest text-gray-500">Exchange Rate</h3>
      <div class="flex gap-4 text-[10px] font-mono">
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 bg-[#10b981]"></span>
          <span>USD/KRW</span>
        </div>
      </div>
    </div>
    
    <!-- Chart Body: Single Scrollable View -->
    <div class="flex-1 min-h-0 flex relative">
      <div ref="chartContainer" class="flex-1 overflow-x-auto overflow-y-hidden custom-scrollbar relative z-10">
         <div :style="{ width: Math.max(100, (totalLabels / 500) * 100) + '%' }" class="h-full min-w-full">
            <Line v-if="chartData.datasets.length > 0" :data="chartData" :options="mainChartOptions" />
            <div v-else class="h-full flex items-center justify-center text-gray-300">Loading Data...</div>
         </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { height: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #d1d5db; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #996515; }
</style>
