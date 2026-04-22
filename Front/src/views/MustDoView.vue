<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { api } from '@/api'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'

const todos = ref([])
const form = ref({
    title: '',
    description: '',
    start_date: '',
    end_date: '',
    due_date: '', 
})
const isLoading = ref(false)

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
            setTimeout(() => {
                const el = document.getElementById(`todo-${todoId}`)
                if (el) {
                    el.scrollIntoView({ behavior: 'smooth', block: 'center' })
                    el.classList.add('ring-2', 'ring-sky-400', 'ring-offset-2', 'ring-offset-slate-900')
                    setTimeout(() => el.classList.remove('ring-2', 'ring-sky-400', 'ring-offset-2', 'ring-offset-slate-900'), 2000)
                }
            }, 100)
        }
    },
    editable: false,
    selectable: true
})

const updateCalendarEvents = () => {
    calendarOptions.value.events = todos.value.map(t => ({
        id: t.id,
        title: t.title,
        start: t.start_date || t.created_at,
        end: t.end_date || t.due_date,
        allDay: true,
        backgroundColor: t.is_done ? '#10b981' : '#38bdf8',
        borderColor: t.is_done ? '#10b981' : '#38bdf8',
        textColor: '#ffffff'
    }))
}

watch(todos, () => {
    updateCalendarEvents()
}, { deep: true })

const fetchTodos = async () => {
    isLoading.value = true
    try {
        const response = await api.get('/todos')
        todos.value = response.data.map(t => ({
            ...t,
            title: t.title || t.content, 
            description: t.description || '',
            start_date: t.start_date || null,
            end_date: t.end_date || t.due_date,
            due_date: t.due_date || t.end_date,
            expanded: false
        }))
        updateCalendarEvents()
    } catch (error) {
        console.error('Failed to fetch todos:', error)
    } finally {
        isLoading.value = false
    }
}

const addTodo = async () => {
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
        
        todos.value.push({
            ...response.data,
            title: payload.title,
            description: payload.description,
            start_date: payload.start_date,
            end_date: payload.end_date,
            due_date: payload.due_date,
            expanded: false 
        })
        
        form.value = { title: '', description: '', start_date: '', end_date: '', due_date: '' }
    } catch (error) {
        console.error('Failed to add todo:', error)
    }
}

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
            todo.is_done = !todo.is_done 
        } else {
            console.error('Failed to toggle todo:', error)
        }
    }
}

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

const toggleAccordion = (todo) => {
    todo.expanded = !todo.expanded
}

const beforeEnter = (el) => {
  el.style.maxHeight = '0';
  el.style.opacity = '0';
  el.style.paddingTop = '0';
  el.style.paddingBottom = '0';
  el.style.overflow = 'hidden';
}

const enter = (el) => {
  el.offsetHeight; 
  el.style.transition = 'all 0.5s cubic-bezier(0.25, 0.8, 0.25, 1)';
  el.style.maxHeight = el.scrollHeight + 'px';
  el.style.opacity = '1';
  el.style.paddingTop = ''; 
  el.style.paddingBottom = '';
}

const afterEnter = (el) => {
  el.style.transition = '';
  el.style.maxHeight = ''; 
  el.style.overflow = '';
}

const beforeLeave = (el) => {
  el.style.maxHeight = el.scrollHeight + 'px';
  el.style.overflow = 'hidden';
}

const leave = (el) => {
  el.offsetHeight; 
  el.style.transition = 'all 0.3s ease-in-out';
  el.style.maxHeight = '0';
  el.style.opacity = '0';
  el.style.paddingTop = '0';
  el.style.paddingBottom = '0';
}

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

