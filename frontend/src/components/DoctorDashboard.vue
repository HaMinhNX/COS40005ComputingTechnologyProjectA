<template>
  <div class="dashboard-container">
    <!-- Welcome Header -->
    <header class="dashboard-header">
      <div class="header-left">
        <h1 class="welcome-text">
          Xin chào, <span class="text-primary">{{ currentUser.full_name }}</span> 👋
        </h1>
        <p class="date-text">{{ currentDate }} • Chúc bác sĩ một ngày làm việc hiệu quả!</p>
      </div>
      <div class="header-right">
        <button class="action-btn primary">
          <Plus :size="20" />
          <span>Thêm bệnh nhân</span>
        </button>
      </div>
    </header>

    <!-- Stats Overview -->
    <div class="stats-row">
      <div class="stat-card blue">
        <div class="stat-icon">
          <Users :size="24" />
        </div>
        <div class="stat-info">
          <span class="stat-label">Tổng bệnh nhân</span>
          <h3 class="stat-value">{{ stats.totalPatients || 0 }}</h3>
          <span :class="['stat-trend', trends.patientTrend >= 0 ? 'positive' : 'negative']">
            <TrendingUp :size="14" /> {{ trends.patientTrend >= 0 ? '+' : ''
            }}{{ trends.patientTrend }}% tháng này
          </span>
        </div>
        <div class="stat-bg-icon"><Users :size="100" /></div>
      </div>

      <div class="stat-card green">
        <div class="stat-icon">
          <Activity :size="24" />
        </div>
        <div class="stat-info">
          <span class="stat-label">Đang hoạt động</span>
          <h3 class="stat-value">{{ activePatientsCount }}</h3>
          <span :class="['stat-trend', trends.activityTrend >= 0 ? 'positive' : 'negative']">
            <TrendingUp :size="14" /> {{ trends.activityTrend >= 0 ? '+' : ''
            }}{{ trends.activityTrend }}% hôm nay
          </span>
        </div>
        <div class="stat-bg-icon"><Activity :size="100" /></div>
      </div>

      <div class="stat-card orange">
        <div class="stat-icon">
          <AlertTriangle :size="24" />
        </div>
        <div class="stat-info">
          <span class="stat-label">Cần chú ý</span>
          <h3 class="stat-value">{{ criticalPatientsCount }}</h3>
          <span class="stat-trend negative">
            <AlertCircle :size="14" /> {{ trends.newAlerts }} cảnh báo mới
          </span>
        </div>
        <div class="stat-bg-icon"><AlertTriangle :size="100" /></div>
      </div>

      <div class="stat-card purple">
        <div class="stat-icon">
          <CheckCircle :size="24" />
        </div>
        <div class="stat-info">
          <span class="stat-label">Không hoạt động</span>
          <h3 class="stat-value">{{ inactivePatientsCount }}</h3>
          <span class="stat-trend negative"> <AlertCircle :size="14" /> Cần theo dõi sát </span>
        </div>
        <div class="stat-bg-icon"><CheckCircle :size="100" /></div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="main-grid">
      <!-- Left: Patient List -->
      <div class="content-card patient-list-section">
        <div class="card-header">
          <h3 class="card-title">Danh sách bệnh nhân</h3>
          <div class="search-box">
            <Search :size="18" />
            <input v-model="searchQuery" type="text" placeholder="Tìm kiếm tên, email..." />
          </div>
        </div>

        <div class="table-container custom-scrollbar">
          <table class="patient-table">
            <thead>
              <tr>
                <th class="th-num">#</th>
                <th>Bệnh nhân</th>
                <th>Trạng thái</th>
                <th>Tiến độ</th>
                <th>Hoạt động cuối</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(patient, index) in filteredPatients"
                :key="patient.patient_id"
                @click="selectPatient(patient)"
                :class="{ 'active-row': selectedPatientId === patient.patient_id }"
              >
                <td class="td-num">{{ index + 1 }}</td>
                <td>
                  <div class="patient-cell">
                    <div class="avatar">{{ getInitials(patient.full_name) }}</div>
                    <div class="info">
                      <span class="name">{{ patient.full_name }}</span>
                      <span class="email">{{ patient.email }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <span :class="['status-badge', getPatientStatus(patient)]">
                    {{ getPatientStatusText(patient) }}
                  </span>
                </td>
                <td>
                  <div class="progress-cell">
                    <div class="progress-bar">
                      <div class="fill" :style="{ width: `${patient.progress || 0}%` }"></div>
                    </div>
                    <span class="percent">{{ patient.progress || 0 }}%</span>
                  </div>
                </td>
                <td class="text-muted">
                  {{ getLastActive(patient) }}
                </td>
                <td>
                  <button class="icon-btn" title="Xem chi tiết">
                    <ChevronRight :size="20" />
                  </button>
                </td>
              </tr>
              <tr v-if="filteredPatients.length === 0">
                <td colspan="6" class="empty-table-row">Không tìm thấy bệnh nhân</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Right: Detail Panel -->
      <div class="content-card detail-section" v-if="selectedPatient">
        <div class="detail-header">
          <div class="patient-profile">
            <div class="large-avatar">{{ getInitials(selectedPatient.full_name) }}</div>
            <div>
              <h2 class="detail-name">{{ selectedPatient.full_name }}</h2>
              <p class="detail-email">{{ selectedPatient.email }}</p>
            </div>
          </div>
          <div class="detail-actions">
            <button class="action-icon-btn"><MessageSquare :size="20" /></button>
            <button class="action-icon-btn"><Phone :size="20" /></button>
          </div>
        </div>

        <div class="detail-tabs">
          <button
            v-for="tab in tabs"
            :key="tab"
            @click="activeTab = tab"
            :class="['tab-item', { active: activeTab === tab }]"
          >
            {{ getTabLabel(tab) }}
          </button>
        </div>

        <div class="detail-content custom-scrollbar">
          <!-- Overview Tab: real multi-chart dashboard -->
          <div v-if="activeTab === 'overview'" class="tab-pane fade-in">
            <!-- Quick Stats Row -->
            <div class="overview-stats-row">
              <div class="ov-stat">
                <span class="ov-stat-val">{{ patientCharts.totalReps || 0 }}</span>
                <span class="ov-stat-label">Tổng reps</span>
              </div>
              <div class="ov-stat">
                <span class="ov-stat-val">{{ patientCharts.totalSessions || 0 }}</span>
                <span class="ov-stat-label">Buổi tập</span>
              </div>
              <div class="ov-stat">
                <span class="ov-stat-val">{{ exerciseDistribution.length || 0 }}</span>
                <span class="ov-stat-label">Bài tập khác nhau</span>
              </div>
              <div class="ov-stat">
                <span class="ov-stat-val">{{ patientCharts.activeDays || 0 }}</span>
                <span class="ov-stat-label">Ngày tập</span>
              </div>
            </div>

            <!-- Weekly Activity Bar Chart -->
            <div class="chart-box">
              <h4 class="chart-title">
                <BarChart2 :size="16" /> Hoạt động tuần này (Số reps theo ngày)
              </h4>
              <div class="bar-chart">
                <div v-for="day in weeklyActivity" :key="day.date" class="bar-col">
                  <div class="bar-wrap">
                    <div
                      class="bar-fill"
                      :style="{ height: `${day.heightPct}%` }"
                      :title="`${day.reps} reps`"
                    ></div>
                  </div>
                  <span class="bar-label">{{ day.label }}</span>
                  <span class="bar-val">{{ day.reps }}</span>
                </div>
              </div>
            </div>

            <!-- Exercise Distribution -->
            <div class="chart-box" v-if="exerciseDistribution.length">
              <h4 class="chart-title"><PieChart :size="16" /> Phân bố bài tập</h4>
              <div class="exercise-dist">
                <div
                  v-for="ex in exerciseDistribution"
                  :key="ex.exercise_type"
                  class="ex-dist-item"
                >
                  <div class="ex-dist-bar-wrap">
                    <div
                      class="ex-dist-bar"
                      :style="{ width: `${ex.pct}%`, background: ex.color }"
                    ></div>
                  </div>
                  <div class="ex-dist-info">
                    <span class="ex-name">{{ ex.exercise_type }}</span>
                    <span class="ex-count">{{ ex.count }} lần ({{ ex.pct }}%)</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Recent Sessions -->
            <div class="recent-activity-list">
              <h4>Buổi tập gần đây</h4>
              <div v-if="recentSessions.length === 0" class="empty-state">
                Chưa có dữ liệu tập luyện
              </div>
              <div
                v-for="session in recentSessions"
                :key="session.session_id"
                class="activity-item"
              >
                <div class="activity-icon" :class="getSessionQuality(session)">
                  <Activity :size="16" />
                </div>
                <div class="activity-details">
                  <span class="act-name">{{ session.exercise_type || 'Buổi tập tổng hợp' }}</span>
                  <span class="act-time">{{ formatDate(session.start_time) }}</span>
                </div>
                <div class="activity-score">{{ session.total_reps_completed || 0 }} reps</div>
              </div>
            </div>
          </div>

          <!-- History Tab -->
          <div v-else-if="activeTab === 'history'" class="tab-pane fade-in">
            <h4>Lịch sử tập luyện</h4>
            <div v-if="logs.length === 0" class="empty-state">Chưa có lịch sử tập luyện</div>
            <div v-else class="history-list">
              <div v-for="(log, idx) in logs.slice(0, 10)" :key="idx" class="history-item">
                <div class="history-icon">
                  <Activity :size="16" />
                </div>
                <div class="history-content">
                  <span class="history-exercise">{{ log.exercise_type }}</span>
                  <span class="history-date">{{ formatDate(log.completed_at) }}</span>
                </div>
                <div class="history-stats">
                  <span class="reps">{{ log.rep_number }} reps</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Notes Tab -->
          <div v-else-if="activeTab === 'notes'" class="tab-pane fade-in">
            <h4>Ghi chú bệnh nhân</h4>
            <div v-if="patientNotes.length === 0" class="empty-state">Chưa có ghi chú nào</div>
            <div v-else class="notes-list">
              <div v-for="note in patientNotes" :key="note.note_id" class="note-item">
                <div class="note-header">
                  <span class="note-title">{{ note.title }}</span>
                  <span class="note-date">{{ formatDate(note.created_at) }}</span>
                </div>
                <p class="note-content">{{ note.content }}</p>
                <span class="note-author">{{ note.doctor_name }}</span>
              </div>
            </div>
          </div>

          <!-- AI Chat Tab (New) -->
          <div v-else-if="activeTab === 'ai_chat'" class="tab-pane fade-in h-[600px]">
            <AIChatbox :initialPatientId="selectedPatientId" />
          </div>
        </div>
      </div>

      <!-- Empty State for Right Panel -->
      <div v-else class="content-card empty-detail">
        <div class="empty-content">
          <div class="illustration">
            <Users :size="64" />
          </div>
          <h3>Chọn một bệnh nhân</h3>
          <p>
            Chọn bệnh nhân từ danh sách bên trái để xem chi tiết hồ sơ, lịch sử tập luyện và phân
            tích.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import {
  Users,
  Activity,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  AlertCircle,
  Plus,
  Search,
  ChevronRight,
  MessageSquare,
  Phone,
  BarChart2,
  PieChart,
} from 'lucide-vue-next'
import AIChatbox from './AIChatbox.vue'
import { API_BASE_URL } from '../config'

// State
const API_BASE = API_BASE_URL
const PATIENT_DATA_CACHE_TTL_MS = 60 * 1000
const patients = ref([])
const selectedPatientId = ref(null)
const selectedPatient = ref(null)
const sessions = ref([])
const logs = ref([])
const searchQuery = ref('')
const activeTab = ref('overview')
const tabs = ['overview', 'history', 'notes', 'ai_chat']
const stats = ref({
  totalPatients: 0,
})
const trends = ref({
  patientTrend: 0,
  activityTrend: 0,
  newAlerts: 0,
})
const patientNotes = ref([])
const currentUser = ref({ full_name: 'Bác sĩ' })
const patientDataCache = new Map()

// Patient charts data
const patientCharts = ref({
  totalReps: 0,
  totalSessions: 0,
  activeDays: 0,
  weeklyActivity: [],
  muscleFocus: [],
})

// Computed
const currentDate = new Date().toLocaleDateString('vi-VN', {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric',
})

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      currentUser.value = JSON.parse(userStr)
    } catch (e) {
      console.error('Error parsing user data', e)
    }
  }
  loadPatients()
})

