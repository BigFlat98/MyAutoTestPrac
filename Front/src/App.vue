<script setup>
import { RouterView } from 'vue-router'
import NavBar from './components/NavBar.vue'
</script>

<template>
  <main class="min-h-screen bg-white">
    <NavBar />
    
    <RouterView />
  </main>
</template>