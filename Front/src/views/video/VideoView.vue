<script setup>
import { ref } from 'vue';
import VideoList from '../../components/video/VideoList.vue';
import VideoRegisterModal from '../../components/video/VideoRegisterModal.vue';
import { dummyVideos } from '../../data/dummyVideoData';

const videos = ref([...dummyVideos]);
const isModalOpen = ref(false);

const openModal = () => {
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const handleRegisterVideo = (newVideo) => {
  // Add new video to the top of the list (local only)
  videos.value.unshift(newVideo);
  closeModal();
};
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
    <VideoList :videos="videos" />

    <!-- Modals -->
    <VideoRegisterModal 
      v-if="isModalOpen" 
      @close="closeModal" 
      @register="handleRegisterVideo" 
    />
  </div>
</template>
