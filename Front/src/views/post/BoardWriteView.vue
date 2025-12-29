<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api'

const router = useRouter()
const route = useRoute()

const isEditMode = computed(() => !!route.params.id)
const postId = route.params.id

const form = ref({
    title: '',
    content: '',
    is_public: true,
})
const imageFile = ref(null)
const imagePreview = ref(null)
const isLoading = ref(false)
const activeTab = ref('write')

const parsedContent = computed(() => {
    if (!form.value.content) return []
    
    const text = form.value.content
    const regex = /!\[(.*?)\]\((.*?)\)/g
    
    const segments = []
    let lastIndex = 0
    let match
    
    while ((match = regex.exec(text)) !== null) {
        if (match.index > lastIndex) {
            segments.push({ type: 'text', content: text.substring(lastIndex, match.index) })
        }
        segments.push({ type: 'image', alt: match[1], src: match[2] })
        lastIndex = regex.lastIndex
    }
    
    if (lastIndex < text.length) {
        segments.push({ type: 'text', content: text.substring(lastIndex) })
    }
    
    return segments
})

// Load Post data if Edit Mode
const loadPost = async () => {
    if (!isEditMode.value) return
    
    isLoading.value = true
    try {
        const response = await api.get(`/posts/${postId}`)
        const data = response.data
        
        form.value = {
            title: data.title,
            content: data.description,
            is_public: data.is_public !== undefined ? data.is_public : true
        }
        
        // If has image
        if (data.image) {
            imagePreview.value = data.image // Assuming backend returns full URL or path
            // Note: imageFile logic needs care if not changing image. Backend handles optional image.
        }

    } catch (error) {
        console.error('Failed to load post:', error)
        alert('Failed to load post data.')
        router.push({ name: 'board-list' })
    } finally {
        isLoading.value = false
    }
}

const handleFileUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
        imageFile.value = file
        // Create preview
        const reader = new FileReader()
        reader.onload = (e) => {
            imagePreview.value = e.target.result
        }
        reader.readAsDataURL(file)
    }
}

const removeImage = () => {
    imageFile.value = null
    imagePreview.value = null
}

const savePost = async () => {
    if (!form.value.title.trim() || !form.value.content.trim()) {
        alert('Title and Content are required.')
        return
    }

    isLoading.value = true
    try {
        // Form Data for Multipart
        const formData = new FormData()
        formData.append('title', form.value.title)
        formData.append('description', form.value.content)
        // formData.append('is_public', form.value.is_public) // Backend might expect string 'true'/'false' or bool handled by FastAPI Form
        formData.append('is_public', String(form.value.is_public)) 
        
        if (imageFile.value) {
            formData.append('image', imageFile.value)
        }

        if (isEditMode.value) {
            await api.put(`/posts/${postId}`, formData) // PUT strictly expects body, with FormData axios handles content-type
        } else {
            await api.post('/posts', formData)
        }
        
        // await new Promise(resolve => setTimeout(resolve, 800)) // Sim delay

        alert(isEditMode.value ? 'Post Updated!' : 'Post Created!')
        router.push({ name: 'board-list' })

    } catch (error) {
        console.error('Failed to save post:', error)
        if (error.response && error.response.status === 422) {
            const detail = error.response.data.detail
            if (Array.isArray(detail)) {
                const msg = detail.map(d => `${d.loc[1]}: ${d.msg}`).join('\n')
                alert(`Validation Error:\n${msg}`)
            } else {
                alert(`Validation Error: ${detail}`)
            }
        } else {
            alert('Error saving post.')
        }
    } finally {
        isLoading.value = false
    }
}

const cancel = () => {
    router.back()
}

// Inline Image Upload Logic
const textareaRef = ref(null)

const handlePaste = (event) => {
    const items = (event.clipboardData || event.originalEvent.clipboardData).items
    for (const item of items) {
        if (item.type.indexOf('image') !== -1) {
            const file = item.getAsFile()
            uploadInlineImage(file)
            event.preventDefault() // Prevent default paste of binary data
        }
    }
}

