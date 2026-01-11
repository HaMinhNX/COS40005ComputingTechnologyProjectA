<template>
  <div class="flex flex-col h-full bg-slate-50" data-isolated-ui>
    <!-- Header -->
    <header class="bg-white border-b border-slate-200 px-8 py-6 flex items-center justify-between shadow-sm relative z-20">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-gradient-to-br from-indigo-600 to-violet-600 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
          <Activity :size="24" />
        </div>
        <div>
          <h1 class="text-2xl font-black text-slate-900">Giao diện Bệnh nhân</h1>
          <p class="text-sm text-slate-500 font-medium">{{ userName }}</p>
        </div>
      </div>

      <!-- Logout Button -->
      <button
        @click="showLogoutModal = true"
        class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-red-500 to-rose-500 text-white hover:from-red-600 hover:to-rose-600 transition-all font-bold text-sm shadow-lg shadow-red-500/20 hover:shadow-xl hover:shadow-red-500/30 group"
      >
        <LogOut :size="18" class="group-hover:scale-110 transition-transform" />
        <span>Đăng xuất</span>
      </button>
    </header>

    <!-- Tab Navigation -->
    <div class="bg-white border-b border-slate-200 px-8 sticky top-0 z-10">
      <div class="flex gap-8 overflow-x-auto custom-scrollbar">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="currentTab = tab.id"
          :class="[
            'flex items-center gap-2 py-4 text-sm font-bold border-b-2 transition-all whitespace-nowrap',
            currentTab === tab.id
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-900 hover:border-slate-300'
          ]"
        >
          <component :is="tab.iconComponent" :size="18" />
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <main class="flex-1 overflow-y-auto p-8 custom-scrollbar">
      <div class="max-w-7xl mx-auto">
        <transition name="fade" mode="out-in">
          <component :is="currentComponent" :userId="userId" :key="currentTab" @start-workout="handleStartWorkout" />
        </transition>
      </div>
    </main>

    <!-- Logout Confirmation Modal -->
    <Transition name="fade">
      <div v-if="showLogoutModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden">
          <div class="p-8 text-center">
            <div class="w-20 h-20 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
              <LogOut :size="40" class="text-red-500" />
            </div>
            <h3 class="text-2xl font-black text-slate-900 mb-2">Đăng xuất?</h3>
            <p class="text-slate-500 font-medium">Bạn có chắc chắn muốn đăng xuất khỏi hệ thống không?</p>
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
              class="flex-1 py-3.5 rounded-xl font-bold text-white bg-gradient-to-r from-red-500 to-rose-500 hover:from-red-600 hover:to-rose-600 shadow-lg shadow-red-500/30 hover:shadow-xl hover:shadow-red-500/40 transition-all"
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Activity, LogOut, BarChart3, Brain, Calendar, Phone } from 'lucide-vue-next'

// Import các component con (đảm bảo đã tạo chúng)
import PatientDashboard from './PatientDashboard.vue'
import PatientWorkout from './PatientWorkout.vue'
import BrainExercise from './BrainExercise.vue'
import SportsTraining from './SportsTraining.vue'
import PatientScheduling from './PatientScheduling.vue'
import PatientContact from './PatientContact.vue'

const router = useRouter()

const userId = ref('')
const userName = ref('Bệnh nhân')
const currentTab = ref('dashboard')
const showLogoutModal = ref(false)

const tabs = [
  { id: 'dashboard', label: 'Tổng quan', iconComponent: BarChart3 },
  { id: 'workout', label: 'Tập luyện', iconComponent: Activity },
  { id: 'brain', label: 'Trí tuệ', iconComponent: Brain },
  { id: 'sports', label: 'Thể thao', iconComponent: Activity },
  { id: 'scheduling', label: 'Lịch hẹn', iconComponent: Calendar },
  { id: 'contact', label: 'Liên hệ', iconComponent: Phone },
]

const currentComponent = computed(() => {
  switch (currentTab.value) {
    case 'dashboard': return PatientDashboard
    case 'workout': return PatientWorkout
    case 'brain': return BrainExercise
    case 'sports': return SportsTraining
    case 'scheduling': return PatientScheduling
    case 'contact': return PatientContact
    default: return PatientWorkout
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
    } catch (e) {
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
  transition: opacity 0.3s ease, transform 0.3s ease;
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
