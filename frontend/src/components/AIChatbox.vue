<template>
  <div class="ai-chatbox-container glass-morphism">
    <!-- Header -->
    <header class="chat-header" :class="{ 'has-patient': selectedPatientId }">
      <div class="header-main">
        <div class="logo-orb-wrapper">
          <div class="logo-orb">
            <Sparkles :size="20" class="sparkle-icon" />
          </div>
          <div class="status-pulse"></div>
        </div>
        <div class="header-text">
          <h2 v-if="!selectedPatientId">MEDIC1 Intelligence</h2>
          <div v-else class="active-patient-profile">
            <div class="patient-info">
              <span class="patient-label">Đang phân tích</span>
              <h2 class="patient-name">{{ currentPatientName }}</h2>
            </div>
            <button @click="selectedPatientId = null" class="change-patient-btn">
              <Users :size="14" />
              Thay đổi
            </button>
          </div>
          <span class="status-badge">Gemini 3 Flash • Real-time Analysis</span>
        </div>
      </div>
      
      <div class="header-actions">
        <button @click="clearChat" class="icon-button trash" title="Xóa hội thoại">
          <Trash2 :size="18" />
        </button>
      </div>
    </header>

    <!-- Chat Messages & Selection Area -->
    <div class="chat-main-stage">
      <!-- Chat History Sidebar (New) -->
      <aside v-if="selectedPatientId" class="chat-history-sidebar" :class="{ 'collapsed': isHistoryCollapsed }">
        <div class="sidebar-header">
          <button @click="isHistoryCollapsed = !isHistoryCollapsed" class="collapse-toggle">
            <LayoutPanelLeft :size="18" />
          </button>
          <span v-if="!isHistoryCollapsed" class="sidebar-title">Lịch sử hội thoại</span>
        </div>
        
        <div v-if="!isHistoryCollapsed" class="history-list-mini custom-scrollbar">
          <div v-for="h in mockHistory" :key="h.id" class="history-item-brief">
            <MessageSquare :size="14" />
            <span class="history-text">{{ h.title }}</span>
          </div>
          <div v-if="mockHistory.length === 0" class="empty-history-text">Chưa có lịch sử</div>
        </div>
      </aside>

      <div ref="messageContainer" 
           class="chat-viewport custom-scrollbar" 
           :class="{ 'sidebar-open': !isHistoryCollapsed && selectedPatientId }"
           @scroll="handleScroll">
        <!-- Patient Selector Grid (Visible when no patient selected) -->
        <div v-if="!selectedPatientId && userRole === 'doctor'" class="patient-selection-stage">
          <div class="selection-content">
            <div class="selection-header">
              <div class="icon-circle">
                <Users :size="32" />
              </div>
              <h3>Chọn bệnh nhân để phân tích</h3>
              <p>Chọn một bệnh nhân từ danh sách để bắt đầu phân tích dữ liệu y tế và hiệu suất tập luyện.</p>
            </div>
            
            <div class="patient-grid">
              <div v-for="p in patients" :key="p.patient_id" 
                   @click="selectPatient(p)"
                   class="patient-card-premium">
                <div class="card-avatar">
                  {{ p.full_name.charAt(0) }}
                </div>
                <div class="card-body">
                  <span class="name">{{ p.full_name }}</span>
                  <span class="status" :class="getStatusClass(p)">{{ getStatusLabel(p) }}</span>
                </div>
                <ChevronRight :size="18" class="arrow" />
              </div>
            </div>
          </div>
        </div>

        <!-- Main Chat Flow -->
        <template v-else>
          <!-- Empty State with Suggestions -->
          <div v-if="messages.length === 0" class="empty-state">
            <div class="ai-hero">
              <div class="ai-icon-hex">
                <Bot :size="48" />
              </div>
              <h3>Tôi có thể giúp gì cho {{ userRole === 'doctor' ? 'ca bệnh này' : 'bạn' }}?</h3>
              <p>Hỏi về bệnh nhân, phân tích chỉ số sức khỏe, hoặc yêu cầu tóm tắt quá trình phục hồi.</p>
            </div>
            
            <div class="suggestions-container">
              <button 
                v-for="sug in suggestedPrompts" 
                :key="sug"
                @click="useSuggestion(sug)"
                class="suggestion-card"
              >
                <span class="sug-text">{{ sug }}</span>
                <ArrowUpRight :size="16" />
              </button>
            </div>
          </div>

          <!-- Message List -->
          <div class="messages-list">
            <div v-for="(msg, idx) in messages" :key="idx" 
                 :class="['message-row', msg.role === 'user' ? 'user' : 'assistant']">
              
              <div class="message-bubble" :class="{ 'streaming': msg.isStreaming }">
                <div class="message-content markdown-body" v-html="renderMarkdown(msg.displayContent || msg.content)"></div>
                <div class="message-meta">
                  <span class="time">{{ msg.timestamp }}</span>
                  <span v-if="msg.isStreaming" class="streaming-indicator">Đang trả lời...</span>
                </div>
              </div>
            </div>

            <!-- Thinking Indicator -->
            <div v-if="isStreaming && !currentStreamingMessage" class="message-row assistant">
              <div class="message-bubble thinking-bubble">
                <div class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Input Area -->
    <div class="chat-input-area" :class="{ 'disabled': !selectedPatientId }">
      <div class="input-container-inner">
        <div class="input-wrapper">
          <textarea
            v-model="inputMessage"
            @keydown.enter.prevent="sendMessage"
            placeholder="Nhập câu hỏi tại đây..."
            :disabled="isStreaming || !selectedPatientId"
            rows="1"
            ref="inputRef"
            @input="adjustTextarea"
          ></textarea>
          <button 
            @click="sendMessage"
            :disabled="!inputMessage.trim() || isStreaming || !selectedPatientId"
            class="send-button-premium"
          >
            <Send :size="20" />
          </button>
        </div>
        <p v-if="!selectedPatientId && userRole === 'doctor'" class="helper-text warning">
          <AlertCircle :size="14" />
          Vui lòng chọn bệnh nhân phía trên để bắt đầu
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { Sparkles, Send, Bot, Trash2, Users, ChevronRight, ArrowUpRight, AlertCircle, LayoutPanelLeft, MessageSquare } from 'lucide-vue-next'
import { API_BASE_URL } from '../config'
import { marked } from 'marked'

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
const inputRef = ref(null)

