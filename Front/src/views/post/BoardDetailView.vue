<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api'
import { useAuthStore } from '@/stores/auth'
import CommentItem from './CommentItem.vue'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const postId = route.params.id

const post = ref(null)
const comments = ref([])
const newComment = ref('')
const isLoading = ref(false)

const parsedContent = computed(() => {
    if (!post.value || !post.value.content) return []
    
    const text = post.value.content
    const regex = /!\[(.*?)\]\((.*?)\)/g
    
    const segments = []
    let lastIndex = 0
    let match
    
    while ((match = regex.exec(text)) !== null) {
        if (match.index > lastIndex) {
            segments.push({
                type: 'text',
                content: text.substring(lastIndex, match.index)
            })
        }
        segments.push({
            type: 'image',
            alt: match[1],
            src: match[2]
        })
        lastIndex = regex.lastIndex
    }
    
    if (lastIndex < text.length) {
        segments.push({
            type: 'text',
            content: text.substring(lastIndex)
        })
    }
    
    return segments
})

const fetchPostDetail = async () => {
    isLoading.value = true
    try {
        const [postRes, commentRes] = await Promise.all([
            api.get(`/posts/${postId}`),
            api.get(`/posts/${postId}/comments`)
        ])
        
        post.value = postRes.data
        post.value.content = post.value.description 
        comments.value = commentRes.data

    } catch (error) {
        console.error('Failed to load post:', error)
        alert('Post not found or error loading data.')
        router.back()
    } finally {
        isLoading.value = false
    }
}

const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleString()
}

const goBack = () => {
    router.push({ name: 'board-list' })
}

const submitComment = async () => {
    if (!newComment.value.trim()) return
    
    try {
        await api.post(`/posts/${postId}/comments`, {
            description: newComment.value,
            reply_id: null
        })
        newComment.value = ''
        const res = await api.get(`/posts/${postId}/comments`)
        comments.value = res.data
    } catch (error) {
        console.error('Failed to submit comment:', error)
        alert('Error submitting comment.')
    }
}

const deletePost = async () => {
    if(confirm("Are you sure you want to delete this post?")) {
        try {
            await api.delete(`/posts/${postId}`)
            router.push({ name: 'board-list' })
        } catch (error) {
            console.error('Failed to delete post:', error)
            alert('Error deleting post.')
        }
    }
}

const editPost = () => {
    router.push({ name: 'board-edit', params: { id: postId } })
}

const handleReply = (id) => {
    const content = prompt("Enter your reply:")
    if(content) {
        api.post(`/posts/${postId}/comments`, {
            description: content,
            reply_id: id
        }).then(async () => {
             const res = await api.get(`/posts/${postId}/comments`)
             comments.value = res.data
        }).catch(err => alert("Failed to reply"))
    }
}

const handleModify = (id) => {
    alert(`Modify comment ${id} (Implementation pending)`)
}

const handleDelete = async (id) => {
    if(confirm('Delete this comment?')) {
        try {
            await api.delete(`/posts/comments/${id}`)
            const res = await api.get(`/posts/${postId}/comments`)
            comments.value = res.data
        } catch (error) {
            console.error('Failed to delete comment:', error)
            alert('Error deleting comment.')
        }
    }
}

onMounted(() => {
    fetchPostDetail()
})
</script>

