<script setup>
import VideoItem from './VideoItem.vue';

defineProps({
  videos: {
    type: Array,
    required: true
  }
});
const emit = defineEmits(['delete']);
</script>

<template>
  <div class="border-t border-black">
    <VideoItem 
      v-for="video in videos" 
      :key="video.id" 
      :video="video" 
      @delete="$emit('delete', $event)"
    />
  </div>
</template>
