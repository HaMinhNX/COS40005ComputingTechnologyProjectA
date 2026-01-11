<template>
  <div class="h-full flex flex-col space-y-6" data-isolated-ui>
    <!-- Header with Gradient -->
    <div class="relative overflow-hidden bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-600 p-8 rounded-3xl shadow-2xl shadow-purple-500/20 text-white">
      <div class="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl -mr-20 -mt-20"></div>

      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
        <div>
          <h2 class="text-3xl font-black tracking-tight mb-2">Lịch Hẹn & Cuộc Họp</h2>
          <p class="text-purple-100 font-medium flex items-center gap-2">
            <span class="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            Quản lý cuộc hẹn và buổi tập với bệnh nhân
          </p>
        </div>

        <div class="flex items-center gap-3">
          <div class="flex bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl p-1 shadow-sm">
            <button
              v-for="view in ['Tháng', 'Tuần', 'Ngày']"
              :key="view"
              @click="currentView = view"
              :class="[
                'px-4 py-2 rounded-lg text-sm font-bold transition-all',
                currentView === view ? 'bg-white text-indigo-600 shadow-md' : 'text-white/80 hover:text-white hover:bg-white/10'
              ]"
            >
              {{ view }}
            </button>
          </div>
          
          <!-- Settings Button (Reset Delete Confirmation) -->
          <button 
            v-if="hasDeleteConfirmationDisabled"
            @click="resetDeleteConfirmation" 
            class="p-2.5 bg-white/20 backdrop-blur-sm border border-white/30 text-white rounded-xl hover:bg-white/30 transition-all shadow-sm"
            title="Bật lại xác nhận khi xóa"
          >
            <Settings :size="20" />
          </button>

          
          <button @click="openNew = true" class="px-5 py-2.5 bg-white text-indigo-600 rounded-xl text-sm font-bold hover:bg-indigo-50 transition-all shadow-lg flex items-center gap-2">
            <Plus :size="18" />
            <span class="hidden sm:inline">Tạo mới</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Calendar Card -->
    <div class="flex-1 bg-white rounded-3xl border border-slate-200 shadow-xl shadow-slate-200/50 flex flex-col overflow-hidden">
      <!-- Toolbar -->
      <div class="p-6 border-b border-slate-100 flex items-center justify-between bg-gradient-to-r from-slate-50 to-white">
        <div class="flex items-center gap-4">
          <button @click="today" class="px-4 py-2 border-2 border-indigo-200 rounded-xl text-sm font-bold text-indigo-600 hover:bg-indigo-50 transition-colors shadow-sm">Hôm nay</button>
          <div class="flex items-center gap-2">
            <button @click="prev" class="p-2 hover:bg-indigo-50 rounded-full text-indigo-500 hover:text-indigo-700 transition-colors"><ChevronLeft :size="20" /></button>
            <button @click="next" class="p-2 hover:bg-indigo-50 rounded-full text-indigo-500 hover:text-indigo-700 transition-colors"><ChevronRight :size="20" /></button>
          </div>
          <h3 class="text-xl font-black text-slate-900 capitalize">{{ monthYear }}</h3>
        </div>

        <!-- Legend -->
        <div class="hidden lg:flex items-center gap-4 text-xs font-bold text-slate-600">
          <div class="flex items-center gap-2 px-3 py-1.5 bg-blue-50 rounded-lg border border-blue-100">
            <span class="w-3 h-3 rounded-full bg-blue-500"></span> Khám bệnh
          </div>
          <div class="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 rounded-lg border border-emerald-100">
            <span class="w-3 h-3 rounded-full bg-emerald-500"></span> Tái khám
          </div>
          <div class="flex items-center gap-2 px-3 py-1.5 bg-amber-50 rounded-lg border border-amber-100">
            <span class="w-3 h-3 rounded-full bg-amber-500"></span> Đánh giá
          </div>
        </div>
      </div>

      <!-- Month View -->
      <div v-if="currentView === 'Tháng'" class="flex-1 flex flex-col min-h-0 w-full">
        <!-- Days Header -->
        <div class="grid grid-cols-7 border-b border-slate-200 bg-gradient-to-r from-indigo-50 to-purple-50 w-full">
          <div v-for="day in ['CN', 'Hai', 'Ba', 'Tư', 'Năm', 'Sáu', 'Bảy']" :key="day" class="py-4 text-center text-xs font-black text-slate-600 uppercase tracking-wider">
            {{ day }}
          </div>
        </div>

        <!-- Days Grid -->
        <div class="flex-1 grid grid-cols-7 auto-rows-fr w-full">
          <div
            v-for="(cell, i) in calendarCells"
            :key="i"
            @click="selectDate(cell.date)"
            :class="[
              'border-b border-r border-slate-100 p-2 transition-all hover:bg-gradient-to-br hover:from-indigo-50 hover:to-purple-50 cursor-pointer relative flex flex-col gap-1 min-h-[100px]',
              !cell.inMonth ? 'bg-slate-50/50 text-slate-400' : 'bg-white',
              cell.isToday ? 'bg-gradient-to-br from-indigo-50/50 to-purple-50/50 ring-2 ring-inset ring-indigo-200' : ''
            ]"
          >
            <div class="flex justify-between items-start mb-1">
              <span :class="[
                'w-7 h-7 flex items-center justify-center rounded-full text-xs font-bold transition-all',
                cell.isToday ? 'bg-gradient-to-br from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/40 scale-110' : cell.inMonth ? 'text-slate-700 hover:bg-slate-100' : 'text-slate-400'
              ]">
                {{ cell.date.getDate() }}
              </span>
            </div>

            <!-- Events -->
            <div class="flex-1 overflow-y-auto custom-scrollbar space-y-1.5">
              <div
                v-for="ev in cell.events.slice(0, 3)"
                :key="ev.id"
                @click.stop="edit(ev)"
                :class="['px-3 py-2 rounded-lg text-xs font-bold truncate border-l-4 shadow-sm transition-all duration-200 cursor-pointer', getEventClass(ev.type)]"
                style="will-change: transform;"
              >
                <div class="flex items-center gap-1.5">
                  <span class="font-black opacity-80 text-[11px]">{{ ev.time }}</span>
                  <span class="truncate font-semibold">{{ ev.name }}</span>
                </div>
              </div>
              <div v-if="cell.events.length > 3" class="text-xs font-bold text-indigo-600 px-2 py-1">
                +{{ cell.events.length - 3 }} thêm
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Week View -->
      <div v-else-if="currentView === 'Tuần'" class="flex-1 flex flex-col min-h-0">
        <!-- Week Days Header -->
        <div class="grid grid-cols-8 border-b border-slate-200 bg-gradient-to-r from-indigo-50 to-purple-50 sticky top-0 z-10">
          <div class="py-3 px-2 text-center text-xs font-black text-slate-600 uppercase tracking-wider border-r border-slate-200">Giờ</div>
          <div v-for="day in weekDays" :key="day.date.toISOString()" class="py-3 px-2 text-center border-r border-slate-200">
            <div class="text-xs font-black text-slate-600 uppercase">{{ day.dayName }}</div>
            <div :class="['text-lg font-black mt-1', day.isToday ? 'text-indigo-600' : 'text-slate-800']">{{ day.date.getDate() }}</div>
          </div>
        </div>

        <!-- Time Slots -->
        <div class="flex-1 overflow-y-auto custom-scrollbar">
          <div class="grid grid-cols-8">
            <div v-for="hour in 24" :key="hour" class="contents">
              <!-- Hour Label -->
              <div class="py-4 px-2 text-center text-xs font-bold text-slate-500 border-b border-r border-slate-100 bg-slate-50">
                {{ String(hour - 1).padStart(2, '0') }}:00
              </div>
              
              <!-- Day Columns -->
              <div 
                v-for="day in weekDays" 
                :key="day.date.toISOString() + '-' + hour"
                class="relative min-h-[60px] border-b border-r border-slate-100 hover:bg-indigo-50/30 transition-colors cursor-pointer group"
                @click="selectTimeSlot(day.date, hour - 1)"
              >
                <!-- Events in this time slot -->
                <div 
                  v-for="ev in getEventsForTimeSlot(day.date, hour - 1)" 
                  :key="ev.id"
                  @click.stop="edit(ev)"
                  :class="['absolute inset-x-1 top-1 px-3 py-2 rounded-lg text-xs font-bold border-l-4 cursor-pointer shadow-md transition-all duration-200 z-10', getEventClass(ev.type)]"
                  style="will-change: transform;"
                >
                  <div class="font-black text-[11px]">{{ ev.time }}</div>
                  <div class="truncate font-semibold">{{ ev.name }}</div>
                </div>
                
                <!-- Hover indicator -->
                <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                  <div class="absolute top-1 right-1 text-indigo-400">
                    <Plus :size="14" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Day View -->
      <div v-else-if="currentView === 'Ngày'" class="flex-1 flex flex-col min-h-0">
        <!-- Day Header -->
        <div class="p-6 border-b border-slate-200 bg-gradient-to-r from-indigo-50 to-purple-50">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-2xl font-black text-slate-900">{{ formatDayViewDate(current) }}</h3>
              <p class="text-sm font-medium text-slate-600 mt-1">{{ getDayEvents(current).length }} cuộc hẹn</p>
            </div>
            <div class="flex gap-2">
              <button @click="prevDay" class="p-2 hover:bg-white rounded-lg transition-colors">
                <ChevronLeft :size="20" class="text-slate-600" />
              </button>
              <button @click="nextDay" class="p-2 hover:bg-white rounded-lg transition-colors">
                <ChevronRight :size="20" class="text-slate-600" />
              </button>
            </div>
          </div>
        </div>

        <!-- Time Slots for Single Day -->
        <div class="flex-1 overflow-y-auto custom-scrollbar">
          <div class="max-w-4xl mx-auto p-4">
            <div v-for="hour in 24" :key="hour" class="flex gap-4 mb-2">
              <!-- Hour Label -->
              <div class="w-20 flex-shrink-0 text-right pr-4 pt-2">
                <span class="text-sm font-bold text-slate-500">{{ String(hour - 1).padStart(2, '0') }}:00</span>
              </div>
              
              <!-- Time Slot -->
              <div 
                class="flex-1 min-h-[80px] border-2 border-slate-200 rounded-xl hover:border-indigo-300 hover:bg-indigo-50/30 transition-all cursor-pointer group relative"
                @click="selectTimeSlot(current, hour - 1)"
              >
                <!-- Events in this time slot -->
                <div 
                  v-for="ev in getEventsForTimeSlot(current, hour - 1)" 
                  :key="ev.id"
                  @click.stop="edit(ev)"
                  :class="['m-2 p-4 rounded-xl border-l-4 cursor-pointer shadow-lg transition-all duration-200', getEventClass(ev.type)]"
                  style="will-change: transform;"
                >
                  <div class="flex items-center justify-between mb-2">
                    <span class="font-black text-base">{{ ev.time }}</span>
                    <span class="text-sm font-bold opacity-75 px-2 py-1 rounded-md bg-white/50">{{ ev.type }}</span>
                  </div>
                  <div class="font-bold text-sm">{{ ev.name }}</div>
                  <div v-if="ev.notes" class="text-xs mt-2 opacity-75 font-medium">{{ ev.notes }}</div>
                </div>

                <!-- Empty state / Hover indicator -->
                <div v-if="getEventsForTimeSlot(current, hour - 1).length === 0" class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <div class="flex items-center gap-2 text-indigo-400 font-bold text-sm">
                    <Plus :size="16" />
                    <span>Thêm cuộc hẹn</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="openNew" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
      <div class="bg-white rounded-3xl p-8 w-full max-w-lg shadow-2xl border border-slate-100 transform scale-100 transition-all">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-black text-slate-900">{{ editingEvent ? 'Sửa Cuộc Hẹn' : 'Cuộc Hẹn Mới' }}</h3>
          <button @click="closeModal" class="p-2 hover:bg-slate-50 rounded-xl transition-colors text-slate-400 hover:text-slate-900">
            <X :size="20" />
          </button>
        </div>

        <form @submit.prevent="saveEvent" class="space-y-5">
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Tên Bệnh Nhân</label>
            <select v-model="form.patient_id" required class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-200 rounded-xl text-sm focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all font-medium">
              <option value="" disabled>Chọn bệnh nhân</option>
              <option v-for="p in patients" :key="p.patient_id" :value="p.patient_id">
                {{ p.full_name }} ({{ p.email }})
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Ngày</label>
              <input type="date" v-model="form.date" required class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-200 rounded-xl text-sm focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all font-medium" />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Giờ</label>
              <input type="time" v-model="form.time" required class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-200 rounded-xl text-sm focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all font-medium" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Loại Cuộc Hẹn</label>
            <select v-model="form.type" class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-200 rounded-xl text-sm focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all font-medium">
              <option value="Khám">Khám bệnh</option>
              <option value="Tái khám">Tái khám</option>
              <option value="Đánh giá bài tập">Đánh giá bài tập</option>
              <option value="Vật lý trị liệu">Vật lý trị liệu</option>
            </select>
          </div>
          
          <div>
             <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Ghi chú</label>
             <textarea v-model="form.notes" rows="2" class="w-full px-4 py-3 bg-slate-50 border-2 border-slate-200 rounded-xl text-sm focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all font-medium"></textarea>
          </div>

          <div class="flex justify-between items-center pt-4">
            <button v-if="editingEvent" type="button" @click="deleteEvent" class="px-4 py-3 bg-red-50 text-red-600 rounded-xl text-sm font-bold hover:bg-red-100 transition-colors flex items-center gap-2">
              <Trash2 :size="18" />
              Xóa
            </button>
            <div v-else></div> <!-- Spacer -->
            
            <div class="flex gap-3">
              <button type="button" @click="closeModal" class="px-6 py-3 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-100 transition-colors">Hủy</button>
              <button 
                type="submit" 
                :disabled="isSaving"
                :class="[
                  'px-6 py-3 rounded-xl text-sm font-bold shadow-lg transition-all flex items-center gap-2',
                  isSaving 
                    ? 'bg-slate-400 text-white cursor-not-allowed' 
                    : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 shadow-indigo-500/30'
                ]"
              >
                <span v-if="isSaving" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                {{ isSaving ? 'Đang lưu...' : (editingEvent ? 'Cập Nhật' : 'Tạo Mới') }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-slate-900/70 backdrop-blur-sm flex items-center justify-center z-[110] p-4">
      <div class="bg-white rounded-3xl p-8 w-full max-w-md shadow-2xl border border-slate-100 transform scale-100 transition-all">
        <div class="flex flex-col items-center text-center">
          <!-- Warning Icon -->
          <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <AlertTriangle :size="32" class="text-red-600" />
          </div>


          <!-- Title -->
          <h3 class="text-2xl font-black text-slate-900 mb-2">Xác Nhận Xóa</h3>
          
          <!-- Message -->
          <p class="text-slate-600 font-medium mb-6">
            Bạn có chắc chắn muốn xóa cuộc hẹn này không? Hành động này không thể hoàn tác.
          </p>

          <!-- Don't show again checkbox -->
          <label class="flex items-center gap-3 mb-6 cursor-pointer group">
            <input 
              type="checkbox" 
              v-model="dontShowDeleteConfirm"
              class="w-5 h-5 rounded border-2 border-slate-300 text-indigo-600 focus:ring-2 focus:ring-indigo-500/20 cursor-pointer"
            />
            <span class="text-sm font-medium text-slate-600 group-hover:text-slate-900 transition-colors">
              Không hiện thông báo này nữa
            </span>
          </label>

          <!-- Action Buttons -->
          <div class="flex gap-3 w-full">
            <button 
              @click="cancelDelete" 
              class="flex-1 px-6 py-3 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-100 transition-colors border-2 border-slate-200"
            >
              Hủy
            </button>
            <button 
              @click="confirmDelete" 
              class="flex-1 px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-xl text-sm font-bold hover:from-red-700 hover:to-red-800 shadow-lg shadow-red-500/30 transition-all"
            >
              Xóa
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ChevronLeft, ChevronRight, Plus, X, Calendar, Trash2, Settings, AlertTriangle } from 'lucide-vue-next'
import { API_BASE_URL } from '../config';

