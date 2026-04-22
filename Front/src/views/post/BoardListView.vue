<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'

const router = useRouter()
const posts = ref([])
const isLoading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1) // Mock for now

// Fetch Posts
const fetchPosts = async () => {
    isLoading.value = true
    try {
        const response = await api.get(`/posts?page=${currentPage.value}&limit=15`)
        posts.value = response.data.posts
        totalPages.value = Math.ceil(response.data.total / 15)
    } catch (error) {
        console.error('Failed to fetch posts:', error)
    } finally {
        isLoading.value = false
    }
}

const changePage = (page) => {
    if (page < 1 || page > totalPages.value) return
    currentPage.value = page
    fetchPosts()
}

const goToWrite = () => {
    router.push({ name: 'board-write' })
}

const goToDetail = (id) => {
    router.push({ name: 'board-detail', params: { id } })
}

const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
    fetchPosts()
})
</script>

<template>
    <div class="max-w-6xl mx-auto py-12 px-6">
        <!-- Header -->
        <div class="mb-12 flex flex-col md:flex-row justify-between items-end gap-6">
            <header class="glass-header slide-up text-left" style="animation-delay: 0.1s; padding: 20px 32px; border-radius: 20px;">
                <h1 class="glass-title text-4xl mb-2">BULLETIN BOARD</h1>
                <p class="glass-subtitle font-mono text-sm">Community & Insights</p>
            </header>
            
            <button 
                @click="goToWrite"
                class="px-6 py-2 bg-sky-500/20 text-sky-400 text-xs uppercase tracking-widest border border-sky-400/50 hover:bg-sky-400 hover:text-white hover:border-sky-400 transition-all rounded-full shadow-[0_0_15px_rgba(56,189,248,0.2)] hover:shadow-[0_0_20px_rgba(56,189,248,0.6)]"
            >
                Write Post
            </button>
        </div>

        <!-- Board List -->
        <div class="glass-card overflow-hidden relative min-h-[400px] p-0 border-white/10 slide-up" style="animation-delay: 0.2s;">
            
            <!-- Loading State -->
            <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm z-10">
                <div class="flex flex-col items-center gap-3">
                    <div class="w-8 h-8 border-2 border-white/20 border-t-sky-400 rounded-full animate-spin"></div>
                    <span class="text-xs uppercase tracking-widest text-slate-300">Loading...</span>
                </div>
            </div>

            <!-- Table Header -->
            <div class="grid grid-cols-12 gap-4 p-4 border-b border-white/10 bg-white/5 text-xs uppercase tracking-widest text-slate-400 font-medium">
                <div class="col-span-1 text-center">No.</div>
                <div class="col-span-7 md:col-span-6">Title</div>
                <div class="col-span-2 hidden md:block text-center">Author</div>
                <div class="col-span-2 text-center">Date</div>
                <div class="col-span-1 hidden md:block text-center">Views</div>
            </div>

            <!-- Empty State -->
            <div v-if="!isLoading && posts.length === 0" class="py-20 text-center">
                <p class="text-slate-400 font-light italic">No posts found. Be the first to share your thoughts.</p>
            </div>

            <!-- Items -->
            <div v-else class="divide-y divide-white/5">
                <div 
                    v-for="(post, index) in posts" 
                    :key="post.id"
                    @click="goToDetail(post.id)"
                    class="grid grid-cols-12 gap-4 p-5 items-center hover:bg-white/5 cursor-pointer group transition-colors duration-200"
                >
                    <div class="col-span-1 text-center font-mono text-slate-500 text-sm group-hover:text-sky-400 transition-colors">
                        {{ ((currentPage - 1) * 15) + index + 1 }}
                    </div>
                    <div class="col-span-7 md:col-span-6">
                        <h3 class="text-base font-light text-slate-200 group-hover:text-sky-300 transition-colors duration-300 truncate pr-4">
                            {{ post.title }}
                        </h3>
                    </div>
                    <div class="col-span-2 hidden md:block text-center text-sm font-light text-slate-400">
                        {{ post.author }}
                    </div>
                    <div class="col-span-2 text-center text-xs text-slate-500 font-mono">
                        {{ formatDate(post.created_at) }}
                    </div>
                    <div class="col-span-1 hidden md:block text-center text-xs text-slate-500 font-mono">
                        {{ post.view_count }}
                    </div>
                </div>
            </div>
        </div>

        <!-- Pagination -->
        <div class="mt-8 flex justify-center gap-2 slide-up" style="animation-delay: 0.3s;" v-if="totalPages > 1">
            <button 
                @click="changePage(currentPage - 1)" 
                :disabled="currentPage === 1"
                class="w-10 h-10 border border-white/20 rounded-full flex items-center justify-center text-slate-400 bg-transparent hover:border-sky-400 hover:text-sky-400 hover:shadow-[0_0_15px_rgba(56,189,248,0.3)] transition-all disabled:opacity-30 disabled:hover:border-white/20 disabled:hover:text-slate-400 disabled:hover:shadow-none"
            >
                &lt;
            </button>
            
            <button 
                v-for="page in totalPages" 
                :key="page"
                @click="changePage(page)"
                :class="currentPage === page ? 'bg-sky-500/20 text-sky-400 border-sky-400 shadow-[0_0_15px_rgba(56,189,248,0.3)]' : 'text-slate-400 border-white/20 bg-transparent hover:border-sky-400 hover:text-sky-400 hover:shadow-[0_0_15px_rgba(56,189,248,0.3)]'"
                class="w-10 h-10 border rounded-full flex items-center justify-center text-sm font-light transition-all"
            >
                {{ page }}
            </button>
            
            <button 
                @click="changePage(currentPage + 1)" 
                :disabled="currentPage === totalPages"
                class="w-10 h-10 border border-white/20 rounded-full flex items-center justify-center text-slate-400 bg-transparent hover:border-sky-400 hover:text-sky-400 hover:shadow-[0_0_15px_rgba(56,189,248,0.3)] transition-all disabled:opacity-30 disabled:hover:border-white/20 disabled:hover:text-slate-400 disabled:hover:shadow-none"
            >
                &gt;
            </button>
        </div>
    </div>
</template>

<style scoped>
</style>
