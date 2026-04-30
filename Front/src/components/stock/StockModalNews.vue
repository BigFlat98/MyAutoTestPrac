<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/index.js';

const props = defineProps({
  stockName: {
    type: String,
    required: true
  }
});

const newsList = ref([]);
const loading = ref(true);

const fetchNews = async () => {
  loading.value = true;
  try {
    const res = await api.get(`/stock/${encodeURIComponent(props.stockName)}/news`);
    newsList.value = res.data;
  } catch (error) {
    console.error("Failed to fetch news data:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchNews);

const formatDate = (dateStr) => {
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
};

const stripHtml = (html) => {
  const tmp = document.createElement("DIV");
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || "";
};
</script>

<template>
  <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm relative overflow-hidden">
    <!-- background glow -->
    <div class="absolute -top-10 -left-10 w-32 h-32 bg-rose-500/10 rounded-full blur-3xl pointer-events-none"></div>

    <h3 class="text-sm uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9.5a2.5 2.5 0 00-2.5-2.5H15M9 11l3 3m0 0l3-3m-3 3V8" />
      </svg>
      관련 뉴스
    </h3>

    <div v-if="loading" class="animate-pulse flex flex-col gap-4">
      <div v-for="i in 3" :key="i" class="h-10 bg-white/10 rounded w-full"></div>
    </div>

    <div v-else-if="newsList.length > 0" class="flex flex-col gap-3">
      <a 
        v-for="(news, index) in newsList" 
        :key="index"
        :href="news.link" 
        target="_blank"
        class="block group p-3 bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/20 rounded transition-all"
      >
        <div class="flex justify-between items-start gap-4">
          <h4 class="text-sm text-slate-200 font-medium group-hover:text-sky-300 transition-colors line-clamp-1" v-html="news.title"></h4>
          <span class="text-[10px] text-slate-500 whitespace-nowrap">{{ formatDate(news.pubDate) }}</span>
        </div>
        <p class="text-xs text-slate-400 mt-1 line-clamp-1" v-html="stripHtml(news.description)"></p>
      </a>
    </div>

    <div v-else class="text-sm text-slate-500 py-4 text-center">
      검색된 관련 뉴스가 없습니다.
    </div>
  </div>
</template>
