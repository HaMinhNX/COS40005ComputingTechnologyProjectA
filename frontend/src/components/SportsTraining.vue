<template>
  <div class="h-full flex flex-col bg-slate-50 p-4 gap-4 overflow-hidden">
    <!-- Header -->
    <div class="flex justify-between items-center shrink-0">
      <div>
        <h1 class="text-2xl font-black text-slate-900 uppercase tracking-tight">
          Luyện Tập Thể Thao
        </h1>
        <p class="text-slate-600 font-medium text-sm">
          AI hỗ trợ chỉnh sửa tư thế & đếm số lần tập
        </p>
      </div>
      <div class="flex items-center gap-3">
        <div
          class="px-5 py-2 rounded-full font-bold text-sm tracking-wider flex items-center gap-2 transition-colors"
          :class="isCameraOn ? 'bg-red-100 text-red-600' : 'bg-slate-200 text-slate-500'"
        >
          <div
            class="w-2.5 h-2.5 rounded-full"
            :class="isCameraOn ? 'bg-red-600 animate-pulse' : 'bg-slate-400'"
          ></div>
          {{ isCameraOn ? 'ĐANG TẬP' : 'CHƯA BẮT ĐẦU' }}
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="flex-1 grid grid-cols-12 gap-4 min-h-0">
      <!-- LEFT: Video Feed (Larger, Horizontal) -->
      <div
        class="col-span-9 bg-black rounded-2xl overflow-hidden relative shadow-2xl flex items-center justify-center border-2 border-slate-800 aspect-video max-h-[75vh] mx-auto w-full"
      >
        <div class="w-full h-full relative">
          <video
            ref="videoEl"
            autoplay
            playsinline
            class="absolute inset-0 w-full h-full object-contain bg-black"
          ></video>
          <canvas ref="canvasEl" class="absolute inset-0 w-full h-full object-contain"></canvas>

          <!-- Overlay: Current Action Guidance (Top) -->
          <div
            v-if="isCameraOn"
            class="absolute top-4 left-1/2 -translate-x-1/2 px-6 py-3 rounded-2xl backdrop-blur-md bg-black/60 border border-white/20"
          >
            <p class="text-white font-bold text-xl tracking-wide text-center">
              {{ currentActionGuidance }}
            </p>
          </div>

          <!-- Overlay: Rep Counter (Top Right) -->
          <div
            v-if="isCameraOn"
            class="absolute top-4 right-4 bg-indigo-600 rounded-2xl px-6 py-4 shadow-2xl border-2 border-white/30"
          >
            <div class="text-white/80 text-xs font-bold uppercase tracking-widest mb-1">Số lần</div>
            <div class="flex items-baseline gap-2">
              <span class="text-6xl font-black text-white leading-none">{{ currentReps }}</span>
              <span class="text-2xl font-bold text-white/60">/ {{ effectiveTargetReps }}</span>
            </div>
          </div>

          <!-- Overlay: Form Feedback (Bottom) - Only shows after rep or errors -->
          <div
            v-if="isCameraOn && formFeedback"
            class="absolute bottom-4 left-1/2 -translate-x-1/2 px-8 py-4 rounded-2xl backdrop-blur-md shadow-2xl border-2 transition-all duration-300 max-w-2xl"
            :class="feedbackStyleClass"
          >
            <div class="flex items-center gap-3">
              <component :is="feedbackIcon" :size="32" class="shrink-0" />
              <p class="text-2xl font-black leading-tight">{{ formFeedback }}</p>
            </div>
          </div>

          <!-- Placeholder when camera is off -->
          <div
            v-if="!isCameraOn"
            class="absolute inset-0 flex flex-col items-center justify-center text-slate-400 bg-slate-900"
          >
            <Activity :size="100" class="opacity-20 mb-6" />
            <p class="text-2xl font-bold opacity-60 mb-2">Sẵn sàng luyện tập</p>
            <p class="text-sm opacity-40">Chọn bài tập và nhấn "BẮT ĐẦU TẬP"</p>
          </div>
        </div>
      </div>

      <!-- RIGHT: Controls & Exercise Selection -->
      <div class="col-span-3 flex flex-col gap-3 min-h-0">
        <!-- 1. Exercise Selection -->
        <div
          class="bg-white rounded-2xl p-4 shadow-lg border border-slate-200 flex-1 flex flex-col min-h-0"
        >
          <h3 class="font-bold text-slate-900 mb-3 flex items-center gap-2 text-sm">
            <Dumbbell :size="18" class="text-indigo-600" />
            Chọn bài tập
          </h3>
          <div class="overflow-y-auto pr-1 space-y-2 flex-1 custom-scrollbar">
            <button
              v-for="ex in exercises"
              :key="ex.id"
              @click="selectExercise(ex)"
              :disabled="isCameraOn"
              class="w-full p-3 rounded-xl border-2 transition-all flex items-start gap-3 text-left group disabled:opacity-50 disabled:cursor-not-allowed"
              :class="
                currentExercise?.id === ex.id
                  ? 'border-indigo-600 bg-indigo-50 shadow-md'
                  : 'border-slate-200 hover:border-indigo-300 bg-white hover:bg-slate-50'
              "
            >
              <div
                class="w-10 h-10 rounded-lg flex items-center justify-center transition-colors shrink-0"
                :class="
                  currentExercise?.id === ex.id
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-100 text-slate-400 group-hover:text-slate-600'
                "
              >
                <component :is="ex.icon" :size="20" />
              </div>
              <div class="flex-1 min-w-0">
                <div
                  class="font-bold text-sm"
                  :class="{
                    'text-indigo-700': currentExercise?.id === ex.id,
                    'text-slate-900': currentExercise?.id !== ex.id,
                  }"
                >
                  {{ ex.name }}
                </div>
                <div class="text-xs text-slate-500 leading-tight mt-0.5">{{ ex.desc }}</div>
              </div>
            </button>
          </div>
        </div>

        <!-- 2. Target Adjustment -->
        <div
          class="bg-white rounded-2xl p-3 flex items-center justify-between shadow-md border border-slate-200"
        >
          <button
            @click="adjustTarget(-5)"
            :disabled="isCameraOn"
            class="w-9 h-9 rounded-xl bg-slate-100 hover:bg-slate-200 flex items-center justify-center font-bold text-slate-700 transition-colors disabled:opacity-50"
          >
            -
          </button>
          <div class="text-center">
            <div class="text-xs text-slate-500 font-semibold">Mục tiêu</div>
            <div class="text-2xl font-black text-slate-900">{{ targetReps }}</div>
          </div>
          <button
            @click="adjustTarget(5)"
            :disabled="isCameraOn"
            class="w-9 h-9 rounded-xl bg-slate-100 hover:bg-slate-200 flex items-center justify-center font-bold text-slate-700 transition-colors disabled:opacity-50"
          >
            +
          </button>
        </div>

        <!-- 3. Start/Stop Button -->
        <button
          v-if="!isCameraOn"
          @click="startTraining"
          :disabled="!currentExercise"
          class="bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl py-4 font-black text-base shadow-xl flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
        >
          <Play :size="22" class="fill-current" />
          BẮT ĐẦU TẬP
        </button>
        <button
          v-else
          @click="stopTraining"
          class="bg-red-500 hover:bg-red-600 text-white rounded-2xl py-4 font-black text-base shadow-xl flex items-center justify-center gap-2 transition-all active:scale-95"
        >
          <Square :size="22" class="fill-current" />
          DỪNG LẠI
        </button>

        <!-- 4. Exercise Info Card -->
        <div v-if="currentExercise" class="bg-slate-100 rounded-2xl p-4 border border-slate-200">
          <div class="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1">
            Đang chọn
          </div>
          <div class="text-lg font-black text-slate-900">{{ currentExercise.name }}</div>
          <div class="text-xs text-slate-600 mt-1">{{ currentExercise.desc }}</div>
        </div>
      </div>
    </div>

    <!-- Session Complete Overlay -->
    <div
      v-if="sessionComplete"
      class="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 animate-fade-in"
    >
      <div
        class="bg-white rounded-[32px] p-10 text-center max-w-md w-full shadow-2xl transform transition-all animate-bounce-in"
      >
        <div
          class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-5"
        >
          <CheckCircle :size="48" class="text-green-600" stroke-width="3" />
        </div>
        <h2 class="text-3xl font-black text-slate-900 mb-2">XUẤT SẮC!</h2>
        <p class="text-slate-500 text-lg font-medium mb-6">Bạn đã hoàn thành mục tiêu.</p>

        <div class="bg-indigo-50 rounded-2xl p-5 mb-6 border border-indigo-100">
          <div class="grid grid-cols-2 gap-4">
            <div class="text-left">
              <div class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
                Bài tập
              </div>
              <div class="text-base font-black text-slate-900">{{ currentExercise?.name }}</div>
            </div>
            <div class="text-right">
              <div class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
                Hoàn thành
              </div>
              <div class="text-2xl font-black text-indigo-600">{{ currentReps }}</div>
            </div>
          </div>
        </div>

        <button
          @click="resetSession"
          class="w-full py-4 bg-indigo-600 text-white rounded-2xl font-bold text-lg hover:bg-indigo-700 transition-all shadow-xl active:scale-95"
        >
          Tập tiếp bài khác
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, computed } from 'vue'
import { FilesetResolver, PoseLandmarker, DrawingUtils } from '@mediapipe/tasks-vision'
import {
  Play,
  Square,
  Activity,
  Dumbbell,
  ArrowUp,
  User,
  CheckCircle,
  AlertCircle,
  ThumbsUp,
  Zap,
} from 'lucide-vue-next'
import { CAMERA_API_URL } from '../config'

