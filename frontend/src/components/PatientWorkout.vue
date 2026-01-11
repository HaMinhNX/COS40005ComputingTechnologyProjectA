<template>
  <div class="workout-container">
    <!-- 1. LOADING STATE -->
    <div v-if="sessionState === 'loading'" class="state-screen loading-screen">
      <div class="spinner"></div>
      <p>Đang tải kế hoạch tập luyện...</p>
    </div>

    <!-- 2. OVERVIEW STATE -->
    <div v-else-if="sessionState === 'overview'" class="state-screen overview-screen">
      <div class="overview-card">
        <div class="overview-header">
          <h2>Kế hoạch hôm nay</h2>
          <p>{{ todayDate }}</p>
        </div>
        
        <div v-if="planItems.length === 0" class="empty-plan">
          <div class="empty-icon"><Calendar :size="48" /></div>

          <h3>Không có bài tập nào hôm nay</h3>
          <p>Hãy nghỉ ngơi hoặc liên hệ bác sĩ của bạn.</p>
        </div>

        <div v-else class="plan-list">
          <div v-for="(item, idx) in planItems" :key="idx" class="plan-item">
            <div class="item-icon">
              <component :is="getIcon(item.name)" :size="24" />
            </div>

            <div class="item-info">
              <h4>{{ item.name }}</h4>
              <p>{{ item.instructions || 'Thực hiện theo hướng dẫn' }}</p>
            </div>
            <div class="item-target">
              <span v-if="item.is_completed" class="text-emerald-600 font-bold flex items-center gap-1">
                <Check :size="16" /> Đã hoàn thành
              </span>

              <span v-else>
                {{ formatTarget(item) }}
              </span>
            </div>
          </div>
        </div>

        <button v-if="planItems.length > 0" @click="startSession" class="btn-primary btn-xl">
          BẮT ĐẦU TẬP LUYỆN
        </button>
      </div>
    </div>

    <!-- 3. INSTRUCTION STATE -->
    <div v-else-if="sessionState === 'instruction'" class="state-screen instruction-screen">
      <div class="instruction-card">
        <div class="instruction-icon">
          <component :is="getIcon(currentStep.name)" :size="48" />
        </div>

        <h2>{{ currentStep.name }}</h2>
        <div class="instruction-content">
          <p class="instruction-text">{{ currentStep.instructions }}</p>
          <div class="target-box">
            <span>Mục tiêu:</span>
            <strong>{{ formatTarget(currentStep) }}</strong>
          </div>
        </div>
        <button @click="startStep" class="btn-primary btn-lg">
          SẴN SÀNG
        </button>
      </div>
    </div>

    <!-- 4. EXERCISING STATE -->
    <div v-else-if="sessionState === 'exercising'" class="exercise-screen">
      
      <!-- BRAIN GAME -->
      <div v-if="currentStep.type === 'brain_game'" class="brain-game-wrapper">
        <BrainExercise 
          :userId="props.userId" 
          mode="flow" 
          @completed="handleBrainGameComplete" 
        />
      </div>

      <!-- PHYSICAL EXERCISE (CAMERA) -->
      <div v-else class="layout-wrapper">
        <!-- VIDEO FEED (LARGE, HORIZONTAL) -->
        <div class="video-section">
          <div class="video-card" :class="{ 'camera-active': isCameraOn }">
            <div class="video-header">
              <div class="live-indicator" v-if="isCameraOn">
                <span class="blink-dot"></span> LIVE
              </div>
              <div class="camera-status" v-else>Camera Off</div>
              <div class="exercise-badge">{{ currentStep.name }}</div>
            </div>

            <div class="video-frame">
              <video ref="videoEl" autoplay playsinline></video>
              <canvas ref="canvasEl"></canvas>
              
              <div v-if="isLoadingCamera" class="loading-overlay">
                <div class="spinner"></div>
                <p>Đang khởi động camera...</p>
              </div>
            </div>
          </div>
        </div>

        <!-- STATS & FEEDBACK PANEL -->
        <div class="stats-panel">
          <!-- REP COUNTER (MASSIVE) -->
          <div class="rep-counter-card">
            <div class="counter-label">Số lần</div>
            <div class="counter-display">
              <span class="current-count">{{ currentReps }}</span>
              <span class="target-count">/ {{ currentStep.target }}</span>
            </div>
            <div class="progress-ring">
              <svg width="200" height="200">
                <circle cx="100" cy="100" r="90" fill="none" stroke="#e2e8f0" stroke-width="12"/>
                <circle 
                  cx="100" cy="100" r="90" fill="none" 
                  stroke="#6366f1" stroke-width="12"
                  :stroke-dasharray="565.48"
                  :stroke-dashoffset="565.48 * (1 - (currentReps / currentStep.target))"
                  transform="rotate(-90 100 100)"
                  style="transition: stroke-dashoffset 0.3s ease"
                />
              </svg>
            </div>
          </div>

          <!-- FEEDBACK DISPLAY (LARGE) -->
          <div class="feedback-card" :class="feedbackClass">
            <div class="feedback-header">
              <span class="feedback-icon-large">
                <component :is="feedbackIcon" :size="32" />
              </span>
              <span class="feedback-label">Hướng dẫn</span>
            </div>

            <div class="feedback-message">{{ feedbackText }}</div>
          </div>

          <!-- CONTROLS -->
          <div class="action-controls">
            <button @click="skipStep" class="btn-skip">
              <FastForward :size="20" /> Bỏ qua bài này
            </button>

          </div>

          <!-- PROGRESS -->
          <div class="session-progress">
            <div class="progress-bar-container">
              <div class="progress-bar-fill" :style="{ width: progressPercent + '%' }"></div>
            </div>
            <p class="progress-text">Bài {{ currentStepIndex + 1 }} / {{ planItems.length }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 5. SUMMARY STATE -->
    <div v-else-if="sessionState === 'summary'" class="state-screen summary-screen">
      <div class="summary-card">
        <div class="summary-icon"><Trophy :size="64" class="text-indigo-600" /></div>

        <h2>Hoàn thành buổi tập!</h2>
        <p>Bạn đã hoàn thành xuất sắc kế hoạch hôm nay.</p>
        
        <div class="summary-stats">
          <div class="stat-item">
            <span class="stat-val">{{ planItems.length }}</span>
            <span class="stat-lbl">Bài tập</span>
          </div>
          <div class="stat-item">
            <span class="stat-val">{{ totalDurationFormatted }}</span>
            <span class="stat-lbl">Thời gian</span>
          </div>
        </div>

        <button @click="finishSession" class="btn-primary btn-lg">
          Về trang chủ
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { FilesetResolver, PoseLandmarker, DrawingUtils } from '@mediapipe/tasks-vision';
import BrainExercise from './BrainExercise.vue';
import { API_BASE_URL, CAMERA_API_URL } from '../config';
import { 
  Dumbbell, 
  Activity, 
  User, 
  Brain, 
  Timer, 
  CheckCircle2, 
  AlertCircle, 
  ChevronRight,
  Play,
  Calendar,
  Info,
  Trophy,
  FastForward,
  Loader2,
  Check,
  X,
  Clock
} from 'lucide-vue-next';


const props = defineProps(['userId']);
const API_URL = API_BASE_URL;
const CAMERA_BASE = CAMERA_API_URL;


// State
const sessionState = ref('loading'); // loading, overview, instruction, exercising, summary
const planItems = ref([]);
const currentStepIndex = ref(0);
const sessionId = ref(null);
const sessionStartTime = ref(null);
const stepStartTime = ref(null);

// Exercise State
const currentReps = ref(0);
const feedbackText = ref('Sẵn sàng...');
const feedbackClass = ref('fb-neutral');
const feedbackIcon = ref(markRaw(Info));


// Camera State
const videoEl = ref(null);
const canvasEl = ref(null);
const isCameraOn = ref(false);
const isLoadingCamera = ref(false);
let poseLandmarker = null;
let animationFrameId = null;
let lastProcessTime = 0;
let isProcessing = false;
const PROCESS_INTERVAL = 200; // ms

// Computed
const currentStep = computed(() => planItems.value[currentStepIndex.value] || {});
const todayDate = computed(() => new Date().toLocaleDateString('vi-VN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }));
const progressPercent = computed(() => ((currentStepIndex.value + 1) / planItems.value.length) * 100);
const totalDurationFormatted = computed(() => {
  if (!sessionStartTime.value) return '0p';
  const diff = Math.floor((Date.now() - sessionStartTime.value) / 1000);
  const m = Math.floor(diff / 60);
  const s = diff % 60;
  return `${m}p ${s}s`;
});

// Exercise Name Mapping - Convert Vietnamese/Display names to Backend API keys
const EXERCISE_MAPPING = {
  // Vietnamese names
  'Đứng lên ngồi xuống': 'squat',
  'Gập bắp tay': 'bicep-curl',
  'Nâng 2 tay lên cao liên tục để tập vai': 'shoulder-flexion',
  'Nâng 2 tay lên cao liên tục để tập tay cùng nâng đầu gối so le chân và tay': 'knee-raise',
  // English names
  'Squat': 'squat',
  'Bicep Curl': 'bicep-curl',
  'Shoulder Flexion': 'shoulder-flexion',
  'Knee Raise': 'knee-raise',
  // Lowercase variants
  'squat': 'squat',
  'bicep curl': 'bicep-curl',
  'shoulder flexion': 'shoulder-flexion',
  'knee raise': 'knee-raise',
};

const mapExerciseName = (name) => {
  if (!name) return null;
  
  // Direct mapping
  if (EXERCISE_MAPPING[name]) {
    return EXERCISE_MAPPING[name];
  }
  
  // Keyword-based fallback
  const lowerName = name.toLowerCase();
  if (lowerName.includes('squat') || lowerName.includes('ngồi xuống') || lowerName.includes('đứng lên')) {
    return 'squat';
  }
  if (lowerName.includes('curl') || lowerName.includes('bắp tay') || lowerName.includes('gập')) {
    return 'bicep-curl';
  }
  if (lowerName.includes('shoulder') || lowerName.includes('vai')) {
    return 'shoulder-flexion';
  }
  if (lowerName.includes('knee') || lowerName.includes('đầu gối')) {
    return 'knee-raise';
  }
  
  console.warn(`[EXERCISE MAPPING] Unknown exercise name: "${name}"`);
  return null;
};

// Icons
const getIcon = (name) => {
  if (!name) return markRaw(Info);
  const mappedName = mapExerciseName(name) || name.toLowerCase();
  if (mappedName.includes('squat') || name.includes('ngồi')) return markRaw(Dumbbell);
  if (mappedName.includes('curl') || name.includes('bắp')) return markRaw(Activity);
  if (mappedName.includes('shoulder') || name.includes('vai')) return markRaw(User);
  if (mappedName.includes('knee') || name.includes('gối')) return markRaw(Activity);
  if (name.includes('Brain') || name.includes('Trí tuệ')) return markRaw(Brain);
  return markRaw(Activity);
};


const formatTarget = (item) => {
  if (item.type === 'brain_game') return `${item.target} điểm`;
  
  if (item.duration_seconds > 0) {
    return `${Math.round(item.duration_seconds / 60)} phút`;
  }
  
  if (item.sets > 1) {
    return `${item.sets} hiệp x ${item.target} lần`;
  }
  
  return `${item.target} lần`;
};

// === API & FLOW ===

const loadPlan = async () => {
  if (!props.userId) {
    console.warn("No user ID provided for workout plan");
    sessionState.value = 'overview';
    return;
  }
  sessionState.value = 'loading';
  try {
    const res = await fetch(`${API_URL}/patient/today/${props.userId}`);
    if (res.ok) {
      planItems.value = await res.json();
    }
  } catch (e) {
    console.error(e);
  } finally {
    sessionState.value = 'overview';
  }
};

const startSession = async () => {
  try {
    const res = await fetch(`${API_URL}/session/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: props.userId })
    });
    if (res.ok) {
      const data = await res.json();
      sessionId.value = data.session_id;
      sessionStartTime.value = Date.now();
      currentStepIndex.value = 0;
      sessionState.value = 'instruction';
    }
  } catch (e) {
    console.error(e);
  }
};

const startStep = async () => {
  sessionState.value = 'exercising';
  currentReps.value = 0;
  feedbackText.value = 'Bắt đầu!';
  
  if (currentStep.value.type === 'exercise') {
    const exerciseType = mapExerciseName(currentStep.value.name);
    if (exerciseType) {
      try {
        await fetch(`${CAMERA_BASE}/select_exercise?exercise_name=${exerciseType}`, { method: 'POST' });
      } catch (e) { console.error(e); }
    }
    await startCamera();
  }
  stepStartTime.value = Date.now();
};


const logStep = async (data) => {
  if (!sessionId.value) return;
  try {
    await fetch(`${API_URL}/session/log`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId.value,
        exercise_type: currentStep.value.name,
        reps_completed: data.reps || currentReps.value,
        duration_seconds: stepStartTime.value ? Math.floor((Date.now() - stepStartTime.value) / 1000) : 0,
        mistakes_count: data.mistakes || 0,
        accuracy_score: data.accuracy || 100
      })
    });
  } catch (e) { console.error(e); }
};

const nextStep = () => {
  if (currentStepIndex.value < planItems.value.length - 1) {
    currentStepIndex.value++;
    sessionState.value = 'instruction';
  } else {
    endSession();
  }
};

const skipStep = () => {
  stopCamera();
  nextStep();
};

const endSession = async () => {
  if (sessionId.value) {
    try {
      await fetch(`${API_URL}/session/end/${sessionId.value}`, { method: 'POST' });
    } catch (e) { console.error(e); }
  }
  sessionState.value = 'summary';
};

const finishSession = () => {
  // Reload or emit event to parent to go back to dashboard
  window.location.reload(); 
};

// === BRAIN GAME HANDLER ===
const handleBrainGameComplete = async (result) => {
  await logStep({ reps: result.score, accuracy: (result.score / result.total) * 100 });
  nextStep();
};

// === CAMERA & MEDIAPIPE ===

const createPoseLandmarker = async () => {
  const vision = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm"
  );
  poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task`,
      delegate: "GPU"
    },
    runningMode: "VIDEO",
    numPoses: 1
  });
};

const startCamera = async () => {
  isLoadingCamera.value = true;
  try {
    if (!poseLandmarker) await createPoseLandmarker();
    
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    if (videoEl.value) {
      videoEl.value.srcObject = stream;
      videoEl.value.addEventListener("loadeddata", predictWebcam);
      isCameraOn.value = true;
    }
  } catch (e) {
    console.error("Camera Error:", e);
    feedbackText.value = "Lỗi Camera!";
  } finally {
    isLoadingCamera.value = false;
  }
};

const stopCamera = () => {
  isCameraOn.value = false;
  if (videoEl.value && videoEl.value.srcObject) {
    videoEl.value.srcObject.getTracks().forEach(track => track.stop());
    videoEl.value.srcObject = null;
  }
  if (animationFrameId) cancelAnimationFrame(animationFrameId);
};

const predictWebcam = async () => {
  if (!isCameraOn.value || !videoEl.value || !canvasEl.value) return;

  let startTimeMs = performance.now();
  let results;
  
  try {
    results = await poseLandmarker.detectForVideo(videoEl.value, startTimeMs);
  } catch (e) { return; }

  const canvas = canvasEl.value;
  const ctx = canvas.getContext('2d');
  canvas.width = videoEl.value.videoWidth;
  canvas.height = videoEl.value.videoHeight;
  
  ctx.save();
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (results.landmarks && results.landmarks.length > 0) {
    const landmarks = results.landmarks[0];
    const drawingUtils = new DrawingUtils(ctx);
    
    drawingUtils.drawLandmarks(landmarks, { color: '#FFFFFF', lineWidth: 2, radius: 4, fillColor: '#FF0000' });
    drawingUtils.drawConnectors(landmarks, PoseLandmarker.POSE_CONNECTIONS, { color: '#00FF00', lineWidth: 4 });

    // Throttled Backend Call
    const now = Date.now();
    if (!isProcessing && (now - lastProcessTime > PROCESS_INTERVAL)) {
      isProcessing = true;
      processLandmarks(landmarks).finally(() => {
        isProcessing = false;
        lastProcessTime = Date.now();
      });
    }
  }
  ctx.restore();
  animationFrameId = requestAnimationFrame(predictWebcam);
};

const processLandmarks = async (landmarks) => {
  const landmarkData = landmarks.map(lm => ({
    x: lm.x, y: lm.y, z: lm.z, visibility: lm.visibility
  }));

  try {
    // Map exercise name to backend API format
    const exerciseType = mapExerciseName(currentStep.value.name);
    
    if (!exerciseType) {
      console.error(`[EXERCISE ERROR] Cannot map exercise: "${currentStep.value.name}"`);
      feedbackText.value = "Lỗi: Không nhận diện được bài tập";
      return;
    }

    const res = await fetch(`${CAMERA_BASE}/process_landmarks`, {

      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        landmarks: landmarkData,
        current_exercise: exerciseType,
        user_id: props.userId
      })
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error(`[API ERROR] ${res.status}: ${errorText}`);
      return;
    }
    
    const data = await res.json();
    
    // Update Reps based on exercise type
    let newReps = 0;
    if (exerciseType === 'squat') newReps = data.squat_count;
    else if (exerciseType === 'bicep-curl') newReps = data.curl_count;
    else if (exerciseType === 'shoulder-flexion') newReps = data.shoulder_flexion_count;
    else if (exerciseType === 'knee-raise') newReps = data.knee_raise_count;
    
    // Check if reps increased
    if (newReps > currentReps.value) {
      currentReps.value = newReps;
      // Check target
      if (currentReps.value >= currentStep.value.target) {
        // Complete Step
        stopCamera();
        await logStep({ reps: currentReps.value });
        nextStep();
      }
    }

    if (data.feedback) {
      feedbackText.value = data.feedback;
      // Simple feedback classification
      if (data.feedback.includes('Good') || data.feedback.includes('Tốt') || data.feedback.includes('TỐT')) {
        feedbackClass.value = 'fb-success';
        feedbackIcon.value = markRaw(CheckCircle2);
      } else if (data.feedback.includes('!') || data.feedback.includes('⚠')) {
        feedbackClass.value = 'fb-warning';
        feedbackIcon.value = markRaw(AlertCircle);
      } else {
        feedbackClass.value = 'fb-neutral';
        feedbackIcon.value = markRaw(Info);
      }

    }
    
  } catch (e) { 
    console.error('[PROCESS ERROR]', e); 
  }
};

onMounted(() => {
  loadPlan();
});

onUnmounted(() => {
  stopCamera();
});
</script>

<style scoped>
.workout-container {
  width: 100%;
  height: 100%;
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  padding: 20px;
}

.state-screen {
  width: 100%;
  max-width: 800px;
  text-align: center;
}

.loading-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  font-size: 18px;
  color: #64748b;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Overview */
.overview-card, .instruction-card, .summary-card {
  background: white;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.overview-header h2 { font-size: 32px; margin-bottom: 8px; color: #1e293b; }
.overview-header p { color: #64748b; margin-bottom: 32px; }

.plan-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 32px;
}

.plan-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f1f5f9;
  border-radius: 16px;
  text-align: left;
}

.item-icon { font-size: 32px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; background: white; border-radius: 12px; }
.item-info { flex: 1; }
.item-info h4 { margin: 0 0 4px 0; font-size: 18px; }
.item-info p { margin: 0; font-size: 14px; color: #64748b; }
.item-target { font-weight: 700; color: #6366f1; background: #e0e7ff; padding: 6px 12px; border-radius: 20px; }

/* Instruction */
.instruction-icon { font-size: 80px; margin-bottom: 24px; }
.instruction-content { margin: 32px 0; }
.instruction-text { font-size: 20px; color: #334155; margin-bottom: 24px; }
.target-box { font-size: 24px; color: #6366f1; background: #e0e7ff; padding: 16px; border-radius: 16px; display: inline-block; }

/* Exercise Screen */
.exercise-screen { width: 100%; height: 100%; min-height: 90vh; }
.brain-game-wrapper { width: 100%; height: 100%; }

.layout-wrapper {
  display: grid;
  grid-template-columns: 70% 30%;
  gap: 24px;
  height: 90vh;
  padding: 20px;
  background: #f8fafc;
}

/* VIDEO SECTION (LARGE) */
.video-section { 
  height: 100%; 
  display: flex;
  flex-direction: column;
}

.video-card {
  width: 100%;
  height: 100%;
  background: #000;
  border-radius: 24px;
  position: relative;
  overflow: hidden;
  border: 4px solid #e2e8f0;
  box-shadow: 0 20px 50px -10px rgba(0, 0, 0, 0.3);
}

.video-card.camera-active { 
  border-color: #10b981; 
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
}

.video-frame { 
  width: 100%; 
  height: 100%; 
  position: relative; 
}

video, canvas { 
  width: 100%; 
  height: 100%; 
  object-fit: cover; 
  position: absolute; 
  top: 0; 
  left: 0; 
}

.video-header { 
  position: absolute; 
  top: 20px; 
  left: 20px; 
  right: 20px;
  z-index: 10; 
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.live-indicator { 
  background: #ef4444; 
  color: white; 
  padding: 8px 16px; 
  border-radius: 24px; 
  font-weight: 700; 
  font-size: 14px;
  display: flex; 
  align-items: center; 
  gap: 8px; 
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.camera-status {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 24px;
  font-weight: 600;
}

.exercise-badge {
  background: rgba(99, 102, 241, 0.95);
  color: white;
  padding: 8px 16px;
  border-radius: 24px;
  font-weight: 700;
  font-size: 14px;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.blink-dot { 
  width: 10px; 
  height: 10px; 
  background: white; 
  border-radius: 50%; 
  animation: blink 1s infinite; 
}

@keyframes blink { 50% { opacity: 0.3; } }

.loading-overlay { 
  position: absolute; 
  inset: 0; 
  background: rgba(0,0,0,0.8); 
  color: white; 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  justify-content: center; 
  z-index: 20; 
}

/* STATS PANEL */
.stats-panel { 
  display: flex; 
  flex-direction: column; 
  gap: 20px; 
  height: 100%;
}

/* REP COUNTER (MASSIVE) */
.rep-counter-card { 
  background: white; 
  padding: 32px; 
  border-radius: 24px; 
  text-align: center; 
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  position: relative;
}

.counter-label { 
  font-size: 16px; 
  color: #64748b; 
  text-transform: uppercase; 
  font-weight: 700;
  letter-spacing: 1px;
  margin-bottom: 16px;
}

.counter-display { 
  margin: 20px 0; 
  line-height: 1;
}

.current-count { 
  font-size: 140px; 
  font-weight: 900; 
  color: #6366f1; 
  line-height: 1; 
  display: block;
  text-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.target-count { 
  font-size: 36px; 
  color: #94a3b8; 
  font-weight: 700;
  display: block;
  margin-top: 8px;
}

.progress-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.15;
  pointer-events: none;
}

/* FEEDBACK CARD (LARGE) */
.feedback-card { 
  background: white; 
  padding: 28px; 
  border-radius: 24px; 
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  min-height: 180px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: all 0.3s ease;
}

.feedback-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e2e8f0;
}

.feedback-icon-large { 
  font-size: 48px; 
  line-height: 1;
}

.feedback-label {
  font-size: 14px;
  color: #64748b;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 1px;
}

.feedback-message { 
  font-size: 28px; 
  font-weight: 700; 
  line-height: 1.4;
  color: #1e293b;
  flex: 1;
  display: flex;
  align-items: center;
}

/* Feedback States */
.fb-neutral { 
  background: #f1f5f9; 
  border-left: 6px solid #64748b;
}

.fb-neutral .feedback-message { color: #475569; }

.fb-success { 
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); 
  border-left: 6px solid #10b981;
  box-shadow: 0 10px 30px rgba(16, 185, 129, 0.2);
}

.fb-success .feedback-message { color: #047857; }

.fb-warning { 
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); 
  border-left: 6px solid #f59e0b;
  box-shadow: 0 10px 30px rgba(245, 158, 11, 0.2);
}

.fb-warning .feedback-message { color: #b45309; }

/* CONTROLS */
.action-controls {
  display: flex;
  gap: 12px;
}

.btn-skip { 
  background: #f1f5f9; 
  color: #64748b; 
  border: none; 
  padding: 16px 24px; 
  border-radius: 16px; 
  width: 100%; 
  font-weight: 700; 
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-skip:hover { 
  background: #e2e8f0; 
  color: #1e293b; 
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* PROGRESS */
.session-progress {
  margin-top: auto;
}

.progress-bar-container { 
  height: 12px; 
  background: #e2e8f0; 
  border-radius: 6px; 
  overflow: hidden; 
}

.progress-bar-fill { 
  height: 100%; 
  background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%); 
  transition: width 0.3s ease;
  box-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
}

.progress-text { 
  text-align: center; 
  color: #64748b; 
  font-size: 14px; 
  font-weight: 600;
  margin-top: 8px; 
}

/* OLD STYLES (KEEP FOR COMPATIBILITY) */
.controls-column { display: none; }
.video-column { display: none; }
.stats-card { display: none; }
.action-buttons { display: none; }
.stats-header { display: none; }
.main-counter { display: none; }
.feedback-box { display: none; }

/* Button Styles */
.btn-primary { 
  background: #6366f1; 
  color: white; 
  border: none; 
  border-radius: 16px; 
  cursor: pointer; 
  font-weight: 700; 
  transition: all 0.2s; 
}

.btn-primary:hover { 
  background: #4f46e5; 
  transform: translateY(-2px); 
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.btn-xl { 
  padding: 20px 40px; 
  font-size: 20px; 
  width: 100%; 
}

.btn-lg { 
  padding: 16px 32px; 
  font-size: 18px; 
  width: 100%; 
}

.btn-secondary { 
  background: #f1f5f9; 
  color: #64748b; 
  border: none; 
  padding: 12px; 
  border-radius: 12px; 
  width: 100%; 
  font-weight: 600; 
  cursor: pointer; 
}

.btn-secondary:hover { 
  background: #e2e8f0; 
  color: #1e293b; 
}

/* Summary */
.summary-icon { font-size: 80px; margin-bottom: 24px; }
.summary-stats { display: flex; justify-content: center; gap: 40px; margin: 40px 0; }
.stat-item { display: flex; flex-direction: column; }
.stat-val { font-size: 32px; font-weight: 900; color: #1e293b; }
.stat-lbl { font-size: 14px; color: #64748b; }
</style>
