<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const myPosts = ref([])
const myVideos = ref([])
const myTodos = ref([])
const isLoadingPosts = ref(false)
const isLoadingVideos = ref(false)
const isLoadingTodos = ref(false)
const isUploadingImage = ref(false)
const profileImageError = ref(false)

const fileInput = ref(null)

const user = computed(() => authStore.user)

// 탈퇴 예약 여부 및 남은 일수
const deleteDate = computed(() => user.value?.delete_date ? new Date(user.value.delete_date) : null)
const daysUntilDeletion = computed(() => {
  if (!deleteDate.value) return null
  const deleteAt = new Date(deleteDate.value)
  deleteAt.setDate(deleteAt.getDate() + 7)
  return Math.max(0, Math.ceil((deleteAt - new Date()) / (1000 * 60 * 60 * 24)))
})

const profileImageUrl = computed(() => {
  if (!user.value?.profile_image) return null
  // profile_image 컬럼에 '/static/profile/...' 형태로 저장되므로 앞에 /api만 붙임
  return `/api${user.value.profile_image}`
})

const userInitial = computed(() => {
  if (!user.value?.username) return '?'
  return user.value.username.charAt(0).toUpperCase()
})

const joinedAt = computed(() => {
  if (!user.value?.created_at) return null
  return new Date(user.value.created_at).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
})

const fetchMyPosts = async () => {
  isLoadingPosts.value = true
  try {
    const response = await api.get('/posts?author_me=true&limit=10')
    myPosts.value = response.data.posts ?? response.data
  } catch {
    myPosts.value = []
  } finally {
    isLoadingPosts.value = false
  }
}

const fetchMyVideos = async () => {
  isLoadingVideos.value = true
  try {
    const response = await api.get('/videos?uploader_me=true&limit=10')
    myVideos.value = response.data.videos ?? response.data
  } catch {
    myVideos.value = []
  } finally {
    isLoadingVideos.value = false
  }
}

