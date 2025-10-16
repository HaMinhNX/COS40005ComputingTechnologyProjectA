<script setup>
import { ref, onMounted } from 'vue';
import { PoseLandmarker, FilesetResolver, DrawingUtils } from '@mediapipe/tasks-vision';

// --- Hằng số API ---
const API_URL = 'http://127.0.0.1:8000'; // Địa chỉ của server FastAPI

// --- Reactive State ---
const videoEl = ref(null);
const canvasEl = ref(null);
const squatCount = ref(0);
const curlCount = ref(0);
const totalReps = ref(0);
const feedbackText = ref('BẬT CAMERA VÀ CHỌN BÀI TẬP');
const isCameraOn = ref(false);
const isLoading = ref(false);
const loadingMessage = ref('');
const currentExercise = ref(null);

// --- Exercise State Management (Used for UI display/debugging only) ---
const bicepCurlState = ref('IDLE');
const squatState = ref('IDLE');

// --- Non-Reactive Variables ---
let poseLandmarker;
let animationFrameId;

// --- MediaPipe and Camera Logic ---
async function createPoseLandmarker() {
  loadingMessage.value = 'ĐANG TẢI MÔ HÌNH AI...';
  isLoading.value = true;
  try {
    const filesetResolver = await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm");
    poseLandmarker = await PoseLandmarker.createFromOptions(filesetResolver, {
      baseOptions: {
        modelAssetPath: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task`,
        delegate: "GPU"
      },
      runningMode: "VIDEO",
      numPoses: 1,
      minPoseDetectionConfidence: 0.5,
      minPosePresenceConfidence: 0.5,
      minTrackingConfidence: 0.6
    });
  } catch (err) {
    console.error("Lỗi khi tạo Pose Landmarker:", err);
    feedbackText.value = "LỖI TẢI MÔ HÌNH, VUI LÒNG TẢI LẠI TRANG";
  } finally {
    isLoading.value = false;
  }
}

async function startCamera() {
  if (!poseLandmarker) {
    await createPoseLandmarker();
  }
  if (!poseLandmarker) return;

  loadingMessage.value = 'ĐANG MỞ CAMERA...';
  isLoading.value = true;

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoEl.value.srcObject = stream;
    videoEl.value.addEventListener('loadeddata', () => {
      isCameraOn.value = true;
      isLoading.value = false;
      // Không cần khởi tạo ExerciseCounter ở đây nữa
      predictWebcam();
    });
  } catch (err) {
    console.error("Lỗi truy cập camera:", err);
    feedbackText.value = "LỖI CAMERA, VUI LÒNG KIỂM TRA QUYỀN TRUY CẬP";
    isLoading.value = false;
  }
}

function stopCamera() {
  isCameraOn.value = false;
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  const stream = videoEl.value.srcObject;
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
  }
  videoEl.value.srcObject = null;
  const canvasCtx = canvasEl.value.getContext('2d');
  canvasCtx.clearRect(0, 0, canvasEl.value.width, canvasEl.value.height);
}

// --- Exercise Selection (Calls Backend API to reset state) ---
async function selectExercise(exercise) {
  currentExercise.value = exercise;
  const exerciseName = exercise === 'squat' ? 'Đứng lên ngồi xuống' : 'Gập Tay';
  feedbackText.value = `Đã chọn: ${exerciseName}`;
  
  // Gửi lệnh reset state đến backend
  try {
    const response = await fetch(`${API_URL}/select_exercise?exercise_name=${exercise}`, {
        method: 'POST',
    });
    if (response.ok) {
        // Reset local counts after successful server reset
        squatCount.value = 0;
        curlCount.value = 0;
        totalReps.value = 0;
        squatState.value = 'IDLE';
        bicepCurlState.value = 'IDLE';
    }
  } catch (error) {
    console.error("Lỗi khi gửi yêu cầu chọn bài tập đến backend:", error);
    feedbackText.value = "LỖI KẾT NỐI VỚI SERVER AI. VUI LÒNG KIỂM TRA PYTHON BACKEND.";
  }
}

// --- Main Prediction Loop ---
async function predictWebcam() {
  if (!isCameraOn.value) return;

  const canvas = canvasEl.value;
  const video = videoEl.value;
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const startTimeMs = performance.now();
  const results = await poseLandmarker.detectForVideo(video, startTimeMs);
  const canvasCtx = canvas.getContext('2d');

  canvasCtx.save();
  canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
  canvasCtx.drawImage(video, 0, 0, canvas.width, canvas.height);

  if (results.landmarks && results.landmarks.length > 0) {
    const landmarks = results.landmarks[0];
    const drawingUtils = new DrawingUtils(canvasCtx);
    drawingUtils.drawLandmarks(landmarks, { color: '#FF0000', lineWidth: 4, radius: 6 });
    drawingUtils.drawConnectors(landmarks, PoseLandmarker.POSE_CONNECTIONS, { color: '#00FF00', lineWidth: 4 });
    
    // Gửi landmark đến backend Python để xử lý
    await processLandmarks(landmarks);

  } else {
    feedbackText.value = "KHÔNG THẤY NGƯỜI, BẠN HÃY ĐỨNG VÀO KHUNG HÌNH";
  }

  canvasCtx.restore();
  animationFrameId = requestAnimationFrame(predictWebcam);
}

// HÀM MỚI: Gửi dữ liệu landmark đến backend FastAPI
async function processLandmarks(landmarks) {
  if (!currentExercise.value) {
    feedbackText.value = "Vui lòng chọn bài tập";
    return;
  }
  
  // Chuyển đổi dữ liệu landmarks sang định dạng JSON đơn giản (chỉ lấy x, y, z, visibility)
  // Clamp x/y to [0,1] to avoid validation errors; use ?? for visibility to preserve 0
  const landmarkData = landmarks.map(lm => ({ 
    x: Math.max(0, Math.min(1, lm.x || 0)), 
    y: Math.max(0, Math.min(1, lm.y || 0)), 
    z: lm.z || 0, 
    visibility: lm.visibility ?? 0  // Preserve low visibility (0) for accurate angle calc
  }));

  try {
    const response = await fetch(`${API_URL}/process_landmarks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        landmarks: landmarkData,
        current_exercise: currentExercise.value,
      }),
    });

    if (!response.ok) {
        throw new Error(`Lỗi HTTP: ${response.status}`);
    }

    const data = await response.json();

    // Cập nhật reactive state từ phản hồi của server
    squatCount.value = data.squat_count;
    curlCount.value = data.curl_count;
    totalReps.value = data.total_reps;
    
    // Feedback
    feedbackText.value = data.feedback.toUpperCase(); 

    // Cập nhật trạng thái (nếu muốn hiển thị)
    squatState.value = data.squat_state_name;
    bicepCurlState.value = data.curl_state_name;

  } catch (error) {
    console.error("Lỗi xử lý landmark với backend:", error);
    
    // UPDATED: Show more specific error if available
    if (error.message.includes('422')) {
      feedbackText.value = "DỮ LIỆU KHÔNG HỢP LỆ - HÃY ĐỨNG VÀO KHUNG HÌNH RÕ HƠN";
    } else {
      feedbackText.value = "LỖI KẾT NỐI VỚI SERVER AI. VUI LÒNG KIỂM TRA PYTHON BACKEND.";
    }
  }
}

