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
  <!-- 기존 흰색/보더 속성 제거하고 glass-nav 클래스 추가 -->
  <nav class="glass-nav relative flex items-center justify-between px-4 md:px-8 py-0 z-50 slide-up" style="animation-delay: 0.1s;">
    <!-- Logo -->
    <router-link to="/" class="flex items-center transition-opacity hover:opacity-80">
      <!-- 다크 테마이므로 로고를 흰색으로 반전 (brightness-0 invert) -->
      <img src="/HadaLogo.png?v=2" alt="Hadaboni Logo" class="h-16 md:h-20 object-contain brightness-0 invert opacity-90" />
    </router-link>

    <!-- Desktop Centered Links -->
    <div class="hidden md:flex absolute left-1/2 -translate-x-1/2 gap-8">
      <router-link to="/" class="text-xs uppercase tracking-widest text-slate-300 hover:text-sky-400 transition-colors font-medium">
        Home
      </router-link>
      <router-link to="/mustdo" class="text-xs uppercase tracking-widest text-slate-300 hover:text-sky-400 transition-colors font-medium">
        Todo
      </router-link>
      <router-link to="/board" class="text-xs uppercase tracking-widest text-slate-300 hover:text-sky-400 transition-colors font-medium">
        Board
      </router-link>
      <router-link to="/chat" class="text-xs uppercase tracking-widest text-slate-300 hover:text-sky-400 transition-colors font-medium">
        Chat
      </router-link>
      <router-link to="/video" class="text-xs uppercase tracking-widest text-slate-300 hover:text-sky-400 transition-colors font-medium">
        Video
      </router-link>

    </div>

    <!-- Right Side Actions (Auth + Mobile Menu Toggle) -->
    <div class="flex items-center gap-4">
      <!-- My Page Icon -->
      <router-link
        v-if="authStore.isAuthenticated"
        to="/mypage"
        class="text-slate-300 hover:text-sky-400 transition-colors duration-200"
        title="My Page"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
        </svg>
      </router-link>

      <!-- Auth Button -->
      <div>
        <template v-if="authStore.isAuthenticated">
            <button @click="handleLogout" class="px-3 md:px-4 py-0.5 rounded-full border border-sky-400/50 text-sky-400 text-[9px] uppercase tracking-widest transition-all duration-300 hover:bg-sky-400/20 hover:text-white hover:border-sky-400 hover:shadow-[0_0_15px_rgba(56,189,248,0.4)] font-medium leading-none flex items-center h-6">
              Logout
            </button>
        </template>
        <template v-else>
            <router-link to="/login" class="px-3 md:px-4 py-0.5 rounded-full border border-sky-400/50 text-sky-400 text-[9px] uppercase tracking-widest transition-all duration-300 hover:bg-sky-400/20 hover:text-white hover:border-sky-400 hover:shadow-[0_0_15px_rgba(56,189,248,0.4)] font-medium leading-none flex items-center h-6">
              Login
            </router-link>
        </template>
      </div>

      <!-- Mobile Menu Button -->
      <button @click="isMenuOpen = !isMenuOpen" class="md:hidden flex flex-col justify-center items-center w-6 h-6 gap-1 border-none bg-transparent p-0 min-w-0 min-h-0 shadow-none hover:bg-transparent hover:shadow-none translate-y-0">
        <!-- 모바일 햄버거 흰색으로 변경 -->
        <span class="block w-5 h-0.5 bg-white transition-all duration-300" :class="{ 'rotate-45 translate-y-1.5': isMenuOpen }"></span>
        <span class="block w-5 h-0.5 bg-white transition-all duration-300" :class="{ 'opacity-0': isMenuOpen }"></span>
        <span class="block w-5 h-0.5 bg-white transition-all duration-300" :class="{ '-rotate-45 -translate-y-1.5': isMenuOpen }"></span>
      </button>
    </div>

    <!-- Mobile Menu Dropdown -->
    <div v-show="isMenuOpen" class="absolute top-full left-0 w-full glass-mobile-menu md:hidden flex flex-col p-4 gap-4 z-40 transition-all duration-300 ease-in-out">
      <router-link @click="isMenuOpen = false" to="/" class="text-sm uppercase tracking-widest text-slate-300 hover:text-sky-400 transition-colors font-medium">
        Home
      </router-link>
      <router-link @click="isMenuOpen = false" to="/mustdo" class="text-sm uppercase tracking-widest text-slate-300 hover:text-sky-400 transition-colors font-medium">
        Todo
      </router-link>
      <router-link @click="isMenuOpen = false" to="/board" class="text-sm uppercase tracking-widest text-slate-300 hover:text-sky-400 transition-colors font-medium">
        Board
      </router-link>
      <router-link @click="isMenuOpen = false" to="/chat" class="text-sm uppercase tracking-widest text-slate-300 hover:text-sky-400 transition-colors font-medium">
        Chat
      </router-link>
      <router-link @click="isMenuOpen = false" to="/video" class="text-sm uppercase tracking-widest text-slate-300 hover:text-sky-400 transition-colors font-medium">
        Video
      </router-link>

    </div>
  </nav>
</template>

<style lang="scss" scoped>
@use '@/assets/glassmorphism.scss' as *;

.glass-nav {
  @include glass-panel(0.02, 16px);
  position: fixed;
  top: 0;
  left: 4.5rem;
  right: 4.5rem;
  border-radius: 0 0 24px 24px; // 네비게이션은 아래쪽만 둥글게
  border-top: none;
  margin-bottom: 0;
  z-index: 100;
}

.glass-mobile-menu {
  @include glass-panel(0.05, 16px);
  border-radius: 0 0 24px 24px;
}
</style>