const filteredPatients = computed(() => {
  if (!searchQuery.value) return patients.value
  const query = searchQuery.value.toLowerCase()
  return patients.value.filter(
    (p) => p.full_name.toLowerCase().includes(query) || p.email.toLowerCase().includes(query),
  )
})

const activePatientsCount = ref(0)
const criticalPatientsCount = ref(0)
const inactivePatientsCount = ref(0)

const recentSessions = computed(() => sessions.value.slice(0, 5))

// Weekly activity derived from chart data
const weeklyActivity = computed(() => {
  const data = patientCharts.value.weeklyActivity || []
  if (!data.length) return []
  const maxReps = Math.max(...data.map((d) => d.reps), 1)
  const dayNames = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']
  return data.map((d) => ({
    date: d.date,
    reps: d.reps,
    label: dayNames[new Date(d.date).getDay()],
    heightPct: Math.round((d.reps / maxReps) * 100),
  }))
})

// Exercise distribution with color
const CHART_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
const exerciseDistribution = computed(() => {
  const data = patientCharts.value.muscleFocus || []
  const total = data.reduce((a, b) => a + b.count, 0) || 1
  return data.map((d, i) => ({
    ...d,
    pct: Math.round((d.count / total) * 100),
    color: CHART_COLORS[i % CHART_COLORS.length],
  }))
})