const API_URL = API_BASE_URL;


const currentView = ref('Tháng')
const current = ref(new Date())
const openNew = ref(false)
const editingEvent = ref(null)
const form = ref({ patient_id: '', date: '', time: '09:00', type: 'Khám', notes: '' })
const doctorId = ref(null)
const patients = ref([])
const isSaving = ref(false) // Prevent duplicate submissions

// Delete confirmation modal
const showDeleteConfirm = ref(false)
const dontShowDeleteConfirm = ref(false)
const eventToDelete = ref(null)

const events = ref([])

// Computed property to check if delete confirmation is disabled
const hasDeleteConfirmationDisabled = computed(() => {
  return localStorage.getItem('skipDeleteConfirmation') === 'true'
})

const monthYear = computed(() => current.value.toLocaleString('vi-VN', { month: 'long', year: 'numeric' }))

const calendarCells = computed(() => {
  const year = current.value.getFullYear()
  const month = current.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)

  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - startDate.getDay())

  const cells = []
  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)

    const dayEvents = events.value.filter(e =>
      e.date.getDate() === date.getDate() &&
      e.date.getMonth() === date.getMonth() &&
      e.date.getFullYear() === date.getFullYear()
    )

    cells.push({
      date,
      inMonth: date.getMonth() === month,
      isToday: isSameDay(date, new Date()),
      events: dayEvents
    })
  }
  return cells
})

