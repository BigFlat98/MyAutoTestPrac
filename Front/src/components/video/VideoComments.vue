<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  comments: {
    type: Array,
    default: () => []
  },
  videoId: {
    type: Number,
    required: true
  }
});

const newComment = ref('');
const replyContent = ref('');
const activeReplyId = ref(null);

// Organize comments into hierarchy
const nestedComments = computed(() => {
  const map = {};
  const roots = [];

  // Initialize map
  props.comments.forEach(comment => {
    map[comment.id] = { ...comment, replies: [] };
  });

  // Link children to parents
  props.comments.forEach(comment => {
    if (comment.reply_id) {
      if (map[comment.reply_id]) {
        map[comment.reply_id].replies.push(map[comment.id]);
      }
    } else {
      roots.push(map[comment.id]);
    }
  });

  return roots;
});

const addComment = () => {
  if (!newComment.value.trim()) return;
  
  props.comments.unshift({
    id: Date.now(),
    author: 'Me',
    content: newComment.value,
    created_at: new Date().toLocaleString(),
    reply_id: null
  });
  
  newComment.value = '';
};

const toggleReplyForm = (commentId) => {
  if (activeReplyId.value === commentId) {
    activeReplyId.value = null;
    replyContent.value = '';
  } else {
    activeReplyId.value = commentId;
    replyContent.value = '';
  }
};

const addReply = (parentId) => {
  if (!replyContent.value.trim()) return;

  props.comments.push({
    id: Date.now(),
    author: 'Me',
    content: replyContent.value,
    created_at: new Date().toLocaleString(),
    reply_id: parentId
  });

  activeReplyId.value = null;
  replyContent.value = '';
};
</script>

<template>
  <div class="h-full flex flex-col bg-white/50 border-l border-gray-100">
    <!-- Header -->
    <div class="p-4 flex justify-between items-center bg-transparent">
      <h4 class="text-xs font-bold tracking-widest text-gray-400">COMMENTS <span class="text-luxury-gold ml-1">{{ comments.length }}</span></h4>
    </div>

    <!-- Comment List -->
    <div class="flex-1 overflow-y-auto max-h-[400px] p-4 space-y-4">
      <div v-if="comments.length === 0" class="text-center text-gray-400 py-8 text-sm">
        첫 번째 댓글을 남겨보세요!
      </div>
      
      <!-- Root Comments -->
      <div 
        v-for="comment in nestedComments" 
        :key="comment.id" 
        class="border-b border-gray-100 last:border-0 pb-3 last:pb-0"
      >
        <!-- Parent Comment -->
        <div class="flex justify-between items-start mb-1 group">
          <span class="font-bold text-xs text-gray-800">{{ comment.author }}</span>
          <div class="flex items-center space-x-2">
            <span class="text-[10px] text-gray-400">{{ comment.created_at }}</span>
            <button 
              @click="toggleReplyForm(comment.id)"
              class="border border-gray-200 text-gray-400 text-[9px] px-1.5 h-4 flex items-center justify-center rounded-[2px] bg-white transition-all duration-300 hover:border-luxury-gold hover:text-luxury-gold hover:shadow-[0_0_8px_rgba(153,101,21,0.4)] leading-none"
            >
              REPLY
            </button>
          </div>
        </div>
        <p class="text-sm text-gray-600 break-words mb-2 text-left">{{ comment.content }}</p>

        <!-- Reply Input Form -->
        <div v-if="activeReplyId === comment.id" class="ml-4 mb-3 mt-2 animate-in fade-in slide-in-from-top-1">
          <div class="flex space-x-2">
            <input 
              v-model="replyContent"
              @keyup.enter="addReply(comment.id)"
              type="text" 
              placeholder="대댓글 기능..." 
              class="flex-1 bg-gray-50 border border-gray-200 px-3 py-1.5 text-xs focus:outline-none focus:border-luxury-gold transition-colors w-full"
              autoFocus
            />
            <button 
              @click="addReply(comment.id)"
              class="bg-gray-800 text-white px-3 py-1.5 text-[10px] font-bold hover:bg-luxury-gold transition-colors rounded-md h-auto"
            >
              등록
            </button>
          </div>
        </div>

        <!-- Nested Replies -->
        <div v-if="comment.replies.length > 0" class="ml-4 pl-3 border-l-2 border-gray-100 space-y-3 mt-2 bg-gray-50/50 p-2">
          <div v-for="reply in comment.replies" :key="reply.id">
            <div class="flex justify-between items-start mb-0.5">
              <span class="font-bold text-xs text-gray-700 flex items-center">
                <span class="mr-1 text-luxury-gold">↳</span> {{ reply.author }}
              </span>
              <span class="text-[10px] text-gray-400">{{ reply.created_at }}</span>
            </div>
            <p class="text-xs text-gray-500 break-words pl-3 text-left">{{ reply.content }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Input Area -->
    <div class="p-4 bg-transparent mt-auto">
      <div class="flex items-stretch gap-3">
        <input 
          v-model="newComment"
          @keyup.enter="addComment"
          type="text" 
          class="flex-1 bg-white border-b border-gray-200 pl-0 py-3 text-sm focus:outline-none focus:border-luxury-gold transition-colors rounded-none h-auto placeholder-gray-300 shadow-none ring-0 appearance-none"
        />
        <button 
          @click="addComment"
          class="post-btn"
        >
          POST
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-btn {
  /* Layout */
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  
  /* Size & Shape */
  /* Height handled by flex stretch */
  padding: 0 16px !important;
  border: 1px solid #e5e7eb !important; /* Gray-200 */
  border-radius: 2px !important; /* Slight soft edge */
  background: white !important;
  
  /* Text Style */
  font-size: 10px;
  font-weight: bold;
  letter-spacing: 0.1em;
  color: #9ca3af; /* text-gray-400 */
  
  /* Transitions */
  transition: all 0.2s ease;
  cursor: pointer;
  box-shadow: none !important;
  transform: none !important;
}

.post-btn:hover {
  color: #f3c246 !important;
  border-color: #f3c246 !important;
  background: white !important;
  box-shadow: 0 2px 8px rgba(243, 194, 70, 0.15) !important;
  letter-spacing: 0.1em !important;
  transform: none !important;
}
</style>
