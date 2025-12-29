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
            <div>
                <h1 class="text-4xl font-light tracking-tight mb-2">BULLETIN BOARD</h1>
                <div class="w-16 h-px bg-luxury-gold mb-4"></div>
                <p class="text-xs uppercase tracking-widest text-gray-500 font-medium">
                    Community & Insights
                </p>
            </div>
            
            <button 
                @click="goToWrite"
                class="px-6 py-2 bg-black text-white text-xs uppercase tracking-widest hover:bg-luxury-gold transition-colors rounded-sm"
            >
                Write Post
            </button>
        </div>

        <!-- Board List -->
        <div class="bg-white border border-gray-100 shadow-lg overflow-hidden relative min-h-[400px]">
            
            <!-- Loading State -->
            <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-white/80 z-10">
                <div class="flex flex-col items-center gap-3">
                    <div class="w-8 h-8 border-2 border-gray-200 border-t-luxury-gold rounded-full animate-spin"></div>
                    <span class="text-xs uppercase tracking-widest text-gray-400">Loading...</span>
                </div>
            </div>

            <!-- Table Header -->
            <div class="grid grid-cols-12 gap-4 p-4 border-b border-gray-100 bg-gray-50 text-xs uppercase tracking-widest text-gray-400 font-medium">
                <div class="col-span-1 text-center">No.</div>
                <div class="col-span-7 md:col-span-6">Title</div>
                <div class="col-span-2 hidden md:block text-center">Author</div>
                <div class="col-span-2 text-center">Date</div>
                <div class="col-span-1 hidden md:block text-center">Views</div>
            </div>

            <!-- Empty State -->
            <div v-if="!isLoading && posts.length === 0" class="py-20 text-center">
                <p class="text-gray-400 font-light italic">No posts found. Be the first to share your thoughts.</p>
            </div>

            <!-- Items -->
            <div v-else class="divide-y divide-gray-50">
                <div 
                    v-for="(post, index) in posts" 
                    :key="post.id"
                    @click="goToDetail(post.id)"
                    class="grid grid-cols-12 gap-4 p-5 items-center hover:bg-gray-50 cursor-pointer group transition-colors duration-200"
                >
                    <div class="col-span-1 text-center font-mono text-gray-400 text-sm">
                        {{ ((currentPage - 1) * 15) + index + 1 }}
                    </div>
                    <div class="col-span-7 md:col-span-6">
                        <h3 class="text-base font-light text-black group-hover:text-luxury-gold transition-colors duration-300 truncate pr-4">
                            {{ post.title }}
                        </h3>
                    </div>
                    <div class="col-span-2 hidden md:block text-center text-sm font-light text-gray-600">
                        {{ post.author }}
                    </div>
                    <div class="col-span-2 text-center text-xs text-gray-400 font-mono">
                        {{ formatDate(post.created_at) }}
                    </div>
                    <div class="col-span-1 hidden md:block text-center text-xs text-gray-400 font-mono">
                        {{ post.view_count }}
                    </div>
                </div>
            </div>
        </div>

        <!-- Pagination -->
        <div class="mt-8 flex justify-center gap-2" v-if="totalPages > 1">
            <button 
                @click="changePage(currentPage - 1)" 
                :disabled="currentPage === 1"
                class="w-10 h-10 border border-gray-200 flex items-center justify-center text-gray-400 hover:border-luxury-gold hover:text-luxury-gold transition-colors disabled:opacity-30 disabled:hover:border-gray-200 disabled:hover:text-gray-400"
            >
                &lt;
            </button>
            
            <button 
                v-for="page in totalPages" 
                :key="page"
                @click="changePage(page)"
                :class="currentPage === page ? 'bg-black text-white border-black' : 'text-gray-600 border-gray-200 hover:border-luxury-gold hover:text-luxury-gold'"
                class="w-10 h-10 border flex items-center justify-center text-sm font-light transition-colors"
            >
                {{ page }}
            </button>
            
            <button 
                @click="changePage(currentPage + 1)" 
                :disabled="currentPage === totalPages"
                class="w-10 h-10 border border-gray-200 flex items-center justify-center text-gray-400 hover:border-luxury-gold hover:text-luxury-gold transition-colors disabled:opacity-30 disabled:hover:border-gray-200 disabled:hover:text-gray-400"
            >
                &gt;
            </button>
        </div>
    </div>
</template>

<style scoped>
/* Additional custom styles if needed, mostly using Tailwind */
</style>
