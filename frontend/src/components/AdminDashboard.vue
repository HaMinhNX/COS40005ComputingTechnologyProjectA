<template>
  <div class="admin-page" data-isolated-ui>
    <header class="admin-header">
      <div>
        <h1>Admin Dashboard</h1>
        <p>Review and approve doctor registration requests.</p>
      </div>
      <div class="header-actions">
        <button class="secondary-btn" @click="fetchPending" :disabled="loading">
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
        <button class="danger-btn" @click="logout">Logout</button>
      </div>
    </header>

    <div class="tab-actions">
      <button :class="['tab-btn', activeTab === 'pending' ? 'tab-active' : '']" @click="switchTab('pending')">
        Pending Requests
      </button>
      <button :class="['tab-btn', activeTab === 'history' ? 'tab-active' : '']" @click="switchTab('history')">
        History
      </button>
    </div>

    <div v-if="activeTab === 'history'" class="filters">
      <select v-model="historyStatusFilter" class="filter-input">
        <option value="all">All statuses</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
      </select>
      <input v-model="historyFromDate" type="date" class="filter-input" />
      <input v-model="historyToDate" type="date" class="filter-input" />
      <button class="clear-filter-btn" @click="clearHistoryFilters">Clear</button>
    </div>

    <p v-if="message" class="message">{{ message }}</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="!loading && currentList.length === 0" class="empty-state">
      {{ activeTab === 'pending' ? 'No pending doctor registrations.' : 'No history yet.' }}
    </div>

    <div v-else class="cards">
      <article v-for="doctor in currentList" :key="doctor.doctor_id" class="card">
        <div class="card-grid">
          <div><strong>Name:</strong> {{ doctor.full_name || doctor.username }}</div>
          <div><strong>Email:</strong> {{ doctor.email }}</div>
          <div><strong>Username:</strong> {{ doctor.username }}</div>
          <div><strong>Submitted:</strong> {{ formatDate(doctor.submitted_at) }}</div>
          <div class="full-row">
            <strong>Certificate:</strong>
            <a :href="doctor.certificate_url" target="_blank" rel="noopener noreferrer">View source</a>
          </div>
          <div v-if="isLikelyImage(doctor.certificate_url) && !imageLoadErrors[doctor.doctor_id]" class="full-row cert-preview-wrap">
            <img
              :src="doctor.certificate_url"
              alt="Doctor certificate preview"
              class="cert-preview"
              @error="markImageError(doctor.doctor_id)"
            />
          </div>
          <div v-if="activeTab === 'history'" class="full-row">
            <strong>Reviewed at:</strong> {{ formatDate(doctor.reviewed_at) }}
            <span v-if="doctor.reviewed_by_name"> | <strong>By:</strong> {{ doctor.reviewed_by_name }}</span>
          </div>
          <div v-if="activeTab === 'history' && doctor.rejection_reason" class="full-row">
            <strong>Rejection reason:</strong> {{ doctor.rejection_reason }}
          </div>
        </div>

        <div v-if="activeTab === 'pending'" class="actions">
          <input
            v-model="rejectionReasons[doctor.doctor_id]"
            type="text"
            class="reason-input"
            placeholder="Optional rejection reason"
          />
          <button class="reject-btn" @click="rejectDoctor(doctor.doctor_id)" :disabled="actionLoading">
            Reject
          </button>
          <button class="approve-btn" @click="approveDoctor(doctor.doctor_id)" :disabled="actionLoading">
            Approve
          </button>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { API_BASE_URL } from '../config'

const pendingDoctors = ref([])
const historyDoctors = ref([])
const loading = ref(false)
const actionLoading = ref(false)
const error = ref('')
const message = ref('')
const rejectionReasons = ref({})
const imageLoadErrors = ref({})
const activeTab = ref('pending')
const historyStatusFilter = ref('all')
const historyFromDate = ref('')
const historyToDate = ref('')

const authHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
}

const fetchPending = async () => {
  loading.value = true
  error.value = ''
  message.value = ''
  try {
    const res = await fetch(`${API_BASE_URL}/admin/doctor-registrations/pending`, {
      headers: authHeaders(),
    })
    const data = await res.json()
    if (!res.ok) {
      throw new Error(data.detail || 'Failed to load pending requests')
    }
    pendingDoctors.value = data
  } catch (err) {
    error.value = err.message || 'Failed to load pending requests'
  } finally {
    loading.value = false
  }
}

const fetchHistory = async () => {
  loading.value = true
  error.value = ''
  message.value = ''
  try {
    const res = await fetch(`${API_BASE_URL}/admin/doctor-registrations/history`, {
      headers: authHeaders(),
    })
    const data = await res.json()
    if (!res.ok) {
      throw new Error(data.detail || 'Failed to load history')
    }
    historyDoctors.value = data
  } catch (err) {
    error.value = err.message || 'Failed to load history'
  } finally {
    loading.value = false
  }
}

