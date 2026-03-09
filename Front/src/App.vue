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

<template>
  <div class="min-h-screen bg-white flex flex-col">
    <NavBar />
    
    <main>
      <RouterView />
    </main>

    <Footer />
  </div>
</template>