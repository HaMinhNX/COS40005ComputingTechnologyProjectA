<template>
  <div class="dashboard-container">
    <!-- Welcome Header -->
    <header class="dashboard-header">
      <div class="header-left">
        <h1 class="welcome-text">
          Xin chào, <span class="text-gradient">{{ currentUser.full_name }}</span> 👋
        </h1>
        <p class="date-text">{{ currentDate }} • Chúc bác sĩ một ngày làm việc hiệu quả!</p>
      </div>
      <div class="header-right">
        <button class="action-btn primary">
          <Plus :size="20" />
          <span>Thêm bệnh nhân</span>
        </button>
        <!-- <button class="action-btn secondary">
          <Bell :size="20" />
          <span class="notification-badge">3</span>
        </button> -->
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
          <span class="stat-trend positive">
            <TrendingUp :size="14" /> +12% tháng này
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
          <span class="stat-trend positive">
            <TrendingUp :size="14" /> +5% hôm nay
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
            <AlertCircle :size="14" /> 2 cảnh báo mới
          </span>
        </div>
        <div class="stat-bg-icon"><AlertTriangle :size="100" /></div>
      </div>

      <div class="stat-card purple">
        <div class="stat-icon">
          <CheckCircle :size="24" />
        </div>
        <div class="stat-info">
          <span class="stat-label">Điểm trung bình</span>
          <h3 class="stat-value">{{ stats.avgFormScore }}%</h3>
          <div class="progress-mini">
            <div class="progress-fill" :style="{ width: `${stats.avgFormScore}%` }"></div>
          </div>
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
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Tìm kiếm tên, email..."
            />
          </div>
        </div>

        <div class="table-container custom-scrollbar">
          <table class="patient-table">
            <thead>
              <tr>
                <th>Bệnh nhân</th>
                <th>Trạng thái</th>
                <th>Tiến độ</th>
                <th>Hoạt động cuối</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="patient in filteredPatients"
                :key="patient.patient_id"
                @click="selectPatient(patient)"
                :class="{ 'active-row': selectedPatientId === patient.patient_id }"
              >
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
                      <div class="fill" :style="{ width: '75%' }"></div> <!-- Mock data -->
                    </div>
                    <span class="percent">75%</span>
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
            </tbody>
          </table>
        </div>
      </div>

      <!-- Right: Detail Panel (Slide over or embedded) -->
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
          <!-- Overview Tab -->
          <div v-if="activeTab === 'overview'" class="tab-pane fade-in">
            <div class="chart-box">
              <h4>Biểu đồ phong độ</h4>
              <div ref="progressChart" class="chart-canvas"></div>
            </div>

            <div class="recent-activity-list">
              <h4>Hoạt động gần đây</h4>
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
                  <span class="act-name">{{ session.exercise_type }}</span>
                  <span class="act-time">{{ formatDate(session.start_time) }}</span>
                </div>
                <div class="activity-score">
                  {{ session.total_reps_completed }} reps
                </div>
              </div>
            </div>
          </div>

          <!-- Other tabs placeholders -->
          <div v-else class="tab-pane fade-in">
            <p class="text-center text-muted mt-10">Đang cập nhật tính năng...</p>
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
          <p>Chọn bệnh nhân từ danh sách bên trái để xem chi tiết hồ sơ, lịch sử tập luyện và phân tích.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import * as d3 from 'd3';
import {
  Users, Activity, AlertTriangle, CheckCircle, TrendingUp, AlertCircle,
  Plus, Bell, Search, ChevronRight, MessageSquare, Phone, Calendar, Clock
} from 'lucide-vue-next';
import { API_BASE_URL } from '../config';

// State
const API_BASE = API_BASE_URL;
const patients = ref([]);
const selectedPatientId = ref(null);
const selectedPatient = ref(null);
const sessions = ref([]);
const logs = ref([]);
const searchQuery = ref('');
const activeTab = ref('overview');
const tabs = ['overview', 'history', 'notes'];
const stats = ref({
  totalPatients: 0,
  avgFormScore: 0,
  totalReps: 0
});
const currentUser = ref({ full_name: 'Bác sĩ' });

// Refs for charts
const progressChart = ref(null);

// Computed
const currentDate = new Date().toLocaleDateString('vi-VN', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
});

onMounted(() => {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      currentUser.value = JSON.parse(userStr);
    } catch (e) {
      console.error("Error parsing user data", e);
    }
  }
  loadPatients();
});

const filteredPatients = computed(() => {
  if (!searchQuery.value) return patients.value;
  const query = searchQuery.value.toLowerCase();
  return patients.value.filter(p =>
    p.full_name.toLowerCase().includes(query) ||
    p.email.toLowerCase().includes(query)
  );
});

const activePatientsCount = computed(() => {
  // Mock logic: 80% of patients are active
  return Math.floor(patients.value.length * 0.8);
});

const criticalPatientsCount = computed(() => {
  // Mock logic: Random small number
  return Math.floor(patients.value.length * 0.1);
});

const recentSessions = computed(() => sessions.value.slice(0, 5));

// Methods
const getInitials = (name) => name ? name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() : '??';

const getTabLabel = (tab) => {
  const map = { overview: 'Tổng quan', history: 'Lịch sử', notes: 'Ghi chú' };
  return map[tab] || tab;
};

const getPatientStatus = (patient) => {
  // Mock status logic
  const statuses = ['active', 'active', 'warning', 'active'];
  return statuses[patient.patient_id % statuses.length] || 'active';
};

const getPatientStatusText = (patient) => {
  const status = getPatientStatus(patient);
  return status === 'active' ? 'Hoạt động' : 'Cần chú ý';
};

const getLastActive = (patient) => {
  return '2 giờ trước'; // Mock
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
};

