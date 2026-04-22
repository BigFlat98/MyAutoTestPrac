<script setup>
import { ref, computed } from 'vue';
import VideoComments from './VideoComments.vue';
import { api } from '@/api';
import { useAuthStore } from '@/stores/auth';

const props = defineProps({
  video: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['delete']);
const authStore = useAuthStore();

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
        props.video.reported_count++;
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

const canDelete = computed(() => {
    if (!authStore.user) return false;
    return authStore.user.id === props.video.uploader_id || authStore.user.check_admin;
});

// Helper to get embed URL from youtube link or ID
const embedUrl = computed(() => {
  if (!props.video || !props.video.url) return '';
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
    if (url.pathname.startsWith('/shorts/')) {
        return `https://www.youtube.com/embed/${url.pathname.split('/shorts/')[1]}`;
    }
    if (url.hostname.includes('youtu.be')) return `https://www.youtube.com/embed${url.pathname}`;
  } catch (e) {
    return '';
  }
  return '';
});

const thumbnailUrl = computed(() => {
  if (!props.video) return '';
  let videoId = props.video.video_key || props.video.videoId;
  if (!videoId) {
      try {
        if (!props.video.url) return '';
        const url = new URL(props.video.url);
        videoId = url.searchParams.get('v');
        if (!videoId && url.pathname.startsWith('/shorts/')) {
            videoId = url.pathname.split('/shorts/')[1];
        }
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
  <div class="glass-video-item overflow-hidden transition-all duration-500 rounded-2xl mb-4 border border-white/5" :class="{ 'active-item border-sky-400/30 ring-1 ring-sky-400/10': isOpen }">
    <!-- List Item Header -->
    <div 
      @click="toggleAccordion"
      class="flex items-center p-5 cursor-pointer bg-white/5 backdrop-blur-md hover:bg-white/10 transition-all duration-300 group relative overflow-hidden"
    >
      <!-- Background Glow Effect -->
      <div v-if="isOpen" class="absolute inset-0 bg-gradient-to-r from-sky-400/5 to-transparent pointer-events-none"></div>

      <!-- ID -->
      <div class="text-[10px] text-slate-500 w-10 text-center font-mono tracking-wider group-hover:text-sky-400 transition-colors shrink-0">
        {{ String(video.id).padStart(2, '0') }}
      </div>

      <!-- Thumbnail -->
      <div v-if="thumbnailUrl" class="mr-6 w-[140px] aspect-video overflow-hidden rounded-lg shadow-lg relative shrink-0 border border-white/10">
          <img :src="thumbnailUrl" alt="Thumbnail" class="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-700" />
          <div class="absolute inset-0 bg-black/20 group-hover:bg-black/0 transition-colors duration-300"></div>
          <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
             <div class="w-10 h-10 bg-sky-400/80 rounded-full flex items-center justify-center backdrop-blur-sm">
                <svg class="w-5 h-5 text-white translate-x-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
             </div>
          </div>
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0 flex flex-col justify-center items-start text-left space-y-2">
        <h3 class="text-base font-light tracking-wide text-slate-200 group-hover:text-white transition-colors truncate w-full text-left">
          {{ video.title }}
        </h3>
        
        <div class="flex items-center flex-wrap gap-x-3 gap-y-1 text-[10px] text-slate-500 uppercase tracking-widest font-mono">
             <span class="flex items-center gap-1" :class="{'text-sky-400': isLiked}">
                 <span class="text-xs">👍</span>{{ video.like_count }}
             </span>
             <span class="flex items-center gap-1" :class="{'text-rose-400': isHated}">
                 <span class="text-xs">👎</span>{{ video.hate_count }}
             </span>
             <span class="w-px h-2 bg-white/10"></span>
             <span class="text-slate-300 font-medium tracking-normal text-xs">{{ video.author }}</span> 
             <span class="text-slate-600 hidden sm:block">•</span> 
             <span class="hidden sm:block">{{ new Date(video.created_at).toLocaleDateString() }}</span>
             <span class="text-slate-600 hidden sm:block">•</span> 
             <span>{{ video.view_count }} views</span>
             
             <button 
                v-if="canDelete"
                @click.stop="deleteVideo"
                class="ml-1 px-1.5 py-px bg-rose-500 text-white hover:bg-transparent hover:text-rose-400 border border-rose-500 hover:border-rose-400 transition-all text-[9px] uppercase tracking-wider leading-tight rounded"
             >
                Delete
             </button>
        </div>
      </div>
      
      <!-- Arrow -->
      <div class="text-slate-500 group-hover:text-sky-400 transition-all duration-300 ml-4 shrink-0">
        <svg 
          class="w-6 h-6 transform transition-transform duration-500"
          :class="{ 'rotate-180 text-sky-400': isOpen }"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>

    <!-- Accordion Content -->
    <transition
      enter-active-class="transition-all duration-500 ease-out"
      enter-from-class="max-h-0 opacity-0"
      enter-to-class="max-h-[1200px] opacity-100"
      leave-active-class="transition-all duration-300 ease-in"
      leave-from-class="max-h-[1200px] opacity-100"
      leave-to-class="max-h-0 opacity-0"
    >
      <div v-if="isOpen" class="bg-black/20 backdrop-blur-xl border-t border-white/10 overflow-hidden">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-0">
          <!-- Left: Video & Info -->
          <div class="lg:col-span-8 p-6 md:p-8 space-y-8">
            <!-- Player Wrapper -->
            <div class="aspect-video bg-black rounded-xl overflow-hidden shadow-2xl ring-1 ring-white/10 group/player relative">
              <iframe 
                v-if="embedUrl"
                class="w-full h-full"
                :src="embedUrl" 
                title="YouTube video player"
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen
                referrerpolicy="strict-origin-when-cross-origin"
              ></iframe>
              <div v-else class="w-full h-full flex items-center justify-center text-slate-500 font-mono text-xs uppercase tracking-widest">
                Video Unavailable
              </div>
            </div>

            <div class="space-y-4">
              <div class="flex items-start justify-between gap-4">
                <h2 class="text-2xl font-light text-white tracking-tight leading-tight">{{ video.title }}</h2>
                
                <!-- Social Actions -->
                <div class="flex items-center gap-2 shrink-0">
                    <button 
                      @click="toggleLike"
                      class="flex items-center gap-2 px-4 py-2 rounded-lg border transition-all duration-300"
                      :class="isLiked ? 'bg-sky-400/20 border-sky-400 text-sky-400' : 'bg-white/5 border-white/10 text-slate-400 hover:border-sky-400/50 hover:text-sky-300'"
                    >
                      <span class="text-sm">👍</span>
                      <span class="text-xs font-mono">{{ video.like_count }}</span>
                    </button>
                    <button 
                      @click="toggleHate"
                      class="flex items-center gap-2 px-4 py-2 rounded-lg border transition-all duration-300"
                      :class="isHated ? 'bg-rose-400/20 border-rose-400 text-rose-400' : 'bg-white/5 border-white/10 text-slate-400 hover:border-rose-400/50 hover:text-rose-300'"
                    >
                      <span class="text-sm">👎</span>
                      <span class="text-xs font-mono">{{ video.hate_count }}</span>
                    </button>
                </div>
              </div>

              <p class="text-slate-400 text-sm whitespace-pre-line leading-relaxed font-light bg-white/5 p-5 rounded-xl border border-white/5">
                {{ video.description || 'No description provided.' }}
              </p>

              <div class="flex flex-wrap items-center justify-between gap-4 pt-4">
                  <div class="flex flex-wrap gap-2">
                    <span 
                        v-if="video.tag_name"
                        class="text-[10px] px-3 py-1 bg-sky-400/10 border border-sky-400/20 text-sky-400 uppercase tracking-widest rounded-full"
                    >
                        #{{ video.tag_name }}
                    </span>
                  </div>
                  
                  <button 
                    @click="reportVideo"
                    class="px-1.5 py-px bg-rose-500 text-white hover:bg-transparent hover:text-rose-400 border border-rose-500 hover:border-rose-400 transition-all text-[9px] uppercase tracking-wider leading-tight rounded"
                  >
                    Report
                  </button>
              </div>
            </div>
          </div>

          <!-- Right: Comments Section -->
          <div class="lg:col-span-4 border-l border-white/10 flex flex-col h-[600px] lg:h-auto">
            <VideoComments :comments="video.comments" :videoId="video.id" />
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.glass-video-item {
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.active-item {
  background: rgba(255, 255, 255, 0.03);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

/* Custom Scrollbar for comments handled in child but good to keep in mind */
</style>