<template>
    <div class="max-w-[1400px] mx-auto py-12 px-6">
        
        <!-- Navigation -->
        <button 
            @click="goBack" 
            class="mb-8 px-3 py-1 bg-sky-400/10 text-sky-400 border border-sky-400/20 hover:bg-sky-400 hover:text-slate-900 transition-all text-[10px] uppercase tracking-wider rounded flex items-center gap-2 slide-up" style="animation-delay: 0.1s;"
        >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
            Back to Board
        </button>

        <div v-if="isLoading" class="py-20 text-center">
            <div class="w-8 h-8 border-2 border-white/20 border-t-sky-400 rounded-full animate-spin mx-auto mb-4"></div>
            <span class="text-xs text-slate-400 uppercase tracking-widest">Loading Post...</span>
        </div>

        <div v-else-if="post" class="glass-card overflow-hidden p-0 slide-up" style="animation-delay: 0.2s;">
            <!-- Article Header -->
            <div class="p-8 md:p-12 border-b border-white/10 bg-white/5 backdrop-blur-md">
                <span class="block text-xs uppercase tracking-widest text-sky-400 mb-4 font-medium">Article</span>
                <h1 class="text-3xl md:text-4xl font-light text-slate-100 mb-6 leading-tigher">
                    {{ post.title }}
                </h1>
                
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 text-xs font-mono text-slate-400">
                    <div class="flex items-center gap-4">
                        <span class="text-sky-300 font-medium">{{ post.author }}</span>
                        <span class="w-px h-3 bg-white/20"></span>
                        <span>{{ formatDate(post.created_at) }}</span>
                    </div>
                    <div class="flex items-center gap-4">
                        <span>Views {{ post.view_count }}</span>
                        <!-- Owner Actions -->
                        <div class="flex gap-2" v-if="authStore.user">
                             <button 
                                v-if="post.author === authStore.user.nick_name || post.author_id === authStore.user.id" 
                                @click="editPost" 
                                class="px-3 py-1 bg-sky-400/10 text-sky-400 border border-sky-400/20 hover:bg-sky-400 hover:text-slate-900 transition-all text-[10px] uppercase tracking-widest leading-none rounded-full"
                            >
                                Edit
                            </button>
                             <button 
                                v-if="post.author === authStore.user.nick_name || post.author_id === authStore.user.id || authStore.user.check_admin"
                                @click="deletePost" 
                                class="px-3 py-1 bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500 hover:text-slate-900 transition-all text-[10px] uppercase tracking-widest leading-none rounded-full"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Article Body -->
            <div class="p-8 md:p-12 min-h-[300px]">
                <div v-if="post.image" class="mb-8 flex justify-center bg-black/20 rounded-lg p-4 border border-white/10">
                    <img :src="post.image" alt="Post Image" class="max-w-full max-h-[600px] h-auto object-contain shadow-sm rounded-lg" />
                </div>
                
                <div class="prose max-w-none font-light text-slate-200 leading-relaxed whitespace-pre-wrap text-left indent-4">
                    <template v-for="(segment, index) in parsedContent" :key="index">
                        <img 
                            v-if="segment.type === 'image'" 
                            :src="segment.src" 
                            :alt="segment.alt" 
                            class="max-w-full h-auto mx-auto my-4 shadow-sm rounded-lg"
                        />
                        <span v-else>{{ segment.content }}</span>
                    </template>
                </div>
            </div>

            <!-- Comments Section -->
            <div class="bg-black/20 p-8 md:p-12 border-t border-white/10">
                <h3 class="text-sm uppercase tracking-widest text-slate-200 mb-8 flex items-center gap-2">
                    Comments <span class="bg-sky-500 text-white text-[10px] px-2 py-0.5 rounded-full">{{ comments.length }}</span>
                </h3>

                <!-- Comment Input -->
                <div class="mb-10 flex gap-4">
                    <div class="w-10 h-10 bg-white/10 rounded-full flex-shrink-0"></div> <!-- Avatar Placeholder -->
                    <div class="flex-1">
                        <textarea 
                            v-model="newComment"
                            rows="3" 
                            placeholder="Join the discussion..." 
                            class="w-full bg-white/5 border border-white/10 text-white p-4 focus:border-sky-400 focus:ring-1 focus:ring-sky-400 focus:outline-none font-light text-sm transition-all resize-none mb-2 rounded-lg"
                        ></textarea>
                        <div class="flex justify-end">
                            <button 
                                @click="submitComment"
                                class="px-4 py-1.5 bg-sky-400/10 text-sky-400 border border-sky-400/20 hover:bg-sky-400 hover:text-slate-900 transition-all text-[10px] uppercase tracking-widest leading-none rounded-full"
                            >
                                Post Comment
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Comment List -->
                <div class="space-y-8">
                     <CommentItem 
                        v-for="comment in comments" 
                        :key="comment.id" 
                        :comment="comment"
                        @reply="handleReply"
                        @modify="handleModify"
                        @delete="handleDelete"
                     />
                </div>
            </div>

        </div>
    </div>
</template>