const getUrgencyClass = (dueDate, createdAt, isDone) => {
    if (isDone) return 'border-emerald-400 bg-emerald-400/5'

    if (createdAt) {
        const created = new Date(createdAt)
        const now = new Date()
        const diffCreatedHours = (now - created) / (1000 * 60 * 60)
        if (diffCreatedHours < 1) return 'border-sky-400 bg-sky-400/5' 
    }

    if (!dueDate) return 'border-white/10 bg-white/5' 
    
    const now = new Date()
    now.setHours(0,0,0,0)
    const due = new Date(dueDate)
    const diffMs = due - now
    const diffDays = diffMs / (1000 * 60 * 60 * 24)

    if (diffDays < 0) return 'border-red-500 bg-red-500/10' 
    if (diffDays < 1) return 'border-orange-500 bg-orange-500/10 animate-pulse-slow' 
    if (diffDays < 3) return 'border-orange-400 bg-orange-400/5' 
    if (diffDays < 7) return 'border-yellow-400 bg-yellow-400/5' 
    if (diffDays < 14) return 'border-emerald-400 bg-emerald-400/5' 
    
    return 'border-white/10 bg-white/5' 
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

onMounted(() => {
    fetchTodos() 
})
</script>

<template>
  <div class="max-w-7xl mx-auto py-12 px-6">
    <!-- Header -->
    <header class="glass-header slide-up mb-12" style="animation-delay: 0.1s; display: block; text-align: left; padding: 20px 32px; border-radius: 20px;">
      <h1 class="glass-title text-4xl mb-2">MUST DO LIST</h1>
      <p class="glass-subtitle font-mono text-sm">
        Prioritize what matters
      </p>
    </header>

    <!-- Form & Calendar Layout (Side by Side) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-12">
      <!-- Input Form Area (Left) -->
      <div class="lg:col-span-4 flex flex-col">
        <div class="glass-card p-6 slide-up h-full flex flex-col" style="animation-delay: 0.2s;">
          <h2 class="text-sm uppercase tracking-widest text-sky-400 mb-6 font-medium shrink-0">New Task</h2>
          <div class="flex flex-col gap-4 flex-1 min-h-0">
              <!-- Title Input -->
              <div class="shrink-0">
                  <label class="block text-xs uppercase tracking-widest text-slate-400 mb-1">Title</label>
                  <input 
                      v-model="form.title"
                      type="text" 
                      placeholder="Task Title" 
                      class="w-full h-[3.2rem] bg-white/5 border border-white/10 px-4 focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all font-light text-white placeholder-slate-500 rounded-md"
                  />
              </div>
              
              <!-- Date Inputs -->
              <div class="grid grid-cols-2 gap-4 shrink-0">
                  <div>
                      <label class="block text-xs uppercase tracking-widest text-slate-400 mb-1">Start Date</label>
                      <input 
                          v-model="form.start_date"
                          type="date" 
                          class="w-full h-[3.2rem] bg-white/5 border border-white/10 px-4 focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all font-light text-white rounded-md [color-scheme:dark]"
                      />
                  </div>
                  <div>
                      <label class="block text-xs uppercase tracking-widest text-slate-400 mb-1">End Date</label>
                      <input 
                          v-model="form.end_date"
                          type="date" 
                          class="w-full h-[3.2rem] bg-white/5 border border-white/10 px-4 focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all font-light text-white rounded-md [color-scheme:dark]"
                      />
                  </div>
              </div>

              <!-- Description Input -->
              <div class="flex flex-col flex-1 min-h-[80px]">
                  <label class="block text-xs uppercase tracking-widest text-slate-400 mb-1 shrink-0">Description</label>
                  <textarea 
                      v-model="form.description"
                      placeholder="Detailed description..."
                      class="flex-1 w-full bg-white/5 border border-white/10 p-4 focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 transition-all font-light text-white placeholder-slate-500 rounded-md resize-none"
                  ></textarea>
              </div>

              <!-- Add Button -->
              <div class="flex justify-end mt-auto pt-2 shrink-0">
                  <button 
                      @click="addTodo"
                      class="h-[3.2rem] px-8 w-full bg-sky-500/20 text-sky-400 text-xs uppercase tracking-widest hover:bg-sky-400 hover:text-white transition-all duration-300 border border-sky-400/50 rounded-lg shadow-[0_0_15px_rgba(56,189,248,0.2)] hover:shadow-[0_0_20px_rgba(56,189,248,0.6)]"
                  >
                      Add Must Do
                  </button>
              </div>
          </div>
        </div>
      </div>

      <!-- Calendar Area (Right) -->
      <div class="lg:col-span-8 flex flex-col">
        <div class="glass-card p-6 slide-up h-full min-h-[500px]" style="animation-delay: 0.3s;">
          <FullCalendar :options="calendarOptions" class="h-full" />
        </div>
      </div>
    </div>

    <!-- Todo List -->
    <div class="space-y-4 slide-up" style="animation-delay: 0.4s;">
      <div v-if="isLoading" class="py-8 text-center text-slate-400 font-light">
        Loading...
      </div>

      <div v-else-if="todos.length === 0" class="py-12 text-center border border-dashed border-white/20 rounded-2xl">
        <p class="text-slate-400 font-light italic">No critical tasks yet. Add one above.</p>
      </div>

      <div 
        v-else
        v-for="todo in todos" 
        :key="todo.id"
        :id="'todo-' + todo.id"
        class="group border-l-4 transition-all duration-300 bg-white/5 backdrop-blur-md rounded-r-xl border-y border-r border-white/10 overflow-hidden hover:bg-white/10"
        :class="[getUrgencyClass(todo.end_date || todo.due_date, todo.created_at, todo.is_done)]"
      >
        <div class="flex items-center justify-between p-4 cursor-pointer" @click="toggleAccordion(todo)">
            <div class="flex items-center gap-4 flex-1">
                <button 
                    @click.stop="toggleTodo(todo)"
                    class="focus:outline-none transition-all duration-300 shrink-0 bg-transparent border-none p-1"
                    :title="todo.is_done ? 'Mark as Undone' : 'Mark as Done'"
                >
                    <svg 
                        class="w-7 h-7 transition-colors duration-300"
                        :class="todo.is_done ? 'text-emerald-400' : 'text-slate-500 hover:text-emerald-400'"
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
                        :class="todo.is_done ? 'text-slate-500 line-through' : 'text-slate-100'"
                        :title="todo.title"
                    >
                        {{ todo.title }}
                    </span>
                    <span class="text-xs text-slate-400 font-mono flex items-center gap-1 shrink-0" v-if="todo.end_date || todo.due_date">
                        {{ new Date(todo.end_date || todo.due_date).toLocaleDateString() }}
                        <span class="font-medium ml-1" :class="{
                            'text-red-400': getDaysLeftText(todo.end_date || todo.due_date) === 'Overdue',
                            'text-orange-400': getDaysLeftText(todo.end_date || todo.due_date) === 'Due Today',
                            'text-sky-400': getDaysLeftText(todo.end_date || todo.due_date).includes('days left')
                        }">
                           ({{ getDaysLeftText(todo.end_date || todo.due_date) }})
                        </span>
                    </span>
                </div>
            </div>

            <div class="text-slate-400 transition-transform duration-300" :class="{ 'rotate-180': todo.expanded }">
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
                class="border-t border-white/10 bg-black/20 p-6 overflow-hidden"
            >
                <div class="flex flex-col gap-4">
                     <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
                        <div class="md:col-span-12">
                            <label class="block text-xs uppercase tracking-widest text-slate-400 mb-1">Title</label>
                            <input 
                                v-model="todo.title"
                                type="text"
                                class="w-full bg-white/5 border border-white/10 h-[2.8rem] px-3 font-light text-sm text-white focus:outline-none focus:border-sky-400 rounded-md transition-colors"
                            />
                        </div>
                        <div class="md:col-span-6">
                            <label class="block text-xs uppercase tracking-widest text-slate-400 mb-1">Start Date</label>
                            <input 
                                v-model="todo.start_date"
                                type="date"
                                class="w-full bg-white/5 border border-white/10 h-[2.8rem] px-3 font-light text-sm text-white focus:outline-none focus:border-sky-400 rounded-md transition-colors [color-scheme:dark]"
                            />
                        </div>
                        <div class="md:col-span-6">
                            <label class="block text-xs uppercase tracking-widest text-slate-400 mb-1">End Date</label>
                            <input 
                                v-model="todo.end_date"
                                type="date"
                                class="w-full bg-white/5 border border-white/10 h-[2.8rem] px-3 font-light text-sm text-white focus:outline-none focus:border-sky-400 rounded-md transition-colors [color-scheme:dark]"
                            />
                        </div>
                     </div>

                     <div>
                        <label class="block text-xs uppercase tracking-widest text-slate-400 mb-1">Description</label>
                        <textarea 
                            v-model="todo.description"
                            rows="3"
                            class="w-full bg-white/5 border border-white/10 p-3 font-light text-sm text-white focus:outline-none focus:border-sky-400 rounded-md transition-colors"
                            placeholder="Add details..."
                        ></textarea>
                     </div>
                    
                    <div class="flex justify-end gap-2 mt-2">
                        <button 
                            @click="deleteTodo(todo.id)"
                            class="px-4 py-2 text-xs text-red-400 uppercase tracking-widest hover:bg-red-400/10 transition-colors border border-transparent hover:border-red-400/50 rounded-full"
                        >
                            Delete
                        </button>
                        <button 
                            @click="saveDescription(todo)"
                            class="px-6 py-2 bg-sky-500/20 text-sky-400 border border-sky-400/50 text-xs uppercase tracking-widest hover:bg-sky-400 hover:text-white transition-colors rounded-full shadow-[0_0_15px_rgba(56,189,248,0.2)]"
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
:deep(.fc) {
  --fc-border-color: rgba(255,255,255,0.1); 
  --fc-page-bg-color: transparent;
  color: #e2e8f0; 
  font-family: inherit;
}

