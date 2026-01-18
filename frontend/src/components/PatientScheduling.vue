<template>
  <div class="h-full flex flex-col space-y-6" data-isolated-ui>
    <!-- Header with Gradient -->
    <div
      class="relative overflow-hidden bg-gradient-to-br from-violet-600 via-purple-600 to-fuchsia-600 p-8 rounded-3xl shadow-2xl shadow-purple-500/20 text-white"
    >
      <div
        class="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl -mr-20 -mt-20"
      ></div>

      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
        <div>
          <h2 class="text-3xl font-black tracking-tight mb-2">Lịch Hẹn Của Tôi</h2>
          <p class="text-purple-100 font-medium flex items-center gap-2">
            <span class="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            Theo dõi lịch khám và tập luyện với bác sĩ
          </p>
        </div>

        <div class="flex items-center gap-3">
          <div
            class="flex bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl p-1 shadow-sm"
          >
            <button
              v-for="view in ['Tháng', 'Tuần', 'Ngày']"
              :key="view"
              @click="currentView = view"
              :class="[
                'px-4 py-2 rounded-lg text-sm font-bold transition-all',
                currentView === view
                  ? 'bg-white text-purple-600 shadow-md'
                  : 'text-white/80 hover:text-white hover:bg-white/10',
              ]"
            >
              {{ view }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Calendar Card -->
    <div
      class="flex-1 bg-white rounded-3xl border border-slate-200 shadow-xl shadow-slate-200/50 flex flex-col overflow-hidden"
    >
      <!-- Toolbar -->
      <div
        class="p-6 border-b border-slate-100 flex items-center justify-between bg-gradient-to-r from-slate-50 to-white"
      >
        <div class="flex items-center gap-4">
          <button
            @click="today"
            class="px-4 py-2 border-2 border-purple-200 rounded-xl text-sm font-bold text-purple-600 hover:bg-purple-50 transition-colors shadow-sm"
          >
            Hôm nay
          </button>
          <div class="flex items-center gap-2">
            <button
              @click="prev"
              class="p-2 hover:bg-purple-50 rounded-full text-purple-500 hover:text-purple-700 transition-colors"
            >
              <ChevronLeft :size="20" />
            </button>
            <button
              @click="next"
              class="p-2 hover:bg-purple-50 rounded-full text-purple-500 hover:text-purple-700 transition-colors"
            >
              <ChevronRight :size="20" />
            </button>
          </div>
          <h3 class="text-xl font-black text-slate-900 capitalize">{{ monthYear }}</h3>
        </div>
      </div>

      <!-- Month View -->
      <div v-if="currentView === 'Tháng'" class="flex-1 flex flex-col min-h-0 w-full">
        <!-- Days Header -->
        <div
          class="grid grid-cols-7 border-b border-slate-200 bg-gradient-to-r from-purple-50 to-fuchsia-50 w-full"
        >
          <div
            v-for="day in ['CN', 'Hai', 'Ba', 'Tư', 'Năm', 'Sáu', 'Bảy']"
            :key="day"
            class="py-4 text-center text-xs font-black text-slate-600 uppercase tracking-wider"
          >
            {{ day }}
          </div>
        </div>

        <!-- Days Grid -->
        <div class="flex-1 grid grid-cols-7 auto-rows-fr w-full">
          <div
            v-for="(cell, i) in calendarCells"
            :key="i"
            :class="[
              'border-b border-r border-slate-100 p-2 transition-all relative flex flex-col gap-1 min-h-[100px]',
              !cell.inMonth ? 'bg-slate-50/50 text-slate-400' : 'bg-white',
              cell.isToday
                ? 'bg-gradient-to-br from-purple-50/50 to-fuchsia-50/50 ring-2 ring-inset ring-purple-200'
                : '',
            ]"
          >
            <div class="flex justify-between items-start mb-1">
              <span
                :class="[
                  'w-7 h-7 flex items-center justify-center rounded-full text-xs font-bold transition-all',
                  cell.isToday
                    ? 'bg-gradient-to-br from-purple-600 to-fuchsia-600 text-white shadow-lg shadow-purple-500/40 scale-110'
                    : cell.inMonth
                      ? 'text-slate-700 hover:bg-slate-100'
                      : 'text-slate-400',
                ]"
              >
                {{ cell.date.getDate() }}
              </span>
            </div>

            <!-- Events -->
            <div class="flex-1 overflow-y-auto custom-scrollbar space-y-1.5">
              <div
                v-for="ev in cell.events.slice(0, 3)"
                :key="ev.id"
                @click.stop="edit(ev)"
                :class="[
                  'px-3 py-2 rounded-lg text-xs font-bold truncate border-l-4 shadow-sm transition-all duration-200 cursor-pointer',
                  getEventClass(ev.type),
                ]"
              >
                <div class="flex items-center gap-1.5">
                  <span class="font-black opacity-80 text-[11px]">{{ ev.time }}</span>
                  <span class="truncate font-semibold">{{ ev.name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Week View -->
      <div v-else-if="currentView === 'Tuần'" class="flex-1 flex flex-col min-h-0">
        <!-- Week Days Header -->
        <div
          class="grid grid-cols-8 border-b border-slate-200 bg-gradient-to-r from-purple-50 to-fuchsia-50 sticky top-0 z-10"
        >
          <div
            class="py-3 px-2 text-center text-xs font-black text-slate-600 uppercase tracking-wider border-r border-slate-200"
          >
            Giờ
          </div>
          <div
            v-for="day in weekDays"
            :key="day.date.toISOString()"
            class="py-3 px-2 text-center border-r border-slate-200"
          >
            <div class="text-xs font-black text-slate-600 uppercase">{{ day.dayName }}</div>
            <div
              :class="[
                'text-lg font-black mt-1',
                day.isToday ? 'text-purple-600' : 'text-slate-800',
              ]"
            >
              {{ day.date.getDate() }}
            </div>
          </div>
        </div>

        <!-- Time Slots -->
        <div class="flex-1 overflow-y-auto custom-scrollbar">
          <div class="grid grid-cols-8">
            <div v-for="hour in 24" :key="hour" class="contents">
              <!-- Hour Label -->
              <div
                class="py-4 px-2 text-center text-xs font-bold text-slate-500 border-b border-r border-slate-100 bg-slate-50"
              >
                {{ String(hour - 1).padStart(2, '0') }}:00
              </div>

              <!-- Day Columns -->
              <div
                v-for="day in weekDays"
                :key="day.date.toISOString() + '-' + hour"
                class="relative min-h-[60px] border-b border-r border-slate-100 hover:bg-purple-50/30 transition-colors cursor-pointer group"
                @click="selectTimeSlot(day.date, hour - 1)"
              >
                <!-- Events -->
                <div
                  v-for="ev in getEventsForTimeSlot(day.date, hour - 1)"
                  :key="ev.id"
                  @click.stop="edit(ev)"
                  :class="[
                    'absolute inset-x-1 top-1 px-3 py-2 rounded-lg text-xs font-bold border-l-4 cursor-pointer shadow-md transition-all duration-200 z-10',
                    getEventClass(ev.type),
                  ]"
                >
                  <div class="font-black text-[11px]">{{ ev.time }}</div>
                  <div class="truncate font-semibold">{{ ev.name }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Day View -->
      <div v-else-if="currentView === 'Ngày'" class="flex-1 flex flex-col min-h-0">
        <div class="p-6 border-b border-slate-200 bg-gradient-to-r from-purple-50 to-fuchsia-50">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-2xl font-black text-slate-900">{{ formatDayViewDate(current) }}</h3>
              <p class="text-sm font-medium text-slate-600 mt-1">
                {{ getDayEvents(current).length }} cuộc hẹn
              </p>
            </div>
            <div class="flex gap-2">
              <button @click="prevDay" class="p-2 hover:bg-white rounded-lg transition-colors">
                <ChevronLeft :size="20" />
              </button>
              <button @click="nextDay" class="p-2 hover:bg-white rounded-lg transition-colors">
                <ChevronRight :size="20" />
              </button>
            </div>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto custom-scrollbar">
          <div class="max-w-4xl mx-auto p-4">
            <div v-for="hour in 24" :key="hour" class="flex gap-4 mb-2">
              <div class="w-20 flex-shrink-0 text-right pr-4 pt-2">
                <span class="text-sm font-bold text-slate-500"
                  >{{ String(hour - 1).padStart(2, '0') }}:00</span
                >
              </div>
              <div
                class="flex-1 min-h-[80px] border-2 border-slate-200 rounded-xl hover:border-purple-300 hover:bg-purple-50/30 transition-all cursor-pointer group relative"
                @click="selectTimeSlot(current, hour - 1)"
              >
                <div
                  v-for="ev in getEventsForTimeSlot(current, hour - 1)"
                  :key="ev.id"
                  @click.stop="edit(ev)"
                  :class="[
                    'm-2 p-4 rounded-xl border-l-4 cursor-pointer shadow-lg transition-all duration-200',
                    getEventClass(ev.type),
                  ]"
                >
                  <div class="flex items-center justify-between mb-2">
                    <span class="font-black text-base">{{ ev.time }}</span>
                    <span class="text-sm font-bold opacity-75 px-2 py-1 rounded-md bg-white/50">{{
                      ev.type
                    }}</span>
                  </div>
                  <div class="font-bold text-sm">{{ ev.name }}</div>
                  <div v-if="ev.notes" class="text-xs mt-2 opacity-75 font-medium">
                    {{ ev.notes }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ChevronLeft, ChevronRight, Plus, X } from 'lucide-vue-next'