// History functionality
const isHistoryCollapsed = ref(true)
const mockHistory = ref([
  { id: 1, title: 'Tư vấn đau vai gáy' },
  { id: 2, title: 'Phân tích tập squat' },
  { id: 3, title: 'Báo cáo tuần 12' }
])

// Markdown configuration
marked.setOptions({
  breaks: true,
  gfm: true
})

const renderMarkdown = (content) => {
  if (!content) return ''
  return marked.parse(content)
}

const currentPatientName = computed(() => {
  const p = patients.value.find(p => p.patient_id === selectedPatientId.value)
  return p ? p.full_name : 'Bệnh nhân'
})

const getStatusClass = (p) => {
  const s = p.status?.toLowerCase() || ''
  if (s === 'active') return 'status-active'
  if (s === 'inactive') return 'status-inactive'
  return 'status-warning'
}

const getStatusLabel = (p) => {
  const s = p.status?.toLowerCase() || ''
  if (s === 'active') return 'Hoạt động'
  if (s === 'inactive') return 'Không hoạt động'
  return 'Cần chú ý'
}

const suggestedPrompts = computed(() => {
  if (userRole.value === 'doctor') {
    return [
      'Tóm tắt tình trạng bệnh nhân này',
      'Phân tích hiệu suất tập luyện gần đây',
      'Đánh giá tiến độ phục hồi',
      'Cảnh báo các chỉ số bất thường'
    ]
  } else {
    return [
      'Tóm tắt tuần tập luyện của tôi',
      'Độ chính xác của tôi thế nào?',
      'Tôi cần cải thiện bài tập nào?',
      'Phân tích xu hướng sức khỏe'
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
      if (props.initialPatientId) {
        selectedPatientId.value = props.initialPatientId
      }
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

const selectPatient = (patient) => {
  selectedPatientId.value = patient.patient_id
  clearChat()
}

const adjustTextarea = () => {
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
    inputRef.value.style.height = inputRef.value.scrollHeight + 'px'
  }
}


const clearChat = () => {
  messages.value = []
}

const useSuggestion = (text) => {
  inputMessage.value = text
  sendMessage()
}

// Smart Scroll logic
const isAtBottom = ref(true)
const handleScroll = () => {
  if (!messageContainer.value) return
  const { scrollTop, scrollHeight, clientHeight } = messageContainer.value
  // Allowing 50px threshold
  isAtBottom.value = scrollHeight - scrollTop - clientHeight < 50
}

const scrollToEnd = (force = false) => {
  nextTick(() => {
    if (messageContainer.value && (isAtBottom.value || force)) {
      messageContainer.value.scrollTo({
        top: messageContainer.value.scrollHeight,
        behavior: force ? 'smooth' : 'auto'
      })
    }
  })
}

// Typing animation queue - now per-session to avoid collisions
const typingQueue = []
let isTyping = false

const processTypingQueue = async (msg) => {
  if (isTyping) return
  isTyping = true
  
  while (typingQueue.length > 0) {
    const char = typingQueue.shift()
    if (char) {
      msg.displayContent += char
      // Dynamic speed: faster for longer queues to catch up
      const delay = typingQueue.length > 20 ? 2 : (Math.random() * 8 + 4)
      await new Promise(r => setTimeout(r, delay))
      
      // Throttled scroll: only if we added a significant chunk or at end of loop
      if (typingQueue.length % 5 === 0 || typingQueue.length === 0) {
        scrollToEnd()
      }
    }
  }
  
  isTyping = false
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isStreaming.value) return
  if (!selectedPatientId.value) return

  const userMsg = inputMessage.value
  inputMessage.value = ''
  if (inputRef.value) inputRef.value.style.height = 'auto'
  
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
      if (response.status === 401) {
        console.warn('DEBUG: 401 Unauthorized detected')
        throw new Error('Phiên làm việc hết hạn hoặc không hợp lệ. Vui lòng đăng xuất và đăng nhập lại.')
      }
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Yêu cầu thất bại')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    let assistantMsg = {
      role: 'assistant',
      content: '',
      displayContent: '', // For the typing effect
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isStreaming: true
    }
    messages.value.push(assistantMsg)
    currentStreamingMessage.value = assistantMsg

    let buffer = ''
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      
      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk
      
      const lines = buffer.split('\n')
      // Keep the last partial line in the buffer
      buffer = lines.pop()
      
      for (const line of lines) {
        if (line.trim().startsWith('data: ')) {
          const data = line.trim().slice(6)
          if (data === '[DONE]') continue
          try {
            const parsed = JSON.parse(data)
            if (parsed.text) {
              const text = parsed.text
              assistantMsg.content += text
              
              // Add to typing queue
              for (const char of text) {
                typingQueue.push(char)
              }
              // Ensure processing starts
              if (!isTyping) processTypingQueue(assistantMsg)
            }
          } catch (err) {
            // Ignore parse errors for partial JSON if they happen (though rare with line split)
            console.error('Error parsing AI chunk:', err, 'Line:', line)
          }
        }
      }
    }
    
    // Ensure everything is displayed in the end
    assistantMsg.isStreaming = false
    assistantMsg.displayContent = assistantMsg.content
    
  } catch (err) {
    if (err.name !== 'AbortError') {
      console.error('AI Stream Error:', err)
      messages.value.push({
        role: 'assistant',
        content: `Lỗi: ${err.message}`,
        displayContent: `Lỗi: ${err.message}`,
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
  background: #f8fafc;
  border-radius: 28px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 25px 80px -20px rgba(0,0,0,0.1);
}

.glass-morphism {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

/* Header Styles */
.chat-header {
  padding: 24px 32px;
  border-bottom: 1px solid rgba(0,0,0,0.04);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  z-index: 10;
}

.chat-header.has-patient {
  background: linear-gradient(to right, #ffffff, #f1f5f9);
}

.header-main {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo-orb-wrapper {
  position: relative;
}

.logo-orb {
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3);
}

.status-pulse {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 14px;
  height: 14px;
  background: #22c55e;
  border: 3px solid white;
  border-radius: 50%;
}

.header-text h2 {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 2px;
}

.active-patient-profile {
  display: flex;
  align-items: center;
  gap: 16px;
}

.patient-info {
  display: flex;
  flex-direction: column;
}

.patient-label {
  font-size: 10px;
  font-weight: 800;
  color: #6366f1;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.patient-name {
  font-size: 18px !important;
  color: #1e293b !important;
}

.change-patient-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f1f5f9;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
  color: #475569;
  transition: all 0.2s;
}

.change-patient-btn:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.status-badge {
  font-size: 11px;
  font-weight: 600;
  color: #94a3b8;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.icon-button {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  color: #94a3b8;
  background: #f8fafc;
  transition: all 0.2s;
}

.icon-button:hover {
  background: #f1f5f9;
  color: #475569;
}

.icon-button.trash:hover {
  background: #fee2e2;
  color: #ef4444;
}

/* Viewport & Scrolling */
.chat-main-stage {
  flex: 1;
  display: flex;
  overflow: hidden; /* Prevent stage from scrolling, viewport handles it */
  position: relative;
  background: white;
}

.chat-history-sidebar {
  width: 260px;
  background: #f8fafc;
  border-right: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  z-index: 5;
}

.chat-history-sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(0,0,0,0.02);
}

.collapse-toggle {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #64748b;
  transition: all 0.2s;
}

.collapse-toggle:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.sidebar-title {
  font-size: 13px;
  font-weight: 800;
  color: #1e293b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.history-list-mini {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item-brief {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  color: #64748b;
}

.history-item-brief:hover {
  background: white;
  color: #6366f1;
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}

.history-text {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty-history-text {
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
  margin-top: 20px;
}

.chat-viewport {
  flex: 1;
  overflow-y: auto;
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  scroll-behavior: smooth;
}

/* Patient Selection Stage */
.patient-selection-stage {
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: radial-gradient(circle at top right, rgba(99, 102, 241, 0.05), transparent);
}

.selection-content {
  width: 100%;
  max-width: 900px;
}

.selection-header {
  text-align: center;
  margin-bottom: 48px;
}

.icon-circle {
  width: 80px;
  height: 80px;
  background: #f1f5f9;
  color: #6366f1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.selection-header h3 {
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 12px;
}

.selection-header p {
  color: #64748b;
  font-size: 16px;
  max-width: 500px;
  margin: 0 auto;
}

.patient-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.patient-card-premium {
  background: white;
  border: 1px solid #f1f5f9;
  padding: 20px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}

.patient-card-premium:hover {
  transform: translateY(-4px);
  border-color: #6366f1;
  box-shadow: 0 15px 30px rgba(99, 102, 241, 0.1);
}

.card-avatar {
  width: 48px;
  height: 48px;
  background: #eef2ff;
  color: #6366f1;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-body .name {
  font-weight: 700;
  color: #1e293b;
  font-size: 15px;
}

.card-body .status {
  font-size: 12px;
  font-weight: 700;
}

.status-active { color: #22c55e; }
.status-inactive { color: #ef4444; }
.status-warning { color: #f59e0b; }

.patient-card-premium .arrow {
  color: #cbd5e1;
  transition: transform 0.2s;
}

.patient-card-premium:hover .arrow {
  transform: translateX(4px);
  color: #6366f1;
}

/* Empty State */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.ai-hero {
  text-align: center;
  margin-bottom: 40px;
}

.ai-icon-hex {
  width: 96px;
  height: 96px;
  background: white;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 32px;
  color: #6366f1;
  box-shadow: 0 20px 40px rgba(0,0,0,0.05);
  border: 1px solid #f1f5f9;
}

.ai-hero h3 {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 12px;
}

.ai-hero p {
  color: #64748b;
  font-weight: 500;
  max-width: 400px;
}

.suggestions-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  width: 100%;
  max-width: 600px;
}

.suggestion-card {
  background: white;
  border: 1px solid #f1f5f9;
  padding: 16px 20px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  text-align: left;
  transition: all 0.2s;
  box-shadow: 0 4px 8px rgba(0,0,0,0.02);
}

.suggestion-card:hover {
  border-color: #6366f1;
  background: #f5f3ff;
  color: #6366f1;
  transform: translateY(-2px);
}

.sug-text {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}

/* Messages List */
.messages-list {
  padding: 40px 32px;
  display: flex;
  flex-direction: column;
  gap: 40px;
  min-height: min-content; /* Ensure container can grow */
}

.message-row {
  display: flex;
  width: 100%;
  animation: fadeIn 0.4s ease-out;
}

.message-row.user {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 85%;
  padding: 20px 24px;
  border-radius: 24px;
  font-size: 15px;
  line-height: 1.6;
  position: relative;
}

.user .message-bubble {
  background: #1e293b;
  color: white;
  border-bottom-right-radius: 4px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.15);
}

.assistant .message-bubble {
  background: white;
  color: #334155;
  border: 1px solid #f1f5f9;
  border-bottom-left-radius: 4px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.03);
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
}

.user .message-meta {
  justify-content: flex-end;
}

.streaming-indicator {
  color: #6366f1;
  display: flex;
  align-items: center;
  gap: 4px;
}

.streaming-indicator::after {
  content: "";
  width: 4px;
  height: 4px;
  background: #6366f1;
  border-radius: 50%;
  animation: pulse 1s infinite;
}

/* Markdown Styling */
.markdown-body :deep(h1), .markdown-body :deep(h2), .markdown-body :deep(h3) {
  margin-top: 16px;
  margin-bottom: 8px;
  font-weight: 800;
  color: #0f172a;
}

.markdown-body :deep(p) {
  margin-bottom: 12px;
}

.markdown-body :deep(ul), .markdown-body :deep(ol) {
  margin-bottom: 12px;
  padding-left: 20px;
}

.markdown-body :deep(li) {
  margin-bottom: 4px;
}

.markdown-body :deep(strong) {
  font-weight: 700;
  color: #0f172a;
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin: 16px 0;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.markdown-body :deep(th) {
  background: #f8fafc;
  padding: 12px;
  text-align: left;
  font-weight: 700;
  font-size: 13px;
  border-bottom: 1px solid #e2e8f0;
}

.markdown-body :deep(td) {
  padding: 12px;
  font-size: 14px;
  border-bottom: 1px solid #f1f5f9;
}

.markdown-body :deep(tr:last-child td) {
  border-bottom: none;
}

.markdown-body :deep(tr:nth-child(even)) {
  background: #fcfcfd;
}

/* Input Area */
.chat-input-area {
  padding: 32px;
  background: white;
  border-top: 1px solid #f1f5f9;
}

.chat-input-area.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.input-container-inner {
  max-width: 800px;
  margin: 0 auto;
}

.input-wrapper {
  background: #f8fafc;
  border: 2px solid #f1f5f9;
  border-radius: 22px;
  padding: 10px 14px;
  display: flex;
  align-items: flex-end;
  transition: all 0.3s;
}

.input-wrapper:focus-within {
  border-color: #6366f1;
  background: white;
  box-shadow: 0 10px 30px rgba(99, 102, 241, 0.1);
}

textarea {
  flex: 1;
  background: transparent;
  border: none;
  padding: 12px;
  font-size: 16px;
  font-weight: 500;
  color: #1e293b;
  outline: none;
  resize: none;
  max-height: 180px;
  line-height: 1.5;
}

.send-button-premium {
  width: 48px;
  height: 48px;
  background: #6366f1;
  color: white;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.send-button-premium:disabled {
  background: #e2e8f0;
  cursor: not-allowed;
}

.send-button-premium:not(:disabled):hover {
  background: #4f46e5;
  transform: scale(1.05) translateY(-2px);
}

.helper-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 12px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.helper-text.warning { color: #f59e0b; }

/* Indicators and animations */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 8px;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: #cbd5e1;
  border-radius: 50%;
  animation: typing 1s infinite alternate;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  from { opacity: 0.3; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1.1); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.8); opacity: 0.5; }
}

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #cbd5e1; }
</style>
