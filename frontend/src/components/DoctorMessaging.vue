<template>
  <div class="flex h-[calc(100vh-8rem)] gap-6 p-6 bg-slate-50/50">
    <!-- Sidebar: Doctor List -->
    <div
      class="w-80 bg-white rounded-[2rem] shadow-xl border border-slate-100 flex flex-col overflow-hidden"
    >
      <div
        class="p-6 border-b border-slate-100 bg-gradient-to-r from-indigo-500 to-violet-500 text-white"
      >
        <h3 class="text-xl font-black tracking-tight mb-1">Tin Nhắn</h3>
        <div class="flex gap-2 mt-2">
          <button
            @click="activeTab = 'doctors'"
            :class="[
              'flex-1 py-1.5 text-xs font-bold rounded-lg transition-all',
              activeTab === 'doctors'
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-indigo-100 hover:bg-white/10',
            ]"
          >
            Đồng nghiệp
          </button>
          <button
            @click="activeTab = 'patients'"
            :class="[
              'flex-1 py-1.5 text-xs font-bold rounded-lg transition-all',
              activeTab === 'patients'
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-indigo-100 hover:bg-white/10',
            ]"
          >
            Bệnh nhân
          </button>
        </div>
      </div>

      <div class="p-4">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" :size="18" />
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="activeTab === 'doctors' ? 'Tìm bác sĩ...' : 'Tìm bệnh nhân...'"
            class="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
          />
        </div>
      </div>

      <div class="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2">
        <button
          v-for="user in filteredUsers"
          :key="user.user_id || user.patient_id"
          @click="selectUser(user)"
          :class="[
            'w-full p-3 rounded-xl flex items-center gap-3 transition-all duration-200 group',
            selectedUser?.user_id === user.user_id && selectedUser?.patient_id === user.patient_id
              ? 'bg-indigo-50 border border-indigo-100 shadow-sm'
              : 'hover:bg-slate-50 border border-transparent hover:border-slate-100',
          ]"
        >
          <div class="relative">
            <div
              class="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-400 to-purple-400 flex items-center justify-center text-white font-bold text-sm shadow-md"
            >
              {{ getInitials(user.full_name) }}
            </div>
            <span
              class="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-500 border-2 border-white rounded-full"
            ></span>
          </div>
          <div class="flex-1 text-left">
            <h4
              :class="[
                'text-sm font-bold truncate',
                selectedUser?.user_id === user.user_id &&
                selectedUser?.patient_id === user.patient_id
                  ? 'text-indigo-900'
                  : 'text-slate-700',
              ]"
            >
              {{ user.full_name }}
            </h4>
            <p
              class="text-xs text-slate-500 truncate group-hover:text-indigo-500 transition-colors"
            >
              {{ user.email }}
            </p>
          </div>
        </button>
      </div>
    </div>

    <!-- Main Chat Area -->
    <div
      class="flex-1 bg-white rounded-[2rem] shadow-xl border border-slate-100 flex flex-col overflow-hidden relative"
    >
      <div
        v-if="!selectedUser"
        class="absolute inset-0 flex flex-col items-center justify-center text-slate-400 bg-slate-50/50"
      >
        <div
          class="w-24 h-24 bg-white rounded-full shadow-lg flex items-center justify-center mb-4 animate-bounce-slow"
        >
          <MessageCircle :size="40" class="text-indigo-400" />
        </div>
        <h3 class="text-xl font-bold text-slate-600">Chọn một người để bắt đầu</h3>
      </div>

      <template v-else>
        <!-- Chat Header -->
        <div
          class="p-6 border-b border-slate-100 flex items-center justify-between bg-white/80 backdrop-blur-md z-10"
        >
          <div class="flex items-center gap-4">
            <div
              class="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center text-white font-bold text-lg shadow-lg"
            >
              {{ getInitials(selectedUser.full_name) }}
            </div>
            <div>
              <h3 class="text-lg font-black text-slate-900">{{ selectedUser.full_name }}</h3>
              <p class="text-xs font-bold text-emerald-500 flex items-center gap-1">
                <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                Online
              </p>
            </div>
          </div>
          <button
            class="p-2 hover:bg-slate-50 rounded-xl text-slate-400 hover:text-indigo-600 transition-colors"
          >
            <MoreVertical :size="20" />
          </button>
        </div>

        <!-- Messages List -->
        <div
          class="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6 bg-slate-50/30"
          ref="msgList"
        >
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="[
              'flex gap-4 max-w-[80%]',
              msg.sender_id === currentUserId ? 'ml-auto flex-row-reverse' : '',
            ]"
          >
            <div
              :class="[
                'w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold text-white shadow-md',
                msg.sender_id === currentUserId ? 'bg-indigo-500' : 'bg-slate-400',
              ]"
            >
              {{ msg.sender_id === currentUserId ? 'Me' : getInitials(selectedUser.full_name) }}
            </div>

            <div
              :class="[
                'flex flex-col',
                msg.sender_id === currentUserId ? 'items-end' : 'items-start',
              ]"
            >
              <div
                :class="[
                  'px-5 py-3 rounded-2xl text-sm font-medium shadow-sm',
                  msg.sender_id === currentUserId
                    ? 'bg-gradient-to-br from-indigo-500 to-violet-600 text-white rounded-tr-none'
                    : 'bg-white text-slate-700 border border-slate-100 rounded-tl-none',
                ]"
              >
                {{ msg.content }}
              </div>
              <span class="text-[10px] font-bold text-slate-400 mt-1 px-1">
                {{ formatTime(msg.created_at) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="p-4 bg-white border-t border-slate-100">
          <div
            class="flex items-end gap-3 bg-slate-50 p-2 rounded-[1.5rem] border border-slate-200 focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-500/10 transition-all"
          >
            <button
              class="p-3 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-colors"
            >
              <Paperclip :size="20" />
            </button>

            <textarea
              v-model="newMessage"
              @keydown.enter.prevent="sendMessage"
              placeholder="Nhập tin nhắn..."
              rows="1"
              class="flex-1 bg-transparent border-none focus:ring-0 text-sm font-medium text-slate-700 placeholder-slate-400 resize-none py-3 max-h-32 custom-scrollbar"
            ></textarea>

            <button
              @click="sendMessage"
              :disabled="!newMessage.trim()"
              :class="[
                'p-3 rounded-full transition-all shadow-lg',
                newMessage.trim()
                  ? 'bg-indigo-600 text-white hover:bg-indigo-700 hover:scale-105 shadow-indigo-500/30'
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed',
              ]"
            >
              <Send :size="20" :class="newMessage.trim() ? 'ml-0.5' : ''" />
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { Search, MessageCircle, MoreVertical, Paperclip, Send } from 'lucide-vue-next'

import { API_BASE_URL } from '../config'
const API_BASE = API_BASE_URL

const doctors = ref([])
const patients = ref([])
const searchQuery = ref('')
const selectedUser = ref(null)
const messages = ref([])
const newMessage = ref('')
const currentUserId = ref(null)
const msgList = ref(null)
const activeTab = ref('doctors') // 'doctors' | 'patients'

// Remove Vietnamese diacritics for search
function removeVietnameseTones(str) {
  return str
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D')
}

const filteredUsers = computed(() => {
  const list = activeTab.value === 'doctors' ? doctors.value : patients.value
  return list.filter((u) => {
    // For doctors: exclude self. For patients: show all
    const userId = u.user_id || u.patient_id
    const isSelf = activeTab.value === 'doctors' && userId === currentUserId.value
    if (isSelf) return false

    const name = removeVietnameseTones((u.full_name || '').toLowerCase())
    const email = (u.email || '').toLowerCase()
    const query = removeVietnameseTones(searchQuery.value.toLowerCase())
    return name.includes(query) || email.includes(query)
  })
})

function getInitials(name) {
  return name
    ? name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()
    : '??'
}

function formatTime(isoString) {
  if (!isoString) return ''
  return new Date(isoString).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
}

async function loadDoctors() {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE}/doctors`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) {
      doctors.value = await res.json()
    }
  } catch (e) {
    console.error('Error loading doctors:', e)
  }
}

async function loadPatients() {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE}/patients`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) {
      const data = await res.json()
      // API returns pagination: { items: [...], total, page, size }
      const items = data.items || data
      // Map user_id to patient_id for consistency
      patients.value = items.map((p) => ({
        ...p,
        patient_id: p.patient_id || p.user_id,
        full_name: p.full_name || p.name || 'Unknown',
        email: p.email || '',
      }))
    }
  } catch (e) {
    console.error('Error loading patients:', e)
  }
}

