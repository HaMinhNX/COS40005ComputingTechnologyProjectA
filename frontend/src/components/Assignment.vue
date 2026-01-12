<template>
  <div class="assignment-wrapper">
    <!-- Patient Selector Header -->
    <div class="selector-card">
      <div class="selector-header">
        <div class="header-icon">
          <Users :size="24" />
        </div>
        <div>
          <h3 class="selector-title">Quản lý & Phân công</h3>
          <p class="selector-subtitle">Tạo tổ hợp bài tập và phân công cho bệnh nhân</p>
        </div>
      </div>

      <!-- Patient Search -->
      
      <div v-if="viewMode === 'assign'" class="patient-search-wrapper">
        <Search class="search-icon" :size="18" />
        <input
          v-model="searchQuery"
          @focus="showDropdown = true"
          @blur="hideDropdownDelayed"
          type="text"
          placeholder="Tìm kiếm bệnh nhân..."
          class="patient-search-input"
        />
        
        <div v-if="showDropdown && filteredPatients.length > 0" class="patients-dropdown">
          <button
            v-for="patient in filteredPatients"
            :key="patient.patient_id"
            @click="selectPatient(patient)"
            class="dropdown-patient-item"
          >
            <div class="patient-avatar-sm">{{ getInitials(patient.full_name) }}</div>
            <span class="patient-dropdown-name">{{ patient.full_name }}</span>
            <Check v-if="selectedPatient === patient.patient_id" :size="16" class="check-icon" />
          </button>
        </div>
      </div>
    </div>



    <!-- View Toggle -->
    <div class="flex justify-end mb-4">
      <div class="bg-slate-100 p-1 rounded-xl flex gap-1">
        <button 
          @click="viewMode = 'list'"
          :class="['px-4 py-2 rounded-lg text-sm font-bold transition-all', viewMode === 'list' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']"
        >
          Danh sách
        </button>
        <button 
          @click="viewMode = 'calendar'"
          :class="['px-4 py-2 rounded-lg text-sm font-bold transition-all', viewMode === 'calendar' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']"
        >
          Lịch tập
        </button>
      </div>
    </div>

    <!-- ASSIGN MODE -->
    <div v-if="currentPatient" class="assign-wrapper">

    <!-- Patient Profile Card -->
    <div v-if="currentPatient" class="profile-card">
      <div class="profile-decoration"></div>
      
      <div class="profile-header">
        <div class="profile-avatar-large">
          {{ getInitials(currentPatient.full_name) }}
        </div>
        <div class="profile-info">
          <h2 class="profile-name">{{ currentPatient.full_name }}</h2>
          <p class="profile-email">
            <Mail :size="14" />
            {{ currentPatient.email }}
          </p>
        </div>
      </div>
      
      <div class="profile-stats">
        <div class="stat-item">
          <p class="stat-value">{{ patientStats.compliance }}%</p>
          <p class="stat-label">Tuân thủ</p>
        </div>
        <div class="stat-item">
          <p class="stat-value">{{ patientStats.sessions }}</p>
          <p class="stat-label">Buổi tập</p>
        </div>
        <div class="stat-item">
          <p class="stat-value">{{ patientStats.totalTime }}h</p>
          <p class="stat-label">Tổng thời gian</p>
        </div>
        <div class="stat-item">
          <p class="stat-value">{{ patientStats.avgScore }}</p>
          <p class="stat-label">Điểm TB</p>
        </div>
      </div>
    </div>

    <!-- CALENDAR VIEW -->
    <div v-if="viewMode === 'calendar'" class="calendar-view bg-white rounded-3xl shadow-xl border border-slate-200 overflow-hidden">
      <!-- Calendar Header -->
      <div class="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50">
        <div class="flex items-center gap-4">
          <button @click="calendarToday" class="px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-sm font-bold text-slate-600 hover:bg-slate-50">Hôm nay</button>
          <div class="flex gap-1">
            <button @click="calendarPrev" class="p-1.5 hover:bg-white rounded-lg"><ChevronLeft :size="20" /></button>
            <button @click="calendarNext" class="p-1.5 hover:bg-white rounded-lg"><ChevronRight :size="20" /></button>
          </div>
          <h3 class="text-lg font-black text-slate-800">{{ calendarTitle }}</h3>
        </div>
      </div>

      <!-- Calendar Grid -->
      <div class="grid grid-cols-7 border-b border-slate-200 bg-slate-50">
        <div v-for="day in ['CN', 'Hai', 'Ba', 'Tư', 'Năm', 'Sáu', 'Bảy']" :key="day" class="py-3 text-center text-xs font-bold text-slate-500 uppercase">
          {{ day }}
        </div>
      </div>
      <div class="grid grid-cols-7 auto-rows-fr bg-white">
        <div 
          v-for="(cell, i) in calendarCells" 
          :key="i"
          @click="selectDate(cell.date)"
          :class="[
            'min-h-[120px] border-b border-r border-slate-100 p-2 transition-colors hover:bg-slate-50 cursor-pointer',
            !cell.inMonth ? 'bg-slate-50/50 text-slate-400' : ''
          ]"
        >
          <div class="flex justify-between items-start mb-2">
            <span :class="['w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold', cell.isToday ? 'bg-indigo-600 text-white' : '']">
              {{ cell.date.getDate() }}
            </span>
          </div>
          
          <!-- Events List -->
          <div class="space-y-1">
            <div 
              v-for="ex in cell.exercises" 
              :key="ex.id"
              class="px-2 py-1.5 rounded-lg bg-indigo-50 border border-indigo-100 text-xs hover:bg-indigo-100 transition-colors group"
            >
              <div class="font-bold text-indigo-900 truncate">{{ ex.name }}</div>
              <div class="flex items-center gap-1 text-indigo-700 text-[10px]">
                <span v-if="ex.reps > 0">{{ ex.reps }} reps</span>
                <span v-if="ex.duration > 0">{{ ex.duration }}m</span>
                <span>• {{ ex.session_time === 'Morning' ? 'Sáng' : (ex.session_time === 'Afternoon' ? 'Chiều' : 'Tối') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- LIST VIEW (Original) -->
    <div v-else class="exercises-section">
      <div class="section-header">
        <h3 class="section-title">Bài tập đã giao</h3>
        <button @click="openAddModal" class="add-btn">
          <Plus :size="18" />
          Thêm bài tập
        </button>
      </div>

      <div class="exercises-grid">
        <div v-for="(ex, i) in exercises" :key="ex.id" class="exercise-card">
          <div class="exercise-icon-wrapper">
            <div class="exercise-icon">{{ ex.icon }}</div>
          </div>
          <div class="exercise-content">
            <h4 class="exercise-name">{{ ex.name }}</h4>
            <div class="exercise-meta">
              <span class="meta-text">
                {{ ex.reps > 0 ? `${ex.reps} reps` : `${ex.duration} phút` }} • {{ ex.session_time === 'Morning' ? 'Sáng' : 'Chiều' }}
              </span>
              <span class="meta-date">{{ formatDate(ex.assigned_date) }}</span>
            </div>
          </div>
          <div class="exercise-actions">
            <button @click="removeExercise(i)" class="action-btn action-delete">
              <Trash2 :size="18" />
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="exercises.length === 0" class="empty-state">
          <div class="empty-icon">💪</div>
          <h4 class="empty-title">Chưa có bài tập nào</h4>
          <p class="empty-text">Bắt đầu bằng cách thêm bài tập đầu tiên vào kế hoạch của bệnh nhân.</p>
          <button @click="openAddModal" class="empty-btn">
            <Plus :size="18" />
            Thêm bài tập đầu tiên
          </button>
        </div>
      </div>
    </div>

    </div> <!-- End Assign Wrapper -->

    <!-- Add/Edit Exercise Modal (Modified to support Combos) -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">Giao bài tập</h3>
          <button @click="closeModal" class="modal-close">
            <X :size="20" />
          </button>
        </div>
        
        <div class="modal-body">
          <!-- Type Switcher -->
          <div class="type-tabs">
            <button 
              @click="assignType = 'single'" 
              :class="['type-tab', { active: assignType === 'single' }]"
            >
              Bài tập lẻ
            </button>
            <button 
              @click="assignType = 'combo'" 
              :class="['type-tab', { active: assignType === 'combo' }]"
            >
              Combo mẫu
            </button>
          </div>

          <!-- Single Exercise Form -->
          <div v-if="assignType === 'single'">
            <div class="form-group">
              <label class="form-label">Loại bài tập</label>
              <select v-model="form.exercise_type" class="form-input">
                <option value="Squat">Squat</option>
                <option value="Bicep Curl">Bicep Curl</option>
                <option value="Shoulder Flexion">Shoulder Flexion</option>
                <option value="Knee Raise">Knee Raise</option>
                <option value="Brain Game">Brain Game (Trí tuệ)</option>
              </select>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Chế độ tập</label>
                <select v-model="form.target_mode" class="form-input">
                  <option value="reps">Theo số lần (Reps)</option>
                  <option value="sets_reps">Theo hiệp (Sets x Reps)</option>
                  <option value="duration">Theo thời gian</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div v-if="form.target_mode === 'sets_reps'" class="form-group">
                <label class="form-label">Số hiệp (Sets)</label>
                <input v-model.number="form.sets" type="number" class="form-input" placeholder="3" />
              </div>
              
              <div v-if="form.target_mode !== 'duration'" class="form-group">
                <label class="form-label">Số lần (Reps)</label>
                <input v-model.number="form.target_reps" type="number" class="form-input" placeholder="10" />
              </div>

              <div v-if="form.target_mode === 'duration'" class="form-group">
                <label class="form-label">Thời gian (Phút)</label>
                <input v-model.number="form.duration_minutes" type="number" class="form-input" placeholder="15" />
              </div>
            </div>
          </div>

          <!-- Combo Selection Form -->
          <div v-if="assignType === 'combo'">
             <div class="form-group">
               <label class="form-label">Chọn Combo</label>
               <select v-model="selectedComboId" class="form-input">
                 <option v-for="c in combos" :key="c.combo_id" :value="c.combo_id">
                   {{ c.name }} ({{ c.items?.length || 0 }} bài)
                 </option>
               </select>
             </div>
          </div>

          <div class="form-group">
             <label class="form-label">Ngày bắt đầu</label>
             <input v-model="form.assigned_date" type="date" class="form-input" />
          </div>

          <div class="form-group">
             <label class="form-label">Buổi tập</label>
             <select v-model="form.session_time" class="form-input">
               <option value="Morning">Sáng</option>
               <option value="Afternoon">Chiều</option>
               <option value="Evening">Tối</option>
             </select>
          </div>

          <div class="form-group flex items-center gap-2 mt-4">
             <input type="checkbox" v-model="form.is_daily" id="is_daily" class="w-5 h-5 text-indigo-600 rounded focus:ring-indigo-500" />
             <label for="is_daily" class="text-sm font-bold text-slate-700">Lặp lại hàng ngày (Thêm vào kế hoạch tuần)</label>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeModal" class="modal-btn-cancel">Hủy</button>
          <button @click="saveAssignment" class="modal-btn-save">Giao bài</button>
        </div>
      </div>
    </div>


  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { 
  Plus, Clock, Repeat, Calendar, Trash2, Edit2, X, Search, Check, Users, Mail, ChevronLeft, ChevronRight
} from 'lucide-vue-next'

// API Configuration
const API_BASE = 'http://localhost:8001/api';

const viewMode = ref('assign') // 'assign' or 'combos'
const assignType = ref('single') // 'single' or 'combo'
const combos = ref([])
const selectedComboId = ref(null)
const exercises = ref([])
const isEditing = ref(false)
const showModal = ref(false)
const doctorId = ref(null)

// Form Data
const form = ref({
  exercise_type: 'Squat',
  target_reps: 10,
  assigned_date: new Date().toISOString().split('T')[0],
  session_time: 'Morning',
  is_daily: false
})



// Patient selection
const patients = ref([])
const selectedPatient = ref(null)
const currentPatient = ref(null)
const searchQuery = ref('')
const showDropdown = ref(false)
const dropdownTimeout = ref(null)

// Patient stats (Mocked for now)
const patientStats = ref({
  compliance: 85,
  sessions: 12,
  totalTime: 3,
  avgScore: 4.2
})

// Computed
const filteredPatients = computed(() => {
  if (!searchQuery.value.trim()) {
    return patients.value;
  }
  const query = searchQuery.value.toLowerCase();
  return patients.value.filter(patient => 
    patient.full_name.toLowerCase().includes(query) ||
    patient.email.toLowerCase().includes(query)
  );
})

// Methods
const getInitials = (name) => {
  return name ? name.split(' ').map(s => s[0]).join('').slice(0, 2).toUpperCase() : '??';
}

const selectPatient = (patient) => {
  if (dropdownTimeout.value) {
    clearTimeout(dropdownTimeout.value);
    dropdownTimeout.value = null;
  }
  
  selectedPatient.value = patient.patient_id;
  currentPatient.value = patient;
  searchQuery.value = patient.full_name;
  showDropdown.value = false;
  loadAssignments(patient.patient_id);
}

const hideDropdownDelayed = () => {
  if (dropdownTimeout.value) {
    clearTimeout(dropdownTimeout.value);
  }
  
  dropdownTimeout.value = setTimeout(() => {
    showDropdown.value = false;
  }, 200);
}

const loadPatients = async () => {
  try {
    const token = localStorage.getItem('token');
    // Get Doctor ID first
    const docRes = await fetch(`${API_BASE}/doctor-id`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (docRes.ok) {
      const data = await docRes.json();
      doctorId.value = data.doctor_id;
    }

    const response = await fetch(`${API_BASE}/patients`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!response.ok) throw new Error('Failed to fetch patients');
    patients.value = await response.json();
    
    if (patients.value.length > 0) {
      selectPatient(patients.value[0]);
    }
  } catch (err) {
    console.error('Error loading patients:', err);
  }
}

const loadAssignments = async (patientId) => {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE}/assignments/${patientId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
      const data = await response.json();
      // Map to view format
      exercises.value = data.map(d => ({
        id: d.assignment_id,
        name: d.exercise_type,
        duration: d.duration_seconds ? Math.round(d.duration_seconds / 60) : 0,
        sets: d.sets || 1,
        reps: d.target_reps,
        freq: d.frequency || 'Once',
        difficulty: 'Medium',
        icon: '🏋️'
      }));
    }
  } catch (err) {
    console.error('Error loading assignments:', err);
  }
}

// Modal Logic
const openAddModal = () => { 
  isEditing.value = false; 
  form.value = {
    exercise_type: 'Squat',
    target_reps: 10,
    duration_minutes: 15,
    assigned_date: new Date().toISOString().split('T')[0],
    session_time: 'Morning',
    is_daily: false,
    target_mode: 'reps'
  }
  showModal.value = true 
}

const closeModal = () => showModal.value = false

// Combo Logic
const loadCombos = async () => {
  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE}/combos?doctor_id=${doctorId.value}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) combos.value = await res.json();
  } catch (e) { console.error(e); }
}