const approveDoctor = async (doctorId) => {
  actionLoading.value = true
  error.value = ''
  message.value = ''
  try {
    const res = await fetch(`${API_BASE_URL}/admin/doctor-registrations/${doctorId}/approve`, {
      method: 'POST',
      headers: authHeaders(),
    })
    const data = await res.json()
    if (!res.ok) {
      throw new Error(data.detail || 'Failed to approve doctor')
    }
    message.value = 'Doctor approved successfully.'
    await fetchPending()
    if (activeTab.value === 'history') {
      await fetchHistory()
    }
  } catch (err) {
    error.value = err.message || 'Failed to approve doctor'
  } finally {
    actionLoading.value = false
  }
}

const rejectDoctor = async (doctorId) => {
  actionLoading.value = true
  error.value = ''
  message.value = ''
  try {
    const res = await fetch(`${API_BASE_URL}/admin/doctor-registrations/${doctorId}/reject`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({
        rejection_reason: rejectionReasons.value[doctorId] || null,
      }),
    })
    const data = await res.json()
    if (!res.ok) {
      throw new Error(data.detail || 'Failed to reject doctor')
    }
    message.value = 'Doctor rejected successfully.'
    await fetchPending()
    if (activeTab.value === 'history') {
      await fetchHistory()
    }
  } catch (err) {
    error.value = err.message || 'Failed to reject doctor'
  } finally {
    actionLoading.value = false
  }
}

const formatDate = (value) => {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}

const isLikelyImage = (url) => {
  if (!url) return false
  const lower = url.toLowerCase()
  return (
    lower.includes('/image/upload/') ||
    lower.endsWith('.jpg') ||
    lower.endsWith('.jpeg') ||
    lower.endsWith('.png') ||
    lower.endsWith('.webp')
  )
}

const markImageError = (doctorId) => {
  imageLoadErrors.value[doctorId] = true
}

const switchTab = async (tab) => {
  activeTab.value = tab
  if (tab === 'pending') {
    await fetchPending()
  } else {
    await fetchHistory()
  }
}

const filteredHistoryList = computed(() => {
  return historyDoctors.value.filter((item) => {
    const statusOk =
      historyStatusFilter.value === 'all' || item.approval_status === historyStatusFilter.value

    const reviewedAt = item.reviewed_at ? new Date(item.reviewed_at) : null
    const fromOk =
      !historyFromDate.value ||
      (reviewedAt && reviewedAt >= new Date(`${historyFromDate.value}T00:00:00`))
    const toOk =
      !historyToDate.value ||
      (reviewedAt && reviewedAt <= new Date(`${historyToDate.value}T23:59:59`))

    return statusOk && fromOk && toOk
  })
})

const currentList = computed(() => (activeTab.value === 'pending' ? pendingDoctors.value : filteredHistoryList.value))

const clearHistoryFilters = () => {
  historyStatusFilter.value = 'all'
  historyFromDate.value = ''
  historyToDate.value = ''
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  window.location.href = '/login'
}

onMounted(fetchPending)
</script>

<style scoped>
.admin-page { max-width: 1000px; margin: 0 auto; padding: 24px; }
.admin-header { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 16px; }
.admin-header h1 { margin: 0; font-size: 28px; }
.admin-header p { margin: 4px 0 0; color: #555; }
.header-actions { display: flex; gap: 10px; }
.tab-actions { display: flex; gap: 10px; margin-bottom: 14px; }
.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
  align-items: center;
  flex-wrap: wrap;
}
.filter-input {
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 8px 10px;
  background: #fff;
}
.clear-filter-btn {
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 8px 12px;
  background: #f8fafc;
  color: #334155;
  font-weight: 600;
  cursor: pointer;
}
.tab-btn {
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 8px 12px;
  background: #ffffff;
  color: #334155;
  font-weight: 600;
  cursor: pointer;
}
.tab-active {
  background: #eff6ff;
  border-color: #93c5fd;
  color: #1d4ed8;
}
.secondary-btn, .danger-btn, .approve-btn, .reject-btn { border: none; border-radius: 8px; padding: 10px 14px; cursor: pointer; font-weight: 600; }
.secondary-btn { background: #16a34a; color: #ffffff; }
.secondary-btn:hover { background: #15803d; }
.danger-btn { background: #dc2626; color: #ffffff; }
.danger-btn:hover { background: #b91c1c; }
.approve-btn { background: #16a34a; color: #ffffff; }
.approve-btn:hover { background: #15803d; }
.reject-btn { background: #fee2e2; color: #991b1b; }
.message { color: #166534; margin: 0 0 12px; }
.error { color: #b91c1c; margin: 0 0 12px; }
.empty-state { padding: 20px; border: 1px dashed #cbd5e1; border-radius: 10px; color: #475569; background: #f8fafc; }
.cards { display: grid; gap: 14px; }
.card { border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; background: #fff; }
.card-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; }
.full-row { grid-column: 1 / -1; }
.cert-preview-wrap { margin-top: 6px; }
.cert-preview {
  width: 100%;
  max-width: 360px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  object-fit: cover;
  background: #f8fafc;
}
.actions { display: flex; gap: 10px; align-items: center; }
.reason-input { flex: 1; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px 12px; }
</style>
