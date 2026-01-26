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
    // Simple regex for YouTube URLs (includes youtube.com, youtu.be, embed, watch)
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
            @blur="validateUrl"
            type="text" 
            placeholder="paste your youtube link here..."
            class="w-full h-12 border-b border-gray-200 px-0 text-sm focus:outline-none focus:border-luxury-gold transition-colors rounded-none placeholder-gray-300 bg-transparent"
            :class="{'border-red-500': urlError}"
          />
          <p v-if="urlError" class="text-xs text-red-500 mt-1">{{ urlError }}</p>
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
           <label class="block text-[10px] font-bold text-gray-400 mb-2 tracking-widest uppercase">Tag</label>
           <div class="relative">
               <select 
                v-model="tag_id"
                class="w-full h-12 border-b border-gray-200 px-0 text-sm focus:outline-none focus:border-luxury-gold transition-colors rounded-none bg-transparent appearance-none cursor-pointer"
               >
                   <option value="" disabled selected>Select a tag</option>
                   <option v-for="tag in tags" :key="tag.id" :value="tag.id">
                       {{ tag.name }}
                   </option>
               </select>
               <div class="absolute right-0 top-0 h-full flex items-center pointer-events-none text-gray-400">
                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
               </div>
           </div>
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
