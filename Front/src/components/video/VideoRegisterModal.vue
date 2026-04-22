<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api';

const emit = defineEmits(['close', 'register']);

const title = ref('');
const url = ref('');
const description = ref('');
const tag_id = ref('');
const tags = ref([]);

const fetchTags = async () => {
    try {
        const response = await api.get('/videos/tags');
        tags.value = response.data;
    } catch (error) {
        console.error("Failed to fetch tags:", error);
    }
}

onMounted(() => {
    fetchTags();
});

const urlError = ref('');

const validateUrl = () => {
    if (!url.value) {
        urlError.value = '';
        return true;
    }
    const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/;
    if (!pattern.test(url.value)) {
        urlError.value = '올바른 YouTube URL 형식이 아닙니다.';
        return false;
    }
    urlError.value = '';
    return true;
}

const handleSubmit = async () => {
  if (!validateUrl()) {
      return;
  }

  if (!title.value || !url.value) {
    alert('제목과 URL을 입력해주세요.');
    return;
  }
  
  if (!tag_id.value) {
      alert('태그를 선택해주세요.');
      return;
  }

  try {
      const payload = {
          title: title.value,
          description: description.value,
          url: url.value,
          tag_id: tag_id.value
      }
      
      const response = await api.post('/videos', payload);
      emit('register', response.data);
      emit('close');
  } catch (error) {
      console.error("Failed to register video:", error);
      alert("영상 등록에 실패했습니다.");
  }
};
</script>

<template>
  <div class="fixed inset-0 z-[1000] flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div 
      class="absolute inset-0 bg-black/40 backdrop-blur-md transition-opacity duration-300"
      @click="$emit('close')"
    ></div>

    <!-- Modal Content -->
    <div class="relative w-full max-w-xl glass-card overflow-hidden slide-up" style="animation-delay: 0s;">
      <!-- Header -->
      <div class="px-8 py-6 border-b border-white/10 flex justify-between items-center bg-white/5">
        <div>
            <h3 class="text-xl font-light text-white tracking-tight">Register Video</h3>
            <p class="text-[10px] uppercase tracking-[0.2em] text-slate-500 mt-1">Share your content with community</p>
        </div>
        <button @click="$emit('close')" class="text-slate-500 hover:text-white transition-colors p-2 hover:bg-white/5 rounded-full">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Body -->
      <div class="p-8 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-2">
              <label class="block text-[10px] font-bold text-slate-500 tracking-[0.15em] uppercase px-1">YouTube URL</label>
              <input 
                v-model="url"
                @blur="validateUrl"
                type="text" 
                placeholder="https://youtube.com/..."
                class="w-full h-12 bg-white/5 border border-white/10 px-4 text-sm text-white focus:outline-none focus:border-sky-400/50 focus:ring-1 focus:ring-sky-400/20 transition-all rounded-xl placeholder-slate-600"
                :class="{'border-rose-400/50': urlError}"
              />
              <p v-if="urlError" class="text-[10px] text-rose-400 px-1">{{ urlError }}</p>
            </div>
            
            <div class="space-y-2">
               <label class="block text-[10px] font-bold text-slate-500 tracking-[0.15em] uppercase px-1">Category / Tag</label>
               <div class="relative">
                   <select 
                    v-model="tag_id"
                    class="w-full h-12 bg-white/5 border border-white/10 px-4 text-sm text-white focus:outline-none focus:border-sky-400/50 focus:ring-1 focus:ring-sky-400/20 transition-all rounded-xl cursor-pointer appearance-none"
                   >
                       <option value="" disabled class="bg-slate-900">Select a tag</option>
                       <option v-for="tag in tags" :key="tag.id" :value="tag.id" class="bg-slate-900">
                           {{ tag.name }}
                       </option>
                   </select>
                   <div class="absolute right-4 top-0 h-full flex items-center pointer-events-none text-slate-500">
                       <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                   </div>
               </div>
            </div>
        </div>

        <div class="space-y-2">
          <label class="block text-[10px] font-bold text-slate-500 tracking-[0.15em] uppercase px-1">Display Title</label>
          <input 
            v-model="title"
            type="text" 
            placeholder="Give your video a catchy title"
            class="w-full h-12 bg-white/5 border border-white/10 px-4 text-sm text-white focus:outline-none focus:border-sky-400/50 focus:ring-1 focus:ring-sky-400/20 transition-all rounded-xl placeholder-slate-600"
          />
        </div>

        <div class="space-y-2">
          <label class="block text-[10px] font-bold text-slate-500 tracking-[0.15em] uppercase px-1">Description</label>
          <textarea 
            v-model="description"
            rows="4"
            placeholder="Tell us about this video..."
            class="w-full bg-white/5 border border-white/10 p-4 text-sm text-white focus:outline-none focus:border-sky-400/50 focus:ring-1 focus:ring-sky-400/20 transition-all rounded-xl resize-none placeholder-slate-600 custom-scrollbar"
          ></textarea>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-8 py-6 border-t border-white/10 bg-white/5 flex justify-end gap-3">
        <button 
          @click="$emit('close')"
          class="px-6 h-12 bg-white/5 text-slate-400 hover:text-white hover:bg-white/10 transition-all text-xs tracking-widest font-medium rounded-xl border border-white/5"
        >
          CANCEL
        </button>
        <button 
          @click="handleSubmit"
          class="px-8 h-12 bg-sky-500/20 text-sky-400 hover:bg-sky-400 hover:text-white transition-all text-xs tracking-widest font-bold rounded-xl border border-sky-400/30 shadow-[0_0_15px_rgba(56,189,248,0.2)]"
        >
          REGISTER
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
</style>
