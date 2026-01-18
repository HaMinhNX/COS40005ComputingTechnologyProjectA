<template>
  <div class="max-w-5xl mx-auto relative">
    <!-- Header -->
    <div class="mb-8 flex justify-between items-start">
      <div>
        <h2 class="text-2xl font-black text-slate-900">Tổng quan sức khỏe</h2>
        <p class="text-slate-500 font-medium">Theo dõi tiến độ tập luyện của bạn</p>
      </div>

      <!-- Notification Bell -->
      <div class="relative">
        <button
          @click="showNotifications = !showNotifications"
          class="p-3 bg-white rounded-xl border border-slate-100 shadow-sm hover:bg-slate-50 transition-colors relative"
        >
          <Bell :size="20" class="text-slate-600" />
          <span
            v-if="unreadCount > 0"
            class="absolute top-2 right-2 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white"
          ></span>
        </button>

        <!-- Dropdown -->
        <div
          v-if="showNotifications"
          class="absolute right-0 top-full mt-2 w-80 bg-white rounded-2xl shadow-xl border border-slate-100 z-50 overflow-hidden"
        >
          <div class="p-4 border-b border-slate-100 flex justify-between items-center">
            <h3 class="font-bold text-slate-900">Thông báo</h3>
            <button
              @click="markAllRead"
              class="text-xs font-bold text-indigo-600 hover:text-indigo-700"
            >
              Đã đọc tất cả
            </button>
          </div>

          <div class="max-h-[400px] overflow-y-auto">
            <div
              v-if="notifications.length === 0"
              class="p-8 text-center text-slate-500 text-sm font-medium"
            >
              Không có thông báo mới
            </div>
            <div v-else>
              <div
                v-for="notif in notifications"
                :key="notif.notification_id"
                :class="[
                  'p-4 border-b border-slate-50 hover:bg-slate-50 transition-colors flex gap-3',
                  { 'bg-indigo-50/50': !notif.is_read },
                ]"
              >
                <div class="mt-1">
                  <div
                    v-if="notif.type === 'success'"
                    class="w-2 h-2 rounded-full bg-emerald-500"
                  ></div>
                  <div
                    v-else-if="notif.type === 'warning'"
                    class="w-2 h-2 rounded-full bg-amber-500"
                  ></div>
                  <div v-else class="w-2 h-2 rounded-full bg-blue-500"></div>
                </div>
                <div>
                  <h4 class="text-sm font-bold text-slate-900">{{ notif.title }}</h4>
                  <p class="text-xs text-slate-600 mt-1 leading-relaxed">{{ notif.message }}</p>
                  <p class="text-[10px] text-slate-400 mt-2">{{ formatDate(notif.created_at) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <transition name="toast">
      <div v-if="showToastFlag" :class="['toast-notification', `toast-${toastType}`]">
        <div class="toast-icon">
          <CheckCircle2 v-if="toastType === 'success'" :size="24" class="text-emerald-500" />
          <AlertCircle v-else-if="toastType === 'warning'" :size="24" class="text-amber-500" />
          <Info v-else :size="24" class="text-blue-500" />
        </div>

        <span class="toast-message">{{ toastMessage }}</span>
      </div>
    </transition>

    <!-- Today's Plan Section -->
    <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden mb-8">
      <div
        class="p-6 border-b border-slate-100 flex justify-between items-center bg-gradient-to-r from-indigo-500 to-purple-600 text-white"
      >
        <div>
          <h3 class="font-bold text-lg flex items-center gap-2">
            <Calendar :size="20" />
            Kế hoạch hôm nay
          </h3>
          <p class="text-indigo-100 text-sm mt-1">
            {{
              new Date().toLocaleDateString('vi-VN', {
                weekday: 'long',
                day: 'numeric',
                month: 'numeric',
              })
            }}
          </p>
        </div>
        <div class="bg-white/20 px-4 py-2 rounded-lg backdrop-blur-sm">
          <span class="font-bold"
            >{{ todayPlan.filter((i) => i.is_completed).length }}/{{ todayPlan.length }}</span
          >
          <span class="text-xs ml-1 opacity-80">Hoàn thành</span>
        </div>
      </div>

      <div v-if="todayPlan.length > 0" class="divide-y divide-slate-100">
        <div
          v-for="item in todayPlan"
          :key="item.id"
          class="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors group"
        >
          <div class="flex items-center gap-4">
            <div
              class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl transition-all"
              :class="
                item.is_completed
                  ? 'bg-emerald-100 text-emerald-600'
                  : 'bg-slate-100 text-slate-400 group-hover:bg-indigo-50 group-hover:text-indigo-500'
              "
            >
              <Check v-if="item.is_completed" :size="24" />
              <component v-else :is="getIcon(item.name)" :size="24" />
            </div>
            <div>
              <h4
                class="font-bold text-slate-900"
                :class="{ 'line-through text-slate-400': item.is_completed }"
              >
                {{ getExerciseName(item.name) }}
              </h4>
              <div class="flex items-center gap-3 text-xs font-medium text-slate-500 mt-1">
                <span class="bg-slate-100 px-2 py-1 rounded text-slate-600">
                  {{ item.sets }} hiệp x {{ item.target }} reps
                </span>
                <span v-if="item.session_time" class="text-indigo-500">
                  {{
                    item.session_time === 'Morning'
                      ? 'Buổi sáng'
                      : item.session_time === 'Afternoon'
                        ? 'Buổi chiều'
                        : 'Buổi tối'
                  }}
                </span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <!-- Status Badge -->
            <span
              v-if="item.is_completed"
              class="px-3 py-1 bg-emerald-100 text-emerald-700 text-xs font-bold rounded-full"
            >
              Đã xong
            </span>
            <span
              v-else
              class="px-3 py-1 bg-slate-100 text-slate-500 text-xs font-bold rounded-full"
            >
              Chưa tập
            </span>
          </div>
        </div>

        <!-- Action Button -->
        <div class="p-4 bg-slate-50 flex justify-center">
          <button
            @click="$emit('start-workout')"
            class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-indigo-200 transition-all flex items-center gap-2"
          >
            <Dumbbell :size="20" />
            Bắt đầu tập luyện ngay
          </button>
        </div>
      </div>

      <div v-else class="p-8 text-center text-slate-500">
        <p>Hôm nay bạn không có bài tập nào. Hãy nghỉ ngơi nhé! 😴</p>
      </div>
    </div>

    <!-- Key Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div
        class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-4"
      >
        <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
          <Calendar :size="24" />
        </div>
        <div>
          <div class="text-3xl font-black text-slate-900">{{ stats.total_days || 0 }}</div>
          <div class="text-sm font-bold text-slate-500 uppercase tracking-wider">Ngày tập</div>
        </div>
      </div>

      <div
        class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-4"
      >
        <div
          class="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center"
        >
          <Dumbbell :size="24" />
        </div>
        <div>
          <div class="text-3xl font-black text-slate-900">{{ stats.total_reps || 0 }}</div>
          <div class="text-sm font-bold text-slate-500 uppercase tracking-wider">Tổng Reps</div>
        </div>
      </div>

      <div
        class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-4"
      >
        <div
          class="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center"
        >
          <Clock :size="24" />
        </div>
        <div>
          <div class="text-3xl font-black text-slate-900">
            {{ ((stats.total_duration || 0) / 60).toFixed(0) }}
          </div>
          <div class="text-sm font-bold text-slate-500 uppercase tracking-wider">Phút tập</div>
        </div>
      </div>
    </div>

    <!-- Charts Section - 3 Column Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <!-- Weekly Progress Chart -->
      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
        <h3 class="font-bold text-slate-900 text-base mb-4">Tiến độ tuần này</h3>
        <div id="weekly-chart" class="h-52 w-full"></div>
      </div>

      <!-- Accuracy Trend Chart -->
      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
        <h3 class="font-bold text-slate-900 text-base mb-4">Độ chính xác động tác</h3>
        <div id="accuracy-chart" class="h-52 w-full"></div>
      </div>

      <!-- Muscle Focus Pie Chart -->
      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
        <h3 class="font-bold text-slate-900 text-base mb-4">Phân bố bài tập</h3>
        <div id="muscle-chart" class="h-52 w-full flex justify-center items-center"></div>
      </div>
    </div>

    <!-- Recent Activity List -->
    <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
      <div class="p-6 border-b border-slate-100 flex justify-between items-center">
        <h3 class="font-bold text-slate-900 text-lg">Lịch sử tập luyện</h3>
        <button class="text-sm font-bold text-indigo-600 hover:text-indigo-700">Xem tất cả</button>
      </div>

      <div v-if="history.length > 0" class="divide-y divide-slate-100">
        <div
          v-for="(session, index) in history"
          :key="index"
          class="p-6 flex items-center justify-between hover:bg-slate-50 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div
              class="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 font-bold"
            >
              {{ index + 1 }}
            </div>
            <div>
              <h4 class="font-bold text-slate-900 text-base">
                {{ getExerciseName(session.exercise_type) }}
              </h4>
              <p class="text-xs text-slate-500 font-medium">
                {{ formatDate(session.start_time) }} <br />
                <span class="text-slate-400"
                  >{{ formatTime(session.start_time) }} - {{ formatTime(session.end_time) }}</span
                >
              </p>
            </div>
          </div>
          <div class="text-right">
            <span class="block font-black text-slate-900 text-lg"
              >{{ session.max_reps }}
              <span class="text-xs font-bold text-slate-400 uppercase">reps</span></span
            >
          </div>
        </div>
      </div>

      <div v-else class="p-12 text-center">
        <div
          class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-300"
        >
          <Activity :size="32" />
        </div>
        <h3 class="text-lg font-bold text-slate-900">Chưa có dữ liệu</h3>
        <p class="text-slate-500 font-medium mt-1">Hãy bắt đầu bài tập đầu tiên của bạn!</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed, markRaw } from 'vue'

import {
  Bell,
  Calendar,
  Activity,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Info,
  Dumbbell,
  Brain,
  User,
  CheckCircle2,
  Check,
} from 'lucide-vue-next'

import * as d3 from 'd3'
import { API_BASE_URL } from '../config'

const props = defineProps(['userId'])
const stats = ref({ total_days: 0, total_reps: 0, total_duration: 0 })
const history = ref([])
const todayPlan = ref([])
const chartData = ref({ weekly_activity: [], accuracy_trend: [], muscle_focus: [] })
const notifications = ref([])
const showNotifications = ref(false)

const API_URL = API_BASE_URL

const unreadCount = computed(() => notifications.value.filter((n) => !n.is_read).length)

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
  return date.toLocaleDateString('vi-VN', { weekday: 'long', day: 'numeric', month: 'numeric' })
}