// Audio Feedback System
let lastSpokenText = ''
let lastSpokenAt = 0
const SPEAK_COOLDOWN_MS = 1200

const normalizeSpeech = (text) =>
  String(text || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ')

const localizeFeedbackText = (text) => {
  const source = String(text || '').trim()
  if (!source) return ''

  const phraseMap = {
    'Deeper hip bend!': 'Gập hông sâu hơn!',
    'Even squat': 'Giữ hai bên đều nhau',
    'Lower hips!': 'Hạ hông thấp hơn!',
    'Lean forward': 'Hơi đổ người ra trước',
    'Less lean': 'Giữ lưng thẳng hơn',
  }

  const mapped = source
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => {
      if (phraseMap[part]) return phraseMap[part]

      const holdMatch = part.match(/^Hold longer \(([^)]+)\)$/i)
      if (holdMatch) {
        const duration = holdMatch[1].replace(/s$/i, '').trim()
        return `Giữ lâu hơn (${duration} giây)`
      }

      return part
    })
    .join('. ')

  return mapped
    .replace(/\bleft\b/gi, 'trái')
    .replace(/\bright\b/gi, 'phải')
    .replace(/\barm\b/gi, 'tay')
    .replace(/\bleg\b/gi, 'chân')
    .replace(/\s+/g, ' ')
    .trim()
}

