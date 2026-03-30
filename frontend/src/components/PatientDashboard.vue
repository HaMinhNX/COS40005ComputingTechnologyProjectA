<template>
  <div class="w-full px-6">
    <!-- Header -->
    <div class="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <h1 class="text-4xl font-black text-slate-900 mb-2">Sức khỏe của bạn</h1>
        <p class="text-lg text-slate-600 font-bold flex items-center gap-2">
          <span class="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></span>
          Dữ liệu từ smartwatch
        </p>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="showImportModal = true"
          class="flex items-center gap-2 px-5 py-3 bg-indigo-500 hover:bg-indigo-600 text-white font-black rounded-xl shadow-lg shadow-indigo-500/25 hover:shadow-xl transition-all hover:scale-105 text-sm"
        >
          <Upload :size="20" />
          Nhập dữ liệu
        </button>
        <button
          @click="showEmailModal = true"
          class="flex items-center gap-2 px-5 py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-black rounded-xl shadow-lg shadow-emerald-500/25 hover:shadow-xl transition-all hover:scale-105 text-sm"
        >
          <Mail :size="20" />
          Gửi báo cáo phục hồi
        </button>
      </div>
    </div>

    <!-- Import Modal -->
    <Transition name="fade">
      <div
        v-if="showImportModal"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
        @click.self="showImportModal = false"
      >
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden">
          <div class="p-6 bg-indigo-600 text-white">
            <h3 class="text-xl font-black flex items-center gap-2">
              <Upload :size="24" />
              Nhập dữ liệu buổi tập
            </h3>
            <p class="text-indigo-100 text-sm font-bold mt-1">Hỗ trợ file .csv hoặc .json</p>
          </div>
          <div class="p-6 space-y-4">
            <div class="bg-slate-50 rounded-xl p-4 text-sm text-slate-600 font-medium space-y-1">
              <p class="font-black text-slate-800 mb-2">Định dạng CSV (có header):</p>
              <code class="block text-xs bg-white border border-slate-200 rounded-lg p-2 font-mono">
                date, exercise_type, reps_completed, duration_seconds, accuracy_score, feedback
              </code>
              <p class="text-xs mt-2">exercise_type: squat | bicep-curl | shoulder-flexion | knee-raise</p>
            </div>
            <div>
              <label class="block text-sm font-black text-slate-700 mb-2">Chọn file</label>
              <input
                type="file"
                accept=".csv,.json"
                @change="onImportFileChange"
                class="w-full text-sm text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:font-black file:bg-indigo-100 file:text-indigo-700 hover:file:bg-indigo-200 cursor-pointer"
              />
            </div>
            <div v-if="importResult" :class="['rounded-xl p-4 text-sm font-bold', importResult.errors?.length ? 'bg-amber-50 text-amber-800' : 'bg-emerald-50 text-emerald-800']">
              <p>Đã nhập: {{ importResult.imported }} / {{ importResult.total }} buổi tập</p>
              <ul v-if="importResult.errors?.length" class="mt-2 space-y-1 text-xs">
                <li v-for="e in importResult.errors" :key="e">⚠ {{ e }}</li>
              </ul>
            </div>
          </div>
          <div class="p-6 bg-slate-50 flex gap-3">
            <button
              @click="showImportModal = false; importResult = null"
              class="flex-1 py-3 border-2 border-slate-200 text-slate-700 font-black rounded-xl hover:bg-slate-100 transition-colors"
            >
              Đóng
            </button>
            <button
              @click="submitImport"
              :disabled="!importFile || importLoading"
              class="flex-1 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-black rounded-xl transition-colors"
            >
              {{ importLoading ? 'Đang nhập...' : 'Nhập dữ liệu' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Health Metrics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-10">
      <!-- Heart Rate -->
      <div
        class="bg-white rounded-2xl p-7 border-3 border-red-200 shadow-xl hover:scale-105 transition-transform duration-200"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="w-16 h-16 rounded-xl bg-red-500 shadow-lg flex items-center justify-center">
            <Heart :size="32" class="text-white" />
          </div>
        </div>
        <div class="mb-3">
          <div class="text-5xl font-black text-red-600 mb-1">{{ healthData.heartRate }}</div>
          <div class="text-xl font-black text-red-700 uppercase tracking-wide">BPM</div>
        </div>
        <p class="text-base text-slate-700 font-bold leading-relaxed">Nhịp tim trung bình</p>
      </div>

      <!-- SpO2 -->
      <div
        class="bg-white rounded-2xl p-7 border-3 border-emerald-200 shadow-xl hover:scale-105 transition-transform duration-200"
      >
        <div class="flex items-center justify-between mb-3">
          <div
            class="w-16 h-16 rounded-xl bg-emerald-500 shadow-lg flex items-center justify-center"
          >
            <Wind :size="32" class="text-white" />
          </div>
          <span class="text-sm font-black text-emerald-700 bg-emerald-100 px-3 py-1.5 rounded-xl"
            >Tốt</span
          >
        </div>
        <div class="mb-3">
          <div class="text-5xl font-black text-emerald-600 mb-1">
            {{ healthData.spo2 }}<span class="text-3xl">%</span>
          </div>
          <div class="text-xl font-black text-emerald-700 uppercase tracking-wide">Oxy máu</div>
        </div>
        <p class="text-base text-slate-700 font-bold leading-relaxed">Nồng độ oxy trong máu</p>
      </div>

      <!-- Sleep Quality -->
      <div
        class="bg-white rounded-2xl p-7 border-3 border-purple-200 shadow-xl hover:scale-105 transition-transform duration-200"
      >
        <div class="flex items-center justify-between mb-3">
          <div
            class="w-16 h-16 rounded-xl bg-purple-500 shadow-lg flex items-center justify-center"
          >
            <Moon :size="32" class="text-white" />
          </div>
        </div>
        <div class="mb-3">
          <div class="text-5xl font-black text-purple-600 mb-1">{{ healthData.sleepQuality }}</div>
          <div class="text-xl font-black text-purple-700 uppercase tracking-wide">/ 100</div>
        </div>
        <p class="text-base text-slate-700 font-bold leading-relaxed">Chất lượng giấc ngủ</p>
      </div>

      <!-- Calories -->
      <div
        class="bg-white rounded-2xl p-7 border-3 border-orange-200 shadow-xl hover:scale-105 transition-transform duration-200"
      >
        <div class="flex items-center justify-between mb-3">
          <div
            class="w-16 h-16 rounded-xl bg-orange-500 shadow-lg flex items-center justify-center"
          >
            <Flame :size="32" class="text-white" />
          </div>
        </div>
        <div class="mb-3">
          <div class="text-5xl font-black text-orange-600 mb-1">{{ healthData.calories }}</div>
          <div class="text-xl font-black text-orange-700 uppercase tracking-wide">KCAL</div>
        </div>
        <p class="text-base text-slate-700 font-bold leading-relaxed">Calo đã đốt hôm nay</p>
      </div>

      <!-- Resting Heart Rate -->
      <div
        class="bg-white rounded-2xl p-7 border-3 border-blue-200 shadow-xl hover:scale-105 transition-transform duration-200"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="w-16 h-16 rounded-xl bg-blue-500 shadow-lg flex items-center justify-center">
            <Activity :size="32" class="text-white" />
          </div>
        </div>
        <div class="mb-3">
          <div class="text-5xl font-black text-blue-600 mb-1">{{ healthData.restingHR }}</div>
          <div class="text-xl font-black text-blue-700 uppercase tracking-wide">BPM</div>
        </div>
        <p class="text-base text-slate-700 font-bold leading-relaxed">Nhịp tim lúc nghỉ</p>
      </div>

      <!-- Exercise Summary -->
      <div
        class="bg-white rounded-2xl p-7 border-3 border-indigo-200 shadow-xl hover:scale-105 transition-transform duration-200"
      >
        <div class="flex items-center justify-between mb-3">
          <div
            class="w-16 h-16 rounded-xl bg-indigo-500 shadow-lg flex items-center justify-center"
          >
            <Dumbbell :size="32" class="text-white" />
          </div>
        </div>
        <div class="space-y-3">
          <div>
            <div class="text-4xl font-black text-indigo-600">{{ stats.total_days || 0 }}</div>
            <div class="text-base font-bold text-indigo-700 uppercase mt-1">Ngày đã tập</div>
          </div>
          <div class="border-t-2 border-slate-200 pt-2">
            <div class="text-3xl font-black text-indigo-600">{{ stats.total_reps || 0 }}</div>
            <div class="text-base font-bold text-indigo-700 uppercase mt-1">Tổng reps</div>
          </div>
          <div class="border-t-2 border-slate-200 pt-2">
            <div class="text-3xl font-black text-emerald-600">{{ brainStats.today_score || 0 }}</div>
            <div class="text-base font-bold text-emerald-700 uppercase mt-1 flex items-center gap-2">
              <Sparkles :size="16" />
              Điểm trí tuệ
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Today's Plan -->
    <div class="bg-white rounded-2xl border-3 border-slate-200 shadow-xl overflow-hidden mb-10">
      <div class="p-6 bg-indigo-600 text-white">
        <h2 class="text-2xl font-black mb-2 flex items-center gap-3">
          <CalendarCheck :size="28" />
          Kế hoạch hôm nay
        </h2>
        <p class="text-base font-bold text-indigo-100">
          {{
            new Date().toLocaleDateString('vi-VN', {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
            })
          }}
        </p>
      </div>

      <div v-if="todayPlan.length > 0" class="divide-y-2 divide-slate-100">
        <div
          v-for="item in todayPlan"
          :key="item.id"
          class="p-4 flex items-center justify-between hover:bg-indigo-50 transition-colors cursor-pointer"
        >
          <div class="flex items-center gap-3">
            <div
              :class="[
                'w-12 h-12 rounded-xl flex items-center justify-center transition-all',
                item.is_completed
                  ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30'
                  : 'bg-slate-200 text-slate-500',
              ]"
            >
              <Check v-if="item.is_completed" :size="24" :stroke-width="3" />
              <component v-else :is="getIcon(item.name)" :size="24" />
            </div>
            <div>
              <h3
                class="text-lg font-black text-slate-900 mb-0.5"
                :class="{ 'line-through text-slate-400': item.is_completed }"
              >
                {{ getExerciseName(item.name) }}
              </h3>
              <div class="flex items-center gap-2 text-xs font-bold text-slate-600">
                <span class="bg-indigo-100 px-2.5 py-1 rounded-lg text-indigo-700">
                  {{ item.sets }} hiệp × {{ item.target }} lần
                </span>
              </div>
            </div>
          </div>

          <span
            :class="[
              'px-4 py-2 text-sm font-black rounded-xl',
              item.is_completed
                ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30'
                : 'bg-slate-200 text-slate-600',
            ]"
          >
            {{ item.is_completed ? '✓ Hoàn thành' : 'Chưa tập' }}
          </span>
        </div>

        <div class="p-6 bg-slate-50 flex justify-center border-t-2 border-slate-100">
          <button
            @click="$emit('start-workout')"
            class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-xl shadow-xl hover:shadow-2xl transition-all flex items-center gap-2 text-base hover:scale-105"
          >
            <Dumbbell :size="20" />
            Bắt đầu tập luyện
          </button>
        </div>
      </div>

      <div v-else class="p-12 text-center">
        <div
          class="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <CalendarOff :size="40" class="text-slate-400" />
        </div>
        <p class="text-xl font-bold text-slate-600">Hôm nay bạn không có bài tập.</p>
        <p class="text-base text-slate-500 mt-2">Hãy nghỉ ngơi và phục hồi! 😴</p>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
      <!-- Heart Rate Trend -->
      <div class="bg-white p-8 rounded-2xl border-2 border-slate-200 shadow-lg">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-black text-slate-900 text-xl flex items-center gap-2">
            <Heart :size="22" class="text-red-500" />
            Nhịp tim tuần này
          </h3>
          <span class="text-xs font-bold text-slate-500 bg-slate-100 px-3 py-1.5 rounded-full"
            >7 ngày</span
          >
        </div>
        <div id="heart-rate-chart" class="h-80 w-full"></div>
      </div>

      <!-- Activity Progress -->
      <div class="bg-white p-8 rounded-2xl border-2 border-slate-200 shadow-lg">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-black text-slate-900 text-xl flex items-center gap-2">
            <TrendingUp :size="22" class="text-indigo-500" />
            Tiến độ tập luyện
          </h3>
          <span class="text-xs font-bold text-slate-500 bg-slate-100 px-3 py-1.5 rounded-full"
            >Tuần này</span
          >
        </div>
        <div id="weekly-chart" class="h-80 w-full"></div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="bg-white rounded-2xl border-3 border-slate-200 shadow-xl overflow-hidden">
      <div class="p-6 border-b-2 border-slate-100 bg-slate-50">
        <h2 class="text-2xl font-black text-slate-900">Hoạt động gần đây</h2>
      </div>

      <div v-if="history.length > 0" class="divide-y-2 divide-slate-100">
        <div
          v-for="(session, index) in history.slice(0, 5)"
          :key="index"
          class="p-6 flex items-center justify-between hover:bg-slate-50 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div
              class="w-12 h-12 rounded-full bg-indigo-500 flex items-center justify-center text-white font-black text-lg shadow-lg"
            >
              {{ index + 1 }}
            </div>
            <div>
              <h3 class="text-xl font-black text-slate-900">
                {{ getExerciseName(session.exercise_type) }}
              </h3>
              <p class="text-sm text-slate-600 font-bold mt-1">
                {{ formatDate(session.start_time) }}
              </p>
            </div>
          </div>
          <div class="text-right">
            <span class="block font-black text-slate-900 text-3xl">
              {{ session.max_reps }}
            </span>
            <span class="text-sm font-bold text-slate-500 uppercase mt-1 block">lần</span>
          </div>
        </div>
      </div>

      <div v-else class="p-12 text-center">
        <div
          class="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <Activity :size="40" class="text-slate-400" />
        </div>
        <h3 class="text-xl font-black text-slate-900 mb-2">Chưa có dữ liệu tập luyện</h3>
        <p class="text-base text-slate-600 font-bold">Hãy bắt đầu bài tập đầu tiên của bạn!</p>
      </div>
    </div>

    <!-- Email Report Modal -->
    <Transition name="fade">
      <div
        v-if="showEmailModal"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
        @click.self="showEmailModal = false"
      >
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden">
          <div class="p-6 bg-emerald-500 text-white">
            <h3 class="text-xl font-black flex items-center gap-2">
              <Mail :size="24" />
              Gửi báo cáo phục hồi qua Email
            </h3>
            <p class="text-emerald-100 text-sm font-bold mt-1">
              Báo cáo tiến độ phục hồi chức năng sẽ được gửi tự động
            </p>
          </div>
          <div class="p-6 space-y-5">
            <div>
              <label class="block text-sm font-black text-slate-700 mb-2">Tên bệnh nhân</label>
              <input
                v-model="emailForm.patientName"
                type="text"
                placeholder="Nhập tên bệnh nhân"
                class="w-full px-4 py-3 border-2 border-slate-200 rounded-xl font-bold text-slate-900 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all"
              />
            </div>
            <div>
              <label class="block text-sm font-black text-slate-700 mb-2">Email người nhận</label>
              <input
                v-model="emailForm.receiverEmail"
                type="email"
                placeholder="example@gmail.com"
                class="w-full px-4 py-3 border-2 border-slate-200 rounded-xl font-bold text-slate-900 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all"
              />
              <p class="text-xs text-slate-400 font-medium mt-1.5">
                Hỗ trợ nhiều email, phân cách bằng dấu phẩy
              </p>
            </div>
          </div>
          <div class="p-6 bg-slate-50 flex gap-3">
            <button
              @click="showEmailModal = false"
              class="flex-1 py-3 rounded-xl font-bold text-slate-600 hover:bg-white hover:shadow-md transition-all border border-transparent hover:border-slate-200"
            >
              Hủy bỏ
            </button>
            <button
              @click="sendReport"
              :disabled="emailSending"
              class="flex-1 py-3 rounded-xl font-black text-white bg-emerald-500 hover:bg-emerald-600 shadow-lg shadow-emerald-500/30 transition-all flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <Send v-if="!emailSending" :size="18" />
              <span
                v-if="emailSending"
                class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"
              ></span>
              {{ emailSending ? 'Đang gửi...' : 'Gửi báo cáo' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast Notification -->
    <Transition name="toast">
      <div
        v-if="emailToast.show"
        :class="[
          'fixed bottom-6 right-6 z-[200] px-6 py-4 rounded-2xl shadow-2xl font-bold text-white flex items-center gap-3 max-w-md',
          emailToast.type === 'success' ? 'bg-emerald-500' : 'bg-red-500',
        ]"
      >
        <span>{{ emailToast.message }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, markRaw } from 'vue'
import {
  Heart,
  Flame,
  Activity,
  Wind,
  Moon,
  Dumbbell,
  CalendarCheck,
  Check,
  Brain,
  User,
  CalendarOff,
  TrendingUp,
  Mail,
  Send,
  Sparkles,
  Upload,
} from 'lucide-vue-next'
import * as d3 from 'd3'
import { API_BASE_URL } from '../config'

const props = defineProps(['userId'])

// Health data from smartwatch
const healthData = ref({
  heartRate: 0,
  calories: 0,
  restingHR: 0,
  spo2: 0,
  sleepQuality: 0,
})

// Exercise stats
const stats = ref({ total_days: 0, total_reps: 0, total_duration: 0 })
const brainStats = ref({ today_score: 0, streak: 0 })
const history = ref([])
const todayPlan = ref([])
// Removed notifications and related logic for simplicity

const API_URL = API_BASE_URL
// Removed unreadCount computed property

// Email report state
const showEmailModal = ref(false)
const emailSending = ref(false)
const emailForm = ref({
  patientName: '',
  receiverEmail: '',
})
const emailToast = ref({ show: false, message: '', type: 'success' })

// Import state
const showImportModal = ref(false)
const importFile = ref(null)
const importLoading = ref(false)
const importResult = ref(null)

const onImportFileChange = (e) => {
  importFile.value = e.target.files[0] || null
  importResult.value = null
}

const submitImport = async () => {
  if (!importFile.value) return
  importLoading.value = true
  importResult.value = null
  try {
    const token = localStorage.getItem('token')
    const formData = new FormData()
    formData.append('file', importFile.value)
    const res = await fetch(`${API_URL}/session/import`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    })
    importResult.value = await res.json()
    if (res.ok && importResult.value.imported > 0) {
      await fetchData()
    }
  } catch {
    importResult.value = { imported: 0, total: 0, errors: ['Lỗi kết nối server'] }
  } finally {
    importLoading.value = false
  }
}