// Methods
const getInitials = (name) =>
  name
    ? name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()
    : '??'

const getTabLabel = (tab) => {
  const map = { overview: 'Tổng quan', history: 'Lịch sử', notes: 'Ghi chú', ai_chat: 'Trợ lý AI' }
  return map[tab] || tab
}

const getPatientStatus = (patient) => {
  return patient.status || 'active'
}

const getPatientStatusText = (patient) => {
  const status = getPatientStatus(patient)
  if (status === 'active') return 'Hoạt động'
  if (status === 'needs_attention') return 'Cần chú ý'
  return 'Không hoạt động'
}

const getLastActive = (patient) => {
  if (!patient.last_active_at) return 'Chưa hoạt động'
  const lastActive = new Date(patient.last_active_at)
  const now = new Date()
  const diffMs = now - lastActive
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 60) return `${diffMins} phút trước`
  if (diffHours < 24) return `${diffHours} giờ trước`
  return `${diffDays} ngày trước`
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getSessionQuality = (session) => {
  return session.total_errors_detected > 2 ? 'poor' : 'good'
}

const selectPatient = async (patient) => {
  selectedPatientId.value = patient.patient_id
  selectedPatient.value = patient
  activeTab.value = 'overview'
  await loadPatientData(patient.patient_id)
}

