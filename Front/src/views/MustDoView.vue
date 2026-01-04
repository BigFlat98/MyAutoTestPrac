<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { api } from '@/api'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'

// Dummy Data Generation for UI Verification
const todos = ref([])
// Form State
const form = ref({
    title: '',
    description: '',
    start_date: '',
    end_date: '',
    due_date: '', // Legacy support if needed, or mapped to end_date
})
const isLoading = ref(false)

// Calendar Options
const calendarOptions = ref({
    plugins: [ dayGridPlugin, interactionPlugin ],
    initialView: 'dayGridMonth',
    headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,dayGridWeek'
    },
    events: [],
    eventClick: (info) => {
        const todoId = info.event.id
        const todo = todos.value.find(t => t.id == todoId)
        if (todo) {
            todo.expanded = true
            // Allow DOM to update with expanded state
            setTimeout(() => {
                const el = document.getElementById(`todo-${todoId}`)
                if (el) {
                    el.scrollIntoView({ behavior: 'smooth', block: 'center' })
                    el.classList.add('ring-2', 'ring-luxury-gold', 'ring-offset-2')
                    setTimeout(() => el.classList.remove('ring-2', 'ring-luxury-gold', 'ring-offset-2'), 2000)
                }
            }, 100)
        }
    },
    editable: false,
    selectable: true
})

// Update Calendar Events from Todos
const updateCalendarEvents = () => {
    calendarOptions.value.events = todos.value.map(t => ({
        id: t.id,
        title: t.title,
        start: t.start_date || t.created_at, // Fallback to created_at if no start_date
        end: t.end_date || t.due_date,
        allDay: true,
        backgroundColor: t.is_done ? '#10B981' : '#3B82F6', // Green if done, Blue otherwise
        borderColor: t.is_done ? '#10B981' : '#3B82F6'
    }))
}

// Watch todos to update calendar
watch(todos, () => {
    updateCalendarEvents()
}, { deep: true })

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
            start_date: t.start_date || null,
            end_date: t.end_date || t.due_date,
            due_date: t.due_date || t.end_date, // Sync for legacy display logic
            expanded: false
        }))
        updateCalendarEvents()
    } catch (error) {
        console.error('Failed to fetch todos:', error)
    } finally {
        isLoading.value = false
    }
}

// Function to add a todo
const addTodo = async () => {
    // Validate: Title required, and at least one date or just title is allowed?
    // Request says "startdate, enddate logic added", implied required? Enforce Title
    if (!form.value.title.trim()) {
        alert("Title is required.");
        return;
    }

    try {
        const payload = {
            content: form.value.title,
            title: form.value.title,
            description: form.value.description,
            start_date: form.value.start_date || null,
            end_date: form.value.end_date || form.value.due_date || null,
            due_date: form.value.end_date || form.value.due_date || null
        }

        const response = await api.post('/todos', payload)
        
        // Add local state
        todos.value.push({
            ...response.data,
            title: payload.title,
            description: payload.description,
            start_date: payload.start_date,
            end_date: payload.end_date,
            due_date: payload.due_date,
            expanded: false 
        })
        
        // Reset Form
        form.value = { title: '', description: '', start_date: '', end_date: '', due_date: '' }
    } catch (error) {
        console.error('Failed to add todo:', error)
    }
}

// Function to toggle todo status
const toggleTodo = async (todo) => {
    try {
        const response = await api.put(`/todos/${todo.id}`, {
            is_done: !todo.is_done,
            title: todo.title,
            description: todo.description,
            due_date: todo.due_date,
            start_date: todo.start_date,
            end_date: todo.end_date
        })
        todo.is_done = response.data.is_done
    } catch (error) {
        if (error.response && error.response.status === 403) {
            alert("권한이 없습니다. (작성자만 수정 가능)")
            todo.is_done = !todo.is_done // visual revert
        } else {
            console.error('Failed to toggle todo:', error)
        }
    }
}

