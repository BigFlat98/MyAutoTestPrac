<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { chat } from '@/api';

const authStore = useAuthStore();
const messageInput = ref('');
const messages = ref([]);
const socket = ref(null);
const connectionStatus = ref('disconnected'); 
const messagesContainer = ref(null);

const isLoading = ref(false);
const isAllLoaded = ref(false);

const editingMessageId = ref(null);
const editInputContent = ref('');

const scrollToBottom = async () => {
    await nextTick();
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
};

const fetchMessages = async (isLoadMore = false) => {
    if (isLoading.value) return;
    if (isLoadMore && isAllLoaded.value) return;
    
    isLoading.value = true;
    const lastId = isLoadMore && messages.value.length > 0 ? messages.value[0].id : null;
    
    try {
        const response = await chat.get('/messages', {
            params: {
                room_id: 1,
                limit: 30,
                last_id: lastId
            }
        });
        
        const newMessages = response.data;
        
        if (newMessages.length < 30) {
            isAllLoaded.value = true;
        }
        
        const reversed = newMessages.reverse();
        const processed = processMessages(reversed);

        if (isLoadMore) {
            messages.value = [...processed, ...messages.value];
        } else {
            messages.value = processed;
            scrollToBottom();
        }
    } catch (error) {
        console.error("Failed to fetch messages:", error);
    } finally {
        isLoading.value = false;
    }
};

const processMessages = (msgs) => {
    return msgs.map(msg => {
         const isMe = msg.user_id === authStore.user?.id;
         return {
             ...msg,
             nickname: msg.nickname || (isMe ? (authStore.user?.nick_name || 'Me') : `User ${msg.user_id}`),
             type: isMe ? 'send' : 'receive',
             isEditing: false
         };
    });
};

const handleScroll = async () => {
    if (!messagesContainer.value) return;
    const container = messagesContainer.value;
    
    if (container.scrollTop === 0 && !isAllLoaded.value && !isLoading.value && messages.value.length > 0) {
        const oldHeight = container.scrollHeight;
        await fetchMessages(true);
        await nextTick();
        container.scrollTop = container.scrollHeight - oldHeight;
    }
};

const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host; 
    const wsUrl = `${protocol}//${host}/chat/ws`;

    connectionStatus.value = 'connecting';
    socket.value = new WebSocket(wsUrl);

    socket.value.onopen = () => {
        console.log('WebSocket Connected');
        connectionStatus.value = 'connected';
    };

    socket.value.onmessage = (event) => {
        try {
            const payload = JSON.parse(event.data);
            
            if (payload.type === 'new') {
                const data = payload.data;
                const isMe = data.user_id === authStore.user?.id;
                const displayNickname = data.nickname || (isMe ? (authStore.user?.nick_name || 'Me') : `User ${data.user_id}`);
                
                messages.value.push({
                    ...data,
                    nickname: displayNickname,
                    type: isMe ? 'send' : 'receive',
                    isEditing: false
                });
                scrollToBottom();

            } else if (payload.type === 'update') {
                const data = payload.data;
                const idx = messages.value.findIndex(m => m.id === data.id);
                if (idx !== -1) {
                    messages.value[idx].content = data.content;
                    messages.value[idx].updated_at = data.updated_at;
                }
            } else if (payload.type === 'delete') {
                const { id } = payload.data;
                const idx = messages.value.findIndex(m => m.id === id);
                if (idx !== -1) {
                    messages.value[idx].deleted_at = new Date().toISOString(); 
                }
            }
        } catch (e) {
            console.error('Message Parse Error:', e);
        }
    };

    socket.value.onclose = () => {
        console.log('WebSocket Disconnected');
        connectionStatus.value = 'disconnected';
    };
};

const sendMessage = () => {
    if (!messageInput.value.trim()) return;
    if (socket.value?.readyState !== WebSocket.OPEN) {
        alert('서버와 연결되어 있지 않습니다.');
        return;
    }

    if (!authStore.user) {
        alert('로그인이 필요합니다.');
        return;
    }

    const payload = {
        user_id: authStore.user.id,
        room_id: 1, 
        content: messageInput.value
    };

    socket.value.send(JSON.stringify(payload));
    messageInput.value = '';
};

const startEdit = (msg) => {
    editingMessageId.value = msg.id;
    editInputContent.value = msg.content;
};

const cancelEdit = () => {
    editingMessageId.value = null;
    editInputContent.value = '';
};

