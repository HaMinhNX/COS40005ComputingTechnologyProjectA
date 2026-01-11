<template>
  <div class="detail-container">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div class="flex items-center gap-4">
        <button @click="$emit('back')" class="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-500 hover:text-indigo-600">
          <ArrowLeft :size="24" />
        </button>
        <div>
          <h2 class="text-2xl font-black text-slate-900">{{ patient?.full_name || 'Chi tiết bệnh nhân' }}</h2>
          <div class="flex items-center gap-3 mt-1">
            <span class="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-700 text-xs font-bold uppercase tracking-wider">
              {{ patient?.role || 'Patient' }}
            </span>
            <span class="text-sm text-slate-500 font-medium">ID: {{ patientId }}</span>
          </div>
        </div>
      </div>
      
      <div class="flex gap-3">
        <button @click="currentTab = 'medical_record'" class="px-4 py-2 bg-white border border-slate-200 text-slate-600 rounded-xl font-bold text-sm hover:bg-slate-50 transition-colors flex items-center gap-2">
          <FileText :size="16" /> Hồ sơ bệnh án
        </button>
        <button @click="navigateToMessages" class="px-4 py-2 bg-indigo-600 text-white rounded-xl font-bold text-sm hover:bg-indigo-700 shadow-lg shadow-indigo-500/20 transition-colors flex items-center gap-2">
          <MessageSquare :size="16" /> Nhắn tin
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 mb-6 bg-slate-100 p-1 rounded-xl w-fit">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="currentTab = tab.id"
        :class="[
          'px-6 py-2.5 rounded-lg text-sm font-bold transition-all',
          currentTab === tab.id 
            ? 'bg-white text-indigo-600 shadow-sm' 
            : 'text-slate-500 hover:text-slate-700'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Content Area -->
    <div class="bg-white rounded-3xl border border-slate-100 shadow-sm p-6 min-h-[500px]">
      
      <!-- 1. OVERVIEW TAB -->
      <div v-if="currentTab === 'overview'">
        <PatientDashboard :userId="patientId" />
      </div>

      <!-- 2. MEDICAL RECORD TAB -->
      <div v-else-if="currentTab === 'medical_record'" class="space-y-6">
        <div class="flex justify-between items-center">
          <h3 class="text-xl font-bold text-slate-800">Hồ sơ bệnh án</h3>
          <button @click="saveMedicalRecord" class="px-4 py-2 bg-indigo-50 text-indigo-600 rounded-lg font-bold text-sm hover:bg-indigo-100">
            Lưu thay đổi
          </button>
        </div>
        
        <div class="grid grid-cols-2 gap-6">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-bold text-slate-500 mb-1">Chẩn đoán</label>
              <textarea v-model="medicalRecord.diagnosis" rows="3" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-indigo-500/20 outline-none"></textarea>
            </div>
            <div>
              <label class="block text-sm font-bold text-slate-500 mb-1">Triệu chứng</label>
              <textarea v-model="medicalRecord.symptoms" rows="3" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-indigo-500/20 outline-none"></textarea>
            </div>
          </div>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-bold text-slate-500 mb-1">Kế hoạch điều trị</label>
              <textarea v-model="medicalRecord.treatment_plan" rows="3" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-indigo-500/20 outline-none"></textarea>
            </div>
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-bold text-slate-500 mb-1">Chiều cao (cm)</label>
                <input v-model="medicalRecord.height_cm" type="number" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium outline-none" />
              </div>
              <div>
                <label class="block text-sm font-bold text-slate-500 mb-1">Cân nặng (kg)</label>
                <input v-model="medicalRecord.weight_kg" type="number" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium outline-none" />
              </div>
              <div>
                <label class="block text-sm font-bold text-slate-500 mb-1">Nhóm máu</label>
                <select v-model="medicalRecord.blood_type" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium outline-none">
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="AB">AB</option>
                  <option value="O">O</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. HISTORY TAB -->
      <div v-else-if="currentTab === 'history'">
        <h3 class="text-xl font-bold text-slate-800 mb-4">Lịch sử tập luyện</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs font-bold text-slate-500 uppercase border-b border-slate-100">
                <th class="py-3 px-4">Ngày & Giờ</th>
                <th class="py-3 px-4">Bài tập</th>
                <th class="py-3 px-4">Số reps</th>
                <th class="py-3 px-4">Đánh giá</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in historyLogs" :key="log.log_id" class="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                <td class="py-3 px-4 text-sm font-medium text-slate-900">
                  {{ formatDate(log.start_time) }}<br/>
                  <span class="text-xs text-slate-500">{{ formatTime(log.start_time) }} - {{ formatTime(log.end_time) }}</span>
                </td>
                <td class="py-3 px-4 text-sm text-slate-600 capitalize">{{ log.exercise_type }}</td>
                <td class="py-3 px-4 text-sm font-bold text-indigo-600">{{ log.rep_number }}</td>
                <td class="py-3 px-4">
                  <span class="px-2 py-1 rounded text-xs font-bold bg-emerald-100 text-emerald-700">{{ log.form_score }}%</span>
                </td>
              </tr>
              <tr v-if="historyLogs.length === 0">
                <td colspan="5" class="py-8 text-center text-slate-500">Chưa có dữ liệu lịch sử</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 4. NOTES TAB -->
      <div v-else-if="currentTab === 'notes'">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-bold text-slate-800">Ghi chú của bác sĩ</h3>
          <button @click="showAddNote = true" class="px-4 py-2 bg-indigo-600 text-white rounded-lg font-bold text-sm hover:bg-indigo-700 flex items-center gap-2">
            <Plus :size="16" /> Thêm ghi chú
          </button>
        </div>

        <!-- Add Note Form -->
        <div v-if="showAddNote" class="mb-6 p-4 bg-slate-50 rounded-xl border border-slate-200">
          <input v-model="newNote.title" placeholder="Tiêu đề" class="w-full mb-3 p-2 rounded-lg border border-slate-200 text-sm font-bold outline-none" />
          <textarea v-model="newNote.content" placeholder="Nội dung ghi chú..." rows="3" class="w-full mb-3 p-2 rounded-lg border border-slate-200 text-sm outline-none"></textarea>
          <div class="flex justify-end gap-2">
            <button @click="showAddNote = false" class="px-3 py-1.5 text-slate-500 text-sm font-bold hover:bg-slate-200 rounded-lg">Hủy</button>
            <button @click="saveNote" class="px-3 py-1.5 bg-indigo-600 text-white text-sm font-bold rounded-lg hover:bg-indigo-700">Lưu</button>
          </div>
        </div>

        <!-- Notes List -->
        <div class="space-y-4">
          <div v-for="note in notes" :key="note.note_id" class="p-4 border border-slate-100 rounded-xl hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start mb-2">
              <h4 class="font-bold text-slate-900">{{ note.title }}</h4>
              <span class="text-xs text-slate-400">{{ formatDate(note.created_at) }}</span>
            </div>
            <p class="text-sm text-slate-600">{{ note.content }}</p>
            <div class="mt-2 text-xs font-bold text-indigo-600">Bác sĩ: {{ note.doctor_name || 'Unknown' }}</div>
          </div>
          <div v-if="notes.length === 0" class="text-center py-8 text-slate-500">Chưa có ghi chú nào</div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ArrowLeft, FileText, MessageSquare, Plus } from 'lucide-vue-next'
