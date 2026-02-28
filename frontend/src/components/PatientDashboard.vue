<template>
  <div class="max-w-7xl mx-auto px-2">
    <!-- Header -->
    <div class="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <h1 class="text-4xl font-black text-slate-900 mb-2">Sức khỏe của bạn</h1>
        <p class="text-lg text-slate-600 font-bold flex items-center gap-2">
          <span class="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></span>
          Dữ liệu từ smartwatch
        </p>
      </div>
      <button
        @click="showEmailModal = true"
        class="flex items-center gap-2 px-5 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-black rounded-xl shadow-lg shadow-emerald-500/25 hover:shadow-xl hover:shadow-emerald-500/40 transition-all hover:scale-105 text-sm"
      >
        <Mail :size="20" />
        Gửi báo cáo phục hồi
      </button>
    </div>

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
        </div>
      </div>
    </div>

    <!-- Today's Plan -->
    <div class="bg-white rounded-2xl border-3 border-slate-200 shadow-xl overflow-hidden mb-10">
      <div class="p-6 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
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

        <div class="p-6 bg-gradient-to-br from-slate-50 to-indigo-50 flex justify-center">
          <button
            @click="$emit('start-workout')"
            class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-black rounded-xl shadow-xl hover:shadow-2xl transition-all flex items-center gap-2 text-base hover:scale-105"
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
      <div class="p-6 border-b-2 border-slate-100 bg-gradient-to-r from-slate-50 to-indigo-50">
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
              class="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-black text-lg shadow-lg"
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
          <div class="p-6 bg-gradient-to-r from-emerald-500 to-teal-600 text-white">
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
              class="flex-1 py-3 rounded-xl font-black text-white bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 shadow-lg shadow-emerald-500/30 transition-all flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
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
  Calendar,
  Dumbbell,
  Clock,
  CalendarCheck,
  Check,
  Brain,
  User,
  CalendarOff,
  TrendingUp,
  Mail,
  Send,
} from 'lucide-vue-next'
import * as d3 from 'd3'
import { API_BASE_URL } from '../config'

const props = defineProps(['userId'])

// Health data from smartwatch
const healthData = ref({
  heartRate: 72,
  calories: 420,
  restingHR: 58,
  spo2: 98,
  sleepQuality: 85,
})

// Exercise stats
const stats = ref({ total_days: 0, total_reps: 0, total_duration: 0 })
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
  } catch (e) {
    showToast('Lỗi kết nối server', 'error')
  } finally {
    emailSending.value = false
  }
}

// Generate dynamic health data
const updateHealthData = () => {
  healthData.value = {
    heartRate: Math.floor(Math.random() * 20) + 65, // 65-85
    calories: Math.floor(Math.random() * 300) + 300, // 300-600
    restingHR: Math.floor(Math.random() * 10) + 55, // 55-65
    spo2: Math.floor(Math.random() * 3) + 96, // 96-99
    sleepQuality: Math.floor(Math.random() * 20) + 75, // 75-95
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
const drawHeartRateChart = () => {
  const container = d3.select('#heart-rate-chart')
  if (container.empty()) return
  container.selectAll('*').remove()

  // Generate mock heart rate data for the week
  const heartRateData = Array.from({ length: 7 }, (_, i) => ({
    date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toLocaleDateString('vi-VN', {
      weekday: 'short',
    }),
    rate: Math.floor(Math.random() * 20) + 65,
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

  x.domain(heartRateData.map((d) => d.date))
  y.domain([0, 100])

  svg.append('g').attr('transform', `translate(0,${height})`).call(d3.axisBottom(x))
  svg.append('g').call(d3.axisLeft(y))

  svg
    .selectAll('.bar')
    .data(heartRateData)
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

const drawWeeklyChart = () => {
  const container = d3.select('#weekly-chart')
  if (container.empty()) return
  container.selectAll('*').remove()

  // Generate mock weekly activity data
  const weeklyData = Array.from({ length: 7 }, (_, i) => ({
    date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toLocaleDateString('vi-VN', {
      weekday: 'short',
    }),
    reps: Math.floor(Math.random() * 50) + 20,
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

  x.domain(weeklyData.map((d) => d.date))
  y.domain([0, d3.max(weeklyData, (d) => d.reps) * 1.2])

  svg.append('g').attr('transform', `translate(0,${height})`).call(d3.axisBottom(x))
  svg.append('g').call(d3.axisLeft(y))

  const line = d3
    .line()
    .x((d) => x(d.date))
    .y((d) => y(d.reps))
    .curve(d3.curveMonotoneX)

  svg
    .append('path')
    .data([weeklyData])
    .attr('d', line)
    .attr('fill', 'none')
    .attr('stroke', '#6366f1')
    .attr('stroke-width', 3)

  svg
    .selectAll('.dot')
    .data(weeklyData)
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

    const [statsRes, historyRes, planRes] = await Promise.all([
      fetch(`${API_URL}/overall-stats${query}`, { headers }),
      fetch(`${API_URL}/weekly-progress${query}`, { headers }),
      fetch(`${API_URL}/patient/today/${props.userId}`, { headers }),
    ])

    if (statsRes.ok) stats.value = await statsRes.json()
    if (historyRes.ok) history.value = await historyRes.json()
    if (planRes.ok) todayPlan.value = await planRes.json()

    updateHealthData()

    nextTick(() => {
      drawHeartRateChart()
      drawWeeklyChart()
    })
  } catch (e) {
    console.error('Error loading dashboard data:', e)
  }
}

let dataInterval = null

onMounted(() => {
  // Pre-fill patient name from localStorage
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      emailForm.value.patientName = user.full_name || ''
    } catch (e) {
      /* ignore */
    }
  }

  fetchData()
  dataInterval = setInterval(() => {
    updateHealthData()
  }, 60000) // Update health data every minute

  window.addEventListener('resize', () => {
    drawHeartRateChart()
    drawWeeklyChart()
  })
})

onUnmounted(() => {
  if (dataInterval) clearInterval(dataInterval)
  window.removeEventListener('resize', () => {
    drawHeartRateChart()
    drawWeeklyChart()
  })
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
