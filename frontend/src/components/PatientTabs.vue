<template>
  <div class="flex flex-col h-full bg-slate-50" data-isolated-ui>
    <!-- Header -->
    <header
      class="bg-white border-b border-slate-200 px-10 py-10 flex items-center justify-between shadow-md relative z-20"
    >
      <div class="flex items-center gap-6">
        <div
          class="w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-700 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-indigo-500/30 transform hover:scale-110 transition-transform duration-300"
        >
          <Activity :size="32" />
        </div>
        <div>
          <h1 class="text-4xl font-black text-slate-900 tracking-tight">Giao diện Bệnh nhân</h1>
          <p class="text-lg text-slate-500 font-bold mt-1 tracking-wide">{{ userName }}</p>
        </div>
      </div>

      <!-- Logout Button -->
      <button
        @click="showLogoutModal = true"
        class="flex items-center gap-3 px-8 py-4 rounded-2xl bg-red-500 text-white hover:bg-red-600 transition-all font-black text-lg shadow-xl shadow-red-500/20 hover:shadow-2xl hover:shadow-red-500/40 transform hover:-translate-y-1 group"
      >
        <LogOut :size="24" class="group-hover:scale-110 transition-transform" />
        <span>Đăng xuất</span>
      </button>
    </header>

    <!-- Tab Navigation -->
    <div class="bg-white border-b border-slate-200 px-10 sticky top-0 z-10 shadow-sm">
      <div class="flex gap-12 overflow-x-auto custom-scrollbar no-scrollbar py-2">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="currentTab = tab.id"
          :class="[
            'flex items-center gap-3 py-6 text-lg font-black border-b-4 transition-all whitespace-nowrap px-4 rounded-t-xl hover:bg-slate-50',
            currentTab === tab.id
              ? 'border-indigo-600 text-indigo-600 bg-indigo-50/30'
              : 'border-transparent text-slate-400 hover:text-slate-900',
          ]"
        >
          <component :is="tab.iconComponent" :size="24" />
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <main class="flex-1 overflow-y-auto p-8 custom-scrollbar">
      <div class="h-full">
        <transition name="fade" mode="out-in">
          <KeepAlive>
            <component
              :is="currentComponent"
              :userId="userId"
              @start-workout="handleStartWorkout"
            />
          </KeepAlive>
        </transition>
      </div>
    </main>

    <!-- Logout Confirmation Modal -->
    <Transition name="fade">
      <div
        v-if="showLogoutModal"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
      >
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden">
          <div class="p-8 text-center">
            <div
              class="w-20 h-20 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6"
            >
              <LogOut :size="40" class="text-red-500" />
            </div>
            <h3 class="text-2xl font-black text-slate-900 mb-2">Đăng xuất?</h3>
            <p class="text-slate-500 font-medium">
              Bạn có chắc chắn muốn đăng xuất khỏi hệ thống không?
            </p>
          </div>
          <div class="p-6 bg-slate-50 flex gap-4">
            <button
              @click="showLogoutModal = false"
              class="flex-1 py-3.5 rounded-xl font-bold text-slate-600 hover:bg-white hover:text-slate-900 hover:shadow-md transition-all border border-transparent hover:border-slate-200"
            >
              Hủy bỏ
            </button>
            <button
              @click="handleLogout"
              class="flex-1 py-3.5 rounded-xl font-bold text-white bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/30 hover:shadow-xl hover:shadow-red-500/40 transition-all"
            >
              Đăng xuất
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
import {
  Activity,
  LogOut,
  BarChart3,
  Brain,
  Calendar,
  MessageSquare,
  Sparkles,
  ClipboardList,
  Target,
} from 'lucide-vue-next'

// Lazy-load tab components to reduce initial bundle and first paint cost.
const PatientDashboard = defineAsyncComponent(() => import('./PatientDashboard.vue'))
const PatientWorkout = defineAsyncComponent(() => import('./PatientWorkout.vue'))
const BrainExercise = defineAsyncComponent(() => import('./BrainExercise.vue'))
const SportsTraining = defineAsyncComponent(() => import('./SportsTraining.vue'))
const PatientScheduling = defineAsyncComponent(() => import('./PatientScheduling.vue'))
const PatientMessaging = defineAsyncComponent(() => import('./PatientMessaging.vue'))
const AIChatbox = defineAsyncComponent(() => import('./AIChatbox.vue'))

const router = useRouter()

const userId = ref('')
const userName = ref('Bệnh nhân')
const currentTab = ref('dashboard')
const showLogoutModal = ref(false)

const tabs = [
  { id: 'dashboard', label: 'Tổng quan', iconComponent: BarChart3 },
  { id: 'workout', label: 'Kế hoạch phục hồi', iconComponent: ClipboardList },
  { id: 'brain', label: 'Trí tuệ', iconComponent: Brain },
  { id: 'sports', label: 'Luyện tập tự do', iconComponent: Target },
  { id: 'messages', label: 'Tin nhắn', iconComponent: MessageSquare },
  { id: 'aiChat', label: 'Trợ lý AI', iconComponent: Sparkles },
  { id: 'scheduling', label: 'Lịch hẹn', iconComponent: Calendar },
]

const currentComponent = computed(() => {
  switch (currentTab.value) {
    case 'dashboard':
      return PatientDashboard
    case 'workout':
      return PatientWorkout
    case 'brain':
      return BrainExercise
    case 'sports':
      return SportsTraining
    case 'messages':
      return PatientMessaging
    case 'aiChat':
      return AIChatbox
    case 'scheduling':
      return PatientScheduling
    default:
      return PatientWorkout
  }
})

const handleStartWorkout = () => {
  currentTab.value = 'workout'
}

const handleLogout = () => {
  localStorage.removeItem('user')
  showLogoutModal.value = false
  router.push('/login')
}

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      userId.value = user.user_id
      userName.value = user.full_name || 'Bệnh nhân'
    } catch {
      console.error('Dữ liệu người dùng không hợp lệ')
      router.push('/login')
    }
  } else {
    router.push('/login')
  }
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
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

.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: scale(0.95);
}
.fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
