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
    // Regex to capture ![alt](url)
    const regex = /!\[(.*?)\]\((.*?)\)/g
    
    const segments = []
    let lastIndex = 0
    let match
    
    while ((match = regex.exec(text)) !== null) {
        // Text before match
        if (match.index > lastIndex) {
            segments.push({
                type: 'text',
                content: text.substring(lastIndex, match.index)
            })
        }
        
        // Image match
        segments.push({
            type: 'image',
            alt: match[1],
            src: match[2]
        })
        
        lastIndex = regex.lastIndex
    }
    
    // Remaining text
    if (lastIndex < text.length) {
        segments.push({
            type: 'text',
            content: text.substring(lastIndex)
        })
    }
    
    return segments
})

// Fetch Post Details
// Fetch Post Details
const fetchPostDetail = async () => {
    isLoading.value = true
    try {
        const [postRes, commentRes] = await Promise.all([
            api.get(`/posts/${postId}`),
            api.get(`/posts/${postId}/comments`)
        ])
        
        post.value = postRes.data
        // Adapt backend 'description' to frontend 'content'
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
        // Reload comments
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
    // Navigate to write view with ID
    router.push({ name: 'board-edit', params: { id: postId } })
}

const handleReply = (id) => {
    // Logic for replying to a comment (e.g. set reply_id and focus input, or open modal)
    // For now, let's just use a prompt or simple logic
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
            // Reload comments
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
    <div class="max-w-5xl mx-auto py-12 px-6">
        
        <!-- Navigation -->
        <button 
            @click="goBack" 
            class="mb-8 text-xs uppercase tracking-widest text-gray-400 hover:text-black transition-colors flex items-center gap-2"
        >
            &larr; Back to Board
        </button>

        <div v-if="isLoading" class="py-20 text-center">
            <div class="w-8 h-8 border-2 border-gray-200 border-t-luxury-gold rounded-full animate-spin mx-auto mb-4"></div>
            <span class="text-xs text-gray-400 uppercase tracking-widest">Loading Post...</span>
        </div>

        <div v-else-if="post" class="bg-white border border-gray-100 shadow-xl overflow-hidden">
            <!-- Article Header -->
            <div class="p-8 md:p-12 border-b border-gray-50 bg-gray-50/30">
                <span class="block text-xs uppercase tracking-widest text-luxury-gold mb-4 font-medium">Article</span>
                <h1 class="text-3xl md:text-4xl font-light text-black mb-6 leading-tigher">
                    {{ post.title }}
                </h1>
                
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 text-xs font-mono text-gray-500">
                    <div class="flex items-center gap-4">
                        <span class="text-black font-medium">{{ post.author }}</span>
                        <span class="w-px h-3 bg-gray-300"></span>
                        <span>{{ formatDate(post.created_at) }}</span>
                    </div>
                    <div class="flex items-center gap-4">
                        <span>Views {{ post.view_count }}</span>
                        <!-- Owner Actions -->
                        <div class="flex gap-2" v-if="authStore.user">
                             <button 
                                v-if="post.author === authStore.user.nick_name || post.author_id === authStore.user.id" 
                                @click="editPost" 
                                class="px-4 py-2 bg-black text-white text-xs uppercase tracking-widest hover:bg-luxury-gold transition-colors rounded-sm"
                            >
                                Edit
                            </button>
                             <button 
                                v-if="post.author === authStore.user.nick_name || post.author_id === authStore.user.id || authStore.user.check_admin"
                                @click="deletePost" 
                                class="px-4 py-2 text-xs text-red-500 uppercase tracking-widest hover:bg-red-50 transition-colors border border-transparent hover:border-red-100 rounded-sm"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Article Body -->
            <div class="p-8 md:p-12 min-h-[300px]">
                <div v-if="post.image" class="mb-8 flex justify-center bg-gray-50/50 rounded-lg p-4 border border-gray-100">
                    <img :src="post.image" alt="Post Image" class="max-w-full max-h-[600px] h-auto object-contain shadow-sm" />
                </div>
                
                <div class="prose max-w-none font-light text-gray-800 leading-relaxed whitespace-pre-wrap text-left indent-4">
                    <template v-for="(segment, index) in parsedContent" :key="index">
                        <img 
                            v-if="segment.type === 'image'" 
                            :src="segment.src" 
                            :alt="segment.alt" 
                            class="max-w-full h-auto mx-auto my-4 shadow-sm"
                        />
                        <span v-else>{{ segment.content }}</span>
                    </template>
                </div>
            </div>

            <!-- Comments Section -->
            <div class="bg-gray-50 p-8 md:p-12 border-t border-gray-100">
                <h3 class="text-sm uppercase tracking-widest text-black mb-8 flex items-center gap-2">
                    Comments <span class="bg-black text-white text-[10px] px-2 py-0.5 rounded-full">{{ comments.length }}</span>
                </h3>

                <!-- Comment Input -->
                <div class="mb-10 flex gap-4">
                    <div class="w-10 h-10 bg-gray-200 rounded-full flex-shrink-0"></div> <!-- Avatar Placeholder -->
                    <div class="flex-1">
                        <textarea 
                            v-model="newComment"
                            rows="3" 
                            placeholder="Join the discussion..." 
                            class="w-full border border-gray-200 p-4 focus:border-luxury-gold focus:outline-none bg-white font-light text-sm transition-colors resize-none mb-2"
                        ></textarea>
                        <div class="flex justify-end">
                            <button 
                                @click="submitComment"
                                class="px-4 py-1.5 bg-black text-white text-[10px] uppercase tracking-widest hover:bg-luxury-gold transition-colors rounded-sm"
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
