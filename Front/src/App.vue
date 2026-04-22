<script setup>
import { RouterView } from 'vue-router'
import NavBar from './components/NavBar.vue'
import Footer from './components/Footer.vue'
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

onMounted(() => {
  authStore.checkAuth();
});
</script>

<style lang="scss">
// 전역 글래스모피즘 & 오로라 배경 스타일 임포트
@use '@/assets/glassmorphism.scss';
</style>

<template>
  <div class="glass-page-wrapper flex flex-col">
    <!-- Premium Aurora Background (Global) -->
    <div class="todesktop-bg fade-in">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
    </div>

    <!-- Content Area -->
    <div class="content-overlay flex flex-col flex-grow">
      <NavBar />
      
      <main class="flex-grow w-full h-full flex flex-col pt-16 md:pt-20">
        <RouterView />
      </main>

      <Footer />
    </div>
  </div>
</template>