onMounted(() => {
  // Bắt đầu tải mô hình sớm (nếu cần)
  // createPoseLandmarker();
});
</script>

<template>
  <div id="container">
    <h1>BÀI TẬP TẠI NHÀ</h1>
    
    <div class="video-container">
      <video ref="videoEl" autoplay playsinline></video>
      <canvas ref="canvasEl"></canvas>
      <div v-if="isLoading" class="loading-overlay">
        <p>{{ loadingMessage }}</p>
      </div>
    </div>
    
    <div id="feedback">{{ feedbackText }}</div>
    
    <div id="controls" :class="{ 'exercise-selected': currentExercise }">
      <button v-if="!isCameraOn" @click="startCamera" class="start-button">BẬT CAMERA</button>
      <button v-if="isCameraOn" @click="stopCamera" class="stop-button">TẮT</button>
      
      <button 
        @click="selectExercise('squat')" 
        :disabled="!isCameraOn"
        :class="{ 'active-button': currentExercise === 'squat' }">
        ĐỨNG LÊN NGỒI XUỐNG
      </button>
      <button 
        @click="selectExercise('bicep-curl')" 
        :disabled="!isCameraOn"
        :class="{ 'active-button': currentExercise === 'bicep-curl' }">
        GẬP TAY
      </button>
    </div>
      
    <div id="counters">
      <div class="counter-item">
        <span>ĐỨNG LÊN NGỒI XUỐNG: ({{ squatState }})</span>
        <span class="count-value">{{ squatCount }}</span>
      </div>
      <div class="counter-item">
        <span>GẬP KHUỶU TAY: ({{ bicepCurlState }})</span>
        <span class="count-value">{{ curlCount }}</span>
      </div>
      <div class="counter-item total">
        <span>TỔNG CỘNG:</span>
        <span class="count-value">{{ totalReps }}</span>
      </div>
    </div>
  </div>