import { API_BASE_URL } from '../config'
const API_BASE = API_BASE_URL

const currentView = ref('Tháng')
const current = ref(new Date())
const openNew = ref(false)
const editingEvent = ref(null)
const form = ref({ date: '', time: '09:00', type: 'Khám', notes: '' })
const doctorId = ref(null)
const patientId = ref(null)
const isSaving = ref(false)
const events = ref([])

const monthYear = computed(() =>
  current.value.toLocaleString('vi-VN', { month: 'long', year: 'numeric' }),
)

const calendarCells = computed(() => {
  const year = current.value.getFullYear()
  const month = current.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - startDate.getDay())

  const cells = []
  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)

    const dayEvents = events.value.filter(
      (e) =>
        e.date.getDate() === date.getDate() &&
        e.date.getMonth() === date.getMonth() &&
        e.date.getFullYear() === date.getFullYear(),
    )

    cells.push({
      date,
      inMonth: date.getMonth() === month,
      isToday: isSameDay(date, new Date()),
      events: dayEvents,
    })
  }
  return cells
})

const weekDays = computed(() => {
  const startOfWeek = new Date(current.value)
  const day = startOfWeek.getDay()
  const diff = startOfWeek.getDate() - day + (day === 0 ? -6 : 1)
  startOfWeek.setDate(diff)
  startOfWeek.setHours(0, 0, 0, 0)

  const days = []
  const dayNames = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
  for (let i = 0; i < 7; i++) {
    const date = new Date(startOfWeek)
    date.setDate(startOfWeek.getDate() + i)
    days.push({
      date,
      dayName: dayNames[i],
      isToday: isSameDay(date, new Date()),
    })
  }
  return days
})

