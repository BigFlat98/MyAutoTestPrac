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

// 스크롤을 맨 아래로 이동
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
        
        // Backend returns DESC (newest first). ASC로 변환
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
             isEditing: false // Frontend state
         };
    });
};

const handleScroll = async () => {
    if (!messagesContainer.value) return;
    const container = messagesContainer.value;
    
    // 맨 위 도달 시 로딩
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
            // WsEvent: { type: 'new'|'update'|'delete', data: ... }
            const payload = JSON.parse(event.data);
            console.log('WS Event:', payload);
            
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
                    // Update content and timestamps
                    messages.value[idx].content = data.content;
                    messages.value[idx].updated_at = data.updated_at;
                }
            } else if (payload.type === 'delete') {
                const { id } = payload.data; // data is { id: ... } or full object depending on backend. Check Rust payload.
                // Rust sends { id: i32 } inside Delete variant content "data"
                const idx = messages.value.findIndex(m => m.id === id);
                if (idx !== -1) {
                    // Mark as deleted locally if we want to show "deleted message"
                    // If backend sends full object with deleted_at, we use that.
                    // Rust code sends `WsEvent::Delete { id }`.
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

// --- Edit & Delete Logic ---

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
        // Axios delete doesn't support body by default in simple syntax, use config
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
    <div class="chat-container">
        <!-- Header -->
        <header class="chat-header">
            <div class="header-content">
                <h1>General Chat</h1>
                <span class="status-badge online">
                    <span class="dot"></span> Online
                </span>
            </div>
        </header>

        <!-- Message List -->
        <main class="chat-messages" ref="messagesContainer" @scroll="handleScroll">
            <div v-for="msg in messages" :key="msg.id" 
                 class="message-wrapper" 
                 :class="{ 'my-message': msg.type === 'send', 'other-message': msg.type === 'receive' }">
                
                <!-- Nickname -->
                <span class="message-nickname">{{ msg.nickname }}</span>

                <div class="message-bubble" :class="{ 'deleted': msg.deleted_at }">
                    <template v-if="msg.deleted_at">
                        <span class="text-gray-400 italic">삭제된 메시지입니다.</span>
                    </template>
                    <template v-else>
                         <!-- Edit Mode -->
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
                        <!-- View Mode -->
                        <div v-else>
                            {{ msg.content }}
                            <span v-if="msg.updated_at" class="text-[0.65rem] text-yellow-600/70 ml-1">(edit)</span>
                        </div>
                    </template>
                </div>

                <div class="message-meta">
                    <span class="message-time">
                        {{ new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
                    </span>
                    
                    <!-- Edit/Delete Actions (Only for my active messages) -->
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
            <div class="input-wrapper">
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
/* 전체 레이아웃 - 화이트/골드 테마 */
.chat-container {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 64px); /* 네비게이션 바 높이 제외 */
    max-width: 900px;
    margin: 0 auto;
    background-color: #ffffff;
    font-family: 'Inter', sans-serif;
    border-left: 1px solid #f3f4f6;
    border-right: 1px solid #f3f4f6;
}

/* 헤더 스타일 */
.chat-header {
    padding: 1.25rem 2rem;
    background-color: #ffffff; /* White background */
    border-bottom: 1px solid #f3f4f6;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.header-content h1 {
    font-size: 1.5rem;
    font-weight: 300; /* 얇고 세련된 폰트 */
    color: #111;
    margin: 0;
    font-family: 'Pinyon Script', cursive; /* 로고와 같은 폰트 느낌 혹은 Serif */
    /* 만약 Pinyon Script가 없으면 일반 Serif 사용 */
    font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
    color: #bfa57d; /* Muted Luxury Gold */
}

.status-badge {
    font-size: 0.75rem;
    padding: 0.25rem 0.6rem;
    border: 1px solid #e5e7eb;
    border-radius: 9999px;
    color: #4b5563;
    display: flex;
    align-items: center;
    gap: 6px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.status-badge .dot {
    width: 6px;
    height: 6px;
    background-color: #10b981; /* Green dot for online */
    border-radius: 50%;
}

/* 메시지 리스트 영역 */
.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    background-color: #fdfbf7; /* Very warm light gray/beige for premium feel */
}

/* 스크롤바 커스텀 */
.chat-messages::-webkit-scrollbar {
    width: 6px;
}
.chat-messages::-webkit-scrollbar-thumb {
    background-color: #e5e7eb;
    border-radius: 3px;
}

/* 메시지 버블 공통 */
.message-wrapper {
    display: flex;
    flex-direction: column;
    max-width: 65%;
    position: relative;
    padding-bottom: 1.2rem;
}

.message-nickname {
    font-size: 0.75rem;
    color: #9ca3af;
    margin-bottom: 6px;
    font-weight: 500;
    padding-left: 4px;
}

.message-bubble {
    padding: 0.9rem 1.2rem;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03); /* Softer shadow */
    word-break: break-word;
    border: 1px solid transparent;
    position: relative;
}

.message-bubble.deleted {
    background-color: #f9fafb !important;
    border: 1px dashed #e5e7eb !important;
    color: #9ca3af !important;
    box-shadow: none;
    border-radius: 16px !important;
}

/* Edit Box Styles */
.edit-box {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.edit-input {
    background: rgba(255, 255, 255, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.5);
    color: inherit;
    border-radius: 12px;
    padding: 6px 10px;
    font-size: 0.9rem;
    outline: none;
    min-width: 150px;
    backdrop-filter: blur(4px);
    transition: all 0.2s;
}

.edit-input:focus {
    border-color: #bfa57d;
    background: rgba(255, 255, 255, 0.8);
    box-shadow: 0 2px 8px rgba(191,165,125,0.1);
}

.edit-actions {
    display: flex;
    gap: 4px;
}

.edit-btn {
    border: none;
    font-size: 0.7rem;
    padding: 4px 10px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s;
}

.edit-btn.save {
    background-color: #bfa57d; /* Matching Gold theme */
    color: white;
}

.edit-btn.save:hover {
    background-color: #a88e66;
}

.edit-btn.cancel {
    background-color: #f3f4f6;
    color: #6b7280;
}

.edit-btn.cancel:hover {
    background-color: #e5e7eb;
}

/* Message Meta & Action Links */
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
    color: #9ca3af;
    letter-spacing: 0.02em;
}

.action-links {
    display: flex;
    align-items: center;
    gap: 4px; /* Reduced gap for text links */
    font-size: 0.7rem;
    color: #9ca3af;
    opacity: 0; /* Hide by default, show on hover */
    transition: opacity 0.2s;
}

.message-wrapper:hover .action-links {
    opacity: 1;
}

.action-btn {
    cursor: pointer;
    text-decoration: underline; /* Back to text style */
    padding: 0;
    border-radius: 0;
    background-color: transparent;
    color: #9ca3af;
    transition: color 0.2s;
    font-weight: normal;
}

.action-btn:hover {
    background-color: transparent;
    color: #bfa57d; /* Matching Gold hover */
}

.separator {
    display: inline; /* Show separator again */
    color: #d1d5db;
    font-size: 0.6rem;
}

/* Adjustments for My Message alignment */
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
    /* Muted, Elegant Gold (Sand/Champagne) */
    background: #eaddcf; /* Soft beige base */
    background: linear-gradient(135deg, #eaddcf 0%, #e3d5b0 100%); /* Subtle sand-gold gradient */
    color: #4a4238; /* Soft dark brown */
    border-radius: 18px 18px 2px 18px; 
    border: 1px solid rgba(220, 204, 174, 0.3); /* Very subtle border */
}

.my-message .message-time {
    position: static;
}

/* Adjustments for Other Message */
.other-message {
    align-self: flex-start;
    align-items: flex-start;
}

.other-message .message-meta {
    justify-content: flex-start;
}

.other-message .message-bubble {
    background-color: #ffffff;
    color: #374151;
    border: 1px solid #f3f4f6;
    border-radius: 18px 18px 18px 2px;
}

/* Input Area */
.chat-input-area {
    padding: 1.5rem 2rem;
    background-color: #ffffff;
    /* border-top: 1px solid #f3f4f6; removed for cleaner look */
}

.input-wrapper {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    
    /* New Sophisticated Style: Rounded Box */
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 24px; /* Full pill shape */
    padding: 0.6rem 1.2rem;
    transition: all 0.3s ease;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}

.input-wrapper:focus-within {
    border-color: #d1b88a; /* Soft Gold Border */
    background-color: #ffffff;
    box-shadow: 0 4px 12px rgba(210, 180, 140, 0.15); /* Gold glow */
}

.input-wrapper input {
    flex: 1;
    background: transparent;
    border: none;
    color: #374151;
    font-size: 0.95rem;
    padding: 0.2rem;
    outline: none;
}

.input-wrapper input::placeholder {
    color: #9ca3af;
    font-weight: 300;
}

.send-btn {
    border: none;
    background: #bfa57d; /* Button background */
    color: white;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    letter-spacing: 0.05em;
    padding: 0.5rem 1.2rem;
    border-radius: 20px; /* Rounded button inside input */
    transition: all 0.2s;
    box-shadow: 0 2px 4px rgba(191, 165, 125, 0.3);
}

.send-btn:hover {
    background-color: #ac926b;
    transform: translateY(-1px);
}
</style>
