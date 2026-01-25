<script setup>
import { ref } from 'vue';

const emit = defineEmits(['close', 'register']);

const title = ref('');
const url = ref('');
const description = ref('');

const extractVideoId = (inputUrl) => {
  try {
    const urlObj = new URL(inputUrl);
    if (urlObj.hostname.includes('youtube.com')) {
      return urlObj.searchParams.get('v');
    } else if (urlObj.hostname.includes('youtu.be')) {
      return urlObj.pathname.slice(1);
    }
  } catch (e) {
    return null;
  }
  return null;
};

const handleSubmit = () => {
  if (!title.value || !url.value) {
    alert('제목과 URL을 입력해주세요.');
    return;
  }

  const videoId = extractVideoId(url.value);
  if (!videoId) {
    alert('올바른 유튜브 URL을 입력해주세요.');
    return;
  }

  const newVideo = {
    id: Date.now(),
    title: title.value,
    url: url.value,
    videoId: videoId,
    author: 'Me',
    view_count: 0,
    like_count: 0,
    hate_count: 0,
    created_at: new Date().toLocaleString(),
    description: description.value,
    tags: ['New'],
    comments: []
  };

  emit('register', newVideo);
};
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div 
      class="absolute inset-0 bg-black/60 backdrop-blur-sm"
      @click="$emit('close')"
    ></div>

    <!-- Modal Content -->
    <div class="relative bg-white w-full max-w-lg shadow-2xl animate-in fade-in zoom-in duration-200">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
        <h3 class="text-lg font-bold tracking-tight">VIDEO REGISTRATION</h3>
        <button @click="$emit('close')" class="text-gray-400 hover:text-black">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="square" stroke-linejoin="miter" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Body -->
      <div class="p-8 space-y-6">
        <div>
          <label class="block text-[10px] font-bold text-gray-400 mb-2 tracking-widest uppercase">YouTube URL</label>
          <input 
            v-model="url"
            type="text" 
            placeholder="paste your youtube link here..."
            class="w-full h-12 border-b border-gray-200 px-0 text-sm focus:outline-none focus:border-luxury-gold transition-colors rounded-none placeholder-gray-300 bg-transparent"
          />
        </div>
        
        <div>
          <label class="block text-[10px] font-bold text-gray-400 mb-2 tracking-widest uppercase">Title</label>
          <input 
            v-model="title"
            type="text" 
            placeholder="enter video title..."
            class="w-full h-12 border-b border-gray-200 px-0 text-sm focus:outline-none focus:border-luxury-gold transition-colors rounded-none placeholder-gray-300 bg-transparent"
          />
        </div>

        <div>
          <label class="block text-[10px] font-bold text-gray-400 mb-2 tracking-widest uppercase">Description</label>
          <textarea 
            v-model="description"
            rows="4"
            placeholder="tell us about this video..."
            class="w-full border border-gray-200 p-4 text-sm focus:outline-none focus:border-luxury-gold focus:ring-1 focus:ring-luxury-gold transition-all rounded-none resize-none placeholder-gray-300 bg-gray-50/30"
          ></textarea>
        </div>
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-gray-100 bg-gray-50 flex justify-end space-x-0">
        <button 
          @click="$emit('close')"
          class="px-8 h-12 border border-gray-200 bg-white text-gray-500 hover:text-black hover:border-gray-400 transition-colors text-xs tracking-[0.2em] font-medium border-r-0"
        >
          CANCEL
        </button>
        <button 
          @click="handleSubmit"
          class="px-8 h-12 bg-black text-white hover:bg-luxury-gold transition-colors text-xs tracking-[0.2em] font-medium"
        >
          REGISTER
        </button>
      </div>
    </div>
  </div>
</template>
