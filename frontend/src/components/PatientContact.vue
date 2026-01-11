<template>
  <div class="flex h-[calc(100vh-140px)] bg-white rounded-[2rem] shadow-xl border border-slate-100 overflow-hidden">
    <!-- Sidebar: Doctors List -->
    <div class="w-80 bg-slate-50 border-r border-slate-100 flex flex-col">
      <div class="p-6 border-b border-slate-100">
        <h2 class="text-xl font-black text-slate-900 mb-4">Bác sĩ</h2>
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" :size="18" />
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Tìm bác sĩ..." 
            class="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-sm font-bold focus:ring-2 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all"
          />
        </div>
      </div>

      <div class="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-2">
        <button 
          v-for="doc in filteredDoctors" 
          :key="doc.doctor_id"
          @click="selectDoctor(doc)"
          :class="['w-full p-4 rounded-2xl flex items-center gap-4 transition-all text-left group',
            selectedDoctor?.doctor_id === doc.doctor_id 
              ? 'bg-white shadow-lg shadow-indigo-500/10 border border-indigo-100' 
              : 'hover:bg-white hover:shadow-md border border-transparent'
          ]"
        >
          <div class="relative">
            <div class="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-lg shadow-md">
              {{ getInitials(doc.full_name) }}
            </div>
            <span class="absolute bottom-0 right-0 w-3.5 h-3.5 bg-emerald-500 border-2 border-white rounded-full"></span>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-bold text-slate-900 truncate group-hover:text-indigo-600 transition-colors">{{ doc.full_name }}</h3>
            <p class="text-xs font-medium text-slate-500 truncate">{{ doc.specialty || 'Bác sĩ' }}</p>
          </div>
        </button>
      </div>
    </div>

    <!-- Chat Area -->
    <div class="flex-1 flex flex-col bg-white relative">
      <div v-if="selectedDoctor" class="flex-1 flex flex-col h-full">
        <!-- Chat Header -->
        <div class="h-20 px-8 border-b border-slate-100 flex items-center justify-between bg-white/80 backdrop-blur-xl z-10">
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold">
              {{ getInitials(selectedDoctor.full_name) }}
            </div>
            <div>
              <h3 class="font-bold text-slate-900">{{ selectedDoctor.full_name }}</h3>
              <span class="flex items-center gap-1.5 text-xs font-bold text-emerald-500">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                Trực tuyến
              </span>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <div class="flex-1 overflow-y-auto p-8 space-y-6 custom-scrollbar bg-slate-50/50" ref="messagesContainer">
          <div v-for="(msg, index) in messages" :key="index" 
               :class="['flex w-full', msg.sender_id === userId ? 'justify-end' : 'justify-start']">
            <div :class="['max-w-[70%] rounded-2xl p-4 shadow-sm font-medium text-sm leading-relaxed',
              msg.sender_id === userId 
                ? 'bg-gradient-to-br from-indigo-600 to-violet-600 text-white rounded-tr-none' 
                : 'bg-white border border-slate-100 text-slate-600 rounded-tl-none'
            ]">
              {{ msg.content }}
              <div :class="['text-[10px] font-bold mt-2 opacity-70', msg.sender_id === userId ? 'text-indigo-100' : 'text-slate-400']">
                {{ formatTime(msg.created_at) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="p-6 bg-white border-t border-slate-100">
          <div class="flex items-center gap-4 bg-slate-50 p-2 rounded-2xl border border-slate-200 focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-500/10 transition-all">
            <input 
              v-model="newMessage" 
              @keyup.enter="sendMessage"
              type="text" 
              placeholder="Nhập tin nhắn..." 
              class="flex-1 bg-transparent border-none outline-none px-4 py-2 text-sm font-bold text-slate-900 placeholder-slate-400"
            />
            <button 
              @click="sendMessage"
              :disabled="!newMessage.trim()"
              class="p-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-indigo-500/20"
            >
              <Send :size="18" />
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="flex-1 flex flex-col items-center justify-center text-slate-400 bg-slate-50/30">
        <div class="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mb-6 animate-bounce">
          <MessageCircle :size="40" class="text-slate-300" />
        </div>
        <h3 class="text-xl font-black text-slate-900 mb-2">Chọn bác sĩ để trò chuyện</h3>
        <p class="text-sm font-medium max-w-xs text-center">Kết nối trực tiếp với đội ngũ y tế để được tư vấn và hỗ trợ kịp thời.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { Search, Send, MessageCircle } from 'lucide-vue-next'

const props = defineProps(['userId'])
const API_BASE = 'http://localhost:8000/api'

const doctors = ref([])
const searchQuery = ref('')
const selectedDoctor = ref(null)
const messages = ref([])
const newMessage = ref('')
const messagesContainer = ref(null)

// Mock data if API fails
const mockDoctors = [
  { doctor_id: 'd1', full_name: 'BS. Lê Minh', specialty: 'Tim mạch' },
  { doctor_id: 'd2', full_name: 'BS. Nguyễn Lan', specialty: 'Phục hồi chức năng' },
  { doctor_id: 'd3', full_name: 'BS. Trần Hùng', specialty: 'Thần kinh' }
]

const filteredDoctors = computed(() => {
  if (!searchQuery.value) return doctors.value
  const query = searchQuery.value.toLowerCase()
  return doctors.value.filter(d => 
    d.full_name.toLowerCase().includes(query) ||
    (d.specialty && d.specialty.toLowerCase().includes(query))
  )
})

function getInitials(name) {
  return name ? name.split(' ').map(s => s[0]).join('').slice(0, 2).toUpperCase() : 'BS'
}

function formatTime(isoString) {
  if (!isoString) return ''
  return new Date(isoString).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
}

async function loadDoctors() {
  try {
    const res = await fetch(`${API_BASE}/doctors`)
    if (res.ok) {
      doctors.value = await res.json()
    } else {
      doctors.value = mockDoctors
    }
  } catch (e) {
    console.error("Error loading doctors:", e)
    doctors.value = mockDoctors
  }
}

async function selectDoctor(doc) {
  selectedDoctor.value = doc
  await loadMessages()
}

async function loadMessages() {
  if (!selectedDoctor.value || !props.userId) return
  try {
    const res = await fetch(`${API_BASE}/messages/${props.userId}?other_user_id=${selectedDoctor.value.doctor_id}`)
    if (res.ok) {
      messages.value = await res.json()
      scrollToBottom()
    }
  } catch (e) {
    console.error("Error loading messages:", e)
  }
}

async function sendMessage() {
  if (!newMessage.value.trim() || !selectedDoctor.value) return
  
  const content = newMessage.value
  newMessage.value = '' // Optimistic clear

  // Optimistic UI update
  messages.value.push({
    sender_id: props.userId,
    receiver_id: selectedDoctor.value.doctor_id,
    content: content,
    created_at: new Date().toISOString()
  })
  scrollToBottom()

  try {
    const res = await fetch(`${API_BASE}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sender_id: props.userId,
        receiver_id: selectedDoctor.value.doctor_id,
        content: content
      })
    })
    
    if (!res.ok) {
      // Handle error (maybe remove message or show error)
      console.error("Failed to send message")
    }
  } catch (e) {
    console.error("Error sending message:", e)
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

onMounted(() => {
  loadDoctors()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}
</style>
