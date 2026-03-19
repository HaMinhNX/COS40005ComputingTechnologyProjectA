<template>
  <div class="flex flex-col h-full bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200">
    <!-- Header -->
    <header class="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
          <Sparkles :size="20" />
        </div>
        <div>
          <h2 class="text-lg font-black text-slate-900 leading-tight">Trợ lý MEDIC1 AI</h2>
          <p class="text-[11px] text-slate-500 font-bold uppercase tracking-wider">Sức mạnh từ Gemini 1.5</p>
        </div>
      </div>
      
      <!-- Patient Selector for Doctors -->
      <div v-if="userRole === 'doctor'" class="flex items-center gap-2">
        <span class="text-xs font-bold text-slate-400">Đang hỏi về:</span>
        <select 
          v-model="selectedPatientId" 
          @change="clearChat"
          class="bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-xs font-bold text-slate-700 focus:ring-2 focus:ring-indigo-500 outline-none transition-all shadow-sm"
        >
          <option :value="null" disabled>Chọn bệnh nhân...</option>
          <option v-for="p in patients" :key="p.patient_id" :value="p.patient_id">
            {{ p.full_name }}
          </option>
        </select>
      </div>
    </header>

    <!-- Chat Messages -->
    <div ref="messageContainer" class="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:24px_24px]">
      <div v-if="messages.length === 0" class="h-full flex flex-col items-center justify-center text-center opacity-40 py-12">
        <div class="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mb-4">
          <Bot :size="32" class="text-slate-400" />
        </div>
        <h3 class="text-xl font-black text-slate-900 mb-2">Xin chào! Tôi có thể giúp gì?</h3>
        <p class="text-sm font-medium text-slate-500 max-w-sm">Hãy đặt câu hỏi về bệnh nhân, các bài tập hoặc kết quả phục hồi chức năng.</p>
      </div>

      <div v-for="(msg, idx) in messages" :key="idx" 
           :class="['flex gap-4 animate-in slide-in-from-bottom-2 duration-300', msg.role === 'user' ? 'justify-end' : '']">
        
        <!-- AI Avatar -->
        <div v-if="msg.role === 'assistant'" class="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-white shrink-0 shadow-lg">
          <Sparkles :size="18" />
        </div>

        <div :class="[
          'max-w-[85%] rounded-2xl p-4 shadow-sm relative',
          msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-white border border-slate-100 text-slate-800 rounded-tl-none'
        ]">
          <!-- Simple formatting -->
          <div class="text-sm leading-relaxed whitespace-pre-wrap font-medium" v-html="formatContent(msg.content)"></div>
          <div :class="['text-[10px] mt-2 opacity-50 font-bold', msg.role === 'user' ? 'text-indigo-100' : 'text-slate-400']">
            {{ msg.timestamp }}
          </div>
        </div>
      </div>

      <!-- Typing indicator / Streaming target -->
      <div v-if="isStreaming" class="flex gap-4 animate-pulse">
        <div class="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-white shrink-0 shadow-lg">
          <Sparkles :size="18" />
        </div>
        <div class="bg-white border border-slate-100 p-4 rounded-2xl rounded-tl-none max-w-[85%] shadow-sm">
          <div class="flex gap-1">
            <div class="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce"></div>
            <div class="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce [animation-delay:0.2s]"></div>
            <div class="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce [animation-delay:0.4s]"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="p-6 bg-slate-50/80 border-t border-slate-200">
      <div class="relative max-w-4xl mx-auto flex gap-3">
        <button v-if="messages.length > 0" @click="clearChat" 
                class="p-4 bg-white border border-slate-200 rounded-2xl text-slate-400 hover:text-red-500 hover:border-red-200 transition-all shadow-sm">
          <Trash2 :size="20" />
        </button>
        
        <div class="flex-1 relative group">
          <textarea
            v-model="inputMessage"
            @keydown.enter.prevent="sendMessage"
            rows="1"
            placeholder="Đặt câu hỏi cho MEDIC1 AI..."
            class="w-full bg-white border border-slate-200 rounded-2xl px-5 py-4 pr-14 text-sm font-medium focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none shadow-sm resize-none"
            :disabled="isStreaming || (userRole === 'doctor' && !selectedPatientId)"
          ></textarea>
          <button 
            @click="sendMessage"
            :disabled="!inputMessage.trim() || isStreaming || (userRole === 'doctor' && !selectedPatientId)"
            class="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-indigo-600 text-white rounded-xl flex items-center justify-center hover:bg-indigo-700 disabled:opacity-30 disabled:hover:bg-indigo-600 transition-all shadow-md active:scale-95"
          >
            <Send :size="18" />
          </button>
        </div>
      </div>
      <p v-if="userRole === 'doctor' && !selectedPatientId" class="text-[10px] text-red-500 font-bold mt-2 text-center uppercase tracking-widest">Vui lòng chọn bệnh nhân phía trên để bắt đầu hỏi đáp</p>
      <p class="text-[10px] text-slate-400 font-bold mt-2 text-center uppercase tracking-widest text-center block w-full">AI có thể cung cấp thông tin không hoàn toàn chính xác. Hãy tham khảo chuyên gia.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { Sparkles, Send, Bot, Trash2 } from 'lucide-vue-next'