const speak = (text, force = false) => {
  if (!window.speechSynthesis) return
  const normalized = normalizeSpeech(text)
  if (!normalized) return

  const now = Date.now()
  if (!force) {
    if (normalized === lastSpokenText) return
    if (now - lastSpokenAt < SPEAK_COOLDOWN_MS) return
  }

  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'vi-VN'
  utterance.rate = 1.1
  window.speechSynthesis.speak(utterance)
  lastSpokenText = normalized
  lastSpokenAt = now
}

// Exercise definitions - ALL 4 EXERCISES
const exercises = [
  { id: 'squat', name: 'Squat', desc: 'Đứng lên ngồi xuống', icon: Activity },
  { id: 'bicep-curl', name: 'Bicep Curl', desc: 'Gập bắp tay', icon: Dumbbell },
  {
    id: 'shoulder-flexion',
    name: 'Shoulder Press',
    desc: 'Nâng 2 tay lên cao (tập vai)',
    icon: ArrowUp,
  },
  { id: 'knee-raise', name: 'Knee Raise', desc: 'Nâng đầu gối + tay đối diện', icon: User },
]

const currentExercise = ref(exercises[0])
const targetReps = ref(10)
const currentReps = ref(0)
const isCameraOn = ref(false)
const sessionComplete = ref(false)