const commitEdit = async (msg) => {
    if (!editInputContent.value.trim()) return;
    
    try {
        await chat.patch(`/messages/${msg.id}`, {
            content: editInputContent.value,
            user_id: authStore.user.id
        });
        cancelEdit();
    } catch (e) {
        console.error("Failed to edit message", e);
        alert("메시지 수정 실패");
    }
};

const deleteMsg = async (msg) => {
    if (!confirm("정말 삭제하시겠습니까?")) return;
    try {
        await chat.delete(`/messages/${msg.id}`, {
            data: { user_id: authStore.user.id }
        });
    } catch (e) {
        console.error("Failed to delete message", e);
        alert("메시지 삭제 실패");
    }
};

onMounted(async () => {
    if (!authStore.isAuthenticated) {
        await authStore.checkAuth();
    }
    
    if (authStore.isAuthenticated) {
        await fetchMessages();
        connectWebSocket();
    }
});

onUnmounted(() => {
    if (socket.value) {
        socket.value.close();
    }
});
</script>

<template>
    <div class="chat-container glass-card slide-up" style="animation-delay: 0.1s;">
        <!-- Header -->
        <header class="glass-header flex justify-between items-center" style="display: flex; text-align: left; padding: 20px 32px; border-radius: 20px 20px 0 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin: 0;">
            <div>
                <h1 class="glass-title text-3xl mb-1 m-0">General Chat</h1>
                <p class="glass-subtitle font-mono text-sm m-0">Real-time community</p>
            </div>
            <span class="status-badge" :class="connectionStatus === 'connected' ? 'online' : 'offline'">
                <span class="dot" :class="connectionStatus === 'connected' ? 'bg-emerald-400' : 'bg-red-400'"></span> 
                {{ connectionStatus === 'connected' ? 'Online' : 'Offline' }}
            </span>
        </header>

        <!-- Message List -->
        <main class="chat-messages custom-scrollbar" ref="messagesContainer" @scroll="handleScroll">
            <div v-for="msg in messages" :key="msg.id" 
                 class="message-wrapper" 
                 :class="{ 'my-message': msg.type === 'send', 'other-message': msg.type === 'receive' }">
                
                <!-- Nickname -->
                <span class="message-nickname">{{ msg.nickname }}</span>

                <div class="message-bubble" :class="{ 'deleted': msg.deleted_at }">
                    <template v-if="msg.deleted_at">
                        <span class="text-slate-500 italic">삭제된 메시지입니다.</span>
                    </template>
                    <template v-else>
                        <div v-if="editingMessageId === msg.id" class="edit-box">
                            <input 
                                v-model="editInputContent" 
                                @keyup.enter="commitEdit(msg)"
                                @keyup.esc="cancelEdit"
                                class="edit-input"
                            />
                            <div class="edit-actions">
                                <button @click="commitEdit(msg)" class="edit-btn save">Save</button>
                                <button @click="cancelEdit" class="edit-btn cancel">Cancel</button>
                            </div>
                        </div>
                        <div v-else>
                            {{ msg.content }}
                            <span v-if="msg.updated_at" class="text-[0.65rem] text-sky-400/70 ml-1">(edit)</span>
                        </div>
                    </template>
                </div>

                <div class="message-meta">
                    <span class="message-time">
                        {{ new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
                    </span>
                    
                    <span v-if="msg.type === 'send' && !msg.deleted_at && editingMessageId !== msg.id" class="action-links">
                        <span class="action-btn" @click="startEdit(msg)">수정</span>
                        <span class="separator">|</span>
                        <span class="action-btn" @click="deleteMsg(msg)">삭제</span>
                    </span>
                 </div>
            </div>
        </main>

        <!-- Input Area -->
        <footer class="chat-input-area">
            <div class="input-wrapper focus-within:ring-1 focus-within:ring-sky-400">
                <input 
                    v-model="messageInput" 
                    @keyup.enter="sendMessage"
                    type="text" 
                    placeholder="메시지를 입력하세요..." 
                />
                <button @click="sendMessage" class="send-btn">
                    SEND
                </button>
            </div>
        </footer>
    </div>
</template>

<style scoped>
.chat-container {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 120px); 
    max-width: 900px;
    margin: 0 auto;
    padding: 0;
    overflow: hidden;
    margin-bottom: 2rem;
}

.chat-header {
    padding: 1.25rem 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    display: flex;
    align-items: center;
    background: rgba(0,0,0,0.2);
}

.status-badge {
    font-size: 0.75rem;
    padding: 0.25rem 0.6rem;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.05);
    border-radius: 9999px;
    color: #cbd5e1;
    display: flex;
    align-items: center;
    gap: 6px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.status-badge .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    box-shadow: 0 0 8px currentColor;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: rgba(255,255,255,0.2);
    border-radius: 3px;
}