const loadPatients = async () => {
  try {
    const token = localStorage.getItem('token')

    const res = await fetch(`${API_BASE}/patients-with-status`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) {
      patients.value = await res.json()
      stats.value.totalPatients = patients.value.length
    }

    const summaryRes = await fetch(`${API_BASE}/dashboard/summary`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (summaryRes.ok) {
      const summary = await summaryRes.json()
      activePatientsCount.value = summary.active_count
      criticalPatientsCount.value = summary.needs_attention_count
      inactivePatientsCount.value = summary.inactive_count || 0
      trends.value.patientTrend = summary.patient_trend || 0
      trends.value.activityTrend = summary.activity_trend || 0
      trends.value.newAlerts = summary.new_alerts || 0
    }
  } catch (e) {
    console.error(e)
  }
}

const loadPatientData = async (id) => {
  const cached = patientDataCache.get(id)
  const isFreshCache = cached && Date.now() - cached.timestamp < PATIENT_DATA_CACHE_TTL_MS

  if (isFreshCache) {
    sessions.value = cached.sessions
    logs.value = cached.logs
    patientNotes.value = cached.notes
    patientCharts.value = cached.charts
    return
  }

  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE}/patient/overview/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })

    if (!res.ok) return

    const payload = await res.json()
    sessions.value = payload.sessions || []
    logs.value = payload.logs || []
    patientNotes.value = payload.notes || []

    const chartsData = payload.charts || {}
    patientCharts.value.weeklyActivity = chartsData.weekly_activity || []
    patientCharts.value.muscleFocus = chartsData.muscle_focus || []

    const st = payload.overall_stats || {}
    patientCharts.value.totalReps = st.total_reps || 0
    patientCharts.value.totalSessions = st.total_sessions || 0
    patientCharts.value.activeDays = st.total_days || 0

    patientDataCache.set(id, {
      timestamp: Date.now(),
      sessions: [...sessions.value],
      logs: [...logs.value],
      notes: [...patientNotes.value],
      charts: {
        ...patientCharts.value,
        weeklyActivity: [...patientCharts.value.weeklyActivity],
        muscleFocus: [...patientCharts.value.muscleFocus],
      },
    })
  } catch (e) {
    console.error(e)
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.welcome-text {
  font-size: 28px;
  font-weight: 800;
  color: #1e293b;
  margin: 0;
}

.text-primary {
  color: #6366f1;
}

.date-text {
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.action-btn.primary {
  background: #6366f1;
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.action-btn.primary:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  position: relative;
  z-index: 2;
}

.stat-card.blue .stat-icon {
  background: #3b82f6;
}
.stat-card.green .stat-icon {
  background: #10b981;
}
.stat-card.orange .stat-icon {
  background: #f59e0b;
}
.stat-card.purple .stat-icon {
  background: #8b5cf6;
}

.stat-info {
  position: relative;
  z-index: 2;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
}

.stat-value {
  font-size: 32px;
  font-weight: 800;
  color: #1e293b;
  margin: 4px 0;
}

.stat-trend {
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-trend.positive {
  color: #10b981;
}
.stat-trend.negative {
  color: #ef4444;
}

.stat-bg-icon {
  position: absolute;
  right: -20px;
  bottom: -20px;
  opacity: 0.05;
  transform: rotate(-15deg);
  z-index: 1;
  color: currentColor;
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 24px;
  flex: 1;
  min-height: 0;
}

@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}

.content-card {
  background: white;
  border-radius: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #f1f5f9;
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f8fafc;
  padding: 8px 12px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  gap: 8px;
  color: #64748b;
}

.search-box input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
  width: 200px;
}

/* Table Styles */
.table-container {
  flex: 1;
  overflow-y: auto;
}

.empty-table-row {
  text-align: center;
  color: #94a3b8;
  padding: 32px;
  font-size: 14px;
}

.patient-table {
  width: 100%;
  border-collapse: collapse;
}

.patient-table th {
  text-align: left;
  padding: 14px 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: #94a3b8;
  background: #f8fafc;
  position: sticky;
  top: 0;
  z-index: 10;
}

.th-num {
  width: 42px;
  text-align: center !important;
}

.patient-table td {
  padding: 14px 20px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 14px;
  color: #334155;
}

.td-num {
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  color: #94a3b8;
  background: #f8fafc;
}

.patient-table tr:hover {
  background: #f8fafc;
  cursor: pointer;
}

.patient-table tr.active-row {
  background: #eff6ff;
}

.patient-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  background: #e0e7ff;
  color: #4f46e5;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}

.info {
  display: flex;
  flex-direction: column;
}

.name {
  font-weight: 600;
  color: #0f172a;
}
.email {
  font-size: 12px;
  color: #64748b;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.active {
  background: #dcfce7;
  color: #166534;
}
.status-badge.needs_attention {
  background: #fef3c7;
  color: #92400e;
}
.status-badge.inactive {
  background: #f1f5f9;
  color: #64748b;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  width: 80px;
  height: 6px;
  background: #f1f5f9;
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar .fill {
  height: 100%;
  background: #10b981;
  border-radius: 10px;
}

.percent {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
}

.icon-btn {
  background: transparent;
  border: none;
  color: #cbd5e1;
  cursor: pointer;
  padding: 4px;
  border-radius: 8px;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: #e0e7ff;
  color: #4f46e5;
}

/* Detail Section */
.detail-section {
  background: white;
  display: flex;
  flex-direction: column;
}

.detail-header {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: #f8fafc;
}

.patient-profile {
  display: flex;
  gap: 16px;
  align-items: center;
}

.large-avatar {
  width: 64px;
  height: 64px;
  background: #6366f1;
  color: white;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.25);
}

.detail-name {
  font-size: 20px;
  font-weight: 800;
  color: #1e293b;
  margin: 0;
}

.detail-email {
  color: #64748b;
  margin-top: 4px;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.action-icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.action-icon-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
  background: #eef2ff;
}

.detail-tabs {
  display: flex;
  padding: 0 24px;
  border-bottom: 1px solid #f1f5f9;
  gap: 24px;
}

.tab-item {
  padding: 12px 0;
  background: transparent;
  border: none;
  font-weight: 600;
  color: #94a3b8;
  cursor: pointer;
  position: relative;
  font-size: 14px;
}

.tab-item.active {
  color: #6366f1;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #6366f1;
}

.detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* =========== OVERVIEW STATS =========== */
.overview-stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 16px;
}