:deep(.fc-theme-standard td), 
:deep(.fc-theme-standard th),
:deep(.fc-theme-standard .fc-scrollgrid) {
    border-color: rgba(255,255,255,0.1) !important;
}

:deep(.fc-button) {
  border-radius: 8px !important; 
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.75rem !important; 
  font-weight: 500;
  padding: 0.8rem 1.2rem !important;
  transition: all 0.3s ease;
  background-color: transparent !important;
  border: 1px solid rgba(255,255,255,0.2) !important; 
  color: #94a3b8 !important; 
  box-shadow: none !important;
}

:deep(.fc-button:hover) {
  border-color: #38bdf8 !important; 
  color: #38bdf8 !important;
  background-color: rgba(56, 189, 248, 0.1) !important;
}

:deep(.fc-button-active) {
  background-color: rgba(56, 189, 248, 0.2) !important; 
  border-color: #38bdf8 !important;
  color: #38bdf8 !important;
}

:deep(.fc-button-active:hover) {
  background-color: rgba(56, 189, 248, 0.3) !important; 
  border-color: #38bdf8 !important;
  color: #38bdf8 !important; 
}

:deep(.fc-today-button) {
  background-color: rgba(255,255,255,0.1) !important; 
  color: #e2e8f0 !important; 
  border: 1px solid rgba(255,255,255,0.2) !important;
  opacity: 1 !important;
}
:deep(.fc-today-button:disabled) {
  opacity: 0.5 !important;
}

