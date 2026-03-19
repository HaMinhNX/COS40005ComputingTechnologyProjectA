<template>
  <div class="ai-chatbox-container glass-morphism">
    <!-- Header -->
    <header class="chat-header">
      <div class="header-main">
        <div class="logo-orb">
          <Sparkles :size="20" class="sparkle-icon" />
        </div>
        <div class="header-text">
          <h2>MEDIC1 Intelligence</h2>
          <span class="status-badge">Powered by Gemini 1.5 Pro</span>
        </div>
      </div>
      
      <!-- Patient Selector for Doctors -->
      <div v-if="userRole === 'doctor'" class="patient-selector-wrapper">
        <select v-model="selectedPatientId" @change="clearChat" class="premium-select">
          <option :value="null" disabled>Chọn bệnh nhân phân tích...</option>
          <option v-for="p in patients" :key="p.patient_id" :value="p.patient_id">
            {{ p.full_name }}
          </option>
        </select>
      </div>

      <button @click="clearChat" class="icon-button" title="Xóa hội thoại">
        <Trash2 :size="18" />
      </button>
    </header>

    <!-- Chat Messages -->
    <div ref="messageContainer" class="chat-messages custom-scrollbar">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon-wrapper">
          <Bot :size="48" />
        </div>
        <h3 class="font-black text-2xl text-slate-900 mb-2">Tôi có thể giúp gì cho bạn?</h3>
        <p class="text-slate-500 max-w-sm mx-auto font-medium">
          Hỏi về bệnh nhân, phân tích chỉ số sức khỏe, hoặc yêu cầu tóm tắt quá trình phục hồi.
        </p>
      </div>

      <div v-for="(msg, idx) in messages" :key="idx" 
           :class="['message-row', msg.role === 'user' ? 'user' : 'assistant']">
        
        <div class="message-bubble" :class="{ 'streaming': msg.isStreaming }">
          <div class="message-content" v-html="formatContent(msg.content)"></div>
          <div class="message-meta">
            {{ msg.timestamp }}
          </div>
        </div>
      </div>

      <!-- Streaming Indicator -->
      <div v-if="isStreaming && !currentStreamingMessage" class="message-row assistant">
        <div class="message-bubble thinking">
          <div class="dot-typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
      <!-- Suggested Questions (The fix for "it fails to give chat questions") -->
      <div v-if="selectedPatientId && messages.length < 30" class="px-6 py-3 flex gap-2 overflow-x-auto custom-scrollbar no-scrollbar scroll-smooth">
        <button 
          v-for="sug in suggestedPrompts" 
          :key="sug"
          @click="useSuggestion(sug)"
          class="suggestion-pill"
        >
          {{ sug }}
        </button>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-container">
      <div class="input-wrapper">
        <textarea
          v-model="inputMessage"
          @keydown.enter.prevent="sendMessage"
          placeholder="Nhắn tin cho MEDIC1 AI..."
          :disabled="isStreaming || (userRole === 'doctor' && !selectedPatientId)"
          rows="1"
          ref="inputRef"
        ></textarea>
        <button 
          @click="sendMessage"
          :disabled="!inputMessage.trim() || isStreaming || (userRole === 'doctor' && !selectedPatientId)"
          class="send-button"
        >
          <Send :size="20" />
        </button>
      </div>
      <p v-if="userRole === 'doctor' && !selectedPatientId" class="error-text">Vui lòng chọn một bệnh nhân để bắt đầu phân tích</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { Sparkles, Send, Bot, Trash2 } from 'lucide-vue-next'
import { API_BASE_URL } from '../config'

const props = defineProps({
  initialPatientId: { type: String, default: null }
})

const messages = ref([])
const inputMessage = ref('')
const isStreaming = ref(false)
const messageContainer = ref(null)
const selectedPatientId = ref(props.initialPatientId)
const patients = ref([])
const userRole = ref('')
const currentUser = ref(null)
const currentStreamingMessage = ref(null)

const suggestedPrompts = computed(() => {
  if (userRole.value === 'doctor') {
    return [
      'Tóm tắt tình trạng bệnh nhân này',
      'Phân tích hiệu suất tập luyện gần đây',
      'Bệnh nhân có tiến bộ không?',
      'Các chỉ số sức khỏe có gì bất thường?'
    ]
  } else {
    return [
      'Tóm tắt tuần tập luyện của tôi',
      'Độ chính xác của tôi thế nào?',
      'Tôi cần cải thiện bài tập nào?',
      'Phân tích xu hướng nhịp tim của tôi'
    ]
  }
})

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
    console.error('Lỗi lấy danh sách:', e)
  }
}

const formatContent = (content) => {
  if (!content) return ''
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^\* (.*)$/gm, '<li>$1</li>')
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

