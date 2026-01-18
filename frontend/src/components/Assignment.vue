<template>
  <div class="assignment-wrapper">
    <!-- Toast Notification -->
    <Transition name="toast">
      <div v-if="toast.show" :class="['toast-notification', toast.type]">
        {{ toast.message }}
      </div>
    </Transition>

    <!-- Unified Page Header -->
    <div class="page-header">
      <!-- Left: Patient Selector/Display -->
      <div class="header-left">
        <!-- Skeleton Loading State -->
        <div v-if="isLoading" class="skeleton-patient">
          <div class="skeleton skeleton-avatar"></div>
          <div class="skeleton-text">
            <div class="skeleton skeleton-line"></div>
            <div class="skeleton skeleton-line-sm"></div>
          </div>
        </div>

        <!-- Search (when no patient and not loading) -->
        <div v-else-if="!selectedPatient" class="patient-search-compact">
          <Search class="search-icon-sm" :size="16" />
          <input
            v-model="searchQuery"
            @focus="showDropdown = true"
            @blur="hideDropdownDelayed"
            type="text"
            placeholder="Tìm bệnh nhân..."
            class="search-input-compact"
          />
          <div v-if="showDropdown && filteredPatients.length > 0" class="patients-dropdown-compact">
            <button
              v-for="patient in filteredPatients"
              :key="patient.patient_id"
              @click="selectPatient(patient)"
              class="dropdown-item-compact"
            >
              <div class="avatar-xs">{{ getInitials(patient.full_name) }}</div>
              <span>{{ patient.full_name }}</span>
            </button>
          </div>
        </div>

        <!-- Selected Patient Display -->
        <div v-else class="patient-display">
          <div class="avatar-md">{{ getInitials(currentPatient.full_name) }}</div>
          <div class="patient-info">
            <h2 class="patient-name">{{ currentPatient.full_name }}</h2>
            <p class="patient-email">{{ currentPatient.email }}</p>
          </div>
          <button @click="clearSelection" class="change-btn">
            <RefreshCw :size="14" />
          </button>
        </div>
      </div>

      <!-- Center: Stats (only when patient selected) -->
      <div v-if="currentPatient" class="header-stats">
        <div class="stat-compact">
          <span class="stat-num">{{ patientStats.compliance }}%</span>
          <span class="stat-lbl">Tuân thủ</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-compact">
          <span class="stat-num">{{ patientStats.sessions }}</span>
          <span class="stat-lbl">Buổi tập</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-compact">
          <span class="stat-num">{{ patientStats.totalTime }}h</span>
          <span class="stat-lbl">Thời gian</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-compact">
          <span class="stat-num">{{ patientStats.avgScore }}</span>
          <span class="stat-lbl">Điểm TB</span>
        </div>
      </div>

      <!-- Right: View Toggle + Add Button -->
      <div class="header-right">
        <div v-if="currentPatient" class="view-toggle">
          <button
            @click="viewMode = 'list'"
            :class="['toggle-btn', viewMode === 'list' && 'active']"
          >
            <List :size="16" />
          </button>
          <button
            @click="viewMode = 'calendar'"
            :class="['toggle-btn', viewMode === 'calendar' && 'active']"
          >
            <Calendar :size="16" />
          </button>
        </div>
        <button
          v-if="currentPatient && viewMode === 'list'"
          @click="openAddModal"
          class="add-btn-header"
        >
          <Plus :size="16" />
          <span>Thêm</span>
        </button>
      </div>
    </div>

    <!-- MAIN CONTENT -->
    <div v-if="currentPatient" class="content-area">
      <!-- CALENDAR VIEW -->
      <div
        v-if="viewMode === 'calendar'"
        class="calendar-view bg-white rounded-3xl shadow-xl border border-slate-200 overflow-hidden"
      >
        <!-- Calendar Header -->
        <div class="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <div class="flex items-center gap-4">
            <button
              @click="calendarToday"
              class="px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-sm font-bold text-slate-600 hover:bg-slate-50"
            >
              Hôm nay
            </button>
            <div class="flex gap-1">
              <button @click="calendarPrev" class="p-1.5 hover:bg-white rounded-lg">
                <ChevronLeft :size="20" />
              </button>
              <button @click="calendarNext" class="p-1.5 hover:bg-white rounded-lg">
                <ChevronRight :size="20" />
              </button>
            </div>
            <h3 class="text-lg font-black text-slate-800">{{ calendarTitle }}</h3>
          </div>
        </div>

        <!-- Calendar Grid -->
        <div class="grid grid-cols-7 border-b border-slate-200 bg-slate-50">
          <div
            v-for="day in ['CN', 'Hai', 'Ba', 'Tư', 'Năm', 'Sáu', 'Bảy']"
            :key="day"
            class="py-3 text-center text-xs font-bold text-slate-500 uppercase"
          >
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
              !cell.inMonth ? 'bg-slate-50/50 text-slate-400' : '',
            ]"
          >
            <div class="flex justify-between items-start mb-2">
              <span
                :class="[
                  'w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold',
                  cell.isToday ? 'bg-indigo-600 text-white' : '',
                ]"
              >
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
                  <span
                    >•
                    {{
                      ex.session_time === 'Morning'
                        ? 'Sáng'
                        : ex.session_time === 'Afternoon'
                          ? 'Chiều'
                          : 'Tối'
                    }}</span
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- LIST VIEW -->
      <div v-else class="exercises-section">
        <div class="exercises-list">
          <div v-for="(ex, i) in exercises" :key="ex.id" class="exercise-card">
            <div class="exercise-icon-wrapper">
              <div class="exercise-icon">{{ ex.icon }}</div>
            </div>
            <div class="exercise-content">
              <h4 class="exercise-name capitalize">{{ ex.name }}</h4>
              <div class="exercise-meta">
                <span class="meta-text">
                  {{ ex.reps > 0 ? `${ex.reps} reps` : `${ex.duration} phút` }} •
                  {{ ex.session_time === 'Morning' ? 'Sáng' : 'Chiều' }}
                </span>
                <span class="meta-date">{{ formatDate(ex.assigned_date) }}</span>
              </div>
            </div>
            <div class="exercise-actions">
              <button
                @click.prevent.stop="removeExercise(i)"
                type="button"
                class="action-btn action-delete"
              >
                <Trash2 :size="18" />
              </button>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="exercises.length === 0" class="empty-state">
            <div class="empty-icon">💪</div>
            <h4 class="empty-title">Chưa có bài tập nào</h4>
            <p class="empty-text">
              Bắt đầu bằng cách thêm bài tập đầu tiên vào kế hoạch của bệnh nhân.
            </p>
            <button @click="openAddModal" class="empty-btn">
              <Plus :size="18" />
              Thêm bài tập đầu tiên
            </button>
          </div>
        </div>
      </div>
    </div>
    <!-- End Assign Wrapper -->

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
                <option value="squat">Squat</option>
                <option value="bicep-curl">Bicep Curl</option>
                <option value="shoulder-flexion">Shoulder Flexion</option>
                <option value="knee-raise">Knee Raise</option>
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
                <input
                  v-model.number="form.sets"
                  type="number"
                  class="form-input"
                  placeholder="3"
                />
              </div>

              <div v-if="form.target_mode !== 'duration'" class="form-group">
                <label class="form-label">Số lần (Reps)</label>
                <input
                  v-model.number="form.target_reps"
                  type="number"
                  class="form-input"
                  placeholder="10"
                />
              </div>

              <div v-if="form.target_mode === 'duration'" class="form-group">
                <label class="form-label">Thời gian (Phút)</label>
                <input
                  v-model.number="form.duration_minutes"
                  type="number"
                  class="form-input"
                  placeholder="15"
                />
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
            <input
              type="checkbox"
              v-model="form.is_daily"
              id="is_daily"
              class="w-5 h-5 text-indigo-600 rounded focus:ring-indigo-500"
            />
            <label for="is_daily" class="text-sm font-bold text-slate-700"
              >Lặp lại hàng ngày (Thêm vào kế hoạch tuần)</label
            >
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
  Plus,
  Clock,
  Repeat,
  Calendar,
  Trash2,
  Edit2,
  X,
  Search,
  Check,
  Users,
  Mail,
  ChevronLeft,
  ChevronRight,
  List,
  RefreshCw,
} from 'lucide-vue-next'