</template>
<style scoped>
body, html {
  margin: 0;
  padding: 0;
  font-family: Arial, Helvetica, sans-serif;
  background-color: #f5f5f5;
}

#container {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background-color: #ffffff;
  border: 1px solid #ccc;
  box-sizing: border-box;
}

h1 {
  font-size: 56px; 
  color: #000000;
  margin-bottom: 20px;
  text-align: center;
}

.video-container {
  position: relative;
  width: 100%;
  max-width: 640px;
  height: 480px;
  border: 5px solid #000000;
  background-color: #000;
}

video { display: none; }
canvas { width: 100%; height: 100%; }

.loading-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 36px; 
  font-weight: bold;
  text-align: center;
}

#feedback {
  width: 100%;
  max-width: 640px;
  margin-top: 20px;
  padding: 20px;
  background-color: #ffffcc;
  border: 3px solid #000000;
  font-size: 32px; 
  font-weight: bold;
  color: #000000;
  text-align: center;
  min-height: 90px;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  align-items: center;
}

#controls {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  width: 100%;
  max-width: 640px;
  margin-top: 20px;
}

button {
  padding: 30px; 
  font-size: 28px; 
  font-weight: bold;
  color: #ffffff;
  border: 3px solid #000000;
  border-radius: 10px;
  cursor: pointer;
  background-color: white;
  transition: opacity 0.3s, background-color 0.3s;
  grid-column: span 1; /* Mặc định 1 cột */
}

button:disabled {
  background-color: #cccccc;
  color: #666666;
  border-color: #666666;
  cursor: not-allowed;
  opacity: 0.6;
}

.start-button, .stop-button {
  grid-column: span 2; /* Chiếm 2 cột khi chỉ có 1 nút */
}
.start-button { background-color: #28a745; }
.stop-button { background-color: #dc3545; }
.active-button { 
  background-color: orange;
  color: #000000;
}

#counters {
  width: 100%;
  max-width: 640px;
  margin-top: 30px;
  border: 3px solid #000;
  padding: 20px;
  background-color: #f8f9fa;
  box-sizing: border-box;
}

.counter-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 28px; 
  font-weight: bold;
  color: #000000;
  margin-bottom: 15px;
}
.counter-item:last-child { margin-bottom: 0; }

.count-value {
  font-size: 38px; 
}

.total {
  border-top: 3px solid #000;
  padding-top: 15px;
  margin-top: 15px;
}
</style>