// Assignment Logic
const saveAssignment = async () => {
  if (!selectedPatient.value || !doctorId.value) return;

  try {
    const payload = {
      patient_id: selectedPatient.value,
      doctor_id: doctorId.value,
      assigned_date: form.value.assigned_date,
      target_reps: form.value.target_reps,
      session_time: form.value.session_time,
      frequency: form.value.is_daily ? 'Daily' : 'Once',
      duration_seconds: (form.value.duration_minutes || 0) * 60
    };

    if (form.value.target_mode === 'reps') {
       payload.sets = 1;
    } else if (form.value.target_mode === 'sets_reps') {
       payload.sets = form.value.sets || 3;
    } else if (form.value.target_mode === 'duration') {
       payload.sets = 1;
       payload.target_reps = 0;
    }

    if (assignType.value === 'single') {
      payload.exercise_type = form.value.exercise_type;
    } else {
      payload.combo_id = selectedComboId.value;
    }

    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE}/assign_plan`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      await loadAssignments(selectedPatient.value);
      closeModal();
    } else {
      alert("Lỗi khi giao bài tập");
    }
  } catch (e) {
    console.error(e);
  }
}

const removeExercise = async (idx) => {
  const ex = exercises.value[idx];
  if (!confirm("Bạn có chắc muốn xóa bài tập này?")) return;

  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE}/assignments/${ex.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (res.ok) {
      exercises.value.splice(idx, 1);
    }
  } catch (e) {
    console.error(e);
  }
}

const getDifficultyClass = (diff) => {
  switch(diff) {
    case 'Easy': return 'difficulty-easy'
    case 'Medium': return 'difficulty-medium'
    case 'Hard': return 'difficulty-hard'
    default: return 'difficulty-medium'
  }
}

// Calendar State
const calendarDate = ref(new Date())
const calendarTitle = computed(() => calendarDate.value.toLocaleString('vi-VN', { month: 'long', year: 'numeric' }))

const calendarCells = computed(() => {
  const year = calendarDate.value.getFullYear()
  const month = calendarDate.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)

  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - startDate.getDay())

  const cells = []
  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)

    const dayExercises = exercises.value.filter(ex => {
      if (!ex.assigned_date) return false
      const exDate = new Date(ex.assigned_date)
      return exDate.getDate() === date.getDate() &&
             exDate.getMonth() === date.getMonth() &&
             exDate.getFullYear() === date.getFullYear()
    })

    cells.push({
      date,
      inMonth: date.getMonth() === month,
      isToday: isSameDay(date, new Date()),
      exercises: dayExercises
    })
  }
  return cells
})

// Calendar Methods
const calendarPrev = () => {
  calendarDate.value = new Date(calendarDate.value.getFullYear(), calendarDate.value.getMonth() - 1, 1)
}

const calendarNext = () => {
  calendarDate.value = new Date(calendarDate.value.getFullYear(), calendarDate.value.getMonth() + 1, 1)
}

const calendarToday = () => {
  calendarDate.value = new Date()
}

const isSameDay = (d1, d2) => {
  return d1.getDate() === d2.getDate() &&
         d1.getMonth() === d2.getMonth() &&
         d1.getFullYear() === d2.getFullYear()
}

const selectDate = (date) => {
  const offset = date.getTimezoneOffset()
  const adjustedDate = new Date(date.getTime() - (offset*60*1000))
  form.value.assigned_date = adjustedDate.toISOString().split('T')[0]
  openAddModal()
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('vi-VN')
}

// Lifecycle
onMounted(async () => {
  await loadPatients();
  if (doctorId.value) loadCombos();
})
</script>

<style scoped>
.assignment-wrapper {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.mode-switcher {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.mode-btn {
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  background: rgba(255,255,255,0.5);
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-btn.active {
  background: #6366f1;
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Combos Styles */
.combos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.combo-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #e2e8f0;
}

.combo-header {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.combo-icon {
  width: 40px;
  height: 40px;
  background: #fef3c7;
  color: #d97706;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.combo-name { margin: 0 0 4px 0; font-size: 16px; font-weight: 700; }
.combo-desc { margin: 0; font-size: 13px; color: #64748b; }

.combo-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.combo-item-tag {
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  color: #475569;
  font-weight: 600;
}

/* Modal Tabs */
.type-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  background: #f1f5f9;
  padding: 4px;
  border-radius: 12px;
}

.type-tab {
  flex: 1;
  padding: 8px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
}

.type-tab.active {
  background: white;
  color: #0f172a;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

/* Builder */
.builder-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.builder-item {
  display: flex;
  gap: 12px;
  align-items: center;
}

.item-number {
  width: 24px;
  height: 24px;
  background: #e2e8f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.builder-select, .builder-input {
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.remove-item-btn {
  background: #fee2e2;
  color: #ef4444;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-item-btn {
  width: 100%;
  padding: 10px;
  border: 2px dashed #e2e8f0;
  background: transparent;
  border-radius: 12px;
  color: #64748b;
  font-weight: 600;
  cursor: pointer;
}

.add-item-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
}

.large-modal {
  max-width: 800px;
}

/* Patient Selector Card */
.selector-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 20;
}

.selector-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.header-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
}

.selector-title {
  font-size: 24px;
  font-weight: 900;
  color: #0f172a;
  margin: 0;
}

.selector-subtitle {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  margin: 4px 0 0 0;
}

.patient-search-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  z-index: 1;
}

.patient-search-input {
  width: 100%;
  padding: 14px 16px 14px 48px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 600;
  outline: none;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.patient-search-input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.patients-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  max-height: 300px;
  overflow-y: auto;
  padding: 8px;
  z-index: 100;
}

.dropdown-patient-item {
  width: 100%;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: transparent;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.dropdown-patient-item:hover {
  background: #eef2ff;
}

.patient-avatar-sm {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  font-weight: 900;
  flex-shrink: 0;
}

.patient-dropdown-name {
  flex: 1;
  font-size: 14px;
  font-weight: 700;
  color: #334155;
}

.check-icon {
  color: #6366f1;
  flex-shrink: 0;
}

/* Profile Card */
.profile-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.profile-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 50%;
  opacity: 0.1;
  z-index: 0;
  transform: translate(50%, -50%);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

.profile-avatar-large {
  width: 96px;
  height: 96px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 36px;
  font-weight: 900;
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
  border: 4px solid white;
  flex-shrink: 0;
}

.profile-info {
  flex: 1;
}

/* Search Dropdown */
.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  margin-top: 8px;
  z-index: 50;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.dropdown-patient-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.dropdown-patient-item:hover {
  background: #f8fafc;
}

.patient-avatar-sm {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e0e7ff;
  color: #4f46e5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.patient-dropdown-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  flex: 1;
}

.check-icon {
  color: #10b981;
}

.profile-name {
  font-size: 28px;
  font-weight: 900;
  color: #0f172a;
  margin: 0 0 8px 0;
}

.profile-email {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  padding-top: 32px;
  border-top: 1px solid #e2e8f0;
  position: relative;
  z-index: 1;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 900;
  color: #0f172a;
  margin: 0 0 4px 0;
}

.stat-label {
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #94a3b8;
  margin: 0;
}

/* Exercises Section */
.exercises-section {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: 900;
  color: #0f172a;
  margin: 0;
}

.add-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(99, 102, 241, 0.4);
}

.exercises-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.exercise-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
}

.exercise-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.exercise-icon-wrapper {
  flex-shrink: 0;
}

.exercise-icon {
  width: 64px;
  height: 64px;
  background: #f8fafc;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.exercise-card:hover .exercise-icon {
  transform: scale(1.1);
}

.exercise-content {
  flex: 1;
  min-width: 0;
}

.exercise-name {
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 12px 0;
}

.exercise-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f1f5f9;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
}

.difficulty-badge {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 800;
}

.difficulty-easy {
  background: #d1fae5;
  color: #065f46;
}

.difficulty-medium {
  background: #fef3c7;
  color: #92400e;
}

.difficulty-hard {
  background: #fee2e2;
  color: #991b1b;
}

.exercise-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  min-width: 90px;
  height: 40px;
  padding: 0 16px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 700;
}

.action-label {
  white-space: nowrap;
}

.action-edit {
  background: #eef2ff;
  color: #6366f1;
  border: 1px solid #c7d2fe;
}

.action-edit:hover {
  background: #6366f1;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.action-delete {
  background: #fee2e2;
  color: #ef4444;
  border: 1px solid #fecaca;
}

.action-delete:hover {
  background: #ef4444;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 64px 32px;
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
  border-radius: 20px;
  border: 2px dashed #cbd5e1;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.empty-title {
  font-size: 20px;
  font-weight: 900;
  color: #0f172a;
  margin: 0 0 8px 0;
}

.empty-text {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  margin: 0 0 24px 0;
}

.empty-btn {
  padding: 12px 32px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
}

.empty-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(99, 102, 241, 0.4);
}

/* Notes Section */
.notes-section {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.notes-title {
  font-size: 18px;
  font-weight: 900;
  color: #0f172a;
  margin: 0 0 16px 0;
}

.notes-textarea {
  width: 100%;
  padding: 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  resize: none;
  outline: none;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.notes-textarea:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.notes-textarea::placeholder {
  color: #94a3b8;
}

.notes-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.notes-cancel {
  padding: 10px 24px;
  background: transparent;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
}

.notes-cancel:hover {
  background: #f1f5f9;
  color: #334155;
}

.notes-save {
  padding: 10px 24px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.notes-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal-content {
  background: white;
  border-radius: 24px;
  width: 100%;
  max-width: 600px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 32px 32px 24px 32px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 24px;
  font-weight: 900;
  color: #0f172a;
  margin: 0;
}

.modal-close {
  width: 40px;
  height: 40px;
  background: #f1f5f9;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.modal-close:hover {
  background: #ef4444;
  color: white;
  transform: scale(1.1);
}

.modal-body {
  padding: 32px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #64748b;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  outline: none;
  transition: all 0.3s ease;
}

.form-input:focus {
  border-color: #6366f1;
  background: white;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.modal-footer {
  padding: 24px 32px 32px 32px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.modal-btn-cancel {
  padding: 12px 24px;
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-btn-cancel:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.modal-btn-save {
  padding: 12px 32px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.modal-btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
}

/* Responsive */
@media (max-width: 768px) {
  .profile-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .exercise-card {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .exercise-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