function isSameDay(d1, d2) {
  return (
    d1.getDate() === d2.getDate() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getFullYear() === d2.getFullYear()
  )
}

function prev() {
  if (currentView.value === 'Tháng') {
    current.value = new Date(current.value.getFullYear(), current.value.getMonth() - 1, 1)
  } else if (currentView.value === 'Tuần') {
    const newDate = new Date(current.value)
    newDate.setDate(newDate.getDate() - 7)
    current.value = newDate
  } else {
    const newDate = new Date(current.value)
    newDate.setDate(newDate.getDate() - 1)
    current.value = newDate
  }
}

function next() {
  if (currentView.value === 'Tháng') {
    current.value = new Date(current.value.getFullYear(), current.value.getMonth() + 1, 1)
  } else if (currentView.value === 'Tuần') {
    const newDate = new Date(current.value)
    newDate.setDate(newDate.getDate() + 7)
    current.value = newDate
  } else {
    const newDate = new Date(current.value)
    newDate.setDate(newDate.getDate() + 1)
    current.value = newDate
  }
}

function prevDay() {
  const newDate = new Date(current.value)
  newDate.setDate(newDate.getDate() - 1)
  current.value = newDate
}

function nextDay() {
  const newDate = new Date(current.value)
  newDate.setDate(newDate.getDate() + 1)
  current.value = newDate
}

