<template>
  <div class="flex items-center justify-center min-h-[calc(100vh-160px)]">
    <div class="w-full max-w-md glass-card p-8 md:p-10 slide-up" style="animation-delay: 0.1s;">
      <h2 class="glass-title text-3xl text-center mb-8">Login</h2>
      
      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label class="block text-xs uppercase tracking-widest text-slate-400 mb-2" for="login_id">Login ID</label>
          <input 
            v-model="loginId" 
            id="login_id" 
            type="text" 
            required 
            placeholder="Enter your ID"
            class="w-full h-[3.2rem] bg-white/5 border border-white/10 px-4 focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all font-light text-white placeholder-slate-500 rounded-lg" 
          />
        </div>
        
        <div>
          <label class="block text-xs uppercase tracking-widest text-slate-400 mb-2" for="login_pw">Password</label>
          <input 
            v-model="loginPw" 
            id="login_pw" 
            type="password" 
            required 
            placeholder="Enter your password"
            class="w-full h-[3.2rem] bg-white/5 border border-white/10 px-4 focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all font-light text-white placeholder-slate-500 rounded-lg" 
          />
        </div>

        <div v-if="errorMsg" class="text-red-400 text-xs bg-red-400/10 border border-red-400/20 p-3 rounded-lg flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ errorMsg }}
        </div>

        <button 
          type="submit" 
          class="w-full h-[3.2rem] bg-sky-500/20 text-sky-400 text-xs uppercase tracking-widest hover:bg-sky-400 hover:text-white transition-all duration-300 border border-sky-400/50 rounded-lg shadow-[0_0_15px_rgba(56,189,248,0.2)] hover:shadow-[0_0_20px_rgba(56,189,248,0.6)]"
        >
          Sign In
        </button>
      </form>

      <div class="mt-8 text-center border-t border-white/10 pt-6">
         <p class="text-sm text-slate-400 font-light">
           Don't have an account? 
           <router-link to="/signup" class="text-sky-400 hover:text-sky-300 transition-colors ml-1 font-medium">Sign up</router-link>
         </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const loginId = ref('');
const loginPw = ref('');
const errorMsg = ref('');

async function handleLogin() {
  errorMsg.value = '';
  try {
    await authStore.login({ login_id: loginId.value, login_pw: loginPw.value });
    router.push('/');
  } catch (e) {
    errorMsg.value = authStore.authError || 'Login failed';
  }
}
</script>

<style scoped>
</style>
