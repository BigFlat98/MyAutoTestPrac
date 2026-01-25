<script setup>
import { ref, computed } from 'vue';
import VideoComments from './VideoComments.vue';

const props = defineProps({
  video: {
    type: Object,
    required: true
  }
});

const isOpen = ref(false);

const toggleAccordion = () => {
  isOpen.value = !isOpen.value;
};

// Toggle-able state for like/dislike (Visual only for now)
const isLiked = ref(false);
const isHated = ref(false);

const toggleLike = () => {
  if (isLiked.value) {
    isLiked.value = false;
    props.video.like_count--;
  } else {
    isLiked.value = true;
    props.video.like_count++;
    if (isHated.value) {
      isHated.value = false;
      props.video.hate_count--;
    }
  }
};

const toggleHate = () => {
  if (isHated.value) {
    isHated.value = false;
    props.video.hate_count--;
  } else {
    isHated.value = true;
    props.video.hate_count++;
    if (isLiked.value) {
      isLiked.value = false;
      props.video.like_count--;
    }
  }
};

// Helper to get embed URL from youtube link or ID
const embedUrl = computed(() => {
  if (props.video.videoId) {
    return `https://www.youtube.com/embed/${props.video.videoId}`;
  }
  // Fallback simple parsing if videoId not provided
  try {
    const url = new URL(props.video.url);
    const v = url.searchParams.get('v');
    if (v) return `https://www.youtube.com/embed/${v}`;
  } catch (e) {
    return '';
  }
  return '';
});
</script>

<template>
  <div class="border-b border-gray-200 last:border-b-0">
    <!-- List Item Header (Always Visible) -->
    <div 
      @click="toggleAccordion"
      class="flex items-center justify-between p-5 cursor-pointer hover:bg-gray-50 border-l-4 border-transparent hover:border-luxury-gold transition-all duration-300 group bg-white"
    >
      <div class="flex items-center space-x-6">
        <div class="text-xs text-gray-300 w-12 text-center font-mono tracking-wider group-hover:text-luxury-gold transition-colors">
          {{ String(video.id).padStart(2, '0') }}
        </div>
        <div>
          <h3 class="text-lg font-light tracking-tight group-hover:text-black transition-colors">
            {{ video.title }}
          </h3>
          <p class="text-[10px] text-gray-400 mt-1 uppercase tracking-wider">
            By <span class="font-bold text-gray-800">{{ video.author }}</span> 
            <span class="mx-2 text-gray-300">|</span> {{ video.created_at }} 
            <span class="mx-2 text-gray-300">|</span> Views {{ video.view_count }}
          </p>
        </div>
      </div>
      <div class="text-gray-300 group-hover:text-luxury-gold transition-colors">
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
              
              <button class="ml-auto text-xs text-gray-300 hover:text-red-500 transition-colors tracking-widest px-4 border-none bg-transparent hover:bg-transparent shadow-none hover:shadow-none h-auto hover:translate-y-0 hover:tracking-widest">
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