// Function to delete todo
const deleteTodo = async (id) => {
    if(!confirm("Are you sure?")) return;
    try {
        await api.delete(`/todos/${id}`)
        todos.value = todos.value.filter(t => t.id !== id)
    } catch (error) {
        if (error.response && error.response.status === 403) {
            alert("권한이 없습니다. (작성자 또는 관리자만 삭제 가능)")
        } else {
            console.error('Failed to delete todo:', error)
        }
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
  el.offsetHeight; // Force reflow
  el.style.transition = 'all 0.5s cubic-bezier(0.25, 0.8, 0.25, 1)';
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
            due_date: todo.due_date,
            start_date: todo.start_date,
            end_date: todo.end_date
        })
        alert("Updated!");
    } catch (error) {
        if (error.response && error.response.status === 403) {
            alert("권한이 없습니다. (작성자만 수정 가능)")
        } else {
             console.error('Failed to update:', error)
        }
    }
}

// Urgency Color Logic
const getUrgencyClass = (dueDate, createdAt, isDone) => {
    if (isDone) return 'border-green-400 bg-green-50'

    if (createdAt) {
        const created = new Date(createdAt)
        const now = new Date()
        const diffCreatedHours = (now - created) / (1000 * 60 * 60)
        if (diffCreatedHours < 1) return 'border-lime-400 bg-lime-50' 
    }

    if (!dueDate) return 'border-gray-100' // Default
    
    const now = new Date()
    now.setHours(0,0,0,0)
    const due = new Date(dueDate)
    const diffMs = due - now
    const diffDays = diffMs / (1000 * 60 * 60 * 24)

    if (diffDays < 0) return 'border-red-600 bg-red-50' // Overdue
    if (diffDays < 1) return 'border-orange-500 bg-orange-50 animate-pulse-slow' // Today/Tomorrow
    if (diffDays < 3) return 'border-orange-300' // < 3 Days
    if (diffDays < 7) return 'border-yellow-400' // < 7 Days
    if (diffDays < 14) return 'border-green-300' // < 2 Weeks (Green)
    
    return 'border-gray-100' // > 2 Weeks (Gray)
}

const getDaysLeftText = (dueDate) => {
    if (!dueDate) return ''
    const now = new Date()
    now.setHours(0,0,0,0)
    const due = new Date(dueDate)
    const diffTime = now - due
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) 
    
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
            <div class="md:col-span-12">
                <label class="block text-xs uppercase tracking-widest text-gray-400 mb-1">Title</label>
                <input 
                    v-model="form.title"
                    type="text" 
                    placeholder="Task Title" 
                    class="w-full h-[3.2rem] border border-gray-200 px-4 focus:outline-none focus:border-luxury-gold focus:ring-1 focus:ring-luxury-gold transition-all font-light"
                />
            </div>
            
            <!-- Date Inputs -->
            <div class="md:col-span-6">
                 <label class="block text-xs uppercase tracking-widest text-gray-400 mb-1">Start Date</label>
                 <input 
                    v-model="form.start_date"
                    type="date" 
                    class="w-full h-[3.2rem] border border-gray-200 px-4 focus:outline-none focus:border-luxury-gold focus:ring-1 focus:ring-luxury-gold transition-all font-light"
                />
            </div>
            <div class="md:col-span-6">
                 <label class="block text-xs uppercase tracking-widest text-gray-400 mb-1">End Date (Due)</label>
                 <input 
                    v-model="form.end_date"
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

    <!-- Calendar Area -->
    <div class="mb-12 shadow-lg border border-gray-100 p-6 bg-white">
        <FullCalendar :options="calendarOptions" />
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
        :id="'todo-' + todo.id"
        class="group border-l-4 transition-all duration-300 shadow-sm bg-white"
        :class="[getUrgencyClass(todo.end_date || todo.due_date, todo.created_at, todo.is_done)]"
      >
        <!-- Summary Row (Click to Expand) -->
        <div class="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50" @click="toggleAccordion(todo)">
            <div class="flex items-center gap-4 flex-1">
                 <!-- Custom Checkbox (Stop propagation to prevent accordion toggle) -->
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
                    <span class="text-xs text-gray-400 font-mono flex items-center gap-1 shrink-0" v-if="todo.end_date || todo.due_date">
                        {{ new Date(todo.end_date || todo.due_date).toLocaleDateString() }}
                        <span class="font-medium ml-1" :class="{
                            'text-red-400': getDaysLeftText(todo.end_date || todo.due_date) === 'Overdue',
                            'text-orange-400': getDaysLeftText(todo.end_date || todo.due_date) === 'Due Today',
                            'text-blue-400': getDaysLeftText(todo.end_date || todo.due_date).includes('days left')
                        }">
                           ({{ getDaysLeftText(todo.end_date || todo.due_date) }})
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
                     <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
                        <div class="md:col-span-12">
                            <label class="block text-xs uppercase tracking-widest text-gray-400 mb-1">Title</label>
                            <input 
                                v-model="todo.title"
                                type="text"
                                class="w-full bg-white border border-gray-200 h-[2.8rem] px-3 font-light text-sm focus:outline-none focus:border-black transition-colors"
                            />
                        </div>
                        <div class="md:col-span-6">
                            <label class="block text-xs uppercase tracking-widest text-gray-400 mb-1">Start Date</label>
                            <input 
                                v-model="todo.start_date"
                                type="date"
                                class="w-full bg-white border border-gray-200 h-[2.8rem] px-3 font-light text-sm focus:outline-none focus:border-black transition-colors"
                            />
                        </div>
                        <div class="md:col-span-6">
                            <label class="block text-xs uppercase tracking-widest text-gray-400 mb-1">End Date</label>
                            <input 
                                v-model="todo.end_date"
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