const useSuggestion = (text) => {
  inputMessage.value = text
  sendMessage()
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

    if (!response.ok) throw new Error('Yêu cầu thất bại')

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    let assistantMsg = {
      role: 'assistant',
      content: '',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isStreaming: true
    }
    messages.value.push(assistantMsg)
    currentStreamingMessage.value = assistantMsg

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      
      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim()
          if (data === '[DONE]') break
          try {
            const parsed = JSON.parse(data)
            assistantMsg.content += parsed.text
            scrollToEnd()
          } catch (err) {}
        }
      }
    }
  } catch (err) {
    if (err.name !== 'AbortError') {
      console.error('AI Stream Error:', err)
      messages.value.push({
        role: 'assistant',
        content: `Lỗi: ${err.message}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      })
    }
  } finally {
    isStreaming.value = false
    currentStreamingMessage.value = null
    scrollToEnd()
  }
}
</script>

<style scoped>
.ai-chatbox-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.05);
  box-shadow: 0 20px 50px rgba(0,0,0,0.05);
}

.glass-morphism {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.chat-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.5);
}

.header-main {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-orb {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 20px rgba(99, 102, 241, 0.2);
}

.sparkle-icon {
  color: white;
  filter: drop-shadow(0 0 4px rgba(255,255,255,0.5));
}

.header-text h2 {
  font-size: 18px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1;
  margin-bottom: 4px;
}

.status-badge {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 6px;
}

.premium-select {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  outline: none;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.premium-select:focus {
  border-color: #6366f1;
  ring: 4px rgba(99, 102, 241, 0.1);
}

.icon-button {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: #94a3b8;
  transition: all 0.2s;
}

.icon-button:hover {
  background: #fee2e2;
  color: #ef4444;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 32px 24px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.empty-state {
  margin-top: auto;
  margin-bottom: auto;
  text-align: center;
  animation: fadeUp 0.6s ease-out;
}

.empty-icon-wrapper {
  width: 80px;
  height: 80px;
  background: #f8fafc;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  color: #cbd5e1;
}

.message-row {
  display: flex;
  width: 100%;
}

.message-row.user {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 80%;
  padding: 16px 20px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.6;
  position: relative;
  transition: transform 0.2s ease;
}

.user .message-bubble {
  background: #1e293b;
  color: white;
  border-bottom-right-radius: 4px;
  box-shadow: 0 10px 25px rgba(30, 41, 59, 0.1);
}

.assistant .message-bubble {
  background: white;
  color: #334155;
  border: 1px solid #f1f5f9;
  border-bottom-left-radius: 4px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}

.message-meta {
  font-size: 10px;
  font-weight: 600;
  margin-top: 8px;
  opacity: 0.5;
}

.user .message-meta {
  text-align: right;
}

.thinking {
  padding: 12px 18px;
}

.dot-typing {
  display: flex;
  gap: 4px;
}

.dot-typing span {
  width: 6px;
  height: 6px;
  background: #cbd5e1;
  border-radius: 50%;
  animation: dotPulse 1.4s infinite ease-in-out both;
}

.dot-typing span:nth-child(2) { animation-delay: 0.2s; }
.dot-typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotPulse {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.input-container {
  padding: 24px;
  background: rgba(255, 255, 255, 0.8);
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 8px;
  display: flex;
  align-items: flex-end;
  box-shadow: 0 10px 30px rgba(0,0,0,0.04);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.input-wrapper:focus-within {
  transform: translateY(-2px);
  border-color: #6366f1;
  box-shadow: 0 15px 40px rgba(99, 102, 241, 0.1);
}

textarea {
  flex: 1;
  background: transparent;
  border: none;
  padding: 12px 16px;
  font-size: 15px;
  font-weight: 500;
  color: #1e293b;
  outline: none;
  resize: none;
  max-height: 200px;
}

.send-button {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #6366f1;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-button:disabled {
  background: #f1f5f9;
  color: #cbd5e1;
}

.send-button:not(:disabled):hover {
  background: #4f46e5;
  transform: scale(1.05);
}

.error-text {
  font-size: 11px;
  color: #ef4444;
  font-weight: 700;
  text-align: center;
  margin-top: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #cbd5e1; }

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-width: 600px;
  margin: 32px auto 0;
  animation: fadeUp 0.8s ease-out 0.2s both;
}

.suggestion-pill {
  background: white;
  border: 1px solid #f1f5f9;
  padding: 12px 16px;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  text-align: left;
  transition: all 0.2s;
  box-shadow: 0 4px 10px rgba(0,0,0,0.02);
}

.suggestion-pill:hover {
  border-color: #6366f1;
  color: #6366f1;
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(99, 102, 241, 0.05);
}
</style>