const showToast = (message, type = 'success') => {
  emailToast.value = { show: true, message, type }
  setTimeout(() => {
    emailToast.value.show = false
  }, 4000)
}

const sendReport = async () => {
  if (!emailForm.value.receiverEmail.trim()) {
    showToast('Vui lòng nhập email người nhận', 'error')
    return
  }
  emailSending.value = true
  try {
    const res = await fetch(`${API_URL}/send-report-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        receiver_email: emailForm.value.receiverEmail.trim(),
        patient_name: emailForm.value.patientName.trim() || 'Bệnh nhân',
      }),
    })
    const data = await res.json()
    if (res.ok && data.success) {
      showToast(data.message, 'success')
      showEmailModal.value = false
    } else {
      showToast(data.message || 'Gửi email thất bại', 'error')
    }
  } catch {
    showToast('Lỗi kết nối server', 'error')
  } finally {
    emailSending.value = false
  }
}

// Generate dynamic health data
const updateHealthData = async () => {
  if (!props.userId) return
  
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    const res = await fetch(`${API_URL}/patient/health-metrics/${props.userId}`, { headers })
    if (res.ok) {
      healthData.value = await res.json()
    }
  } catch {
    console.error('Failed to load real health metrics');
  }
}

const getExerciseName = (type) => {
  const names = {
    squat: 'Squat',
    'bicep-curl': 'Bicep Curl',
    'shoulder-flexion': 'Shoulder Press',
    'knee-raise': 'Knee Raise',
    'Brain Game': 'Trí tuệ',
  }
  return names[type] || type
}

const getIcon = (type) => {
  const icons = {
    squat: markRaw(Dumbbell),
    'bicep-curl': markRaw(Activity),
    'shoulder-flexion': markRaw(User),
    'knee-raise': markRaw(Activity),
    'Brain Game': markRaw(Brain),
  }
  return icons[type] || markRaw(Activity)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('vi-VN', { day: 'numeric', month: 'long', year: 'numeric' })
}

// Chart drawing functions
const drawHeartRateChart = (heartRateData) => {
  const container = d3.select('#heart-rate-chart')
  if (container.empty() || !heartRateData) return
  container.selectAll('*').remove()

  // Format JS date strings
  const formattedData = heartRateData.map(d => ({
    date: new Date(d.date).toLocaleDateString('vi-VN', { weekday: 'short' }),
    rate: d.rate
  }))

  const margin = { top: 20, right: 20, bottom: 30, left: 40 }
  const width = container.node().getBoundingClientRect().width - margin.left - margin.right
  const height = 280 - margin.top - margin.bottom

  const svg = container
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const x = d3.scaleBand().range([0, width]).padding(0.3)
  const y = d3.scaleLinear().range([height, 0])

  x.domain(formattedData.map((d) => d.date))
  y.domain([0, 150]) // cap at 150 bpm

  svg.append('g').attr('transform', `translate(0,${height})`).call(d3.axisBottom(x))
  svg.append('g').call(d3.axisLeft(y))

  svg
    .selectAll('.bar')
    .data(formattedData)
    .enter()
    .append('rect')
    .attr('class', 'bar')
    .attr('x', (d) => x(d.date))
    .attr('width', x.bandwidth())
    .attr('y', (d) => y(d.rate))
    .attr('height', (d) => height - y(d.rate))
    .attr('fill', '#ef4444')
    .attr('rx', 6)
}

const drawWeeklyChart = (weeklyData) => {
  const container = d3.select('#weekly-chart')
  if (container.empty() || !weeklyData) return
  container.selectAll('*').remove()

  const formattedData = weeklyData.map(d => ({
    date: new Date(d.date).toLocaleDateString('vi-VN', { weekday: 'short' }),
    reps: d.reps
  }))

  const margin = { top: 20, right: 20, bottom: 30, left: 40 }
  const width = container.node().getBoundingClientRect().width - margin.left - margin.right
  const height = 280 - margin.top - margin.bottom

  const svg = container
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const x = d3.scalePoint().range([0, width]).padding(0.5)
  const y = d3.scaleLinear().range([height, 0])

  x.domain(formattedData.map((d) => d.date))
  const maxReps = d3.max(formattedData, (d) => d.reps) || 10;
  y.domain([0, maxReps * 1.2])

  svg.append('g').attr('transform', `translate(0,${height})`).call(d3.axisBottom(x))
  svg.append('g').call(d3.axisLeft(y))

  const line = d3
    .line()
    .x((d) => x(d.date))
    .y((d) => y(d.reps))
    .curve(d3.curveMonotoneX)

  svg
    .append('path')
    .data([formattedData])
    .attr('d', line)
    .attr('fill', 'none')
    .attr('stroke', '#6366f1')
    .attr('stroke-width', 3)

  svg
    .selectAll('.dot')
    .data(formattedData)
    .enter()
    .append('circle')
    .attr('cx', (d) => x(d.date))
    .attr('cy', (d) => y(d.reps))
    .attr('r', 5)
    .attr('fill', '#fff')
    .attr('stroke', '#6366f1')
    .attr('stroke-width', 2)
}

async function fetchData() {
  if (!props.userId) return
  try {
    const query = `?user_id=${props.userId}`
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }

    const [statsRes, historyRes, planRes, chartsRes, brainRes] = await Promise.all([
      fetch(`${API_URL}/overall-stats${query}`, { headers }),
      fetch(`${API_URL}/weekly-progress${query}`, { headers }),
      fetch(`${API_URL}/patient/today/${props.userId}`, { headers }),
      fetch(`${API_URL}/patient/health-charts/${props.userId}`, { headers }),
      fetch(`${API_URL}/brain-exercise/stats/${props.userId}`, { headers }),
    ])

    if (statsRes.ok) stats.value = await statsRes.json()
    if (historyRes.ok) history.value = await historyRes.json()
    if (planRes.ok) todayPlan.value = await planRes.json()
    if (brainRes.ok) brainStats.value = await brainRes.json()
    
    let chartData = null
    if (chartsRes.ok) chartData = await chartsRes.json()

    await updateHealthData()

    nextTick(() => {
      if (chartData) {
        drawHeartRateChart(chartData.heartRateData)
        drawWeeklyChart(chartData.weeklyData)
      }
    })
  } catch (e) {
    console.error('Error loading dashboard data:', e)
  }
}

onMounted(() => {
  // Pre-fill patient name from localStorage
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      emailForm.value.patientName = user.full_name || ''
    } catch {
      /* ignore */
    }
  }

  fetchData()

  window.addEventListener('resize', () => {
    // Cannot redraw easily without storing chartData globally, but that's fine for now 
    // Data is static until refresh. 
    // We can just rely on refresh, or optionally define a reactive ref for chartData
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', () => {})
})
</script>

<style scoped>
/* Elderly-friendly styles with larger text and better contrast */
* {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
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

.toast-enter-active {
  transition: all 0.4s ease;
}
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
