<script setup>
import { ref, onMounted } from 'vue';
import VideoList from '../../components/video/VideoList.vue';
import VideoRegisterModal from '../../components/video/VideoRegisterModal.vue';
import { api } from '@/api';

const videos = ref([]);
const isModalOpen = ref(false);
const currentPage = ref(1);
const totalPages = ref(1);
const itemsPerPage = 10;

const fetchVideos = async () => {
    try {
        const response = await api.get(`/videos?page=${currentPage.value}&limit=${itemsPerPage}`);
        videos.value = response.data.videos;
        totalPages.value = Math.ceil(response.data.total / itemsPerPage);
        
        // Fix: If current page > total pages (e.g. after deletion), go to last page
        if (currentPage.value > totalPages.value && totalPages.value > 0) {
            changePage(totalPages.value);
        } else if (totalPages.value === 0) {
             // If no videos left at all
             currentPage.value = 1;
        }
    } catch (error) {
        console.error("Failed to fetch videos:", error);
    }
}

const changePage = (page) => {
    if (page < 1 || (totalPages.value > 0 && page > totalPages.value)) return;
    currentPage.value = page;
    fetchVideos();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

onMounted(() => {
    fetchVideos();
});

const openModal = () => {
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const handleRegisterVideo = (newVideo) => {
  // Reset to page 1 and re-fetch to ensure pagination limit is respected
  currentPage.value = 1;
  fetchVideos();
  closeModal();
};

const handleDeleteVideo = (deletedId) => {
    // Instead of local filter, re-fetch to handle pagination shifts (e.g. item from next page moving up)
    // Local filter: videos.value = videos.value.filter(v => v.id !== deletedId);
    fetchVideos();
}
</script>

<template>
  <div class="w-full max-w-[1400px] mx-auto px-6 py-12">
    <!-- Header Area -->
    <div class="mb-12 flex flex-col md:flex-row justify-between items-end gap-6">
      <header class="glass-header slide-up text-left" style="animation-delay: 0.1s; display: block; text-align: left; padding: 20px 32px; border-radius: 20px;">
        <h1 class="glass-title text-4xl mb-2">VIDEO COMMUNITY</h1>
        <p class="glass-subtitle font-mono text-sm">
          Share your favorite moments
        </p>
      </header>
      <button 
        @click="openModal"
        class="px-6 py-2 bg-sky-500/20 text-sky-400 text-xs uppercase tracking-widest border border-sky-400/50 hover:bg-sky-400 hover:text-white hover:border-sky-400 transition-all rounded-full shadow-[0_0_15px_rgba(56,189,248,0.2)] hover:shadow-[0_0_20px_rgba(56,189,248,0.6)]"
      >
        REGISTER VIDEO
      </button>
    </div>

    <!-- Video List Area -->
    <VideoList :videos="videos" @delete="handleDeleteVideo" />

    <!-- Pagination -->
    <div class="mt-8 flex justify-center gap-2 slide-up" style="animation-delay: 0.3s;" v-if="totalPages > 1">
        <button 
            @click="changePage(currentPage - 1)" 
            :disabled="currentPage === 1"
            class="w-10 h-10 border border-white/20 rounded-full flex items-center justify-center text-slate-400 bg-transparent hover:border-sky-400 hover:text-sky-400 hover:shadow-[0_0_15px_rgba(56,189,248,0.3)] transition-all disabled:opacity-30 disabled:hover:border-white/20 disabled:hover:text-slate-400 disabled:hover:shadow-none"
        >
            &lt;
        </button>
        
        <button 
            v-for="page in totalPages" 
            :key="page"
            @click="changePage(page)"
            :class="currentPage === page ? 'bg-sky-500/20 text-sky-400 border-sky-400 shadow-[0_0_15px_rgba(56,189,248,0.3)]' : 'text-slate-400 border-white/20 bg-transparent hover:border-sky-400 hover:text-sky-400 hover:shadow-[0_0_15px_rgba(56,189,248,0.3)]'"
            class="w-10 h-10 border rounded-full flex items-center justify-center text-sm font-light transition-all"
        >
            {{ page }}
        </button>
        
        <button 
            @click="changePage(currentPage + 1)" 
            :disabled="currentPage === totalPages"
            class="w-10 h-10 border border-white/20 rounded-full flex items-center justify-center text-slate-400 bg-transparent hover:border-sky-400 hover:text-sky-400 hover:shadow-[0_0_15px_rgba(56,189,248,0.3)] transition-all disabled:opacity-30 disabled:hover:border-white/20 disabled:hover:text-slate-400 disabled:hover:shadow-none"
        >
            &gt;
        </button>
    </div>

    <!-- Modals -->
    <VideoRegisterModal 
      v-if="isModalOpen" 
      @close="closeModal" 
      @register="handleRegisterVideo" 
    />
  </div>
</template>