function selectTimeSlot(date, hour) {
  const dateStr = date.toISOString().split('T')[0]
  const timeStr = String(hour).padStart(2, '0') + ':00'
  form.value.date = dateStr
  form.value.time = timeStr
  openNew.value = true
}

function getEventsForTimeSlot(date, hour) {
  return events.value.filter((e) => {
    if (!isSameDay(e.date, date)) return false
    const [eventHour] = e.time.split(':').map(Number)
    return eventHour === hour
  })
}

function getDayEvents(date) {
  return events.value.filter((e) => isSameDay(e.date, date))
}

function formatDayViewDate(date) {
  return date.toLocaleDateString('vi-VN', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function today() {
  current.value = new Date()
}

function selectDate(date) {
  const offset = date.getTimezoneOffset()
  const adjustedDate = new Date(date.getTime() - offset * 60 * 1000)
  form.value.date = adjustedDate.toISOString().split('T')[0]
  openNew.value = true
}

function getEventClass(type) {
  switch (type) {
    case 'Khám':
      return 'bg-blue-100 text-blue-800 border-blue-500 hover:bg-blue-200'
    case 'Tái khám':
      return 'bg-purple-100 text-purple-800 border-purple-500 hover:bg-purple-200'
    default:
      return 'bg-fuchsia-100 text-fuchsia-800 border-fuchsia-500 hover:bg-fuchsia-200'
  }
}

function closeModal() {
  openNew.value = false
  editingEvent.value = null
  form.value = { date: '', time: '09:00', type: 'Khám', notes: '' }
}

function edit(ev) {
  editingEvent.value = ev
  const offset = ev.date.getTimezoneOffset()
  const adjustedDate = new Date(ev.date.getTime() - offset * 60 * 1000)
  form.value = {
    date: adjustedDate.toISOString().split('T')[0],
    time: ev.time,
    type: 'Khám',
    notes: ev.notes,
  }
  openNew.value = true
}

// Type Mapping
const typeMap = {
  consultation: 'Khám',
  followup: 'Tái khám',
  therapy: 'Vật lý trị liệu',
  assessment: 'Đánh giá bài tập',
}

function mapToFrontend(backendType) {
  return typeMap[backendType] || 'Khám'
}

async function loadData() {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      patientId.value = user.user_id
    }

    const token = localStorage.getItem('token')

    if (patientId.value) {
      const res = await fetch(`${API_BASE}/patient-schedules/${patientId.value}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        const data = await res.json()
        events.value = data.map((s) => ({
          id: s.schedule_id,
          name: mapToFrontend(s.session_type), // Use session type as name
          date: new Date(s.start_time), // Fix: use start_time not start
          time: new Date(s.start_time).toLocaleTimeString('vi-VN', {
            hour: '2-digit',
            minute: '2-digit',
          }),
          type: mapToFrontend(s.session_type),
          notes: s.notes,
        }))
      }
    }
  } catch (e) {
    console.error('Error loading schedules:', e)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 10px;
}
</style>