const uploadInlineImage = async (file) => {
    const formData = new FormData()
    formData.append('file', file) // Note: Backend expects 'file'

    try {
        const res = await api.post('/posts/image/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        const imageUrl = res.data.url
        insertAtCursor(`\n![Image](${imageUrl})\n`)
    } catch (error) {
        console.error('Failed to upload inline image:', error)
        alert('Failed to upload image.')
    }
}

const insertAtCursor = (text) => {
    const textarea = textareaRef.value
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const before = form.value.content.substring(0, start)
    const after = form.value.content.substring(end)
    
    form.value.content = before + text + after
    
    // Restore cursor position
    requestAnimationFrame(() => {
        textarea.selectionStart = textarea.selectionEnd = start + text.length
        textarea.focus()
    })
}

onMounted(() => {
    loadPost()
})
</script>

<template>
    <div class="max-w-4xl mx-auto py-12 px-6">
        <!-- Header -->
        <div class="mb-10 text-center">
            <h1 class="text-3xl font-light tracking-tight mb-2">
                {{ isEditMode ? 'EDIT POST' : 'NEW POST' }}
            </h1>
            <div class="w-12 h-px bg-luxury-gold mx-auto"></div>
        </div>

        <div class="bg-white border border-gray-100 shadow-xl p-8 md:p-12 relative">
             <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-white/80 z-20">
                <div class="flex flex-col items-center gap-3">
                    <div class="w-8 h-8 border-2 border-gray-200 border-t-luxury-gold rounded-full animate-spin"></div>
                </div>
            </div>

            <div class="space-y-8">
                <!-- Title -->
                <div>
                    <label class="block text-xs uppercase tracking-widest text-gray-400 mb-2">Title</label>
                    <input 
                        v-model="form.title"
                        type="text" 
                        placeholder="Enter an engaging title..."
                        class="w-full h-12 border-b border-gray-200 focus:border-luxury-gold focus:outline-none text-xl font-light transition-colors placeholder-gray-300"
                    />
                </div>

                <!-- Content -->
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label class="block text-xs uppercase tracking-widest text-gray-400">Content</label>
                        <!-- Tabs -->
                        <div class="flex gap-4 text-xs font-medium">
                            <button 
                                @click="activeTab = 'write'" 
                                :class="activeTab === 'write' ? 'text-black border-b-2 border-black' : 'text-gray-400 hover:text-gray-600'"
                                class="uppercase tracking-widest pb-1 transition-all duration-300 !h-9 !px-4 !py-1 !text-[10px] !min-w-0 !bg-transparent hover:!bg-transparent !border hover:!border-gray-200 !border-transparent !shadow-none hover:!shadow-[0_0_10px_rgba(0,0,0,0.15)] hover:!translate-y-0 rounded-sm"
                            >
                                Write
                            </button>
                            <button 
                                @click="activeTab = 'preview'" 
                                :class="activeTab === 'preview' ? 'text-black border-b-2 border-black' : 'text-gray-400 hover:text-gray-600'"
                                class="uppercase tracking-widest pb-1 transition-all duration-300 !h-9 !px-4 !py-1 !text-[10px] !min-w-0 !bg-transparent hover:!bg-transparent !border hover:!border-gray-200 !border-transparent !shadow-none hover:!shadow-[0_0_10px_rgba(0,0,0,0.15)] hover:!translate-y-0 rounded-sm"
                            >
                                Preview
                            </button>
                        </div>

                    </div>

                    <!-- Write Mode -->
                    <textarea 
                        v-if="activeTab === 'write'"
                        ref="textareaRef"
                        v-model="form.content"
                        @paste="handlePaste"
                        rows="12"
                        placeholder="Share your insights... (Paste images directly!)"
                        class="w-full border border-gray-200 p-4 focus:border-luxury-gold focus:outline-none font-light text-base leading-relaxed transition-colors placeholder-gray-300 resize-y"
                    ></textarea>

                    <!-- Preview Mode -->
                    <div 
                        v-else 
                        class="w-full border border-gray-200 p-4 min-h-[320px] bg-gray-50/30 prose max-w-none font-light text-gray-800 leading-relaxed whitespace-pre-wrap text-left indent-4"
                    >
                         <template v-if="!form.content.trim()">
                            <span class="text-gray-400 opacity-50">Nothing to preview...</span>
                         </template>
                         <template v-else v-for="(segment, index) in parsedContent" :key="index">
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

                <!-- Image Upload -->
                <div>
                    <label class="block text-xs uppercase tracking-widest text-gray-400 mb-2">Featured Image (Optional)</label>
                    
                    <div v-if="!imagePreview" class="border border-dashed border-gray-300 p-8 text-center hover:bg-gray-50 transition-colors cursor-pointer relative">
                        <input type="file" @change="handleFileUpload" accept="image/*" class="absolute inset-0 opacity-0 cursor-pointer" />
                        <span class="text-gray-400 font-light text-sm pointer-events-none">Click or Drag to Upload Image</span>
                    </div>

                    <div v-else class="relative w-fit group">
                        <img :src="imagePreview" alt="Preview" class="max-h-64 object-cover border border-gray-100 shadow-sm" />
                        <button 
                            @click="removeImage"
                            class="absolute top-2 right-2 bg-black/70 text-white w-6 h-6 flex items-center justify-center rounded-full hover:bg-red-600 transition-colors"
                        >
                            &times;
                        </button>
                    </div>
                </div>

                <!-- Options -->
                 <div class="flex items-center gap-2">
                    <input type="checkbox" id="isPublic" v-model="form.is_public" class="accent-black w-4 h-4" />
                    <label for="isPublic" class="text-sm text-gray-600 font-light cursor-pointer select-none">Public Post</label>
                </div>

                <!-- Actions -->
                <div class="flex justify-end gap-4 pt-4 border-t border-gray-50">
                    <button 
                        @click="cancel"
                        class="px-6 py-2 border border-gray-200 text-gray-500 text-xs uppercase tracking-widest transition-all duration-300 hover:border-red-200 hover:text-red-600 hover:bg-red-50 hover:shadow-[0_0_15px_rgba(220,38,38,0.15)] hover:-translate-y-0.5 rounded-sm bg-white"
                    >
                        Cancel
                    </button>
                    <button 
                        @click="savePost"
                        class="px-6 py-2 bg-black text-white text-xs uppercase tracking-widest hover:bg-luxury-gold transition-colors rounded-sm"
                    >
                        {{ isEditMode ? 'Update Post' : 'Publish Post' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
