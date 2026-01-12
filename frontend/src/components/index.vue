<template>
  <div class="flex h-screen w-full bg-slate-50 font-sans text-slate-900 overflow-hidden selection:bg-indigo-100 selection:text-indigo-900 relative" data-isolated-ui>

    <!-- Ultra-Modern Sidebar -->
    <aside :class="[
      'bg-white flex flex-col transition-all duration-300 z-50 shadow-2xl shadow-slate-200/50 relative border-r border-slate-100',
      sidebarCollapsed ? 'w-16' : 'w-64',
      'fixed md:relative h-full',
      mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
    ]">

      <!-- User Profile with Collapse Toggle -->
      <div :class="['border-b border-slate-100 relative z-10 transition-all', sidebarCollapsed ? 'p-3' : 'p-4']">
        <div :class="['flex items-center', sidebarCollapsed ? 'justify-center' : 'gap-3']">
          <div v-if="!sidebarCollapsed" class="relative group">
            <div class="absolute inset-0 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full blur opacity-40 group-hover:opacity-70 transition-opacity"></div>
            <img src="https://ui-avatars.com/api/?name=Dr+Minh&background=6366f1&color=fff" alt="Dr. Minh" class="relative w-11 h-11 rounded-full shadow-lg ring-4 ring-white object-cover" />
          </div>

          <div v-if="!sidebarCollapsed" class="flex-1 min-w-0">
            <h2 class="text-base font-black text-slate-900 truncate">{{ currentUser?.full_name || 'Người dùng' }}</h2>
            <p class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{{ currentUser?.role === 'doctor' ? 'Bác sĩ' : 'Bệnh nhân' }}</p>
          </div>

          <!-- Enhanced Collapse Toggle Button -->
          <button
            @click="sidebarCollapsed = !sidebarCollapsed"
            class="p-2 bg-gradient-to-br from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 rounded-xl transition-all text-white group flex-shrink-0 shadow-lg shadow-indigo-500/30 hover:shadow-xl hover:shadow-indigo-500/40"
            :title="sidebarCollapsed ? 'Mở rộng' : 'Thu gọn'"
          >
            <component :is="sidebarCollapsed ? ChevronRight : ChevronLeft" :size="16" class="group-hover:scale-110 transition-transform font-bold" />
          </button>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-3 py-4 space-y-6 overflow-y-auto custom-scrollbar relative z-10">
        <div v-for="(group, groupName) in groupedMenu" :key="groupName">
          <h3 v-if="!sidebarCollapsed" class="px-3 mb-2 text-[9px] font-black text-slate-400 uppercase tracking-widest">{{ translateGroup(groupName) }}</h3>

          <div class="space-y-1">
            <button
              v-for="item in group.items"
              :key="item.id"
              @click="handleMenuClick(item.id)"
              :class="[
                'w-full text-left rounded-xl flex items-center transition-all duration-300 group relative overflow-hidden',
                sidebarCollapsed ? 'px-2 py-2.5 justify-center' : 'px-3 py-2.5 gap-3',
                'text-[13px] font-bold',
                active === item.id
                  ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-500/30'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-indigo-600'
              ]"
              :title="sidebarCollapsed ? item.label : ''"
            >
              <component
                :is="item.icon"
                :size="18"
                :class="[
                  'transition-all duration-300 relative z-10 flex-shrink-0',
                  active === item.id ? 'text-white' : 'text-slate-400 group-hover:text-indigo-600'
                ]"
              />
              <span v-if="!sidebarCollapsed" class="relative z-10">{{ item.label }}</span>
              <ChevronRight v-if="active === item.id && !sidebarCollapsed" :size="14" class="ml-auto text-white/80 relative z-10" />
            </button>
          </div>
        </div>
      </nav>

      <!-- Sign Out Button (Bottom) -->
      <div class="p-3 border-t border-slate-100">
        <button
          @click="showLogoutModal = true"
          :class="[
            'w-full py-2.5 rounded-xl flex items-center justify-center bg-gradient-to-r from-red-500 to-rose-500 text-white hover:from-red-600 hover:to-rose-600 transition-all font-bold text-xs shadow-lg shadow-red-500/20 hover:shadow-xl hover:shadow-red-500/30 group',
            sidebarCollapsed ? 'px-2' : 'px-3 gap-2'
          ]"
          :title="sidebarCollapsed ? 'Đăng xuất' : ''"
        >
          <LogOut :size="16" class="group-hover:scale-110 transition-transform" />
          <span v-if="!sidebarCollapsed">Đăng xuất</span>
        </button>
      </div>
    </aside>

    <!-- Overlay for mobile -->
    <div
      v-if="mobileMenuOpen"
      @click="mobileMenuOpen = false"
      class="md:hidden fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40"
    ></div>

    <!-- Main Content Area -->
    <main class="flex-1 flex flex-col min-w-0 overflow-hidden relative z-10 bg-slate-50/50">
      <!-- Premium Top Bar -->
      <header class="h-16 md:h-20 flex-shrink-0 px-5 md:px-8 flex items-center justify-between bg-white/80 backdrop-blur-xl border-b border-slate-200/60 sticky top-0 z-40">
        <!-- Left: Title -->
        <div class="flex flex-col justify-center flex-1">
          <h2 class="text-xl md:text-2xl font-black text-slate-900 tracking-tight truncate">{{ title }}</h2>
          <p class="text-xs text-slate-500 font-medium mt-0.5 flex items-center gap-1.5">
            <CalendarIcon :size="12" class="text-indigo-500" />
            {{ currentDate }}
          </p>
        </div>

        <!-- Right: Search Bar & Notification Bell -->
        <div class="flex justify-end items-center gap-3">
          <div class="relative group hidden lg:block w-64">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none z-10">
              <Search class="text-slate-400 group-focus-within:text-indigo-600 transition-colors" :size="16" />
            </div>
            <input
              type="text"
              placeholder="Tìm kiếm..."
              class="block w-full pl-10 pr-3 py-2 bg-slate-100/50 border border-slate-200 focus:bg-white focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 rounded-xl text-xs transition-all outline-none placeholder-slate-400 font-medium"
            />
          </div>

          <!-- Notification Bell (Moved to Right) -->
          <button class="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-all relative group flex items-center justify-center">
            <Bell :size="20" class="relative" />
            <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white animate-pulse"></span>
          </button>
        </div>
      </header>

      <!-- Content Area -->
      <div class="flex-1 overflow-y-auto p-4 md:p-8 custom-scrollbar">
        <Transition name="fade-slide" mode="out-in">
          <component :is="activeComponent" />
        </Transition>
      </div>
    </main>

    <!-- Logout Confirmation Modal -->
    <Transition name="fade">
      <div v-if="showLogoutModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all scale-100">
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
import { ref, computed } from 'vue';
import {
  LayoutDashboard,
  Users,
  Calendar,
  Dumbbell,
  MessageSquare,
  Brain,
  Activity,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Search,
  Bell,
  Calendar as CalendarIcon,
  Phone
} from 'lucide-vue-next';

