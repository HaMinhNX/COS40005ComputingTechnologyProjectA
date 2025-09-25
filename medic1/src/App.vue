<script setup>
import { ref, onMounted } from 'vue';
import { PoseLandmarker, FilesetResolver, DrawingUtils } from '@mediapipe/tasks-vision';
import { AngleCalculator, ExerciseCounter } from './lib/exercise-logic.js';

// --- Reactive State ---
// Refs for DOM elements
const videoEl = ref(null);
const canvasEl = ref(null);

// Refs for UI data
const squatCount = ref(0);
const curlCount = ref(0);
const totalReps = ref(0);
const feedbackText = ref('');
const isCameraOn = ref(false);
const isLoading = ref(false);
const loadingMessage = ref('');

// --- Non-Reactive Variables ---
let poseLandmarker;
let exerciseCounter;
let animationFrameId;

// --- Lifecycle Hooks ---
onMounted(() => {
  exerciseCounter = new ExerciseCounter();
});

// --- MediaPipe and Camera Logic ---
async function createPoseLandmarker() {
  loadingMessage.value = 'Loading AI models...';
  isLoading.value = true;
  try {
    const filesetResolver = await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm");
    poseLandmarker = await PoseLandmarker.createFromOptions(filesetResolver, {
      baseOptions: {
        modelAssetPath: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task`,
        delegate: "GPU"
      },
      runningMode: "VIDEO",
      numPoses: 1
    });
  } catch (err) {
    console.error("Error creating Pose Landmarker:", err);
    feedbackText.value = "Failed to load AI model. Please refresh.";
  } finally {
    isLoading.value = false;
  }
}

async function startCamera() {
  if (!poseLandmarker) {
    await createPoseLandmarker();
  }
  
  if (!poseLandmarker) return; // Don't proceed if model failed to load

  loadingMessage.value = 'Accessing camera...';
  isLoading.value = true;

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoEl.value.srcObject = stream;
    videoEl.value.addEventListener('loadeddata', () => {
      isCameraOn.value = true;
      isLoading.value = false;
      predictWebcam();
    });
  } catch (err) {
    console.error("Error accessing camera:", err);
    feedbackText.value = "Could not access camera. Please check permissions.";
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
    
    // Clear the canvas
    const canvasCtx = canvasEl.value.getContext('2d');
    canvasCtx.clearRect(0, 0, canvasEl.value.width, canvasEl.value.height);
}

// --- Exercise Selection ---
let currentExercise = null;
function selectExercise(exercise) {
  currentExercise = exercise;
  exerciseCounter.bicep_curl_feedback_manager.clear_feedback();
  exerciseCounter.squat_feedback_manager.clear_feedback();
  feedbackText.value = `Mode set to: ${exercise.replace('_', ' ')}`;
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
    drawingUtils.drawLandmarks(landmarks, { color: '#00FF00', lineWidth: 2, radius: 3 });
    drawingUtils.drawConnectors(landmarks, PoseLandmarker.POSE_CONNECTIONS, { color: '#FF0000', lineWidth: 2 });

    // Process landmarks and update UI
    processLandmarks(landmarks);
  }

  canvasCtx.restore();
  animationFrameId = requestAnimationFrame(predictWebcam);
}

function processLandmarks(landmarks) {
  const lm = (index) => landmarks[index] || { x: 0, y: 0, visibility: 0 };
  const left_shoulder = lm(11), right_shoulder = lm(12), left_elbow = lm(13),
        right_elbow = lm(14), left_wrist = lm(15), right_wrist = lm(16),
        left_hip = lm(23), right_hip = lm(24), left_knee = lm(25),
        right_knee = lm(26), left_ankle = lm(27), right_ankle = lm(28);

  // Calculate angles
  const left_bicep_angle = AngleCalculator.calculate_angle(left_shoulder, left_elbow, left_wrist);
  const right_bicep_angle = AngleCalculator.calculate_angle(right_shoulder, right_elbow, right_wrist);
  const left_squat_angle = AngleCalculator.angle_deg(left_hip, left_knee, left_ankle);
  const right_squat_angle = AngleCalculator.angle_deg(right_hip, right_knee, right_ankle);
  const [left_e_t, right_e_t, avg_e_t] = AngleCalculator.calculate_elbow_torso_angle(left_hip, left_shoulder, left_elbow, right_hip, right_shoulder, right_elbow);
  const hip_shoulder_angle = AngleCalculator.calculate_hip_shoulder_angle(left_hip, left_shoulder) || AngleCalculator.calculate_hip_shoulder_angle(right_hip, right_shoulder);
  const knee_angle = (left_squat_angle + right_squat_angle) / 2;
  const back_angle = (AngleCalculator.angle_deg(left_hip, left_shoulder, {x: left_shoulder.x, y: left_hip.y}) + AngleCalculator.angle_deg(right_hip, right_shoulder, {x: right_shoulder.x, y: right_hip.y})) / 2;
  
  let state, feedback;
  if (currentExercise === 'bicep_curl') {
      const isLeftDominant = left_bicep_angle < right_bicep_angle;
      [state, feedback] = exerciseCounter.process_bicep_curl(
          isLeftDominant ? left_shoulder : right_shoulder,
          isLeftDominant ? left_elbow : right_elbow,
          isLeftDominant ? left_wrist : right_wrist,
          isLeftDominant ? left_hip : right_hip,
          isLeftDominant ? left_bicep_angle : right_bicep_angle,
          isLeftDominant ? left_e_t : right_e_t,
          hip_shoulder_angle
      );
  } else if (currentExercise === 'squat') {
      [state, feedback] = exerciseCounter.process_squat(knee_angle, back_angle);
  }

  // Update reactive state which automatically updates the UI
  squatCount.value = exerciseCounter.squat_counter;
  curlCount.value = exerciseCounter.curl_counter;
  totalReps.value = exerciseCounter.total_reps;
  feedbackText.value = feedback ? feedback.join(', ') : '';
}
</script>

<template>
  <div id="container">
    <h1>Exercise Counter</h1>
    <div class="video-container">
      <video ref="videoEl" autoplay playsinline></video>
      <canvas ref="canvasEl" width="640" height="480"></canvas>
      <div v-if="isLoading" class="loading-overlay">
        <p>{{ loadingMessage }}</p>
      </div>
    </div>
    
    <div id="controls">
      <button v-if="!isCameraOn" @click="startCamera">Start Camera</button>
      <button v-if="isCameraOn" @click="stopCamera" class="stop-button">Stop Camera</button>
      
      <button @click="selectExercise('squat')" :disabled="!isCameraOn">Squat Mode</button>
      <button @click="selectExercise('bicep_curl')" :disabled="!isCameraOn">Bicep Curl Mode</button>
      
      <div id="counters">
        Squat Count: <span>{{ squatCount }}</span><br>
        Bicep Curl Count: <span>{{ curlCount }}</span><br>
        Total Reps: <span>{{ totalReps }}</span>
      </div>
      
      <div id="feedback">{{ feedbackText }}</div>
    </div>
  </div>
</template>

<style scoped>
body, html {
  background-color: #f0f0f0;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  margin: 0;
}
#container {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: Arial, sans-serif;
  margin: 20px;
}
.video-container {
  position: relative;
  width: 640px;
  height: 480px;
}
video {
  display: none; /* We draw the video onto the canvas, so we don't need to see the raw video element */
}
canvas {
  border: 2px solid #333;
  background-color: #000;
  width: 640px;
  height: 480px;
}
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.5em;
}
#controls {
  margin-top: 20px;
  text-align: center;
}
#feedback {
  margin-top: 10px;
  color: red;
  font-weight: bold;
  height: 20px; /* Reserve space to prevent layout shift */
}
#counters {
  margin-top: 10px;
  font-size: 18px;
}
button {
  padding: 10px 20px;
  margin: 5px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}
button:hover {
  background-color: #45a049;
}
button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
.stop-button {
  background-color: #f44336;
}
.stop-button:hover {
  background-color: #d32f2f;
}
</style>