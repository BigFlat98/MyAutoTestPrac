<template>
  <div class="flex items-center justify-center min-h-screen bg-white">
    <div class="w-full max-w-sm bg-white border border-black rounded-none p-6 md:p-8 shadow-lg">
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
        <!-- 보안 공지 -->
        <div class="mb-4 p-3 border border-amber-300 bg-amber-50 text-xs text-amber-800 font-light leading-relaxed">
          이 사이트는 개인적으로 쓰고 싶은 기능 구현 연습을 위한 사이트입니다.<br>
          보안이 취약한 부분이 있을 수 있기 때문에 가입 시 평소에 사용하던 비밀번호는 되도록 <span class="font-medium">지양</span>해 주시기 바랍니다.<br>
          해킹에 대한 문제 발생은 운영자와 관련이 없음을 알립니다.ㅋㅋ
        </div>

        <div class="mb-4">
          <label class="block text-sm font-light uppercase tracking-widest mb-1" for="login_pw">Password</label>
          <input v-model="loginPw" id="login_pw" type="password" required class="w-full h-input border border-black rounded-none px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#996515]" placeholder="At least 8 characters" />
        </div>
        <div class="mb-5">
          <label class="block text-sm font-light uppercase tracking-widest mb-1" for="confirm_pw">Confirm Password</label>
          <input 
            v-model="confirmPw" 
            id="confirm_pw" 
            type="password" 
            required 
            class="w-full h-input border rounded-none px-3 py-2 focus:outline-none focus:ring-2 transition-colors duration-200" 
            :class="{
                'border-black focus:ring-[#996515]': !confirmPw,
                'border-red-500 focus:ring-red-500 text-red-600': isPwMismatch,
                'border-green-500 focus:ring-green-500 text-green-600': isPwMatch
            }"
          />
          <p v-if="isPwMismatch" class="text-xs text-red-500 mt-1 font-light">Passwords do not match.</p>
          <p v-if="isPwMatch" class="text-xs text-green-600 mt-1 font-light">Passwords match.</p>
        </div>

        <!-- 동의 체크박스 -->
        <div class="mb-5 flex items-start gap-2">
          <input
            v-model="agreed"
            id="agree"
            type="checkbox"
            class="mt-0.5 w-4 h-4 accent-[#996515] cursor-pointer shrink-0"
          />
          <label for="agree" class="text-xs text-gray-500 font-light leading-relaxed cursor-pointer">
            위 공지 사항을 확인하였으며 이에 동의합니다.
          </label>
        </div>

        <div v-if="errorMsg" class="text-red-600 text-sm mb-4">{{ errorMsg }}</div>
        <button
          type="submit"
          :disabled="!agreed"
          class="w-full h-input text-white font-light uppercase tracking-widest transition-colors duration-200"
          :class="agreed
            ? 'bg-[#996515] hover:bg-[#b8860b] cursor-pointer'
            : 'bg-gray-300 text-gray-400 cursor-not-allowed'"
        >
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

// Computed properties for validation feedback
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

  // Validation
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
.h-input {
  height: 3.2rem;
}
</style>