// API Configuration
const API_BASE = 'http://localhost:8001/api'

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
  exercise_type: 'squat',
  target_reps: 10,
  assigned_date: new Date().toISOString().split('T')[0],
  session_time: 'Morning',
  is_daily: false,
})

// Patient selection
const patients = ref([])
const selectedPatient = ref(null)
const currentPatient = ref(null)
const searchQuery = ref('')
const showDropdown = ref(false)
const dropdownTimeout = ref(null)
const isLoading = ref(true)

// Toast notification
const toast = ref({ show: false, message: '', type: 'success' })
const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// Patient stats (loaded from API)
const patientStats = ref({
  compliance: 0,
  sessions: 0,
  totalTime: 0,
  avgScore: 0,
})

// Computed
const filteredPatients = computed(() => {
  if (!searchQuery.value.trim()) {
    return patients.value
  }
  const query = searchQuery.value.toLowerCase()
  return patients.value.filter(
    (patient) =>
      patient.full_name.toLowerCase().includes(query) ||
      patient.email.toLowerCase().includes(query),
  )
})

// Methods
const getInitials = (name) => {
  return name
    ? name
        .split(' ')
        .map((s) => s[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()
    : '??'
}

const selectPatient = async (patient) => {
  if (dropdownTimeout.value) {
    clearTimeout(dropdownTimeout.value)
    dropdownTimeout.value = null
  }

  selectedPatient.value = patient.patient_id
  currentPatient.value = patient
  searchQuery.value = '' // Clear search query to avoid filtering issues
  showDropdown.value = false

  // Load real patient stats from API
  try {
    const token = localStorage.getItem('token')
    const statsRes = await fetch(`${API_BASE}/patients/${patient.patient_id}/stats`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (statsRes.ok) {
      patientStats.value = await statsRes.json()
    }
  } catch (e) {
    console.error('Error loading patient stats:', e)
  }

  loadAssignments(patient.patient_id)
}

const clearSelection = () => {
  selectedPatient.value = null
  currentPatient.value = null
  searchQuery.value = ''
  // Focus search input on next tick if possible, but simple state change is enough
}

const hideDropdownDelayed = () => {
  if (dropdownTimeout.value) {
    clearTimeout(dropdownTimeout.value)
  }

  dropdownTimeout.value = setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

const loadPatients = async () => {
  isLoading.value = true
  try {
    const token = localStorage.getItem('token')
    // Get Doctor ID first - use authenticated endpoint
    const docRes = await fetch(`${API_BASE}/me/doctor-id`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (docRes.ok) {
      const data = await docRes.json()
      doctorId.value = data.doctor_id
    }

    const response = await fetch(`${API_BASE}/patients-with-status`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!response.ok) throw new Error('Failed to fetch patients')
    patients.value = await response.json()

    if (patients.value.length > 0) {
      selectPatient(patients.value[0])
    }
  } catch (err) {
    console.error('Error loading patients:', err)
  } finally {
    isLoading.value = false
  }
}

const loadAssignments = async (patientId) => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`${API_BASE}/assignments/${patientId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (response.ok) {
      const data = await response.json()
      // Map to view format
      exercises.value = data.map((d) => ({
        id: d.assignment_id,
        name: d.exercise_type,
        duration: d.duration_seconds ? Math.round(d.duration_seconds / 60) : 0,
        sets: d.sets || 1,
        reps: d.target_reps,
        freq: d.frequency || 'Once',
        difficulty: 'Medium',
        icon: '🏋️',
        assigned_date: d.assigned_date,
        session_time: d.session_time,
      }))
    }
  } catch (err) {
    console.error('Error loading assignments:', err)
  }
}

// Modal Logic
const openAddModal = () => {
  isEditing.value = false
  form.value = {
    exercise_type: 'squat',
    target_reps: 10,
    duration_minutes: 15,
    assigned_date: new Date().toISOString().split('T')[0],
    session_time: 'Morning',
    is_daily: false,
    target_mode: 'reps',
  }
  showModal.value = true
}

const closeModal = () => (showModal.value = false)

// Combo Logic
const loadCombos = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE}/combos?doctor_id=${doctorId.value}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) combos.value = await res.json()
  } catch (e) {
    console.error(e)
  }
}

// Assignment Logic
const saveAssignment = async () => {
  if (!selectedPatient.value || !doctorId.value) return

  try {
    // Only include fields defined in AssignmentCreate schema
    const payload = {
      patient_id: selectedPatient.value,
      // doctor_id removed - backend uses current_doctor dependency
      // assigned_date removed - backend likely generates it or uses API date, check if schema has it?
      // Wait, Schema doesn't have assigned_date in AssignmentCreate.
      // It has day_of_week and week_plan_id.
      // If we need assigned_date, it might not be supported in simple assignment or uses current date.
      target_reps: form.value.target_reps,
      session_time: form.value.session_time,
      frequency: form.value.is_daily ? 'Daily' : 'Once',
      duration_seconds: (form.value.duration_minutes || 0) * 60,
    }

    if (form.value.target_mode === 'reps') {
      payload.sets = 1
    } else if (form.value.target_mode === 'sets_reps') {
      payload.sets = form.value.sets || 3
    } else if (form.value.target_mode === 'duration') {
      payload.sets = 1
      payload.target_reps = 0
    }

    if (assignType.value === 'single') {
      payload.exercise_type = form.value.exercise_type
    } else {
      payload.combo_id = selectedComboId.value
    }

    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE}/assign_plan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    })

    if (res.ok) {
      await loadAssignments(selectedPatient.value)
      closeModal()
      showToast('Đã giao bài tập thành công!', 'success')
    } else {
      const err = await res.json()
      showToast(`Lỗi: ${err.detail || 'Không thể giao bài tập'}`, 'error')
    }
  } catch (e) {
    console.error(e)
  }
}

const removeExercise = async (idx) => {
  const ex = exercises.value[idx]
  if (!ex || !ex.id) return

  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE}/assignments/${ex.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })

    if (res.ok) {
      exercises.value.splice(idx, 1)
      showToast('Đã xóa bài tập!', 'success')
    } else {
      console.error('Delete failed:', res.status)
      showToast('Không thể xóa bài tập', 'error')
    }
  } catch (e) {
    console.error('Delete error:', e)
  }
}

const getDifficultyClass = (diff) => {
  switch (diff) {
    case 'Easy':
      return 'difficulty-easy'
    case 'Medium':
      return 'difficulty-medium'
    case 'Hard':
      return 'difficulty-hard'
    default:
      return 'difficulty-medium'
  }
}

// Calendar State
const calendarDate = ref(new Date())
const calendarTitle = computed(() =>
  calendarDate.value.toLocaleString('vi-VN', { month: 'long', year: 'numeric' }),
)

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

    const dayExercises = exercises.value.filter((ex) => {
      if (!ex.assigned_date) return false
      const exDate = new Date(ex.assigned_date)
      return (
        exDate.getDate() === date.getDate() &&
        exDate.getMonth() === date.getMonth() &&
        exDate.getFullYear() === date.getFullYear()
      )
    })

    cells.push({
      date,
      inMonth: date.getMonth() === month,
      isToday: isSameDay(date, new Date()),
      exercises: dayExercises,
    })
  }
  return cells
})

// Calendar Methods
const calendarPrev = () => {
  calendarDate.value = new Date(
    calendarDate.value.getFullYear(),
    calendarDate.value.getMonth() - 1,
    1,
  )
}

const calendarNext = () => {
  calendarDate.value = new Date(
    calendarDate.value.getFullYear(),
    calendarDate.value.getMonth() + 1,
    1,
  )
}

const calendarToday = () => {
  calendarDate.value = new Date()
}

const isSameDay = (d1, d2) => {
  return (
    d1.getDate() === d2.getDate() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getFullYear() === d2.getFullYear()
  )
}

const selectDate = (date) => {
  const offset = date.getTimezoneOffset()
  const adjustedDate = new Date(date.getTime() - offset * 60 * 1000)
  form.value.assigned_date = adjustedDate.toISOString().split('T')[0]
  openAddModal()
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('vi-VN')
}

// Lifecycle
onMounted(async () => {
  await loadPatients()
  if (doctorId.value) loadCombos()
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
  position: relative;
}

/* Toast Notification */
.toast-notification {
  position: fixed;
  top: 24px;
  right: 24px;
  padding: 16px 24px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  z-index: 9999;
}

.toast-notification.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.toast-notification.error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100px);
}

/* Compact Page Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  padding: 16px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
  gap: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  min-width: 280px;
}

.patient-search-compact {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.search-icon-sm {
  position: absolute;
  left: 12px;
  color: #94a3b8;
}

.search-input-compact {
  width: 100%;
  padding: 10px 12px 10px 38px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.search-input-compact:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.patients-dropdown-compact {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  margin-top: 8px;
  max-height: 240px;
  overflow-y: auto;
  z-index: 100;
}

.dropdown-item-compact {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  transition: background 0.15s;
}

.dropdown-item-compact:hover {
  background: #f1f5f9;
}

.avatar-xs {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
}

.avatar-md {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 800;
  flex-shrink: 0;
}

.patient-display {
  display: flex;
  align-items: center;
  gap: 12px;
}

.patient-info {
  display: flex;
  flex-direction: column;
}

.patient-name {
  font-size: 16px;
  font-weight: 800;
  color: #1e293b;
  margin: 0;
}

.patient-email {
  font-size: 12px;
  color: #64748b;
  margin: 0;
}

.change-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: #f1f5f9;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  margin-left: 8px;
}

.change-btn:hover {
  background: #e2e8f0;
  color: #6366f1;
}

/* Header Stats */
.header-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 24px;
  border-left: 1px solid #e2e8f0;
  border-right: 1px solid #e2e8f0;
}

.stat-compact {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
}

.stat-num {
  font-size: 18px;
  font-weight: 800;
  color: #1e293b;
}

.stat-lbl {
  font-size: 10px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-divider {
  width: 1px;
  height: 24px;
  background: #e2e8f0;
}

/* Header Right */
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.view-toggle {
  display: flex;
  background: #f1f5f9;
  border-radius: 10px;
  padding: 4px;
}

.toggle-btn {
  padding: 8px 12px;
  border: none;
  background: none;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-btn:hover {
  color: #6366f1;
}

.toggle-btn.active {
  background: white;
  color: #6366f1;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.add-btn-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.add-btn-header:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

/* Content Area */
.content-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Exercises List */
.exercises-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Skeleton Loading */
.skeleton-patient {
  display: flex;
  align-items: center;
  gap: 12px;
}

.skeleton-text {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.skeleton {
  background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
  border-radius: 6px;
}

.skeleton-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
}

.skeleton-line {
  width: 120px;
  height: 14px;
}

.skeleton-line-sm {
  width: 160px;
  height: 10px;
}

@keyframes skeleton-shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
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
  background: rgba(255, 255, 255, 0.5);
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

.combo-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 700;
}
.combo-desc {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}

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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
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

.builder-select,
.builder-input {
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

.capitalize {
  text-transform: capitalize;
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
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
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
