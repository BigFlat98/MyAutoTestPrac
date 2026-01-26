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
  <div class="container mx-auto px-4 py-8 max-w-5xl">
    <!-- Header Area -->
    <!-- Header Area -->
    <div class="mb-12 flex flex-col md:flex-row justify-between items-end gap-6">
      <div>
        <h1 class="text-4xl font-light tracking-tight mb-2">VIDEO COMMUNITY</h1>
        <div class="w-16 h-px bg-luxury-gold mb-4"></div>
        <p class="text-xs uppercase tracking-widest text-gray-500 font-medium">
          Share your favorite moments
        </p>
      </div>
      <button 
        @click="openModal"
        class="px-6 py-2 bg-black text-white text-xs uppercase tracking-widest hover:bg-luxury-gold transition-colors rounded-sm"
      >
        REGISTER VIDEO
      </button>
    </div>

    <!-- Video List Area -->
    <VideoList :videos="videos" @delete="handleDeleteVideo" />

    <!-- Pagination -->
    <div class="mt-8 flex justify-center gap-2" v-if="totalPages > 1">
        <button 
            @click="changePage(currentPage - 1)" 
            :disabled="currentPage === 1"
            class="w-10 h-10 border border-gray-200 flex items-center justify-center text-gray-400 hover:border-sky-300 hover:text-sky-300 hover:shadow-[0_0_8px_rgba(186,230,253,0.5)] hover:bg-white transition-all duration-300 disabled:opacity-30 disabled:hover:border-gray-200 disabled:hover:text-gray-400 disabled:hover:shadow-none bg-white"
        >
            &lt;
        </button>
        
        <button 
            v-for="page in totalPages" 
            :key="page"
            @click="changePage(page)"
            :class="currentPage === page ? 'bg-black text-white border-black shadow-sm' : 'text-gray-600 border-gray-200 bg-white hover:bg-white hover:border-sky-300 hover:text-sky-300 hover:shadow-[0_0_8px_rgba(186,230,253,0.5)]'"
            class="w-10 h-10 border flex items-center justify-center text-sm font-light transition-all duration-300"
        >
            {{ page }}
        </button>
        
        <button 
            @click="changePage(currentPage + 1)" 
            :disabled="currentPage === totalPages"
            class="w-10 h-10 border border-gray-200 flex items-center justify-center text-gray-400 hover:border-sky-300 hover:text-sky-300 hover:shadow-[0_0_8px_rgba(186,230,253,0.5)] hover:bg-white transition-all duration-300 disabled:opacity-30 disabled:hover:border-gray-200 disabled:hover:text-gray-400 disabled:hover:shadow-none bg-white"
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