// NEW: Improved Feedback System
const currentActionGuidance = ref('Sẵn sàng...') // What to do NOW (always visible)
const formFeedback = ref('') // Corrections/errors (sticky, shows after rep)
const feedbackType = ref('neutral') // 'success', 'warning', 'error', 'neutral'
let feedbackTimeout = null

// Feedback styling
const feedbackStyleClass = computed(() => {
  const baseClass = 'border-2 '
  switch (feedbackType.value) {
    case 'success':
      return baseClass + 'bg-emerald-500/95 border-emerald-300 text-white'
    case 'warning':
      return baseClass + 'bg-amber-500/95 border-amber-300 text-white'
    case 'error':
      return baseClass + 'bg-red-500/95 border-red-300 text-white'
    default:
      return baseClass + 'bg-slate-700/95 border-slate-500 text-white'
  }
})

const feedbackIcon = computed(() => {
  switch (feedbackType.value) {
    case 'success':
      return ThumbsUp
    case 'warning':
      return AlertCircle
    case 'error':
      return AlertCircle
    default:
      return Zap
  }
})

const effectiveTargetReps = computed(() => {
  const parsed = Number(targetReps.value)
  if (!Number.isFinite(parsed) || parsed <= 0) return 1
  return parsed
})

// Camera & AI
const videoEl = ref(null)
const canvasEl = ref(null)
let poseLandmarker = null
let animationFrameId = null
let lastProcessTime = 0
let isProcessing = false
const PROCESS_INTERVAL = 100 // Process every 100ms

// State tracking
let previousReps = 0
let lastCorrectionText = ''

function selectExercise(ex) {
  if (isCameraOn.value) return
  currentExercise.value = ex
}

function adjustTarget(delta) {
  const newVal = targetReps.value + delta
  if (newVal >= 5 && newVal <= 100) targetReps.value = newVal
}

function resetSession() {
  sessionComplete.value = false
  currentReps.value = 0
  previousReps = 0
  lastCorrectionText = ''
  lastSpokenText = ''
  lastSpokenAt = 0
  currentActionGuidance.value = 'Sẵn sàng...'
  formFeedback.value = ''
  feedbackType.value = 'neutral'
  if (window.speechSynthesis) window.speechSynthesis.cancel()
  stopCamera()
}

async function startTraining() {
  if (!currentExercise.value) return
  currentReps.value = 0
  previousReps = 0
  lastCorrectionText = ''
  lastSpokenText = ''
  lastSpokenAt = 0
  sessionComplete.value = false
  currentActionGuidance.value = 'Đang khởi động...'
  formFeedback.value = ''

  if (window.speechSynthesis) window.speechSynthesis.cancel()

  try {
    const token = localStorage.getItem('token')
    // Reset backend state
    await fetch(`${CAMERA_API_URL}/select_exercise?exercise_name=${currentExercise.value.id}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
  } catch {
    console.error('Failed to reset backend state')
  }

  await startCamera()
}

function stopTraining() {
  stopCamera()
  if (window.speechSynthesis) window.speechSynthesis.cancel()
  currentActionGuidance.value = 'Đã dừng'
  formFeedback.value = ''
  feedbackType.value = 'neutral'
}

async function createPoseLandmarker() {
  const vision = await FilesetResolver.forVisionTasks(
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm',
  )
  poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task`,
      delegate: 'GPU',
    },
    runningMode: 'VIDEO',
    numPoses: 1,
  })
}

async function startCamera() {
  try {
    if (!poseLandmarker) await createPoseLandmarker()
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        aspectRatio: 16 / 9,
      },
    })
    if (videoEl.value) {
      videoEl.value.srcObject = stream
      videoEl.value.removeEventListener('loadeddata', predictWebcam)
      videoEl.value.addEventListener('loadeddata', predictWebcam, { once: true })
      isCameraOn.value = true
    }
  } catch {
    console.error('Camera error')
    alert('Không thể mở camera. Vui lòng kiểm tra quyền truy cập.')
  }
}

