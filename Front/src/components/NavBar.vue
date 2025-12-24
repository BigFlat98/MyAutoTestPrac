<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <nav class="relative flex items-center justify-between px-8 py-3 border-b border-gray-100 bg-white z-50">
    <!-- Logo -->
    <!-- Logo -->
    <router-link to="/" class="text-4xl text-black transition-colors group hover:opacity-80" style="font-family: 'Pinyon Script', cursive;">
      Maven<span class="text-luxury-gold">H</span>
    </router-link>

    <!-- Centered Links -->
    <div class="absolute left-1/2 -translate-x-1/2 flex gap-8">
      <router-link to="/" class="text-xs uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Home
      </router-link>
      <router-link to="/playground" class="text-xs uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Playground
      </router-link>
      <router-link to="/mustdo" class="text-xs uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Todo
      </router-link>
    </div>
  </nav>
</template>