.ov-stat {
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px 10px;
  text-align: center;
  border: 1px solid #f1f5f9;
}

.ov-stat-val {
  display: block;
  font-size: 22px;
  font-weight: 800;
  color: #1e293b;
}

.ov-stat-label {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 600;
  margin-top: 2px;
  display: block;
}

/* =========== CHART BOXES =========== */
.chart-box {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #f1f5f9;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 7px;
  margin: 0 0 12px 0;
  font-size: 13px;
  font-weight: 700;
  color: #475569;
}

/* Bar Chart */
.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 90px;
  padding: 0 4px;
}

.bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  height: 100%;
}

.bar-wrap {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.bar-fill {
  width: 70%;
  min-height: 4px;
  background: #6366f1;
  border-radius: 4px 4px 0 0;
  transition: height 0.4s ease;
}

.bar-label {
  font-size: 10px;
  font-weight: 700;
  color: #94a3b8;
}

.bar-val {
  font-size: 9px;
  color: #6366f1;
  font-weight: 700;
}

/* Exercise distribution */
.exercise-dist {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ex-dist-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ex-dist-bar-wrap {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.ex-dist-bar {
  height: 100%;
  border-radius: 10px;
  transition: width 0.4s ease;
}

.ex-dist-info {
  min-width: 120px;
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.ex-name {
  font-size: 12px;
  font-weight: 600;
  color: #334155;
  text-transform: capitalize;
}

.ex-count {
  font-size: 11px;
  color: #64748b;
}

/* Recent activity */
.recent-activity-list h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 10px;
  transition: background 0.2s;
}

.activity-item:hover {
  background: #f8fafc;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.activity-icon.good {
  background: #dcfce7;
  color: #166534;
}
.activity-icon.poor {
  background: #fee2e2;
  color: #991b1b;
}

.activity-details {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.act-name {
  font-weight: 600;
  color: #334155;
  font-size: 13px;
}
.act-time {
  font-size: 11px;
  color: #94a3b8;
}

.activity-score {
  font-weight: 700;
  color: #6366f1;
  font-size: 13px;
}

/* History / Notes */
.history-list,
.notes-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid #f1f5f9;
}

.history-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #e0e7ff;
  color: #4f46e5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.history-exercise {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  text-transform: capitalize;
}

.history-date {
  font-size: 11px;
  color: #94a3b8;
}

.history-stats {
  display: flex;
  gap: 8px;
  align-items: center;
}

.reps {
  font-size: 12px;
  font-weight: 700;
  color: #6366f1;
}

.note-item {
  padding: 12px;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  margin-bottom: 8px;
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.note-title {
  font-weight: 700;
  color: #1e293b;
  font-size: 14px;
}

.note-date {
  font-size: 11px;
  color: #94a3b8;
}

.note-content {
  font-size: 13px;
  color: #475569;
  margin: 0 0 6px 0;
}

.note-author {
  font-size: 11px;
  color: #6366f1;
  font-weight: 700;
}

/* Empty states */
.empty-state {
  text-align: center;
  color: #94a3b8;
  padding: 24px;
  font-size: 14px;
}

.empty-detail {
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px;
  color: #94a3b8;
}

.illustration {
  width: 120px;
  height: 120px;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  color: #cbd5e1;
}

.text-muted {
  color: #94a3b8;
  font-size: 13px;
}

.fade-in {
  animation: fadeIn 0.25s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

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
</style>