function formatTime(dateStr) {
  if (!dateStr) return '--:--'
  const date = new Date(dateStr)
  return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
}

const loadNotifications = async () => {
  if (!props.userId) return
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_URL}/notifications/${props.userId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) {
      const newNotifications = await res.json()
      const oldUnreadCount = notifications.value.filter((n) => !n.is_read).length
      const newUnreadCount = newNotifications.filter((n) => !n.is_read).length
      if (newUnreadCount > oldUnreadCount && notifications.value.length > 0) {
        showToast('Bạn có thông báo mới!', 'info')
      }
      notifications.value = newNotifications
    }
  } catch (e) {
    console.error(e)
  }
}

const markAllRead = () => {
  notifications.value.forEach((n) => (n.is_read = true))
  showToast('Đã đánh dấu tất cả là đã đọc', 'success')
}

// Toast notification system
const toastMessage = ref('')
const toastType = ref('info')
const showToastFlag = ref(false)

const showToast = (message, type = 'info') => {
  toastMessage.value = message
  toastType.value = type
  showToastFlag.value = true
  setTimeout(() => {
    showToastFlag.value = false
  }, 3000)
}

const drawWeeklyChart = () => {
  const container = d3.select('#weekly-chart')
  if (container.empty()) return
  container.selectAll('*').remove()

  if (!chartData.value.weekly_activity.length) return

  const margin = { top: 10, right: 10, bottom: 30, left: 35 }
  const width = container.node().getBoundingClientRect().width - margin.left - margin.right
  const height = 160 - margin.top - margin.bottom

  const svg = container
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const x = d3.scaleBand().range([0, width]).padding(0.3)

  const y = d3.scaleLinear().range([height, 0])

  const data = chartData.value.weekly_activity
  x.domain(data.map((d) => d.date))
  y.domain([0, d3.max(data, (d) => d.reps) * 1.1 || 10])

  svg
    .append('g')
    .attr('transform', `translate(0,${height})`)
    .call(
      d3
        .axisBottom(x)
        .tickFormat((d) => new Date(d).getDate() + '/' + (new Date(d).getMonth() + 1)),
    )

  svg.append('g').call(d3.axisLeft(y))

  svg
    .selectAll('.bar')
    .data(data)
    .enter()
    .append('rect')
    .attr('class', 'bar')
    .attr('x', (d) => x(d.date))
    .attr('width', x.bandwidth())
    .attr('y', (d) => y(d.reps))
    .attr('height', (d) => height - y(d.reps))
    .attr('fill', '#6366f1')
    .attr('rx', 4)
}

