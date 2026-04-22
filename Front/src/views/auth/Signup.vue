<template>
  <div class="flex items-center justify-center min-h-[calc(100vh-160px)] py-12">
    <div class="w-full max-w-md glass-card p-8 md:p-10 slide-up" style="animation-delay: 0.1s;">
      <h2 class="glass-title text-3xl text-center mb-8">Sign Up</h2>
      
      <form @submit.prevent="handleSignup" class="space-y-5">
        <div>
          <label class="block text-xs uppercase tracking-widest text-slate-400 mb-2" for="login_id">Login ID</label>
          <input 
            v-model="loginId" 
            id="login_id" 
            type="text" 
            required 
            placeholder="Choose an ID"
            class="w-full h-[3.2rem] bg-white/5 border border-white/10 px-4 focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all font-light text-white placeholder-slate-500 rounded-lg" 
          />
        </div>
        
        <div>
          <label class="block text-xs uppercase tracking-widest text-slate-400 mb-2" for="nick_name">Nickname</label>
          <input 
            v-model="nickName" 
            id="nick_name" 
            type="text" 
            required 
            placeholder="Your nickname"
            class="w-full h-[3.2rem] bg-white/5 border border-white/10 px-4 focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all font-light text-white placeholder-slate-500 rounded-lg" 
          />
        </div>

        <!-- 보안 공지 -->
        <div class="p-4 bg-amber-400/5 border border-amber-400/20 rounded-lg text-[11px] text-amber-200/70 font-light leading-relaxed">
          <div class="flex items-center gap-2 mb-2 text-amber-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span class="font-medium uppercase tracking-widest">Security Notice</span>
          </div>
          이 사이트는 개인적 기능 구현 연습을 위한 공간입니다.<br>
          가급적 평소 사용하시던 비밀번호는 <span class="text-amber-400 font-medium">사용하지 말아주시기</span> 바랍니다.<br>
          해킹 등 문제 발생 시 운영자는 책임을 지지 않습니다.
        </div>

        <div>
          <label class="block text-xs uppercase tracking-widest text-slate-400 mb-2" for="login_pw">Password</label>
          <input 
            v-model="loginPw" 
            id="login_pw" 
            type="password" 
            required 
            placeholder="At least 8 characters"
            class="w-full h-[3.2rem] bg-white/5 border border-white/10 px-4 focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all font-light text-white placeholder-slate-500 rounded-lg" 
          />
        </div>

        <div>
          <label class="block text-xs uppercase tracking-widest text-slate-400 mb-2" for="confirm_pw">Confirm Password</label>
          <input 
            v-model="confirmPw" 
            id="confirm_pw" 
            type="password" 
            required 
            placeholder="Repeat password"
            class="w-full h-[3.2rem] bg-white/5 border px-4 focus:outline-none focus:ring-1 transition-all font-light text-white rounded-lg" 
            :class="{
                'border-white/10 focus:border-sky-400 focus:ring-sky-400': !confirmPw,
                'border-red-400 focus:border-red-400 focus:ring-red-400': isPwMismatch,
                'border-emerald-400 focus:border-emerald-400 focus:ring-emerald-400': isPwMatch
            }"
          />
          <p v-if="isPwMismatch" class="text-[10px] text-red-400 mt-1 font-light tracking-wide">Passwords do not match.</p>
          <p v-if="isPwMatch" class="text-[10px] text-emerald-400 mt-1 font-light tracking-wide">Passwords match.</p>
        </div>

        <!-- 동의 체크박스 -->
        <div class="flex items-start gap-3 py-2">
          <div class="relative flex items-center">
            <input
              v-model="agreed"
              id="agree"
              type="checkbox"
              class="w-4 h-4 rounded border-white/10 bg-white/5 text-sky-400 focus:ring-sky-400 focus:ring-offset-0 transition-all cursor-pointer accent-sky-400"
            />
          </div>
          <label for="agree" class="text-[11px] text-slate-400 font-light leading-relaxed cursor-pointer select-none">
            위 보안 공지 사항을 확인하였으며 이에 동의합니다.
          </label>
        </div>

        <div v-if="errorMsg" class="text-red-400 text-xs bg-red-400/10 border border-red-400/20 p-3 rounded-lg flex items-center gap-2">
          {{ errorMsg }}
        </div>

        <button
          type="submit"
          :disabled="!agreed"
          class="w-full h-[3.2rem] text-xs uppercase tracking-widest transition-all duration-300 border rounded-lg"
          :class="agreed
            ? 'bg-sky-500/20 text-sky-400 border-sky-400/50 hover:bg-sky-400 hover:text-white shadow-[0_0_15px_rgba(56,189,248,0.2)] hover:shadow-[0_0_20px_rgba(56,189,248,0.6)] cursor-pointer'
            : 'bg-white/5 text-slate-500 border-white/5 cursor-not-allowed'"
        >
          Create Account
        </button>
      </form>

      <div class="mt-8 text-center border-t border-white/10 pt-6">
        <p class="text-sm text-slate-400 font-light">
          Already have an account? 
          <router-link to="/login" class="text-sky-400 hover:text-sky-300 transition-colors ml-1 font-medium">Log in</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const loginId = ref('');
const nickName = ref('');
const loginPw = ref('');
const confirmPw = ref('');
const errorMsg = ref('');
const agreed = ref(false);

const isPwMismatch = computed(() => {
    return loginPw.value && confirmPw.value && loginPw.value !== confirmPw.value;
});

const isPwMatch = computed(() => {
    return loginPw.value && confirmPw.value && loginPw.value === confirmPw.value;
});

async function handleSignup() {
  errorMsg.value = '';

  if (!agreed.value) {
    errorMsg.value = '공지 사항에 동의해 주세요.';
    return;
  }

  if (loginPw.value.length < 8) {
      errorMsg.value = "Password must be at least 8 characters long.";
      return;
  }

  if (loginPw.value !== confirmPw.value) {
      errorMsg.value = "Passwords do not match.";
      return;
  }

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
</style>