async function loadMessages() {
  if (!selectedUser.value || !currentUserId.value) return
  const otherId =
    activeTab.value === 'doctors' ? selectedUser.value.user_id : selectedUser.value.patient_id
  try {
    const token = localStorage.getItem('token')
    // Backend expects: GET /api/messages/{user1_id}/{user2_id}
    const res = await fetch(`${API_BASE}/messages/${currentUserId.value}/${otherId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) {
      const data = await res.json()
      // API returns pagination: { items: [...], total, page, size }
      const items = data.items || data
      // Sort by created_at ascending for chat display
      messages.value = items.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      scrollToBottom()
    }
  } catch (e) {
    console.error('Error loading messages:', e)
  }
}

async function sendMessage() {
  if (!newMessage.value.trim() || !selectedUser.value) return

  const receiverId =
    activeTab.value === 'doctors' ? selectedUser.value.user_id : selectedUser.value.patient_id

  try {
    // Backend only needs receiver_id and content (sender comes from token)
    const payload = {
      receiver_id: receiverId,
      content: newMessage.value,
    }

    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    })

    if (res.ok) {
      const sentMsg = await res.json()
      messages.value.push(sentMsg)
      newMessage.value = ''
      scrollToBottom()
    }
  } catch (e) {
    console.error('Error sending message:', e)
  }
}

function selectUser(user) {
  selectedUser.value = user
  loadMessages()
}

function scrollToBottom() {
  nextTick(() => {
    if (msgList.value) {
      msgList.value.scrollTop = msgList.value.scrollHeight
    }
  })
}

onMounted(async () => {
  // Get current user ID from localStorage (saved when logging in)
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      currentUserId.value = user.user_id
      await loadDoctors()
      await loadPatients()
    } else {
      console.error('No user data in localStorage')
    }
  } catch (e) {
    console.error('Error getting user data:', e)
  }

  // Poll for messages
  setInterval(() => {
    if (selectedUser.value) loadMessages()
  }, 3000)
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
  background-color: #e2e8f0;
  border-radius: 20px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #cbd5e1;
}

.animate-bounce-slow {
  animation: bounce 3s infinite;
}
</style>