const getSessionQuality = (session) => {
  return session.total_errors_detected > 2 ? 'poor' : 'good';
};

const selectPatient = async (patient) => {
  selectedPatientId.value = patient.patient_id;
  selectedPatient.value = patient;
  await loadPatientData(patient.patient_id);
};

const loadPatients = async () => {
  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE}/patients`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) {
      patients.value = await res.json();
      stats.value.totalPatients = patients.value.length;
    }
  } catch (e) {
    console.error(e);
  }
};

const loadPatientData = async (id) => {
  try {
    const token = localStorage.getItem('token');
    const [sessRes, logsRes] = await Promise.all([
      fetch(`${API_BASE}/patient-sessions/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      }),
      fetch(`${API_BASE}/patient-logs/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
    ]);

    if (sessRes.ok) sessions.value = await sessRes.json();
    if (logsRes.ok) logs.value = await logsRes.json();

    // Update stats
    if (logs.value.length) {
      const avg = logs.value.reduce((a, b) => a + b.form_score, 0) / logs.value.length;
      stats.value.avgFormScore = Math.round(avg);
    }

    nextTick(() => drawChart());
  } catch (e) {
    console.error(e);
  }
};

const drawChart = () => {
  if (!progressChart.value || !logs.value.length) return;

  const container = d3.select(progressChart.value);
  container.selectAll('*').remove();

  const width = progressChart.value.clientWidth;
  const height = progressChart.value.clientHeight;
  const margin = { top: 10, right: 10, bottom: 20, left: 30 };

  const svg = container.append('svg')
    .attr('width', width)
    .attr('height', height);

  const data = logs.value.slice(0, 10).reverse();

  const x = d3.scaleLinear()
    .domain([0, data.length - 1])
    .range([margin.left, width - margin.right]);

  const y = d3.scaleLinear()
    .domain([0, 100])
    .range([height - margin.bottom, margin.top]);

  // Gradient
  const gradient = svg.append("defs")
    .append("linearGradient")
    .attr("id", "line-gradient")
    .attr("gradientUnits", "userSpaceOnUse")
    .attr("x1", 0).attr("y1", y(0))
    .attr("x2", 0).attr("y2", y(100));

  gradient.append("stop").attr("offset", "0%").attr("stop-color", "#6366f1");
  gradient.append("stop").attr("offset", "100%").attr("stop-color", "#a855f7");

  const line = d3.line()
    .x((d, i) => x(i))
    .y(d => y(d.form_score))
    .curve(d3.curveCatmullRom);

  svg.append('path')
    .datum(data)
    .attr('fill', 'none')
    .attr('stroke', 'url(#line-gradient)')
    .attr('stroke-width', 3)
    .attr('d', line);

  // Dots
  svg.selectAll('circle')
    .data(data)
    .enter()
    .append('circle')
    .attr('cx', (d, i) => x(i))
    .attr('cy', d => y(d.form_score))
    .attr('r', 4)
    .attr('fill', 'white')
    .attr('stroke', '#6366f1')
    .attr('stroke-width', 2);
};
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

.text-gradient {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
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

.action-btn.secondary {
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
  position: relative;
}

.action-btn.secondary:hover {
  background: #f8fafc;
  color: #6366f1;
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ef4444;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  border: 2px solid white;
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

.stat-card.blue .stat-icon { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.stat-card.green .stat-icon { background: linear-gradient(135deg, #10b981, #059669); }
.stat-card.orange .stat-icon { background: linear-gradient(135deg, #f59e0b, #d97706); }
.stat-card.purple .stat-icon { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }

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

.stat-trend.positive { color: #10b981; }
.stat-trend.negative { color: #ef4444; }

.stat-bg-icon {
  position: absolute;
  right: -20px;
  bottom: -20px;
  opacity: 0.05;
  transform: rotate(-15deg);
  z-index: 1;
  color: currentColor;
}

.progress-mini {
  height: 6px;
  background: #f1f5f9;
  border-radius: 10px;
  overflow: hidden;
  margin-top: 8px;
}

.progress-mini .progress-fill {
  height: 100%;
  background: #8b5cf6;
  border-radius: 10px;
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

.patient-table {
  width: 100%;
  border-collapse: collapse;
}

.patient-table th {
  text-align: left;
  padding: 16px 24px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: #94a3b8;
  background: #f8fafc;
  position: sticky;
  top: 0;
  z-index: 10;
}

.patient-table td {
  padding: 16px 24px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 14px;
  color: #334155;
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
}

.info {
  display: flex;
  flex-direction: column;
}

.name { font-weight: 600; color: #0f172a; }
.email { font-size: 12px; color: #64748b; }

.status-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.active { background: #dcfce7; color: #166534; }
.status-badge.warning { background: #fef3c7; color: #92400e; }

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

.percent { font-size: 12px; font-weight: 600; color: #64748b; }

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
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
}

.patient-profile {
  display: flex;
  gap: 16px;
  align-items: center;
}

.large-avatar {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
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
  padding: 24px;
}

.chart-box {
  background: #f8fafc;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid #f1f5f9;
}

.chart-box h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #64748b;
}

.chart-canvas {
  height: 200px;
  width: 100%;
}

.recent-activity-list h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 12px;
  transition: background 0.2s;
}

.activity-item:hover {
  background: #f8fafc;
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.activity-icon.good { background: #dcfce7; color: #166534; }
.activity-icon.poor { background: #fee2e2; color: #991b1b; }

.activity-details {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.act-name { font-weight: 600; color: #334155; font-size: 14px; }
.act-time { font-size: 12px; color: #94a3b8; }

.activity-score {
  font-weight: 700;
  color: #6366f1;
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
  margin-bottom: 24px;
  color: #cbd5e1;
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
