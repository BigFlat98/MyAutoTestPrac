<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <nav class="relative flex items-center justify-between px-8 py-3 border-b border-gray-100 bg-white z-50">
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
      <router-link to="/board" class="text-xs uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Board
      </router-link>
    </div>

    <!-- Right Side Auth -->
    <div>
      <template v-if="authStore.isAuthenticated">
          <button @click="handleLogout" class="px-4 py-0.5 rounded-full border border-[#996515] text-[#996515] text-[9px] uppercase tracking-widest transition-all duration-300 hover:bg-[#996515] hover:text-white hover:shadow-[0_0_10px_rgba(153,101,21,0.6)] font-medium leading-none flex items-center h-6">
            Logout
          </button>
      </template>
      <template v-else>
          <router-link to="/login" class="px-4 py-0.5 rounded-full border border-[#996515] text-[#996515] text-[9px] uppercase tracking-widest transition-all duration-300 hover:bg-[#996515] hover:text-white hover:shadow-[0_0_10px_rgba(153,101,21,0.6)] font-medium leading-none flex items-center h-6">
            Login
          </router-link>
      </template>
    </div>
  </nav>
</template>