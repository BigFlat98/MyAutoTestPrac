<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api'

// Dummy Data Generation for UI Verification
const todos = ref([])
// Form State
const form = ref({
    title: '',
    description: '',
    due_date: '',
})
const isLoading = ref(false)

// Function to fetch todos
const fetchTodos = async () => {
    isLoading.value = true
    try {
        const response = await api.get('/todos')
        // Ensure data compatibility if backend isn't ready
        todos.value = response.data.map(t => ({
            ...t,
            title: t.title || t.content, // Fallback for old data
            description: t.description || '',
            due_date: t.due_date || null,
            expanded: false
        }))
    } catch (error) {
        console.error('Failed to fetch todos:', error)
    } finally {
        isLoading.value = false
    }
}

// Function to add a todo
const addTodo = async () => {
    if (!form.value.title.trim() || !form.value.due_date) {
        alert("Title and Due Date are required.");
        return;
    }

    try {
        const payload = {
            content: form.value.title, // Backend might still expect 'content' until updated
            title: form.value.title,
            description: form.value.description,
            due_date: form.value.due_date,
            // author: null // Not sending yet as backend logic updates are next
        }

        const response = await api.post('/todos', payload)
        
        // Add local state
        todos.value.push({
            ...response.data,
            title: payload.title,
            description: payload.description,
            due_date: payload.due_date,
            expanded: false 
        })
        
        // Reset Form
        form.value = { title: '', description: '', due_date: '' }
    } catch (error) {
        console.error('Failed to add todo:', error)
    }
}

// Function to toggle todo status
const toggleTodo = async (todo) => {
    try {
        const response = await api.put(`/todos/${todo.id}`, {
            is_done: !todo.is_done,
            // Pass other fields to avoid nulling if backend is partial
            title: todo.title,
            description: todo.description,
            due_date: todo.due_date
        })
        todo.is_done = response.data.is_done
    } catch (error) {
        console.error('Failed to toggle todo:', error)
    }
}

// Function to delete todo
const deleteTodo = async (id) => {
    if(!confirm("Are you sure?")) return;
    try {
        await api.delete(`/todos/${id}`)
        todos.value = todos.value.filter(t => t.id !== id)
    } catch (error) {
        console.error('Failed to delete todo:', error)
    }
}

// Toggle Accordion
const toggleAccordion = (todo) => {
    todo.expanded = !todo.expanded
}

// Accordion Animation Hooks
const beforeEnter = (el) => {
  el.style.maxHeight = '0';
  el.style.opacity = '0';
  el.style.paddingTop = '0';
  el.style.paddingBottom = '0';
  el.style.overflow = 'hidden';
}

const enter = (el) => {
  // Force reflow
  el.offsetHeight;
  
  el.style.transition = 'all 0.5s cubic-bezier(0.25, 0.8, 0.25, 1)';
  // Calculate full height including padding (scrollHeight usually includes padding)
  el.style.maxHeight = el.scrollHeight + 'px';
  el.style.opacity = '1';
  el.style.paddingTop = ''; // Revert to CSS value
  el.style.paddingBottom = '';
}

const afterEnter = (el) => {
  el.style.transition = '';
  el.style.maxHeight = ''; // Allow auto expansion
  el.style.overflow = '';
}

const beforeLeave = (el) => {
  el.style.maxHeight = el.scrollHeight + 'px';
  el.style.overflow = 'hidden';
}

const leave = (el) => {
  el.offsetHeight; // Force reflow
  el.style.transition = 'all 0.3s ease-in-out';
  el.style.maxHeight = '0';
  el.style.opacity = '0';
  el.style.paddingTop = '0';
  el.style.paddingBottom = '0';
}

// Save Description (Edit Mode)
const saveDescription = async (todo) => {
    try {
         await api.put(`/todos/${todo.id}`, {
            is_done: todo.is_done,
            title: todo.title,
            description: todo.description,
            due_date: todo.due_date
        })
        alert("Updated!");
    } catch (error) {
        console.error('Failed to update:', error)
    }
}