<style>
/* FullCalendar Overrides (Global or Deep Selector needed because they are child components) */
/* Note: In Vue scoped styles, use :deep() or place in global style. 
   Since we are in a scoped block, we will use :deep() */

:deep(.fc) {
  --fc-border-color: #f3f4f6; /* gray-100 */
  --fc-today-bg-color: #fdfce7; /* yellow-50 (luxurious warm tint) */
  font-family: inherit;
}

/* Toolbar Buttons */
:deep(.fc-button) {
  border-radius: 0 !important; /* Sharp edges */
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.75rem !important; /* text-xs */
  font-weight: 500;
  padding: 0.8rem 1.2rem !important;
  transition: all 0.3s ease;
  background-color: transparent !important;
  border: 1px solid #e5e7eb !important; /* gray-200 */
  color: #9ca3af !important; /* gray-400 */
  box-shadow: none !important;
}

:deep(.fc-button:hover) {
  border-color: #996515 !important; /* Luxury Gold */
  color: #996515 !important;
  background-color: transparent !important;
}

:deep(.fc-button-active) {
  background-color: #111827 !important; /* Black */
  border-color: #111827 !important;
  color: #ffffff !important;
}

:deep(.fc-button-active:hover) {
  background-color: #996515 !important; /* Gold Hover */
  border-color: #996515 !important;
}

/* Today Button Special Style */
:deep(.fc-today-button) {
  background-color: #f3f4f6 !important; /* gray-100 */
  color: #374151 !important; /* gray-700 */
  border: 1px solid #f3f4f6 !important;
  opacity: 1 !important;
}
:deep(.fc-today-button:disabled) {
  opacity: 0.5 !important;
}

/* Header Title */
:deep(.fc-toolbar-title) {
  font-size: 1.5rem !important;
  font-weight: 300 !important; /* Light */
  letter-spacing: -0.025em;
  color: #111827;
}

/* Calendar Grid */
:deep(.fc-col-header-cell-cushion) {
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  padding: 1rem 0 !important;
  color: #9ca3af; /* gray-400 */
  font-weight: normal;
  text-decoration: none !important;
}

:deep(.fc-daygrid-day-number) {
  color: #374151; /* gray-700 */
  font-weight: 300;
  padding: 0.5rem !important;
  text-decoration: none !important;
}

:deep(.fc-day-today) {
  background-color: transparent !important; /* Remove default yellow */
}
:deep(.fc-day-today .fc-daygrid-day-frame) {
  background-color: #fffbeb !important; /* amber-50 custom today */
}

/* Events */
:deep(.fc-event) {
  border: none !important;
  border-radius: 0 !important; /* Sharp edges */
  padding: 2px 4px;
  font-size: 0.75rem;
  font-weight: 300;
  cursor: pointer;
}
</style>

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