function stopCamera() {
  isCameraOn.value = false
  if (videoEl.value && videoEl.value.srcObject) {
    videoEl.value.removeEventListener('loadeddata', predictWebcam)
    videoEl.value.srcObject.getTracks().forEach((track) => track.stop())
    videoEl.value.srcObject = null
  }
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  animationFrameId = null
  isProcessing = false
  lastProcessTime = 0
}

async function predictWebcam() {
  if (!isCameraOn.value || !videoEl.value || !canvasEl.value) return

  let startTimeMs = performance.now()
  let results
  try {
    results = await poseLandmarker.detectForVideo(videoEl.value, startTimeMs)
  } catch {
    return
  }

  const canvas = canvasEl.value
  const ctx = canvas.getContext('2d')

  if (canvas.width !== videoEl.value.videoWidth || canvas.height !== videoEl.value.videoHeight) {
    canvas.width = videoEl.value.videoWidth
    canvas.height = videoEl.value.videoHeight
  }

  ctx.save()
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  if (results.landmarks && results.landmarks.length > 0) {
    const landmarks = results.landmarks[0]
    const drawingUtils = new DrawingUtils(ctx)

    drawingUtils.drawLandmarks(landmarks, { color: '#FFFFFF', lineWidth: 2, radius: 4 })
    drawingUtils.drawConnectors(landmarks, PoseLandmarker.POSE_CONNECTIONS, {
      color: '#00FF00',
      lineWidth: 4,
    })

    const now = Date.now()
    if (!isProcessing && now - lastProcessTime > PROCESS_INTERVAL) {
      isProcessing = true
      processLandmarks(landmarks).finally(() => {
        isProcessing = false
        lastProcessTime = Date.now()
      })
    }
  }
  ctx.restore()
  animationFrameId = requestAnimationFrame(predictWebcam)
}