// Urgency Color Logic
const getUrgencyClass = (dueDate, createdAt) => {
    // New Task Logic (< 1 hour old)
    if (createdAt) {
        const created = new Date(createdAt)
        const now = new Date()
        const diffCreatedHours = (now - created) / (1000 * 60 * 60)
        // Changed to Lime (brighter green/yellow-green) as requested
        if (diffCreatedHours < 1) return 'border-lime-400 bg-lime-50' 
    }

    if (!dueDate) return 'border-gray-100' // Default
    
    const now = new Date()
    // Reset time for accurate date comparison
    now.setHours(0,0,0,0)
    const due = new Date(dueDate)
    const diffMs = due - now
    const diffDays = diffMs / (1000 * 60 * 60 * 24)

    if (diffDays < 0) return 'border-red-600 bg-red-50' // Overdue
    if (diffDays < 1) return 'border-orange-500 bg-orange-50 animate-pulse-slow' // Today/Tomorrow
    if (diffDays < 3) return 'border-orange-300' // < 3 Days
    if (diffDays < 7) return 'border-yellow-400' // < 7 Days
    
    return 'border-gray-100' // Default > 7 Days
}

const getDaysLeftText = (dueDate) => {
    if (!dueDate) return ''
    const now = new Date()
    now.setHours(0,0,0,0)
    const due = new Date(dueDate)
    const diffTime = now - due
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) 
    // now - due > 0 => Past (Overdue) => diffDays > 0
    // now - due < 0 => Future => diffDays < 0
    // now - due == 0 => Today => diffDays == 0
    
    if (diffDays > 0) return 'Overdue'
    if (diffDays === 0) return 'Due Today'
    if (diffDays < 0) return `${Math.abs(diffDays)} days left`
}

const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
    fetchTodos() 
})
</script>

