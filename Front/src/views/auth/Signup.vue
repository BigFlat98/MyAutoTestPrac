<template>
  <div class="flex items-center justify-center min-h-screen bg-white">
    <div class="w-full max-w-sm bg-white border border-black rounded-none p-8 shadow-lg">
      <h2 class="text-2xl font-light uppercase tracking-widest text-center mb-6" style="color: #996515;">Sign Up</h2>
      <form @submit.prevent="handleSignup">
        <div class="mb-4">
          <label class="block text-sm font-light uppercase tracking-widest mb-1" for="login_id">Login ID</label>
          <input v-model="loginId" id="login_id" type="text" required class="w-full h-input border border-black rounded-none px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#996515]" />
        </div>
        <div class="mb-4">
          <label class="block text-sm font-light uppercase tracking-widest mb-1" for="nick_name">Nickname</label>
          <input v-model="nickName" id="nick_name" type="text" required class="w-full h-input border border-black rounded-none px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#996515]" />
        </div>
        <div class="mb-6">
          <label class="block text-sm font-light uppercase tracking-widest mb-1" for="login_pw">Password</label>
          <input v-model="loginPw" id="login_pw" type="password" required class="w-full h-input border border-black rounded-none px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#996515]" />
        </div>
        <div v-if="errorMsg" class="text-red-600 text-sm mb-4">{{ errorMsg }}</div>
        <button type="submit" class="w-full h-input bg-[#996515] hover:bg-[#b8860b] text-white font-light uppercase tracking-widest transition-colors duration-200">
          Create Account
        </button>
      </form>
      <div class="mt-4 text-center">
        <p class="text-sm">
          Already have an account? 
          <router-link to="/login" class="text-[#996515] hover:underline">Log in</router-link>
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
const nickName = ref('');
const loginPw = ref('');
const errorMsg = ref('');

async function handleSignup() {
  errorMsg.value = '';
  try {
    await authStore.signup({ 
        login_id: loginId.value, 
        login_pw: loginPw.value,
        nick_name: nickName.value 
    });
    alert('Account created successfully! Please log in.');
    router.push('/login');
  } catch (e) {
    errorMsg.value = authStore.authError || 'Signup failed';
  }
}
</script>

<style scoped>
.h-input {
  height: 3.2rem;
}
</style>
