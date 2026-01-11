<template>
  <div v-if="!selectedPatient" class="h-full flex flex-col space-y-6">
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
      <div>
        <h2 class="text-2xl font-black text-slate-900 tracking-tight">Quản Lý Bệnh Nhân</h2>
        <p class="text-slate-500 font-medium mt-1">Theo dõi và quản lý hồ sơ sức khỏe bệnh nhân</p>
      </div>
      <button 
        @click="showAddModal = true"
        class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold shadow-lg shadow-indigo-500/20 transition-all flex items-center gap-2 transform hover:-translate-y-0.5"
      >
        <Plus :size="20" />
        <span>Thêm Bệnh Nhân</span>
      </button>
    </div>

    <!-- Filters & Search -->
    <div class="flex flex-col md:flex-row gap-4">
      <div class="relative flex-1">
        <Search class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" :size="20" />
        <input 
          v-model="searchQuery"
          type="text"
          placeholder="Tìm kiếm bệnh nhân..."
          class="w-full pl-12 pr-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all font-medium"
        />
      </div>
      <div class="flex gap-2">
        <select v-model="filterStatus" class="px-4 py-3 bg-white border border-slate-200 rounded-xl font-medium text-slate-600 outline-none focus:border-indigo-500">
          <option value="All">Tất cả trạng thái</option>
          <option value="Stable">Ổn định</option>
          <option value="Review">Cần theo dõi</option>
          <option value="Critical">Nguy kịch</option>
        </select>
      </div>
    </div>

    <!-- Patient List -->
    <div class="flex-1 bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
      <div class="overflow-x-auto custom-scrollbar flex-1">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100">
              <th class="px-6 py-4 text-xs font-black text-slate-500 uppercase tracking-wider">Bệnh Nhân</th>
              <th class="px-6 py-4 text-xs font-black text-slate-500 uppercase tracking-wider">Trạng Thái</th>
              <th class="px-6 py-4 text-xs font-black text-slate-500 uppercase tracking-wider">Bài Tập</th>
              <th class="px-6 py-4 text-xs font-black text-slate-500 uppercase tracking-wider">Tần Suất</th>
              <th class="px-6 py-4 text-xs font-black text-slate-500 uppercase tracking-wider">Lần Khám Cuối</th>
              <th class="px-6 py-4 text-xs font-black text-slate-500 uppercase tracking-wider text-right">Hành Động</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr 
              v-for="patient in filteredPatients" 
              :key="patient.patient_id"
              @click="viewPatientDetail(patient)"
              class="hover:bg-indigo-50/50 transition-colors group cursor-pointer"
            >
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-100 to-violet-100 text-indigo-600 flex items-center justify-center font-black text-sm">
                    {{ getInitials(patient.full_name) }}
                  </div>
                  <div>
                    <p class="font-bold text-slate-900">{{ patient.full_name }}</p>
                    <p class="text-xs text-slate-500 font-medium">{{ patient.email }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span :class="['px-3 py-1 rounded-full text-xs font-bold border', getStatusClass('Stable')]">
                  {{ getStatusLabel('Stable') }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <Dumbbell :size="16" class="text-slate-400" />
                  --
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <Activity :size="16" class="text-slate-400" />
                  --
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <Clock :size="16" class="text-slate-400" />
                  {{ new Date(patient.created_at).toLocaleDateString('vi-VN') }}
                </div>
              </td>
              <td class="px-6 py-4 text-right" @click.stop>
                <button @click="deletePatient(patient.patient_id)" class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all" title="Xóa bệnh nhân">
                  <Trash2 :size="20" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Patient Modal -->
    <div v-if="showAddModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <div class="bg-white rounded-3xl p-8 w-full max-w-lg shadow-2xl transform scale-100 transition-all border border-slate-100">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-black text-slate-900">Thêm Bệnh Nhân Mới</h3>
          <button @click="showAddModal = false" class="p-2 hover:bg-slate-50 rounded-xl transition-colors text-slate-400 hover:text-slate-900">
            <X :size="20" />
          </button>
        </div>
        
        <form @submit.prevent="addNewPatient" class="space-y-5">
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Họ và Tên</label>
            <input v-model="newPatient.full_name" required class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-200 rounded-xl text-sm focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all font-medium" placeholder="VD: Nguyễn Văn A" />
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Tên đăng nhập</label>
              <input v-model="newPatient.username" required class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-200 rounded-xl text-sm focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all font-medium" placeholder="user123" />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Mật khẩu</label>
              <input v-model="newPatient.password" type="password" required class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-200 rounded-xl text-sm focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all font-medium" placeholder="******" />
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Email</label>
            <input v-model="newPatient.email" type="email" required class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-200 rounded-xl text-sm focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all font-medium" placeholder="email@example.com" />
          </div>
          
          <div class="flex justify-end gap-3 pt-4">
            <button type="button" @click="showAddModal = false" class="px-6 py-3 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-100 transition-colors">Hủy</button>
            <button type="submit" class="px-6 py-3 bg-indigo-600 text-white rounded-xl text-sm font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-500/30 transition-all">
              Thêm Mới
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Patient Detail View -->
  <DoctorPatientDetail 
    v-else 
    :patientId="selectedPatient" 
    @back="selectedPatient = null"
  /></template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Plus, Filter, MoreHorizontal, X, Dumbbell, Activity, Clock, Trash2 } from 'lucide-vue-next'
import DoctorPatientDetail from './DoctorPatientDetail.vue'
import { API_BASE_URL } from '../config'


const searchQuery = ref('')
const filterStatus = ref('All')
const showAddModal = ref(false)
const selectedPatient = ref(null)

const patients = ref([])

const newPatient = ref({ full_name: '', username: '', password: '', email: '' })

const filteredPatients = computed(() => {
  return patients.value.filter(p => {
    const matchesSearch = p.full_name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          p.email.toLowerCase().includes(searchQuery.value.toLowerCase())
    // Status filter is mocked for now as we don't have status in users table
    return matchesSearch
  })
})

function getInitials(name) {
  return name ? name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() : '??'
}

function getStatusClass(status) {
  // Mock status logic
  return 'bg-emerald-50 text-emerald-600 border-emerald-200'
}

function getStatusLabel(status) {
  return 'Ổn định'
}

async function loadPatients() {
  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE_URL}/patients`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (res.ok) {
      const data = await res.json();
      patients.value = data.items || data; // Handle pagination or list
    }
  } catch (e) {
    console.error("Error loading patients:", e);
  }
}

async function addNewPatient() {
  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE_URL}/patients`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(newPatient.value)
    });

    if (res.ok) {
      await loadPatients();
      showAddModal.value = false;
      newPatient.value = { full_name: '', username: '', password: '', email: '' };
    } else {
      const err = await res.json();
      alert("Lỗi: " + err.detail);
    }
  } catch (e) {
    console.error(e);
    alert("Lỗi kết nối");
  }
}

function viewPatientDetail(patient) {
  selectedPatient.value = patient.patient_id;
}

async function deletePatient(id) {
  if (!confirm("Bạn có chắc muốn xóa bệnh nhân này? Hành động này sẽ xóa tất cả dữ liệu liên quan.")) return;
  
  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE_URL}/patients/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (res.ok) {
      await loadPatients();
    } else {
      alert("Lỗi khi xóa bệnh nhân");
    }
  } catch (e) {
    console.error(e);
  }
}

onMounted(() => {
  loadPatients();
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
</style>