const drawAccuracyChart = () => {
  const container = d3.select('#accuracy-chart')
  if (container.empty()) return
  container.selectAll('*').remove()

  if (!chartData.value.accuracy_trend.length) return

  const margin = { top: 10, right: 10, bottom: 30, left: 35 }
  const width = container.node().getBoundingClientRect().width - margin.left - margin.right
  const height = 160 - margin.top - margin.bottom

  const svg = container
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const x = d3.scalePoint().range([0, width]).padding(0.5)

  const y = d3.scaleLinear().range([height, 0]).domain([0, 100])

  const data = chartData.value.accuracy_trend
  x.domain(data.map((d) => d.date))

  svg.append('g').attr('transform', `translate(0,${height})`).call(d3.axisBottom(x))

  svg.append('g').call(d3.axisLeft(y))

  const line = d3
    .line()
    .x((d) => x(d.date))
    .y((d) => y(d.score))
    .curve(d3.curveMonotoneX)

  svg
    .append('path')
    .data([data])
    .attr('class', 'line')
    .attr('d', line)
    .attr('fill', 'none')
    .attr('stroke', '#10b981')
    .attr('stroke-width', 3)

  // Add dots
  svg
    .selectAll('.dot')
    .data(data)
    .enter()
    .append('circle')
    .attr('cx', (d) => x(d.date))
    .attr('cy', (d) => y(d.score))
    .attr('r', 5)
    .attr('fill', '#fff')
    .attr('stroke', '#10b981')
    .attr('stroke-width', 2)
}

