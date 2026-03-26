<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const isMenuOpen = ref(false)

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
  isMenuOpen.value = false
}
</script>

<template>
  <nav class="relative flex items-center justify-between px-4 md:px-8 py-0 border-b border-gray-100 bg-white z-50">
    <!-- Logo -->
    <router-link to="/" class="flex items-center transition-opacity hover:opacity-80">
      <img src="/HadaLogo.png?v=2" alt="Hadaboni Logo" class="h-16 md:h-20 object-contain" />
    </router-link>

    <!-- Desktop Centered Links -->
    <div class="hidden md:flex absolute left-1/2 -translate-x-1/2 gap-8">
      <router-link to="/" class="text-xs uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Home
      </router-link>
      <router-link to="/mustdo" class="text-xs uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Todo
      </router-link>
      <router-link to="/board" class="text-xs uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Board
      </router-link>
      <router-link to="/chat" class="text-xs uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Chat
      </router-link>
      <router-link to="/video" class="text-xs uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Video
      </router-link>
    </div>

    <!-- Right Side Actions (Auth + Mobile Menu Toggle) -->
    <div class="flex items-center gap-4">
      <!-- My Page Icon (로그인 시에만 표시) -->
      <router-link
        v-if="authStore.isAuthenticated"
        to="/mypage"
        class="text-gray-400 hover:text-luxury-gold transition-colors duration-200"
        title="My Page"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
        </svg>
      </router-link>

      <!-- Auth Button -->
      <div>
        <template v-if="authStore.isAuthenticated">
            <button @click="handleLogout" class="px-3 md:px-4 py-0.5 rounded-full border border-[#996515] text-[#996515] text-[9px] uppercase tracking-widest transition-all duration-300 hover:bg-[#996515] hover:text-white hover:shadow-[0_0_10px_rgba(153,101,21,0.6)] font-medium leading-none flex items-center h-6">
              Logout
            </button>
        </template>
        <template v-else>
            <router-link to="/login" class="px-3 md:px-4 py-0.5 rounded-full border border-[#996515] text-[#996515] text-[9px] uppercase tracking-widest transition-all duration-300 hover:bg-[#996515] hover:text-white hover:shadow-[0_0_10px_rgba(153,101,21,0.6)] font-medium leading-none flex items-center h-6">
              Login
            </router-link>
        </template>
      </div>

      <!-- Mobile Menu Button -->
      <button @click="isMenuOpen = !isMenuOpen" class="md:hidden flex flex-col justify-center items-center w-6 h-6 gap-1 border-none bg-transparent p-0 min-w-0 min-h-0 shadow-none hover:bg-transparent hover:shadow-none translate-y-0">
        <span class="block w-5 h-0.5 bg-black transition-all duration-300" :class="{ 'rotate-45 translate-y-1.5': isMenuOpen }"></span>
        <span class="block w-5 h-0.5 bg-black transition-all duration-300" :class="{ 'opacity-0': isMenuOpen }"></span>
        <span class="block w-5 h-0.5 bg-black transition-all duration-300" :class="{ '-rotate-45 -translate-y-1.5': isMenuOpen }"></span>
      </button>
    </div>

    <!-- Mobile Menu Dropdown -->
    <div v-show="isMenuOpen" class="absolute top-full left-0 w-full bg-white border-b border-gray-100 shadow-lg md:hidden flex flex-col p-4 gap-4 z-40 transition-all duration-300 ease-in-out">
      <router-link @click="isMenuOpen = false" to="/" class="text-sm uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Home
      </router-link>
      <router-link @click="isMenuOpen = false" to="/mustdo" class="text-sm uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Todo
      </router-link>
      <router-link @click="isMenuOpen = false" to="/board" class="text-sm uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Board
      </router-link>
      <router-link @click="isMenuOpen = false" to="/chat" class="text-sm uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Chat
      </router-link>
      <router-link @click="isMenuOpen = false" to="/video" class="text-sm uppercase tracking-widest text-gray-500 hover:text-luxury-gold transition-colors font-medium">
        Video
      </router-link>
    </div>
  </nav>
</template>