const fetchMyTodos = async () => {
  isLoadingTodos.value = true
  try {
    const response = await api.get('/todos')
    myTodos.value = response.data ?? []
  } catch {
    myTodos.value = []
  } finally {
    isLoadingTodos.value = false
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleImageUpload = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  isUploadingImage.value = true
  try {
    await api.post('/auth/profile-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    await authStore.checkAuth()
    profileImageError.value = false
  } catch (err) {
    console.error('프로필 이미지 업로드 실패:', err)
  } finally {
    isUploadingImage.value = false
    event.target.value = ''
  }
}

const handleWithdraw = async () => {
  const confirmed = window.confirm(
    '정말 탈퇴하시겠습니까?\n탈퇴 요청 후 7일 이내에 취소할 수 있으며, 7일이 지나면 계정과 모든 데이터가 영구 삭제됩니다.'
  )
  if (!confirmed) return
  try {
    await api.post('/auth/withdraw')
    await authStore.checkAuth()
  } catch (err) {
    console.error('탈퇴 요청 실패:', err)
  }
}

const handleCancelWithdraw = async () => {
  const confirmed = window.confirm('탈퇴를 취소하시겠습니까? 계정이 정상 복구됩니다.')
  if (!confirmed) return
  try {
    await api.delete('/auth/withdraw')
    await authStore.checkAuth()
  } catch (err) {
    console.error('탈퇴 취소 실패:', err)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('ko-KR')
}

const goToPost = (id) => {
  router.push({ name: 'board-detail', params: { id } })
}

onMounted(async () => {
  await Promise.all([fetchMyPosts(), fetchMyVideos(), fetchMyTodos()])
})
</script>

<template>
  <div class="max-w-5xl mx-auto py-12 px-6">

    <!-- Page Header -->
    <header class="glass-header slide-up mb-12" style="animation-delay: 0.1s; display: block; text-align: left; padding: 20px 32px; border-radius: 20px;">
      <h1 class="glass-title text-4xl mb-2">MY PAGE</h1>
      <p class="glass-subtitle font-mono text-sm">
        Profile &amp; Activity
      </p>
    </header>

    <!-- Profile Section -->
    <div class="border border-gray-100 shadow-sm mb-10">
      <div class="flex flex-col md:flex-row items-center md:items-start gap-8 p-8 md:p-10">

        <!-- Avatar -->
        <div class="relative flex-shrink-0 group cursor-pointer" @click="triggerFileInput">
          <div
            class="w-24 h-24 rounded-full overflow-hidden border-2 flex items-center justify-center bg-gray-50 transition-all duration-300 group-hover:border-[#C9A227]"
            style="border-color: #e5e7eb;"
          >
            <img
              v-if="profileImageUrl && !profileImageError"
              :src="profileImageUrl"
              alt="Profile"
              class="w-full h-full object-cover"
              @error="profileImageError = true"
            />
            <span v-else class="text-3xl font-light text-gray-400 select-none">
              {{ userInitial }}
            </span>
          </div>

          <!-- Upload Overlay -->
          <div
            class="absolute inset-0 rounded-full flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
          >
            <span v-if="isUploadingImage" class="w-5 h-5 border-2 border-white/40 border-t-white rounded-full animate-spin"></span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5V19a1.5 1.5 0 001.5 1.5h15A1.5 1.5 0 0021 19v-2.5M12 3v13m0-13l-3.5 3.5M12 3l3.5 3.5" />
            </svg>
          </div>

          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            class="hidden"
            @change="handleImageUpload"
          />
        </div>

        <!-- User Info -->
        <div class="flex-1 text-center md:text-left">
          <h2 class="text-2xl font-light tracking-wide text-black mb-1">
            {{ user?.username ?? '—' }}
          </h2>
          <p v-if="joinedAt" class="text-xs uppercase tracking-widest text-gray-400 font-mono mb-4">
            Joined {{ joinedAt }}
          </p>

          <!-- Stats -->
          <div class="flex flex-wrap gap-6 justify-center md:justify-start mt-4">
            <div class="flex flex-col items-center md:items-start gap-0.5">
              <span class="text-xl font-light text-black font-mono">{{ myPosts.length }}</span>
              <span class="text-[10px] uppercase tracking-widest text-gray-400">Posts</span>
            </div>
            <div class="w-px bg-gray-100 hidden md:block self-stretch"></div>
            <div class="flex flex-col items-center md:items-start gap-0.5">
              <span class="text-xl font-light text-black font-mono">{{ myVideos.length }}</span>
              <span class="text-[10px] uppercase tracking-widest text-gray-400">Videos</span>
            </div>
            <div class="w-px bg-gray-100 hidden md:block self-stretch"></div>
            <div class="flex flex-col items-center md:items-start gap-0.5">
              <span class="text-xl font-light text-black font-mono">{{ myTodos.length }}</span>
              <span class="text-[10px] uppercase tracking-widest text-gray-400">Todos</span>
            </div>
          </div>

          <p class="mt-5 text-[10px] uppercase tracking-widest text-gray-400">
            프로필 사진을 클릭하면 변경할 수 있습니다.
          </p>
        </div>
      </div>
    </div>

    <!-- My Posts Section -->
    <section class="mb-10">
      <div class="flex items-center gap-4 mb-5">
        <h2 class="text-xs uppercase tracking-widest font-medium text-black">My Posts</h2>
        <div class="flex-1 h-px bg-gray-100"></div>
        <span class="text-xs font-mono text-gray-400">{{ myPosts.length }}</span>
      </div>

      <div class="border border-gray-100 shadow-sm overflow-hidden relative min-h-[120px]">

        <!-- Loading -->
        <div v-if="isLoadingPosts" class="absolute inset-0 flex items-center justify-center bg-white/80 z-10">
          <div class="flex flex-col items-center gap-2">
            <div class="w-6 h-6 border-2 border-gray-200 border-t-[#C9A227] rounded-full animate-spin"></div>
            <span class="text-[10px] uppercase tracking-widest text-gray-400">Loading...</span>
          </div>
        </div>

        <!-- Empty -->
        <div v-else-if="myPosts.length === 0" class="flex items-center justify-center py-12">
          <p class="text-sm font-light text-gray-400 italic">작성한 게시글이 없습니다.</p>
        </div>

        <!-- List -->
        <div v-else class="divide-y divide-gray-50">
          <div
            v-for="post in myPosts"
            :key="post.id"
            @click="goToPost(post.id)"
            class="flex items-center gap-4 px-6 py-4 hover:bg-gray-50 cursor-pointer group transition-colors duration-200"
          >
            <span class="text-xs font-mono text-gray-300 w-6 flex-shrink-0">#{{ post.id }}</span>
            <span class="flex-1 text-sm font-light text-black group-hover:text-[#C9A227] transition-colors duration-300 truncate">
              {{ post.title }}
            </span>
            <span class="text-[11px] font-mono text-gray-400 flex-shrink-0">{{ formatDate(post.created_at) }}</span>
            <span class="text-[11px] font-mono text-gray-300 flex-shrink-0 hidden md:block">{{ post.view_count }} views</span>
          </div>
        </div>
      </div>
    </section>

    <!-- My Videos Section -->
    <section>
      <div class="flex items-center gap-4 mb-5">
        <h2 class="text-xs uppercase tracking-widest font-medium text-black">My Videos</h2>
        <div class="flex-1 h-px bg-gray-100"></div>
        <span class="text-xs font-mono text-gray-400">{{ myVideos.length }}</span>
      </div>

      <div class="border border-gray-100 shadow-sm overflow-hidden relative min-h-[120px]">

        <!-- Loading -->
        <div v-if="isLoadingVideos" class="absolute inset-0 flex items-center justify-center bg-white/80 z-10">
          <div class="flex flex-col items-center gap-2">
            <div class="w-6 h-6 border-2 border-gray-200 border-t-[#C9A227] rounded-full animate-spin"></div>
            <span class="text-[10px] uppercase tracking-widest text-gray-400">Loading...</span>
          </div>
        </div>

        <!-- Empty -->
        <div v-else-if="myVideos.length === 0" class="flex items-center justify-center py-12">
          <p class="text-sm font-light text-gray-400 italic">등록한 영상이 없습니다.</p>
        </div>

        <!-- List -->
        <div v-else class="divide-y divide-gray-50">
          <div
            v-for="video in myVideos"
            :key="video.id"
            class="flex items-center gap-4 px-6 py-4 group"
          >
            <!-- YouTube Thumbnail -->
            <div class="w-16 h-10 flex-shrink-0 bg-gray-100 overflow-hidden">
              <img
                v-if="video.video_key"
                :src="`https://img.youtube.com/vi/${video.video_key}/mqdefault.jpg`"
                :alt="video.title"
                class="w-full h-full object-cover"
              />
            </div>

            <div class="flex-1 min-w-0">
              <p class="text-sm font-light text-black truncate">{{ video.title }}</p>
              <div class="flex items-center gap-3 mt-0.5">
                <span
                  v-if="video.tag_name"
                  class="text-[10px] uppercase tracking-widest px-1.5 py-0.5 border"
                  style="border-color: #C9A227; color: #C9A227;"
                >
                  {{ video.tag_name }}
                </span>
                <span class="text-[11px] font-mono text-gray-400">{{ formatDate(video.created_at) }}</span>
              </div>
            </div>

            <div class="flex items-center gap-4 flex-shrink-0 text-[11px] font-mono text-gray-300 hidden md:flex">
              <span>{{ video.view_count ?? 0 }} views</span>
              <span>{{ video.like_count ?? 0 }} likes</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 회원 탈퇴 영역 -->
    <div class="mt-16 flex justify-end">
      <!-- 탈퇴 예약 중 -->
      <div v-if="deleteDate" class="flex flex-col items-end gap-2">
        <p class="text-[11px] font-mono text-red-400">
          탈퇴 예정 — {{ daysUntilDeletion }}일 후 계정이 영구 삭제됩니다
        </p>
        <button
          @click="handleCancelWithdraw"
          class="px-4 py-1.5 text-[11px] uppercase tracking-widest font-medium border rounded-sm
                 border-red-300 text-red-400 bg-transparent
                 hover:border-red-400 hover:text-red-500 hover:bg-red-50
                 transition-colors duration-200 h-auto min-h-0 min-w-0 shadow-none
                 hover:shadow-none hover:-translate-y-0 hover:tracking-widest"
        >
          탈퇴 취소
        </button>
      </div>

      <!-- 탈퇴 버튼 -->
      <button
        v-else
        @click="handleWithdraw"
        class="px-4 py-1.5 text-[11px] uppercase tracking-widest font-medium border rounded-sm
               border-red-200 text-red-300 bg-transparent
               hover:border-red-400 hover:text-red-500 hover:bg-red-50
               transition-colors duration-200 h-auto min-h-0 min-w-0 shadow-none
               hover:shadow-none hover:-translate-y-0 hover:tracking-widest"
      >
        회원 탈퇴
      </button>
    </div>

  </div>
</template>