const drawMuscleChart = () => {
  const container = d3.select('#muscle-chart')
  if (container.empty()) return
  container.selectAll('*').remove()

  if (!chartData.value.muscle_focus.length) return

  const width = 200
  const height = 200
  const radius = Math.min(width, height) / 2

  const svg = container
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${width / 2},${height / 2})`)

  const color = d3
    .scaleOrdinal()
    .domain(chartData.value.muscle_focus.map((d) => d.exercise_type))
    .range(['#6366f1', '#10b981', '#f59e0b', '#ef4444'])

  const pie = d3.pie().value((d) => d.count)
  const arc = d3
    .arc()
    .innerRadius(0)
    .outerRadius(radius - 10)

  const arcs = svg.selectAll('arc').data(pie(chartData.value.muscle_focus)).enter().append('g')

  arcs
    .append('path')
    .attr('d', arc)
    .attr('fill', (d) => color(d.data.exercise_type))
    .attr('stroke', 'white')
    .style('stroke-width', '2px')

  // Labels
  arcs
    .append('text')
    .attr('transform', (d) => `translate(${arc.centroid(d)})`)
    .attr('text-anchor', 'middle')
    .attr('font-size', '10px')
    .attr('fill', 'white')
    .text((d) => (d.data.count > 0 ? getExerciseName(d.data.exercise_type) : ''))
}

async function fetchData() {
  if (!props.userId) return
  try {
    const query = `?user_id=${props.userId}`

    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }

    // Fetch all data in parallel for faster loading
    const [statsRes, historyRes, chartRes, planRes] = await Promise.all([
      fetch(`${API_URL}/overall-stats${query}`, { headers }),
      fetch(`${API_URL}/weekly-progress${query}`, { headers }),
      fetch(`${API_URL}/patient/charts/${props.userId}`, { headers }),
      fetch(`${API_URL}/patient/today/${props.userId}`, { headers }),
    ])

    // Process results
    if (statsRes.ok) stats.value = await statsRes.json()
    if (historyRes.ok) history.value = await historyRes.json()

    if (chartRes.ok) {
      chartData.value = await chartRes.json()
      nextTick(() => {
        drawWeeklyChart()
        drawAccuracyChart()
        drawMuscleChart()
      })
    }

    if (planRes.ok) {
      todayPlan.value = await planRes.json()
    }

    // Load notifications separately (non-blocking)
    loadNotifications()
  } catch (e) {
    console.error('Error loading dashboard data:', e)
  }
}

let dataInterval = null

onMounted(() => {
  fetchData()
  dataInterval = setInterval(fetchData, 30000)
  window.addEventListener('resize', () => {
    drawWeeklyChart()
    drawAccuracyChart()
    drawMuscleChart()
  })
})

onUnmounted(() => {
  if (dataInterval) clearInterval(dataInterval)
  window.removeEventListener('resize', () => {
    drawWeeklyChart()
    drawAccuracyChart()
    drawMuscleChart()
  })
})
</script>

<style scoped>
/* Toast Notification Styles */
.toast-notification {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  border-left: 4px solid;
  min-width: 300px;
}

.toast-success {
  border-left-color: #10b981;
  background: linear-gradient(to right, #ecfdf5, white);
}

.toast-warning {
  border-left-color: #f59e0b;
  background: linear-gradient(to right, #fffbeb, white);
}

.toast-info {
  border-left-color: #3b82f6;
  background: linear-gradient(to right, #eff6ff, white);
}

.toast-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.toast-message {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100px);
}
</style>
