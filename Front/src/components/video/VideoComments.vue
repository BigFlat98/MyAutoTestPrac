<script setup>
import { ref, computed } from 'vue';
import { api } from '@/api';

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

const nestedComments = computed(() => {
  const map = {};
  const roots = [];

  props.comments.forEach(comment => {
    map[comment.id] = { ...comment, replies: [] };
  });

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

const addComment = async () => {
  if (!newComment.value.trim()) return;
  
  try {
      const response = await api.post(`/videos/${props.videoId}/comments`, {
          content: newComment.value
      });
      props.comments.push(response.data);
      newComment.value = '';
  } catch (error) {
      console.error("Failed to post comment:", error);
      alert("댓글 등록에 실패했습니다.");
  }
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

const addReply = async (parentId) => {
  if (!replyContent.value.trim()) return;

  try {
      const response = await api.post(`/videos/${props.videoId}/comments`, {
          content: replyContent.value,
          reply_id: parentId
      });
      props.comments.push(response.data);
      activeReplyId.value = null;
      replyContent.value = '';
  } catch (error) {
      console.error("Failed to post reply:", error);
      alert("답글 등록에 실패했습니다.");
  }
};
</script>

<template>
  <div class="h-full flex flex-col bg-white/2 backdrop-blur-xl">
    <!-- Header -->
    <div class="p-5 border-b border-white/5 flex justify-between items-center bg-white/5">
      <h4 class="text-[10px] font-bold tracking-[0.2em] text-slate-400 uppercase flex items-center gap-2">
        <span>Comments</span>
        <span class="bg-sky-400/20 text-sky-400 px-2 py-0.5 rounded-full text-[9px]">{{ comments.length }}</span>
      </h4>
    </div>

    <!-- Comment List -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-5 space-y-6">
      <div v-if="comments.length === 0" class="text-center text-slate-500 py-10 text-xs italic font-light">
        Be the first to share your thoughts.
      </div>
      
      <!-- Root Comments -->
      <div 
        v-for="comment in nestedComments" 
        :key="comment.id" 
        class="group/comment"
      >
        <div class="flex flex-col space-y-2">
          <!-- User & Meta -->
          <div class="flex justify-between items-center">
            <span class="text-xs font-medium text-slate-200">{{ comment.author }}</span>
            <div class="flex items-center gap-3">
              <span class="text-[9px] font-mono text-slate-600 uppercase">{{ new Date(comment.created_at).toLocaleDateString() }}</span>
              <button 
                @click="toggleReplyForm(comment.id)"
                class="px-1.5 py-px bg-sky-400 text-white hover:bg-transparent hover:text-sky-400 border border-sky-400 transition-all text-[9px] uppercase tracking-wider leading-tight rounded"
              >
                Reply
              </button>
            </div>
          </div>
          
          <!-- Content -->
          <p class="text-sm text-slate-400 leading-relaxed font-light break-words">
            {{ comment.content }}
          </p>

          <!-- Reply Input Form -->
          <div v-if="activeReplyId === comment.id" class="mt-4 animate-in fade-in slide-in-from-top-2">
            <div class="flex gap-2 p-1 bg-white/5 rounded-lg border border-white/10">
              <input 
                v-model="replyContent"
                @keyup.enter="addReply(comment.id)"
                type="text" 
                placeholder="Write a reply..." 
                class="flex-1 bg-transparent border-none px-3 py-2 text-xs text-white focus:outline-none placeholder-slate-600"
                autoFocus
              />
              <button 
                @click="addReply(comment.id)"
                class="shrink-0 px-2 py-1.5 bg-sky-400 text-white hover:bg-transparent hover:text-sky-400 border border-sky-400 transition-all text-[10px] font-bold uppercase tracking-wider rounded-md"
              >
                Add
              </button>
            </div>
          </div>

          <!-- Nested Replies -->
          <div v-if="comment.replies.length > 0" class="ml-4 pl-4 border-l border-white/10 space-y-5 mt-4 pt-2">
            <div v-for="reply in comment.replies" :key="reply.id" class="space-y-1">
              <div class="flex justify-between items-center">
                <span class="text-[11px] font-medium text-slate-300 flex items-center gap-2">
                  <span class="text-sky-400/50">↳</span> {{ reply.author }}
                </span>
                <span class="text-[9px] font-mono text-slate-600">{{ new Date(reply.created_at).toLocaleDateString() }}</span>
              </div>
              <p class="text-xs text-slate-500 font-light leading-relaxed break-words">{{ reply.content }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Input Area -->
    <div class="p-4 bg-white/5 border-t border-white/5 shrink-0">
      <div class="flex gap-2 items-center bg-white/5 border border-white/10 rounded-xl px-3 py-1.5 focus-within:border-sky-400/50 focus-within:ring-1 focus-within:ring-sky-400/20 transition-all">
        <input 
          v-model="newComment"
          @keyup.enter="addComment"
          type="text" 
          placeholder="Add a comment..."
          class="flex-1 min-w-0 bg-transparent border-none px-1 py-2 text-sm text-white focus:outline-none placeholder-slate-600"
        />
        <button 
          @click="addComment"
          class="shrink-0 px-3 py-1.5 bg-sky-400 text-white hover:bg-transparent hover:text-sky-400 border border-sky-400 transition-all text-[10px] font-bold uppercase tracking-wider rounded-md"
        >
          POST
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(56, 189, 248, 0.3);
}
</style>
