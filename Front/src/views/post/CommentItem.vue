<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const props = defineProps({
    comment: {
        type: Object,
        required: true
    },
    depth: {
        type: Number,
        default: 0
    }
})

const emit = defineEmits(['reply', 'modify', 'delete'])

const showReplies = ref(false)

const toggleReplies = () => {
    showReplies.value = !showReplies.value
}

const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleString()
}

const hasReplies = computed(() => props.comment.replies && props.comment.replies.length > 0)
</script>

<template>
    <div class="flex gap-4 group">
        
        <div class="flex-1 w-full min-w-0">
            <!-- Comment Card -->
            <div class="bg-gray-50/50 hover:bg-gray-100/50 transition-colors rounded-lg mb-2">
                <!-- Top Row: Author | Date | Reply Button -->
                <div class="flex items-center justify-between py-2 px-1 mb-1">
                    <span class="font-medium text-sm text-blue-600">{{ comment.author }}</span>
                    <div class="flex items-center gap-3">
                         <span class="text-[10px] text-gray-400 font-mono">{{ formatDate(comment.created_at) }}</span>
                         <button 
                            @click="$emit('reply', comment.id)"
                            class="px-2 py-0.5 border border-luxury-gold text-luxury-gold hover:bg-luxury-gold hover:text-white transition-colors text-[9px] uppercase tracking-widest leading-none rounded-sm"
                        >
                            Reply
                        </button>
                    </div>
                </div>

                <!-- Bottom Row: Content | Actions -->
                <div class="flex items-start justify-between px-1 gap-4">
                     <p class="text-sm font-light text-gray-700 leading-relaxed whitespace-pre-wrap break-words">{{ comment.content }}</p>

                     <div class="flex gap-2 shrink-0 items-center h-fit self-start" v-if="authStore.user">
                        <button 
                            v-if="comment.author === authStore.user.nick_name || comment.user_id === authStore.user.id"
                            @click="$emit('modify', comment.id)"
                            class="px-2 py-0.5 bg-black text-white hover:bg-luxury-gold transition-colors text-[9px] uppercase tracking-widest leading-none rounded-sm border border-transparent"
                        >
                            Modify
                        </button>
                        <button 
                            v-if="comment.author === authStore.user.nick_name || comment.user_id === authStore.user.id || authStore.user.check_admin"
                            @click="$emit('delete', comment.id)"
                            class="px-2 py-0.5 text-[9px] text-red-500 uppercase tracking-widest leading-none hover:bg-red-50 transition-colors border border-transparent hover:border-red-100 rounded-sm"
                        >
                            Delete
                        </button>
                     </div>
                </div>
            </div>

            <!-- Accordion Toggle for Replies -->
            <div v-if="hasReplies" class="mb-2 pl-1">
                <button 
                    @click="toggleReplies"
                    class="text-[10px] font-medium text-luxury-gold flex items-center gap-1 focus:outline-none tracking-widest uppercase bg-transparent border-none p-0 hover:shadow-none shadow-none"
                >
                    <span class="transform transition-transform duration-200" :class="{ 'rotate-90': showReplies }">▶</span>
                    {{ showReplies ? 'Hide' : 'View' }} {{ comment.replies.length }} Replies
                </button>
            </div>

            <!-- Nested Replies (Recursive) -->
             <transition
                enter-active-class="transition-all duration-300 ease-out"
                enter-from-class="opacity-0 max-h-0"
                enter-to-class="opacity-100 max-h-[1000px]"
                leave-active-class="transition-all duration-200 ease-in"
                leave-from-class="opacity-100 max-h-[1000px]"
                leave-to-class="opacity-0 max-h-0"
            >
                <div v-if="showReplies" class="space-y-4 pl-4 border-l border-gray-200 mt-2 overflow-hidden">
                    <CommentItem 
                        v-for="reply in comment.replies" 
                        :key="reply.id" 
                        :comment="reply" 
                        :depth="depth + 1"
                        @reply="$emit('reply', $event)"
                        @modify="$emit('modify', $event)"
                        @delete="$emit('delete', $event)"
                    />
                </div>
            </transition>
        </div>
    </div>
</template>