:deep(.fc-toolbar-title) {
  font-size: 1.5rem !important;
  font-weight: 300 !important; 
  letter-spacing: -0.025em;
  color: #f8fafc;
}

:deep(.fc-col-header-cell-cushion) {
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  padding: 1rem 0 !important;
  color: #94a3b8; 
  font-weight: normal;
  text-decoration: none !important;
}

:deep(.fc-daygrid-day-number) {
  color: #cbd5e1; 
  font-weight: 300;
  padding: 0.5rem !important;
  text-decoration: none !important;
}

:deep(.fc-day-today) {
  background-color: transparent !important; 
}
:deep(.fc-day-today .fc-daygrid-day-frame) {
  background-color: rgba(56, 189, 248, 0.1) !important; 
}

:deep(.fc-day-sat) {
    background-color: rgba(56, 189, 248, 0.05) !important; 
}
:deep(.fc-col-header-cell.fc-day-sat .fc-col-header-cell-cushion),
:deep(.fc-daygrid-day.fc-day-sat .fc-daygrid-day-number) {
    color: #7dd3fc !important; 
}

:deep(.fc-day-sun) {
    background-color: rgba(239, 68, 68, 0.05) !important; 
}
:deep(.fc-col-header-cell.fc-day-sun .fc-col-header-cell-cushion),
:deep(.fc-daygrid-day.fc-day-sun .fc-daygrid-day-number) {
    color: #fca5a5 !important; 
}

:deep(.fc-event) {
  border: none !important;
  border-radius: 4px !important; 
  padding: 2px 4px;
  font-size: 0.75rem;
  font-weight: 400;
  cursor: pointer;
}

@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}
.animate-pulse-slow {
  animation: pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>