import { API_BASE_URL } from '../config'

const props = defineProps({
  userId: { type: String, default: null }
})

const messages = ref([])
const inputMessage = ref('')
const isStreaming = ref(false)
const messageContainer = ref(null)
const selectedPatientId = ref(null)
const patients = ref([])
const userRole = ref('')
const currentUser = ref(null)

onMounted(async () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    currentUser.value = JSON.parse(userStr)
    userRole.value = currentUser.value.role
    if (userRole.value === 'doctor') {
      await fetchPatients()
    } else {
      selectedPatientId.value = currentUser.value.user_id
    }
  }
})

const fetchPatients = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE_URL}/patients-with-status`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      patients.value = await res.json()
    }
  } catch (e) {
    console.error('Lỗi khi lấy danh sách bệnh nhân:', e)
  }
}

const formatContent = (content) => {
  // Simple bold and list formatting
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-black text-slate-900">$1</strong>')
    .replace(/^\* (.*)$/gm, '<li class="ml-4">$1</li>')
    .replace(/\n/g, '<br/>')
}

const scrollToEnd = () => {
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  })
}

const clearChat = () => {
  messages.value = []
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isStreaming.value) return
  if (userRole.value === 'doctor' && !selectedPatientId.value) return

  const userMsg = inputMessage.value
  inputMessage.value = ''
  
  messages.value.push({
    role: 'user',
    content: userMsg,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })
  
  scrollToEnd()
  isStreaming.value = true
  
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`${API_BASE_URL}/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        patient_id: selectedPatientId.value,
        message: userMsg
      })
    })

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'Yêu cầu thất bại');
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    let assistantMsg = {
      role: 'assistant',
      content: '',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    messages.value.push(assistantMsg)

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      
      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim()
          if (data === '[DONE]') break
          if (!data) continue
          try {
            const parsed = JSON.parse(data)
            assistantMsg.content += parsed.text
            scrollToEnd()
          } catch (e) {
             console.error("JSON Parse Error during streaming:", e, "Data:", data)
          }
        }
      }
    }
  } catch (e) {
    console.error('AI Error:', e)
    messages.value.push({
      role: 'assistant',
      content: `Xin lỗi, đã có lỗi xảy ra: ${e.message}`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    })
  } finally {
    isStreaming.value = false
    scrollToEnd()
  }
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

.animate-in {
  animation-duration: 0.3s;
  animation-fill-mode: both;
}

@keyframes slide-in-bottom {
  from { transform: translateY(10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.slide-in-from-bottom-2 {
  animation-name: slide-in-bottom;
}
</style>