import PatientDashboard from './PatientDashboard.vue'
import { API_BASE_URL } from '../config'

const props = defineProps(['patientId'])
const emit = defineEmits(['back'])


const currentTab = ref('overview')
const tabs = [
  { id: 'overview', label: 'Tổng quan' },
  { id: 'medical_record', label: 'Hồ sơ bệnh án' },
  { id: 'history', label: 'Lịch sử' },
  { id: 'notes', label: 'Ghi chú' }
]

const patient = ref(null)
const medicalRecord = ref({})
const historyLogs = ref([])
const notes = ref([])
const showAddNote = ref(false)
const newNote = ref({ title: '', content: '' })
const doctorId = ref(null)

// Fetch Data
const loadPatientInfo = async () => {
  // In a real app, we'd fetch specific patient info. For now, we iterate the list or assume passed prop is enough.
  // Let's try to find in the patients list
  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE_URL}/patients`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) {
      const data = await res.json();
      const patients = data.items || data;
      patient.value = patients.find(p => p.patient_id === props.patientId) || {};
    }
  } catch (e) { console.error(e); }
}

const loadMedicalRecord = async () => {
  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE_URL}/medical-records/${props.patientId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) medicalRecord.value = await res.json();
  } catch (e) { console.error(e); }
}

const loadHistory = async () => {
  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE_URL}/patient-logs/${props.patientId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) historyLogs.value = await res.json();
  } catch (e) { console.error(e); }
}

const loadNotes = async () => {
  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE_URL}/patient-notes/${props.patientId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) notes.value = await res.json();
  } catch (e) { console.error(e); }
}

const getDoctorId = async () => {
  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE_URL}/doctor/doctor-id`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) {
      const data = await res.json();
      doctorId.value = data.doctor_id;
    }
  } catch (e) { console.error(e); }
}

// Actions
const saveMedicalRecord = async () => {
  try {
    const payload = { ...medicalRecord.value };
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE_URL}/medical-records/${props.patientId}`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });
    if (res.ok) alert('Đã lưu hồ sơ bệnh án!');
  } catch (e) { alert('Lỗi khi lưu'); }
}

const saveNote = async () => {
  if (!doctorId.value) await getDoctorId();
  try {
    const payload = {
      patient_id: props.patientId,
      doctor_id: doctorId.value,
      title: newNote.value.title,
      content: newNote.value.content
    };
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE_URL}/patient-notes`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      await loadNotes();
      showAddNote.value = false;
      newNote.value = { title: '', content: '' };
    }
  } catch (e) { alert('Lỗi khi lưu ghi chú'); }
}

const navigateToMessages = () => {
  // Emit event to parent to switch to messages view, or use router
  // Since we don't have router setup in this snippet, we'll alert or try to emit
  alert("Chức năng nhắn tin đang được phát triển (Navigate to /messages)");
}

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('vi-VN', { day: 'numeric', month: 'numeric', year: 'numeric' });
}

const formatTime = (dateStr) => {
  if (!dateStr) return '--:--';
  return new Date(dateStr).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
}

// Watch tab change to load data
watch(currentTab, (newTab) => {
  if (newTab === 'medical_record') loadMedicalRecord();
  if (newTab === 'history') loadHistory();
  if (newTab === 'notes') loadNotes();
})

onMounted(() => {
  loadPatientInfo();
  getDoctorId();
})
</script>

<style scoped>
.detail-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