<template>
  <div class="max-w-4xl mx-auto py-12 px-6">
    <!-- Header -->
    <div class="mb-12 text-center">
      <h1 class="text-4xl font-light tracking-tight mb-2">MUST DO LIST</h1>
      <div class="w-16 h-px bg-luxury-gold mx-auto"></div>
      <p class="text-xs uppercase tracking-widest text-gray-500 mt-4 font-medium">
        Prioritize what matters
      </p>
    </div>

    <!-- Input Form Area -->
    <div class="mb-12 shadow-lg border border-gray-100 p-6 bg-white">
        <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
            <!-- Title Input -->
            <div class="md:col-span-8">
                <label class="block text-xs uppercase tracking-widest text-gray-400 mb-1">Title</label>
                <input 
                    v-model="form.title"
                    type="text" 
                    placeholder="Task Title" 
                    class="w-full h-[3.2rem] border border-gray-200 px-4 focus:outline-none focus:border-luxury-gold focus:ring-1 focus:ring-luxury-gold transition-all font-light"
                />
            </div>
            <!-- Date Input -->
            <div class="md:col-span-4">
                <label class="block text-xs uppercase tracking-widest text-gray-400 mb-1">Due Date</label>
                <input 
                    v-model="form.due_date"
                    type="date" 
                    class="w-full h-[3.2rem] border border-gray-200 px-4 focus:outline-none focus:border-luxury-gold focus:ring-1 focus:ring-luxury-gold transition-all font-light"
                />
            </div>
            <!-- Description Input -->
            <div class="md:col-span-12">
                 <label class="block text-xs uppercase tracking-widest text-gray-400 mb-1">Description</label>
                 <textarea 
                    v-model="form.description"
                    rows="2"
                    placeholder="Detailed description..."
                    class="w-full border border-gray-200 p-4 focus:outline-none focus:border-luxury-gold focus:ring-1 focus:ring-luxury-gold transition-all font-light resize-none"
                 ></textarea>
            </div>
            <!-- Add Button -->
            <div class="md:col-span-12 flex justify-end">
                <button 
                    @click="addTodo"
                    class="h-[3.2rem] px-8 bg-black text-white text-xs uppercase tracking-widest hover:bg-luxury-gold transition-colors duration-300"
                >
                    Add Must Do
                </button>
            </div>
        </div>
    </div>

    <!-- Todo List -->
    <div class="space-y-4">
      <div v-if="isLoading" class="py-8 text-center text-gray-400 font-light">
        Loading...
      </div>

      <div v-else-if="todos.length === 0" class="py-12 text-center border border-dashed border-gray-200">
        <p class="text-gray-400 font-light italic">No critical tasks yet. Add one above.</p>
      </div>

      <div 
        v-else
        v-for="todo in todos" 
        :key="todo.id"
        class="group border-l-4 transition-all duration-300 shadow-sm bg-white"
        :class="[getUrgencyClass(todo.due_date, todo.created_at)]"
      >
        <!-- Summary Row (Click to Expand) -->
        <div class="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50" @click="toggleAccordion(todo)">
            <div class="flex items-center gap-4 flex-1">
                 <!-- Custom Checkbox (Stop propagation to prevent accordion toggle) -->
                 <!-- Custom Checkbox (Bare Checkmark Style) -->
                <button 
                    @click.stop="toggleTodo(todo)"
                    class="focus:outline-none transition-all duration-300 shrink-0 bg-transparent border-none p-1"
                    :title="todo.is_done ? 'Mark as Undone' : 'Mark as Done'"
                >
                    <svg 
                        class="w-7 h-7 transition-colors duration-300"
                        :class="todo.is_done ? 'text-green-500' : 'text-gray-400 hover:text-green-500'"
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                    >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path>
                    </svg>
                </button>

                <div class="flex flex-col md:flex-row md:items-baseline gap-2 min-w-0 flex-1">
                    <span 
                        class="font-light text-lg transition-all duration-300 truncate max-w-[12rem] md:max-w-[24rem]"
                        :class="todo.is_done ? 'text-gray-300 line-through' : 'text-black'"
                        :title="todo.title"
                    >
                        {{ todo.title }}
                    </span>
                    <span class="text-xs text-gray-400 font-mono flex items-center gap-1 shrink-0" v-if="todo.due_date">
                        {{ new Date(todo.due_date).toLocaleDateString() }}
                        <span class="font-medium ml-1" :class="{
                            'text-red-400': getDaysLeftText(todo.due_date) === 'Overdue',
                            'text-orange-400': getDaysLeftText(todo.due_date) === 'Due Today',
                            'text-blue-400': getDaysLeftText(todo.due_date).includes('days left')
                        }">
                           ({{ getDaysLeftText(todo.due_date) }})
                        </span>
                    </span>
                </div>
            </div>

            <!-- Arrow Icon -->
            <div class="text-gray-400 transition-transform duration-300" :class="{ 'rotate-180': todo.expanded }">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
        </div>

        <!-- Accordion Content -->
        <transition
            @before-enter="beforeEnter"
            @enter="enter"
            @after-enter="afterEnter"
            @before-leave="beforeLeave"
            @leave="leave"
        >
            <div 
                v-show="todo.expanded" 
                class="border-t border-gray-100 bg-gray-50 p-6 overflow-hidden"
            >
                <div class="flex flex-col gap-4">
                     <!-- Edit Title & Date -->
                     <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs uppercase tracking-widest text-gray-400 mb-1">Title</label>
                            <input 
                                v-model="todo.title"
                                type="text"
                                class="w-full bg-white border border-gray-200 h-[2.8rem] px-3 font-light text-sm focus:outline-none focus:border-black transition-colors"
                            />
                        </div>
                        <div>
                            <label class="block text-xs uppercase tracking-widest text-gray-400 mb-1">Due Date</label>
                            <input 
                                v-model="todo.due_date"
                                type="date"
                                class="w-full bg-white border border-gray-200 h-[2.8rem] px-3 font-light text-sm focus:outline-none focus:border-black transition-colors"
                            />
                        </div>
                     </div>

                     <div>
                        <label class="block text-xs uppercase tracking-widest text-gray-400 mb-1">Description</label>
                        <textarea 
                            v-model="todo.description"
                            rows="3"
                            class="w-full bg-white border border-gray-200 p-3 font-light text-sm focus:outline-none focus:border-black transition-colors"
                            placeholder="Add details..."
                        ></textarea>
                     </div>
                    
                    <div class="flex justify-end gap-2">
                        <button 
                            @click="deleteTodo(todo.id)"
                            class="px-4 py-2 text-xs text-red-500 uppercase tracking-widest hover:bg-red-50 transition-colors border border-transparent hover:border-red-100 rounded-sm"
                        >
                            Delete
                        </button>
                        <button 
                            @click="saveDescription(todo)"
                            class="px-6 py-2 bg-black text-white text-xs uppercase tracking-widest hover:bg-luxury-gold transition-colors rounded-sm"
                        >
                            Save Details
                        </button>
                    </div>
                </div>
            </div>
        </transition>

      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.95; }
}
.animate-pulse-slow {
  animation: pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Accordion Transitions Handled by JS */
</style>