.message-wrapper {
    display: flex;
    flex-direction: column;
    max-width: 65%;
    position: relative;
    padding-bottom: 0.5rem;
}

.message-nickname {
    font-size: 0.75rem;
    color: #94a3b8;
    margin-bottom: 6px;
    font-weight: 500;
    padding-left: 4px;
}

.message-bubble {
    padding: 0.9rem 1.2rem;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2); 
    word-break: break-word;
    border: 1px solid transparent;
    position: relative;
    backdrop-filter: blur(8px);
}

.message-bubble.deleted {
    background-color: rgba(255,255,255,0.05) !important;
    border: 1px dashed rgba(255,255,255,0.2) !important;
    color: #64748b !important;
    box-shadow: none;
    border-radius: 16px !important;
}

.edit-box {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.edit-input {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #f8fafc;
    border-radius: 12px;
    padding: 6px 10px;
    font-size: 0.9rem;
    outline: none;
    min-width: 150px;
    transition: all 0.2s;
}

.edit-input:focus {
    border-color: #38bdf8;
    box-shadow: 0 0 10px rgba(56,189,248,0.2);
}

.edit-actions { display: flex; gap: 4px; }

.edit-btn {
    border: 1px solid rgba(255,255,255,0.2); 
    background-color: rgba(255, 255, 255, 0.1); 
    font-size: 0.7rem;
    padding: 4px 12px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    color: #e2e8f0; 
    transition: all 0.3s ease;
}

.edit-btn:hover {
    background-color: rgba(56,189,248,0.2);
    border-color: #38bdf8;
    color: #38bdf8;
}

.message-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 6px;
    position: relative;
    height: 16px; 
    padding: 0 4px;
}

.message-time {
    font-size: 0.7rem;
    color: #64748b;
    letter-spacing: 0.02em;
}

.action-links {
    display: flex;
    align-items: center;
    gap: 4px; 
    font-size: 0.7rem;
    color: #94a3b8;
    opacity: 0; 
    transition: opacity 0.2s;
}

.message-wrapper:hover .action-links { opacity: 1; }

.action-btn {
    cursor: pointer;
    text-decoration: underline; 
    padding: 0;
    border-radius: 0;
    background-color: transparent;
    color: #94a3b8;
    transition: color 0.2s;
    font-weight: normal;
}

.action-btn:hover { color: #38bdf8; }
.separator { display: inline; color: #475569; font-size: 0.6rem; }

/* My Message */
.my-message {
    align-self: flex-end;
    align-items: flex-end;
}
.my-message .message-nickname {
    text-align: right;
    padding-right: 4px;
}
.my-message .message-meta {
    justify-content: flex-end;
    flex-direction: row-reverse; 
}
.my-message .message-bubble {
    background-color: rgba(56, 189, 248, 0.15); 
    color: #f8fafc; 
    border-radius: 18px 18px 2px 18px; 
    border: 1px solid rgba(56, 189, 248, 0.3); 
    box-shadow: 0 4px 15px rgba(56,189,248,0.1);
}
.my-message .message-time { position: static; }

/* Other Message */
.other-message {
    align-self: flex-start;
    align-items: flex-start;
}
.other-message .message-meta {
    justify-content: flex-start;
}
.other-message .message-bubble {
    background-color: rgba(255, 255, 255, 0.05);
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 18px 18px 18px 2px;
}

/* Input Area */
.chat-input-area {
    padding: 1.5rem 2rem;
    background-color: rgba(0,0,0,0.2);
    border-top: 1px solid rgba(255,255,255,0.05);
}

.input-wrapper {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    background-color: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px; 
    padding: 0.6rem 1.2rem;
    transition: all 0.3s ease;
}

.input-wrapper input {
    flex: 1;
    background: transparent;
    border: none;
    color: #f8fafc;
    font-size: 0.95rem;
    padding: 0.2rem;
    outline: none;
}

.input-wrapper input::placeholder {
    color: #64748b;
    font-weight: 300;
}

.send-btn {
    border: 1px solid rgba(56,189,248,0.5);
    background: rgba(56,189,248,0.2); 
    color: #38bdf8;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    letter-spacing: 0.05em;
    padding: 0.5rem 1.2rem;
    border-radius: 20px; 
    transition: all 0.2s;
    box-shadow: 0 0 10px rgba(56,189,248,0.2);
}

.send-btn:hover {
    background-color: #38bdf8;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 0 15px rgba(56,189,248,0.5);
}
</style>
