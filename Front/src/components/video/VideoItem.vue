<script setup>
import { ref, computed } from 'vue';
import VideoComments from './VideoComments.vue';
import { api } from '@/api';

const props = defineProps({
  video: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['delete']);

const isOpen = ref(false);
const hasViewed = ref(false);

const toggleAccordion = async () => {
  isOpen.value = !isOpen.value;
  
  if (isOpen.value && !hasViewed.value) {
      try {
          await api.post(`/videos/${props.video.id}/view`);
          props.video.view_count++;
          hasViewed.value = true;
      } catch (error) {
          console.error("Failed to increment view count:", error);
      }
  }
};

// Toggle-able state for like/dislike (Visual only for now)
const isLiked = ref(false);
const isHated = ref(false);

const toggleLike = async () => {
  try {
      if (isLiked.value) {
        await api.delete(`/videos/${props.video.id}/like`);
        isLiked.value = false;
        props.video.like_count--;
      } else {
        await api.post(`/videos/${props.video.id}/like`);
        isLiked.value = true;
        props.video.like_count++;
        
        if (isHated.value) {
            await api.delete(`/videos/${props.video.id}/hate`);
            isHated.value = false;
            props.video.hate_count--;
        }
      }
  } catch (error) {
      console.error("Failed to toggle like:", error);
  }
};

const toggleHate = async () => {
  try {
      if (isHated.value) {
        await api.delete(`/videos/${props.video.id}/hate`);
        isHated.value = false;
        props.video.hate_count--;
      } else {
        await api.post(`/videos/${props.video.id}/hate`);
        isHated.value = true;
        props.video.hate_count++;
        
        if (isLiked.value) {
            await api.delete(`/videos/${props.video.id}/like`);
            isLiked.value = false;
            props.video.like_count--;
        }
      }
  } catch (error) {
      console.error("Failed to toggle hate:", error);
  }
};

const reportVideo = async () => {
    if (!confirm("이 영상을 신고하시겠습니까?")) return;
    try {
        await api.post(`/videos/${props.video.id}/report`);
        alert("신고가 접수되었습니다.");
        props.video.reported_count++; // Optional: update local state if we want to show it or just ack
    } catch (error) {
        console.error("Failed to report video:", error);
        alert("신고 처리 중 오류가 발생했습니다.");
    }
}

const deleteVideo = async () => {
    if (!confirm("정말 이 영상을 삭제하시겠습니까? (복구할 수 없습니다)")) return;
    try {
        await api.delete(`/videos/${props.video.id}`);
        emit('delete', props.video.id);
    } catch (error) {
        console.error("Failed to delete video:", error);
        alert("영상 삭제에 실패했습니다.");
    }
}

// Auth Store for permission check
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();

const canDelete = computed(() => {
    if (!authStore.user) return false;
    // Check if user is author OR user is admin
    // Note: Database schema uses 'uploader_id', frontend video object has 'uploader_id'
    return authStore.user.id === props.video.uploader_id || authStore.user.check_admin;
});


// Helper to get embed URL from youtube link or ID
const embedUrl = computed(() => {
  if (props.video.video_key) {
    return `https://www.youtube.com/embed/${props.video.video_key}`;
  }
  if (props.video.videoId) {
    return `https://www.youtube.com/embed/${props.video.videoId}`;
  }
  // Fallback simple parsing if videoId not provided
  try {
    const url = new URL(props.video.url);
    const v = url.searchParams.get('v');
    if (v) return `https://www.youtube.com/embed/${v}`;
    if (url.hostname.includes('youtu.be')) return `https://www.youtube.com/embed${url.pathname}`;
  } catch (e) {
    return '';
  }
  return '';
  return '';
});

const thumbnailUrl = computed(() => {
  let videoId = props.video.video_key || props.video.videoId;
  if (!videoId) {
      try {
        const url = new URL(props.video.url);
        videoId = url.searchParams.get('v');
        if (!videoId && url.hostname.includes('youtu.be')) {
            videoId = url.pathname.slice(1);
        }
      } catch (e) {}
  }
  
  if (videoId) {
    return `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
  }
  return '';
});
</script>

<template>
  <div class="border-b border-gray-200 last:border-b-0">
    <!-- List Item Header (Always Visible) -->
    <div 
      @click="toggleAccordion"
      class="flex items-center p-5 cursor-pointer hover:bg-gray-50 border-l-4 border-transparent hover:border-luxury-gold transition-all duration-300 group bg-white"
    >
      <!-- ID -->
      <div class="text-xs text-gray-300 w-12 text-center font-mono tracking-wider group-hover:text-luxury-gold transition-colors shrink-0">
        {{ String(video.id).padStart(2, '0') }}
      </div>

      <!-- Thumbnail (Left) -->
      <div v-if="thumbnailUrl" class="mr-4 w-[160px] aspect-video overflow-hidden shadow-sm relative group-hover:shadow-md transition-all shrink-0">
          <img :src="thumbnailUrl" alt="Video Thumbnail" class="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500" />
          <div class="absolute inset-0 bg-black/10 group-hover:bg-transparent transition-colors"></div>
      </div>

      <!-- Content (Right) -->
      <div class="flex-1 min-w-0 flex flex-col justify-center items-start text-left space-y-2">
        <!-- Row 1: User Title -->
        <h3 class="text-lg font-light tracking-tight group-hover:text-black transition-colors truncate pr-8 leading-none text-left w-full">
          {{ video.title }}
        </h3>
        
        <!-- Row 2: Original Title -->
        <a 
          v-if="video.original_title" 
          :href="video.url" 
          target="_blank" 
          class="text-xs text-gray-400 truncate pr-8 font-light hover:text-luxury-gold hover:underline transition-colors block w-fit text-left"
          @click.stop
        >
           {{ video.original_title }}
        </a>

        <!-- Row 3: Metrics & Metadata -->
        <div class="flex items-center text-[10px] text-gray-400 uppercase tracking-wider space-x-3 pt-1 text-left">
             <!-- Like/Hate Counts -->
             <div class="flex items-center space-x-2 border-r border-gray-200 pr-3">
                 <span class="flex items-center space-x-1" :class="{'text-luxury-gold': isLiked}">
                     <span>👍</span>
                     <span>{{ video.like_count }}</span>
                 </span>
                 <span class="flex items-center space-x-1" :class="{'text-black': isHated}">
                     <span>👎</span>
                     <span>{{ video.hate_count }}</span>
                 </span>
             </div>

             <!-- Metadata -->
             <span class="font-bold text-gray-800">{{ video.author }}</span> 
             <span class="text-gray-300">|</span> 
             <span>{{ new Date(video.created_at).toLocaleString() }}</span>
             <span class="text-gray-300">|</span> 
             <span>Views {{ video.view_count }}</span>
             
             <!-- Delete Button -->
             <button 
                v-if="canDelete"
                @click.stop="deleteVideo"
                class="ml-3 px-2 py-0 border border-gray-300 rounded-full flex items-center justify-center text-[10px] leading-tight text-gray-300 hover:text-red-400 hover:border-red-400 transition-all duration-300 bg-white hover:bg-white h-fit mt-0.5"
                title="Delete Video"
             >
                삭제
             </button>
        </div>
      </div>
      
      <!-- Arrow Icon -->
      <div class="text-gray-300 group-hover:text-luxury-gold transition-colors ml-4 mt-1 shrink-0">
        <svg 
          class="w-5 h-5 transform transition-transform duration-500 ease-out"
          :class="{ 'rotate-180': isOpen }"
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="square" stroke-linejoin="miter" stroke-width="1" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>

    <!-- Accordion Content (Visible when isOpen) -->
    <transition
      enter-active-class="transition duration-500 ease-out"
      enter-from-class="transform scale-y-95 opacity-0 max-h-0"
      enter-to-class="transform scale-y-100 opacity-100 max-h-[1000px]"
      leave-active-class="transition duration-300 ease-in"
      leave-from-class="transform scale-y-100 opacity-100 max-h-[1000px]"
      leave-to-class="transform scale-y-95 opacity-0 max-h-0"
    >
      <div v-if="isOpen" class="bg-gray-50/50 border-t border-gray-100 p-8 shadow-inner">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">
          <!-- Left Column: Video Player & Info -->
          <div class="lg:col-span-2 space-y-6">
            <!-- Video Player -->
            <div class="aspect-video bg-black shadow-2xl ring-1 ring-gray-900/5">
              <iframe 
                v-if="embedUrl"
                class="w-full h-full"
                :src="embedUrl" 
                title="YouTube video player" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen
              ></iframe>
              <div v-else class="w-full h-full flex items-center justify-center text-white font-light tracking-widest text-xs">
                VIDEO URL INVALID
              </div>
            </div>

            <!-- Title & Description -->
            <div>
              <h2 class="text-2xl font-light mb-3 tracking-tight">{{ video.title }}</h2>
              <p class="text-gray-500 text-sm whitespace-pre-line leading-loose font-light">
                {{ video.description }}
              </p>
            </div>

            <!-- Tags -->
            <div class="flex flex-wrap gap-2">
              <span 
                v-if="video.tag_name"
                class="text-[10px] px-3 py-1 bg-white border border-gray-200 text-gray-400 uppercase tracking-widest hover:border-luxury-gold hover:text-luxury-gold transition-colors cursor-default"
              >
                #{{ video.tag_name }}
              </span>
              <!-- Fallback to older array tags if present -->
               <span 
                v-else-if="video.tags && video.tags.length"
                v-for="tag in video.tags"
                :key="tag"
                class="text-[10px] px-3 py-1 bg-white border border-gray-200 text-gray-400 uppercase tracking-widest hover:border-luxury-gold hover:text-luxury-gold transition-colors cursor-default"
              >
                #{{ tag }}
              </span>
            </div>

            <!-- Action Buttons -->
            <div class="flex items-center space-x-0 pt-6 border-t border-gray-200">
              <button 
                @click="toggleLike"
                class="flex items-center space-x-3 px-6 py-3 border border-r-0 border-gray-300 transition-all duration-300 group hover:bg-gray-50"
                :class="isLiked ? 'bg-luxury-gold/5 border-luxury-gold text-luxury-gold' : 'text-gray-500'"
              >
                <span class="group-hover:scale-110 transition-transform duration-300">👍</span>
                <span class="font-medium text-xs tracking-widest">{{ video.like_count }}</span>
              </button>
              <button 
                @click="toggleHate"
                class="flex items-center space-x-3 px-6 py-3 border border-gray-300 transition-all duration-300 group hover:bg-gray-50"
                :class="isHated ? 'bg-gray-800 text-white border-gray-800' : 'text-gray-500'"
              >
                <span class="group-hover:scale-110 transition-transform duration-300">👎</span>
                <span class="font-medium text-xs tracking-widest">{{ video.hate_count }}</span>
              </button>
              
              <button 
                @click="reportVideo"
                class="ml-auto text-xs text-gray-300 hover:text-red-500 transition-colors tracking-widest px-4 border-none bg-transparent hover:bg-transparent shadow-none hover:shadow-none h-auto hover:translate-y-0 hover:tracking-widest">
                REPORT
              </button>
            </div>
          </div>

          <!-- Right Column: Comments -->
          <div class="lg:col-span-1">
            <VideoComments :comments="video.comments" :videoId="video.id" />
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>