async function processLandmarks(landmarks) {
  const landmarkData = landmarks.map((lm) => ({
    x: lm.x,
    y: lm.y,
    z: lm.z,
    visibility: lm.visibility,
  }))

  try {
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : null

    const token = localStorage.getItem('token')
    const res = await fetch(`${CAMERA_API_URL}/process_landmarks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        landmarks: landmarkData,
        current_exercise: currentExercise.value.id,
        user_id: user?.user_id || null,
      }),
    })

    if (!res.ok) return
    const data = await res.json()
    const localizedFeedback = localizeFeedbackText(data.feedback)

    let newReps = 0
    if (currentExercise.value.id === 'squat') newReps = data.squat_count
    else if (currentExercise.value.id === 'bicep-curl') newReps = data.curl_count
    else if (currentExercise.value.id === 'shoulder-flexion') newReps = data.shoulder_flexion_count
    else if (currentExercise.value.id === 'knee-raise') newReps = data.knee_raise_count

    updateActionGuidance(data, localizedFeedback)

    const stableReps = Math.max(newReps || 0, previousReps)
    const repCompleted = stableReps > previousReps
    if (repCompleted) {
      previousReps = stableReps
      setFormFeedback('XUẤT SẮC! 👍', 'success', 2000)
      lastCorrectionText = ''
      speak(`${stableReps}`, true)
    } else {
      const feedbackText = localizedFeedback
      const hasUsefulFeedback = feedbackText && !feedbackText.includes('Sẵn sàng')
      if (
        hasUsefulFeedback &&
        feedbackText !== currentActionGuidance.value &&
        feedbackText !== lastCorrectionText
      ) {
        setFormFeedback(feedbackText, 'warning', 2000)
        lastCorrectionText = feedbackText
        if (feedbackText.length > 5) speak(feedbackText)
      }
    }

    currentReps.value = stableReps

    if (currentReps.value >= effectiveTargetReps.value && !sessionComplete.value) {
      sessionComplete.value = true
      speak('Chúc mừng! Bạn đã hoàn thành bài tập.', true)
      stopCamera()
      return
    }
  } catch {
    console.error('Process error')
  }
}

function setFormFeedback(message, type, duration) {
  formFeedback.value = message
  feedbackType.value = type
  if (feedbackTimeout) clearTimeout(feedbackTimeout)
  feedbackTimeout = setTimeout(() => {
    formFeedback.value = ''
    feedbackType.value = 'neutral'
  }, duration)
}

function updateActionGuidance(data, localizedFeedback = '') {
  const stateGuidanceMap = {
    squat: {
      IDLE: 'Đứng thẳng, chân rộng bằng vai, siết cơ bụng',
      SQUAT_START: 'Đẩy hông ra sau và hạ người xuống chậm',
      SQUAT_DOWN: 'Giữ gối mở theo hướng mũi chân',
      SQUAT_HOLD: 'Giữ ổn định',
      SQUAT_UP: 'Đạp gót chân, đứng lên dứt khoát',
    },
    'bicep-curl': {
      IDLE: 'Duỗi tay sát thân, giữ khuỷu tay cố định',
      CURL_START: 'Gập khuỷu tay, nâng tạ lên ngang ngực',
      CURL_UP: 'Siết bắp tay, giữ ngắn rồi hạ xuống',
      CURL_HOLD: 'Giữ ngắn',
      CURL_DOWN: 'Hạ tay chậm và có kiểm soát',
    },
    'shoulder-flexion': {
      IDLE: 'Hạ tay xuống, duỗi thẳng khuỷu tay',
      FLEXION_START: 'Nâng tay thẳng lên phía trước',
      FLEXION_UP: 'Giữ vai ổn định, không nhún vai',
      FLEXION_DOWN: 'Hạ tay từ từ về vị trí ban đầu',
    },
    'knee-raise': {
      IDLE: 'Đứng thẳng, giữ core và nhìn thẳng',
      RAISE_START: 'Nâng gối và tay đối diện lên cùng lúc',
      RAISE_UP: 'Siết bụng, giữ nhịp rồi hạ xuống',
      RAISE_DOWN: 'Trở về tư thế chuẩn bị',
    },
  }

  let currentStateName = ''
  if (currentExercise.value.id === 'squat') currentStateName = data.squat_state_name
  else if (currentExercise.value.id === 'bicep-curl') currentStateName = data.curl_state_name
  else if (currentExercise.value.id === 'shoulder-flexion')
    currentStateName = data.shoulder_flexion_state_name
  else if (currentExercise.value.id === 'knee-raise') currentStateName = data.knee_raise_state_name

  const mappedGuidance = stateGuidanceMap[currentExercise.value.id]?.[currentStateName]
  if (mappedGuidance) {
    if (currentActionGuidance.value !== mappedGuidance) {
      currentActionGuidance.value = mappedGuidance

      // Speak only on actionable guidance transitions, skip idle/hold to reduce noise.
      const quietStates = ['IDLE', 'SQUAT_HOLD', 'CURL_HOLD']
      if (!quietStates.includes(currentStateName)) {
        speak(mappedGuidance)
      }
    }
    return
  }

  if (
    typeof localizedFeedback === 'string' &&
    localizedFeedback.length > 0 &&
    localizedFeedback.length <= 100
  ) {
    currentActionGuidance.value = localizedFeedback
    return
  }

  if (!currentActionGuidance.value || currentActionGuidance.value.includes('Sẵn sàng')) {
    currentActionGuidance.value = 'Giữ tư thế chuẩn bị'
  }
}

onUnmounted(() => {
  stopCamera()
  if (feedbackTimeout) clearTimeout(feedbackTimeout)
  if (window.speechSynthesis) window.speechSynthesis.cancel()
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
  border-radius: 20px;
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

@keyframes bounce-in {
  0% {
    transform: scale(0.9);
    opacity: 0;
  }
  60% {
    transform: scale(1.05);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
.animate-bounce-in {
  animation: bounce-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
</style>