// Week view computed property
const weekDays = computed(() => {
  const startOfWeek = new Date(current.value)
  // Get Monday of current week
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
      isToday: isSameDay(date, new Date())
    })
  }
  return days
})

function isSameDay(d1, d2) {
  return d1.getDate() === d2.getDate() &&
         d1.getMonth() === d2.getMonth() &&
         d1.getFullYear() === d2.getFullYear()
}

function prev() {
  if (currentView.value === 'Tháng') {
    current.value = new Date(current.value.getFullYear(), current.value.getMonth() - 1, 1)
  } else if (currentView.value === 'Tuần') {
    const newDate = new Date(current.value)
    newDate.setDate(newDate.getDate() - 7)
    current.value = newDate
  } else if (currentView.value === 'Ngày') {
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
  } else if (currentView.value === 'Ngày') {
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
  // Pre-fill form with selected date and time
  const dateStr = date.toISOString().split('T')[0]
  const timeStr = String(hour).padStart(2, '0') + ':00'
  form.value.date = dateStr
  form.value.time = timeStr
  openNew.value = true
}

function getEventsForTimeSlot(date, hour) {
  return events.value.filter(e => {
    if (!isSameDay(e.date, date)) return false
    
    // Parse event time
    const [eventHour] = e.time.split(':').map(Number)
    return eventHour === hour
  })
}

function getDayEvents(date) {
  return events.value.filter(e => isSameDay(e.date, date))
}

function formatDayViewDate(date) {
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
  return date.toLocaleDateString('vi-VN', options)
}
function today() {
  current.value = new Date()
}

function selectDate(date) {
  const offset = date.getTimezoneOffset()
  const adjustedDate = new Date(date.getTime() - (offset*60*1000))
  form.value.date = adjustedDate.toISOString().split('T')[0]
  openNew.value = true
}

function getEventClass(type) {
  switch(type) {
    case 'Khám': return 'bg-blue-100 text-blue-800 border-blue-500 hover:bg-blue-200 hover:shadow-xl hover:scale-[1.02]'
    case 'Tái khám': return 'bg-emerald-100 text-emerald-800 border-emerald-500 hover:bg-emerald-200 hover:shadow-xl hover:scale-[1.02]'
    case 'Đánh giá bài tập': return 'bg-amber-100 text-amber-800 border-amber-500 hover:bg-amber-200 hover:shadow-xl hover:scale-[1.02]'
    default: return 'bg-indigo-100 text-indigo-800 border-indigo-500 hover:bg-indigo-200 hover:shadow-xl hover:scale-[1.02]'
  }
}

function closeModal() {
  openNew.value = false
  editingEvent.value = null
  form.value = { patient_id: '', date: '', time: '09:00', type: 'Khám', notes: '' }
}

async function loadData() {
  try {
    // Get Doctor ID
    const docRes = await fetch(`${API_URL}/doctor/doctor-id`);
    if (docRes.ok) {
      const data = await docRes.json();
      doctorId.value = data.doctor_id;
      
      // Load Schedules
      const schedRes = await fetch(`${API_URL}/schedules/${doctorId.value}`);
      if (schedRes.ok) {
        const schedData = await schedRes.json();
        events.value = schedData.map(s => ({
          id: s.id,
          name: s.title || 'Cuộc hẹn', // Backend returns patient_name as title
          patient_id: s.patient_id,
          date: new Date(s.start),
          time: new Date(s.start).toLocaleTimeString('vi-VN', {hour: '2-digit', minute:'2-digit'}),
          type: 'Khám', // Default or parse from notes if stored there
          notes: s.notes
        }));
      }
    }

    // Load Patients
    const patRes = await fetch(`${API_URL}/patients`);
    if (patRes.ok) {
      patients.value = await patRes.json();
    }

  } catch (e) {
    console.error("Error loading data:", e);
  }
}

async function saveEvent() {
  if (!doctorId.value) return;
  
  // Prevent duplicate submissions
  if (isSaving.value) {
    console.log('Already saving, please wait...');
    return;
  }

  const startDateTime = new Date(`${form.value.date}T${form.value.time}`);
  const endDateTime = new Date(startDateTime.getTime() + 60*60*1000); // 1 hour duration

  // Check for duplicate appointments (same patient, date, time)
  const isDuplicate = events.value.some(event => {
    const eventDate = new Date(event.date);
    return event.patient_id === form.value.patient_id &&
           eventDate.toDateString() === startDateTime.toDateString() &&
           event.time === form.value.time;
  });

  if (isDuplicate && !editingEvent.value) {
    alert('Lịch hẹn này đã tồn tại! Vui lòng chọn thời gian khác.');
    return;
  }

  const payload = {
    patient_id: form.value.patient_id,
    doctor_id: doctorId.value,
    start_time: startDateTime.toISOString(),
    end_time: endDateTime.toISOString(),
    notes: form.value.notes || form.value.type
  };

  try {
    isSaving.value = true; // Set saving state
    
    const res = await fetch(`${API_URL}/schedules`, {

      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      await loadData();
      closeModal();
    } else {
      alert("Lỗi khi tạo lịch hẹn");
    }
  } catch (e) {
    console.error(e);
    alert("Lỗi kết nối");
  } finally {
    // Reset saving state after a delay to prevent rapid clicks
    setTimeout(() => {
      isSaving.value = false;
    }, 500);
  }
}

async function deleteEvent() {
  if (!editingEvent.value) return;
  
  // Check if user has disabled delete confirmation
  const skipConfirmation = localStorage.getItem('skipDeleteConfirmation') === 'true';
  
  if (skipConfirmation) {
    // Directly delete without confirmation
    await performDelete();
  } else {
    // Show custom confirmation dialog
    eventToDelete.value = editingEvent.value;
    showDeleteConfirm.value = true;
  }
}

async function confirmDelete() {
  // Save preference if checkbox is checked
  if (dontShowDeleteConfirm.value) {
    localStorage.setItem('skipDeleteConfirmation', 'true');
  }
  
  // Close confirmation dialog
  showDeleteConfirm.value = false;
  
  // Perform the delete
  await performDelete();
  
  // Reset checkbox state
  dontShowDeleteConfirm.value = false;
  eventToDelete.value = null;
}

function cancelDelete() {
  showDeleteConfirm.value = false;
  eventToDelete.value = null;
  dontShowDeleteConfirm.value = false;
}

async function performDelete() {
  if (!editingEvent.value) return;

  try {
    const res = await fetch(`${API_URL}/schedules/${editingEvent.value.id}`, {

      method: 'DELETE'
    });

    if (res.ok) {
      await loadData();
      closeModal();
    } else {
      alert("Lỗi khi xóa lịch hẹn");
    }
  } catch (e) {
    console.error(e);
    alert("Lỗi kết nối");
  }
}

function edit(ev) {
  editingEvent.value = ev
  const offset = ev.date.getTimezoneOffset()
  const adjustedDate = new Date(ev.date.getTime() - (offset*60*1000))

  form.value = {
    patient_id: ev.patient_id,
    date: adjustedDate.toISOString().split('T')[0],
    time: ev.time,
    type: 'Khám', // Simplified
    notes: ev.notes
  }
  openNew.value = true
}

function resetDeleteConfirmation() {
  localStorage.removeItem('skipDeleteConfirmation')
  alert('✅ Đã bật lại xác nhận khi xóa cuộc hẹn!')
  // Force re-render by triggering a reactive update
  // The computed property will automatically update
}


onMounted(() => {
  setTimeout(() => {
    loadData();
  }, 500);
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
  height: 4px;
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