// Import Components
import Dashboard from './Dashboard.vue';
import PatientManagement from './PatientManagement.vue';
import Scheduling from './Scheduling.vue';
import ExerciseLibrary from './ExerciseLibrary.vue';
import DoctorMessaging from './DoctorMessaging.vue';
import Assignment from './Assignment.vue';
import PatientTabs from './PatientTabs.vue';

// State
const sidebarCollapsed = ref(false);
const mobileMenuOpen = ref(false);
const showLogoutModal = ref(false);
const active = ref('dashboard');
const currentUser = ref(JSON.parse(localStorage.getItem('user') || '{}'));

// Menu Configuration
const groupedMenu = {
  main: {
    items: [
      { id: 'dashboard', label: 'Tổng quan', icon: LayoutDashboard }
    ]
  },
  management: {
    items: [
      { id: 'patients', label: 'Bệnh nhân', icon: Users },
      { id: 'scheduling', label: 'Lịch hẹn', icon: Calendar },
      { id: 'assignment', label: 'Phân công bài tập', icon: Dumbbell }
    ]
  },
  resources: {
    items: [
      { id: 'library', label: 'Thư viện bài tập', icon: Dumbbell }
    ]
  },
  communication: {
    items: [
      { id: 'messages', label: 'Tin nhắn', icon: MessageSquare }
    ]
  },
  patientUI: {
    items: [
      { id: 'patientView', label: 'Giao diện Bệnh nhân', icon: Activity }
    ]
  }
};

// Component Mapping
const components = {
  dashboard: Dashboard,
  patients: PatientManagement,
  scheduling: Scheduling,
  library: ExerciseLibrary,
  assignment: Assignment,
  messages: DoctorMessaging,
  patientView: PatientTabs
};

const activeComponent = computed(() => components[active.value] || Dashboard);

// Computed Title
const title = computed(() => {
  const allItems = Object.values(groupedMenu).flatMap(g => g.items);
  const item = allItems.find(i => i.id === active.value);
  return item ? item.label : 'Tổng quan';
});

// Date
const currentDate = new Date().toLocaleDateString('vi-VN', {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric'
});

// Methods
const handleMenuClick = (id) => {
  active.value = id;
  mobileMenuOpen.value = false;
};

const translateGroup = (key) => {
  const map = {
    main: 'Chính',
    management: 'Quản lý',
    resources: 'Tài nguyên',
    communication: 'Giao tiếp',
    patientUI: 'Giao diện BN'
  };
  return map[key] || key;
};

const handleLogout = () => {
  console.log('Logging out...');
  localStorage.removeItem('user');
  // Assuming router is available or using window.location
  window.location.href = '/login';
  showLogoutModal.value = false;
};
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

/* Enhanced Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
