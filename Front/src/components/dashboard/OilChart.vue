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

const grades = {
    WTI:   { name: 'WTI Crude',   symbol: 'WTI',   color: '#f59e0b' },
    BRENT: { name: 'Brent Crude', symbol: 'BRENT', color: '#14b8a6' }
}

const selectedGradeKey = ref('WTI')
const isDropdownOpen = ref(false)
const isLoading = ref(false)

const toggleDropdown = () => { isDropdownOpen.value = !isDropdownOpen.value }
const selectGrade = (key) => { selectedGradeKey.value = key; isDropdownOpen.value = false }

const handleClickOutside = (event) => {
    const dropdown = document.querySelector('.oil-dropdown-container')
    if (dropdown && !dropdown.contains(event.target)) {
        isDropdownOpen.value = false
    }
}

const chartData = ref({ labels: [], datasets: [] })
const oilData = ref({ price: '-', changeRate: 0 })

const fetchOilData = async () => {
    isLoading.value = true
    const key = selectedGradeKey.value
    const grade = grades[key]

    try {
        const response = await api.get(`/dashboard/oil?grade=${key}`)
        const data = response.data

        oilData.value = {
            price: parseFloat(data.price).toFixed(2),
            changeRate: data.changeRate,
        }

        const labels = [...data.history.labels, '', '', '']
        const prices = [...data.history.prices, null, null, null]

        chartData.value = {
            labels,
            datasets: [
                {
                    label: `${grade.name} (USD/bbl)`,
                    borderColor: grade.color,
                    backgroundColor: (context) => {
                        const ctx = context.chart.ctx
                        const gradient = ctx.createLinearGradient(0, 0, 0, 300)
                        gradient.addColorStop(0, `${grade.color}33`)
                        gradient.addColorStop(1, `${grade.color}00`)
                        return gradient
                    },
                    data: prices,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                },
            ],
        }
    } catch (error) {
        console.error('[OilChart] Failed to fetch oil data:', error)
    } finally {
        isLoading.value = false
    }
}

watch(selectedGradeKey, fetchOilData)

onMounted(() => {
    fetchOilData()
    document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => { document.removeEventListener('click', handleClickOutside) })

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    layout: { padding: { right: 40 } },
    plugins: {
        legend: {
            display: true, align: 'end',
            labels: { boxWidth: 8, usePointStyle: true, font: { size: 10 }, color: '#94a3b8' }
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
                label: (context) => {
                    if (context.raw === null) return null
                    return ` ${context.dataset.label}: $${context.raw.toFixed(2)}`
                }
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
            grid: { display: false },
            ticks: { font: { size: 10, family: 'monospace' }, color: '#94a3b8', maxTicksLimit: 10 },
            min: (ctx) => {
                const total = ctx.chart.data.labels.length
                return total > 35 ? total - 35 : 0
            }
        },
        y: {
            position: 'right',
            grid: { color: 'rgba(255, 255, 255, 0.05)', borderDash: [4, 4], drawBorder: false },
            ticks: {
                font: { size: 10, family: 'monospace' },
                color: '#94a3b8',
                callback: (value) => `$${value.toFixed(0)}`
            }
        }
    },
    interaction: { mode: 'nearest', axis: 'x', intersect: false }
}
</script>

<template>
  <div class="glass-card h-full flex flex-col relative group">
    <div class="flex justify-between items-end mb-6 z-20 w-full">
      <div>
        <h2 class="text-sm font-bold text-slate-400 tracking-widest uppercase mb-1">Crude Oil</h2>

        <div class="relative oil-dropdown-container">
          <div @click="toggleDropdown" class="flex items-center gap-2 cursor-pointer group w-fit">
            <h3 class="text-3xl font-light text-slate-100 tracking-tight group-hover:text-slate-300 transition-colors">
              {{ grades[selectedGradeKey].name }}
            </h3>
            <span class="text-base text-slate-400 font-normal mt-2">{{ grades[selectedGradeKey].symbol }}</span>
            <svg class="w-4 h-4 text-slate-400 mt-2 transition-transform duration-300" :class="{ 'rotate-180': isDropdownOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>

          <transition enter-active-class="transition duration-200 ease-out" enter-from-class="transform scale-95 opacity-0" enter-to-class="transform scale-100 opacity-100" leave-active-class="transition duration-75 ease-in" leave-from-class="transform scale-100 opacity-100" leave-to-class="transform scale-95 opacity-0">
            <div v-if="isDropdownOpen" class="absolute top-full left-0 mt-2 w-48 bg-slate-800/90 backdrop-blur-md rounded-xl shadow-xl border border-white/10 overflow-hidden z-50">
              <ul>
                <li v-for="(grade, key) in grades" :key="key" @click="selectGrade(key)" class="px-4 py-3 hover:bg-white/10 cursor-pointer flex items-center justify-between group transition-colors" :class="{ 'bg-white/10': selectedGradeKey === key }">
                  <span class="font-light text-slate-200" :class="{ 'font-medium': selectedGradeKey === key }">{{ grade.name }}</span>
                  <span class="text-xs text-slate-400 font-mono group-hover:text-slate-300">{{ grade.symbol }}</span>
                </li>
              </ul>
            </div>
          </transition>
        </div>
      </div>

      <div class="text-right">
        <div class="text-2xl font-light tracking-tight" :style="{ color: grades[selectedGradeKey].color }">
          ${{ oilData.price }}<span class="text-sm text-slate-400">/bbl</span>
        </div>
        <div :class="oilData.changeRate >= 0 ? 'text-red-400' : 'text-blue-400'" class="text-xs font-mono font-medium">
          {{ oilData.changeRate >= 0 ? '▲' : '▼' }} {{ Math.abs(oilData.changeRate) }}%
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm z-10 rounded-2xl">
      <span class="text-xs text-slate-400 font-mono animate-pulse">Loading...</span>
    </div>

    <div class="flex-1 w-full min-h-0 relative">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>
