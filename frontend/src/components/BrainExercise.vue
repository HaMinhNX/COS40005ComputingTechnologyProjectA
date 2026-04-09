<!-- src/components02/BrainExercise.vue - Beautiful Brain Training Games -->
<template>
  <div class="brain-container">
    <!-- Header Section -->
    <div class="brain-header">
      <div class="header-content">
        <div class="header-icon"><Brain :size="40" /></div>
        <div class="header-text">
          <h2 class="header-title">Trò Chơi Trí Tuệ</h2>
          <p class="header-subtitle">Rèn luyện trí nhớ và tư duy mỗi ngày</p>
        </div>
      </div>
      <div class="header-stats">
        <div class="stat-box">
          <div class="stat-icon"><Trophy :size="18" /></div>
          <div class="stat-value">{{ todayScore }}</div>
          <div class="stat-label">Điểm hôm nay</div>
        </div>
        <div class="stat-box">
          <div class="stat-icon"><Calendar :size="18" /></div>
          <div class="stat-value">{{ streak }}</div>
          <div class="stat-label">Ngày liên tiếp</div>
        </div>
      </div>
    </div>

    <!-- Game Selection (when no game is active) -->
    <div v-if="!activeGame" class="game-selection">
      <h3 class="selection-title">
        <span class="title-icon"><Gamepad2 :size="24" /></span>
        Chọn trò chơi
      </h3>
      <div class="game-grid">
        <div v-for="game in games" :key="game.id" class="game-card-wrapper">
          <button @click="startGame(game.id)" class="game-card" :class="'game-theme-' + game.id">
            <div class="game-card-content">
              <div class="game-icon-container">
                <component :is="game.icon" :size="36" />
              </div>
              <div class="game-info-text">
                <h4 class="game-name">{{ game.name }}</h4>
                <p class="game-description">{{ game.description }}</p>
              </div>
              <div class="game-footer">
                <div class="play-indicator">
                  <Gamepad2 :size="18" />
                  <span>Chơi</span>
                </div>
              </div>
            </div>
            <div class="card-bg-decoration"></div>
          </button>
        </div>
      </div>
    </div>

    <!-- Active Game Area -->
    <div v-else class="game-area">
      <!-- Game Header -->
      <div class="game-header">
        <div class="game-info">
          <span class="game-type-icon">
            <component :is="currentGameIcon" :size="24" />
          </span>
          <span class="game-type-name">{{ currentGameName }}</span>
        </div>

        <div class="game-progress">
          <span class="progress-text">Câu {{ currentQuestion + 1 }}/{{ totalQuestions }}</span>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
        </div>
        <button @click="exitGame" class="btn-exit">
          <CloseIcon :size="20" class="exit-icon" />
          <span class="exit-text">Thoát</span>
        </button>
      </div>

      <!-- Question Display -->
      <transition name="slide" mode="out-in">
        <div :key="currentQuestion" class="question-container glass-card">
          <!-- Math Game -->
          <MathGame
            v-if="currentSubGame === 'math'"
            :level="currentQuestion"
            :answerSubmitted="answerSubmitted"
            @submit="submitAnswer"
          />

          <!-- Memory Game -->
          <MemoryGame
            v-if="currentSubGame === 'memory'"
            :level="currentQuestion"
            @submit="submitAnswer"
          />

          <!-- Pattern Game -->
          <PatternGame
            v-if="currentSubGame === 'pattern'"
            :level="currentQuestion"
            :answerSubmitted="answerSubmitted"
            @submit="submitAnswer"
          />

          <!-- Word Game -->
          <WordGame
            v-if="currentSubGame === 'word'"
            :level="currentQuestion"
            :answerSubmitted="answerSubmitted"
            @submit="submitAnswer"
          />

          <!-- Color Game -->
          <ColorGame
            v-if="currentSubGame === 'color'"
            :level="currentQuestion"
            :answerSubmitted="answerSubmitted"
            @submit="submitAnswer"
          />

          <!-- Card Game -->
          <CardGame
            v-if="currentSubGame === 'card'"
            :level="currentQuestion"
            @submit="submitAnswer"
          />

          <!-- Reflex Game -->
          <ReflexGame
            v-if="currentSubGame === 'reflex'"
            :level="currentQuestion"
            @submit="submitAnswer"
          />

          <!-- NEW GAMES -->
          <!-- Comparison Game -->
          <ComparisonGame
            v-if="currentSubGame === 'comparison'"
            :level="currentQuestion"
            :answerSubmitted="answerSubmitted"
            @submit="submitAnswer"
          />

          <!-- Category Game -->
          <CategoryGame
            v-if="currentSubGame === 'category'"
            :level="currentQuestion"
            :answerSubmitted="answerSubmitted"
            @submit="submitAnswer"
          />

          <!-- Odd One Out Game -->
          <OddOneOutGame
            v-if="currentSubGame === 'odd_one_out'"
            :level="currentQuestion"
            :answerSubmitted="answerSubmitted"
            @submit="submitAnswer"
          />

          <!-- True False Game -->
          <TrueFalseGame
            v-if="currentSubGame === 'true_false'"
            :level="currentQuestion"
            :answerSubmitted="answerSubmitted"
            @submit="submitAnswer"
          />

          <!-- Shadow Match Game -->
          <ShadowMatchGame
            v-if="currentSubGame === 'shadow_match'"
            :level="currentQuestion"
            :answerSubmitted="answerSubmitted"
            @submit="submitAnswer"
          />
        </div>
      </transition>

      <!-- Feedback Overlay -->
      <FeedbackOverlay :show="showFeedback" :tier="feedbackTier" />
    </div>

    <!-- Results Screen -->
    <transition name="fade">
      <div v-if="showResults" class="results-screen">
        <div class="results-content">
          <div class="results-icon"><Trophy :size="64" class="trophy-icon" /></div>
          <h2 class="results-title">Hoàn thành!</h2>

          <div class="results-score">
            <div class="score-circle">
              <div class="score-value">{{ score }}</div>
              <div class="score-total">/ {{ totalQuestions }}</div>
            </div>
            <div class="score-label">Số câu đúng</div>
          </div>
          <div class="results-stats">
            <div class="result-stat">
              <div class="result-stat-icon"><BarChart3 :size="20" /></div>
              <div class="result-stat-value">{{ Math.round((score / totalQuestions) * 100) }}%</div>
              <div class="result-stat-label">Tỷ lệ chính xác</div>
            </div>
            <div class="result-stat">
              <div class="result-stat-icon"><Star :size="20" /></div>
              <div class="result-stat-value">{{ earnedStars }}</div>
              <div class="result-stat-label">Sao đạt được</div>
            </div>
          </div>
          <div class="results-message">{{ resultsMessage }}</div>
          <div class="results-actions">
            <button @click="playAgain" class="btn-play-again" v-if="mode === 'standalone'">
              <RotateCcw :size="20" class="btn-icon" />
              <span class="btn-text">Chơi lại</span>
            </button>
            <button @click="handleFinish" class="btn-menu">
              <component :is="mode === 'flow' ? ArrowRight : Home" :size="20" class="btn-icon" />
              <span class="btn-text">{{ mode === 'flow' ? 'Tiếp tục' : 'Về menu' }}</span>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Exit Confirmation Modal -->
    <transition name="fade">
      <div v-if="showExitConfirm" class="modal-overlay">
        <div class="modal-content">
          <div class="modal-icon">⚠️</div>
          <h3 class="modal-title">Bạn có chắc muốn thoát?</h3>
          <p class="modal-text">Tiến độ chơi hiện tại sẽ không được lưu lại.</p>
          <div class="modal-actions">
            <button @click="confirmExit" class="btn-confirm-exit">Thoát</button>
            <button @click="cancelExit" class="btn-cancel-exit">Ở lại</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, markRaw } from 'vue'
import { API_BASE_URL } from '../config'
import {
  Brain,
  Calculator,
  Grid,
  Type,
  Palette,
  Layers,
  Zap,
  Shuffle,
  X as CloseIcon,
  Star,
  Trophy,
  Calendar,
  Gamepad2,
  BarChart3,
  ArrowRight,
  RotateCcw,
  Home,
  Hash,
} from 'lucide-vue-next'

// Game Components
import MathGame from '../games/MathGame.vue'
import MemoryGame from '../games/MemoryGame.vue'
import PatternGame from '../games/PatternGame.vue'
import WordGame from '../games/WordGame.vue'
import ColorGame from '../games/ColorGame.vue'
import CardGame from '../games/CardGame.vue'
import ReflexGame from '../games/ReflexGame.vue'
import ComparisonGame from '../games/ComparisonGame.vue'
import CategoryGame from '../games/CategoryGame.vue'
import OddOneOutGame from '../games/OddOneOutGame.vue'
import TrueFalseGame from '../games/TrueFalseGame.vue'
import ShadowMatchGame from '../games/ShadowMatchGame.vue'
import FeedbackOverlay from './FeedbackOverlay.vue'

// Props
const props = defineProps({
  userId: String,
  mode: { type: String, default: 'standalone' }, // 'standalone' or 'flow'
})

const emit = defineEmits(['completed', 'exit'])

// API Configuration
const API_URL = API_BASE_URL

// Game Definitions
const games = [
  {
    id: 'math',
    name: 'Toán Đơn Giản',
    description: 'Tính toán cộng, trừ, nhân, chia',
    icon: markRaw(Calculator),
    difficulty: 1,
  },
  {
    id: 'memory',
    name: 'Trí Nhớ Số',
    description: 'Ghi nhớ chuỗi số',
    icon: markRaw(Hash),
    difficulty: 2,
  },
  {
    id: 'pattern',
    name: 'Nhận Dạng Mẫu',
    description: 'Tìm quy luật trong chuỗi',
    icon: markRaw(Grid),
    difficulty: 2,
  },
  {
    id: 'word',
    name: 'Sắp Xếp Chữ',
    description: 'Ghép chữ thành từ có nghĩa',
    icon: markRaw(Type),
    difficulty: 3,
  },
  {
    id: 'color',
    name: 'Màu Sắc Vui Nhộn',
    description: 'Thử thách não bộ với màu sắc',
    icon: markRaw(Palette),
    difficulty: 1,
  },
  {
    id: 'card',
    name: 'Lật Hình Ghi Nhớ',
    description: 'Tìm cặp hình giống nhau',
    icon: markRaw(Layers),
    difficulty: 2,
  },
  {
    id: 'reflex',
    name: 'Phản Xạ Nhanh',
    description: 'Bắt lấy đồ vật xuất hiện',
    icon: markRaw(Zap),
    difficulty: 3,
  },
  {
    id: 'mixed',
    name: 'Tổng Hợp',
    description: 'Thử thách tất cả các kỹ năng',
    icon: markRaw(Shuffle),
    difficulty: 4,
  },
  {
    id: 'comparison',
    name: 'So Sánh Nhanh',
    description: 'So sánh giá trị biểu thức',
    icon: markRaw(Hash),
    difficulty: 2,
  },
  {
    id: 'category',
    name: 'Phân Loại',
    description: 'Sắp xếp theo chủ đề',
    icon: markRaw(Grid),
    difficulty: 2,
  },
  {
    id: 'odd_one_out',
    name: 'Khác Biệt',
    description: 'Tìm hình không cùng loại',
    icon: markRaw(Layers),
    difficulty: 2,
  },
  {
    id: 'true_false',
    name: 'Đúng Hay Sai',
    description: 'Xác minh nhanh thông tin',
    icon: markRaw(Zap),
    difficulty: 1,
  },
  {
    id: 'shadow_match',
    name: 'Ghép Bóng',
    description: 'Tìm bóng của hình ảnh',
    icon: markRaw(Palette),
    difficulty: 2,
  },
]

// State
const activeGame = ref(null)
const currentSubGame = ref(null)
const currentQuestion = ref(0)
const totalQuestions = ref(20)
const score = ref(0)
const todayScore = ref(0)
const streak = ref(0)

const answerSubmitted = ref(false)
const showFeedback = ref(false)
const lastAnswerWasCorrect = ref(false)
const feedbackTier = ref('normal')

const showResults = ref(false)
const showExitConfirm = ref(false)

// Computed
const currentGameIcon = computed(() => {
  const game = games.find((g) => g.id === activeGame.value)
  return game ? game.icon : ''
})

const currentGameName = computed(() => {
  const game = games.find((g) => g.id === activeGame.value)
  return game ? game.name : ''
})

const progressPercent = computed(() => {
  return (currentQuestion.value / totalQuestions.value) * 100
})

const earnedStars = computed(() => {
  const percentage = (score.value / totalQuestions.value) * 100
  if (percentage >= 90) return 3
  if (percentage >= 70) return 2
  if (percentage >= 50) return 1
  return 0
})

const resultsMessage = computed(() => {
  const percentage = (score.value / totalQuestions.value) * 100
  if (percentage >= 90) return 'Xuất sắc! Bạn thật tuyệt vời! 🌟'
  if (percentage >= 70) return 'Rất tốt! Tiếp tục phát huy nhé! 👏'
  if (percentage >= 50) return 'Khá tốt! Hãy cố gắng thêm! 💪'
  return 'Đừng nản chí! Luyện tập nhiều hơn nhé! 🎯'
})

// Game Functions
function startGame(gameId) {
  activeGame.value = gameId
  currentQuestion.value = 0
  score.value = 0
  showResults.value = false
  showFeedback.value = false
  generateQuestion()
}

function generateQuestion() {
  answerSubmitted.value = false
  showFeedback.value = false

  if (activeGame.value === 'mixed') {
    const subGames = [
      'math',
      'memory',
      'pattern',
      'word',
      'color',
      'card',
      'reflex',
      'comparison',
      'category',
      'odd_one_out',
      'true_false',
      'shadow_match',
    ]
    let nextGame
    do {
      nextGame = subGames[Math.floor(Math.random() * subGames.length)]
    } while (nextGame === currentSubGame.value && subGames.length > 1)
    currentSubGame.value = nextGame
  } else {
    currentSubGame.value = activeGame.value
  }
}

function submitAnswer(isCorrect, options = {}) {
  if (answerSubmitted.value && currentSubGame.value !== 'reflex' && currentSubGame.value !== 'card')
    return

  answerSubmitted.value = true
  if (isCorrect) score.value++

  showFeedbackMessage(isCorrect, options)
  logExerciseAttempt(isCorrect)

  setTimeout(() => {
    nextQuestion()
  }, 1500)
}

function showFeedbackMessage(isCorrect, options = {}) {
  const { timeTaken = 0 } = options
  lastAnswerWasCorrect.value = isCorrect

  if (!isCorrect) {
    feedbackTier.value = 'incorrect'
    showFeedback.value = true
    setTimeout(() => {
      showFeedback.value = false
    }, 1600)
    return
  }

  // Determine tier based on speed/difficulty
  if (timeTaken > 0 && timeTaken < 2000) feedbackTier.value = 'excellent'
  else if (timeTaken > 0 && timeTaken < 4000) feedbackTier.value = 'good'
  else feedbackTier.value = 'normal'

  // Fallback for games without time tracking yet
  if (timeTaken === 0) feedbackTier.value = 'good'

  showFeedback.value = true
  setTimeout(() => {
    showFeedback.value = false
  }, 1600)
}

function nextQuestion() {
  currentQuestion.value++
  if (currentQuestion.value < totalQuestions.value) {
    generateQuestion()
  } else {
    finishGame()
  }
}

function finishGame() {
  showResults.value = true
  logGameCompletion()
  loadUserStats() // Update stats after completion
}

function playAgain() {
  startGame(activeGame.value)
}

function handleFinish() {
  if (props.mode === 'flow') {
    emit('completed', { score: score.value, total: totalQuestions.value })
  } else {
    activeGame.value = null
    currentSubGame.value = null
    showResults.value = false
  }
}

function exitGame() {
  showExitConfirm.value = true
}

function confirmExit() {
  showExitConfirm.value = false
  activeGame.value = null
  currentSubGame.value = null
  emit('exit')
}

function cancelExit() {
  showExitConfirm.value = false
}

// Database Functions
async function logExerciseAttempt(isCorrect) {
  try {
    const token = localStorage.getItem('token')
    await fetch(`${API_URL}/brain-exercise/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        user_id: props.userId,
        exercise_type: currentSubGame.value,
        is_correct: isCorrect,
        question_number: currentQuestion.value + 1,
      }),
    })
  } catch (error) {
    console.error('Error logging attempt:', error)
  }
}

async function logGameCompletion() {
  try {
    const token = localStorage.getItem('token')
    await fetch(`${API_URL}/brain-exercise/complete`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        user_id: props.userId,
        exercise_type: activeGame.value,
        score: score.value,
        total_questions: totalQuestions.value,
      }),
    })
  } catch (error) {
    console.error('Error logging completion:', error)
  }
}

async function loadUserStats() {
  try {
    const token = localStorage.getItem('token')
    if (!token || !props.userId) return

    const response = await fetch(`${API_URL}/brain-exercise/stats/${props.userId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (response.ok) {
      const data = await response.json()
      todayScore.value = data.today_score || 0
      streak.value = data.streak || 0
    }
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

// Lifecycle
onMounted(() => {
  if (props.userId) {
    loadUserStats()
  }
})
</script>

<style scoped>
.brain-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

/* ============================================
   HEADER
   ============================================ */

.brain-header {
  background: #6366f1;
  color: white;
  padding: var(--spacing-2xl);
  border-radius: var(--border-radius-xl);
  border: 5px solid transparent;
  border: 4px solid #f43f5e;
  box-shadow: 0 15px 50px rgba(102, 126, 234, 0.5);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-xl);
  position: relative;
  overflow: hidden;
}

.brain-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 3s infinite;
}

.header-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
}

.header-icon {
  font-size: 96px;
  animation: float 3s ease-in-out infinite;
  filter: drop-shadow(0 8px 20px rgba(0, 0, 0, 0.3));
}

.header-title {
  font-size: var(--font-size-4xl);
  font-weight: 900;
  margin: 0 0 var(--spacing-xs) 0;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4);
  letter-spacing: 2px;
  color: #ffe66d;
}

.header-subtitle {
  font-size: var(--font-size-xl);
  margin: 0;
  opacity: 0.95;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  color: #fff5e1;
  background: rgba(255, 255, 255, 0.2);
  padding: 8px 16px;
  border-radius: 12px;
  display: inline-block;
}

.header-stats {
  display: flex;
  gap: var(--spacing-lg);
}

.stat-box {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  padding: var(--spacing-lg) var(--spacing-xl);
  border-radius: var(--border-radius-lg);
  text-align: center;
  border: 3px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  min-width: 120px;
  transition: all var(--transition-normal);
}

.stat-box:hover {
  transform: scale(1.05);
  background: rgba(255, 255, 255, 0.35);
}

.stat-value {
  font-size: var(--font-size-4xl);
  font-weight: 900;
  line-height: 1;
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.3);
}

.stat-label {
  font-size: var(--font-size-base);
  font-weight: 700;
  margin-top: var(--spacing-xs);
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* ============================================
   GAME SELECTION
   ============================================ */

.game-selection {
  background: white;
  padding: var(--spacing-xl);
  border-radius: var(--border-radius-lg);
  border: 3px solid var(--color-text-primary);
  box-shadow: var(--shadow-md);
}

.selection-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  font-size: var(--font-size-2xl);
  font-weight: 900;
  margin: 0 0 var(--spacing-xl) 0;
}

.title-icon {
  font-size: var(--font-size-3xl);
}

.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-xl);
  perspective: 1000px;
}

.game-card-wrapper {
  height: 100%;
}

.game-card {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 24px;
  overflow: hidden;
  padding: 0;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.05);
  text-align: left;
}

.game-card:hover {
  transform: translateY(-12px) scale(1.02);
  box-shadow: 0 25px 40px -15px rgba(0, 0, 0, 0.15);
  border-color: rgba(99, 102, 241, 0.2);
}

.game-card-content {
  position: relative;
  z-index: 2;
  padding: var(--spacing-xl);
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: var(--spacing-lg);
}

.game-icon-container {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20px;
  background: #f1f5f9;
  color: #6366f1;
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}

.game-card:hover .game-icon-container {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 8px 15px -5px rgba(99, 102, 241, 0.4);
}

.game-info-text {
  flex-grow: 1;
}

.game-name {
  font-size: var(--font-size-2xl);
  font-weight: 900;
  color: #1e293b;
  margin-bottom: var(--spacing-xs);
  letter-spacing: -0.5px;
}

.game-description {
  font-size: var(--font-size-md);
  color: #64748b;
  line-height: 1.6;
}

.game-footer {
  margin-top: auto;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-top: var(--spacing-md);
  border-top: 1px dashed #e2e8f0;
}

.play-indicator {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  background: #6366f1;
  color: white;
  padding: 6px 16px;
  border-radius: 12px;
  font-weight: 800;
  font-size: var(--font-size-sm);
  opacity: 0;
  transform: translateX(10px);
  transition: all 0.3s ease;
}

.game-card:hover .play-indicator {
  opacity: 1;
  transform: translateX(0);
}

/* Card Themes */
.game-theme-math .game-icon-container {
  background: #fee2e2;
  color: #ef4444;
}
.game-theme-memory .game-icon-container {
  background: #dcfce7;
  color: #22c55e;
}
.game-theme-pattern .game-icon-container {
  background: #dbeafe;
  color: #3b82f6;
}
.game-theme-word .game-icon-container {
  background: #fef9c3;
  color: #eab308;
}
.game-theme-color .game-icon-container {
  background: #fae8ff;
  color: #d946ef;
}
.game-theme-card .game-icon-container {
  background: #ffedd5;
  color: #f97316;
}
.game-theme-reflex .game-icon-container {
  background: #e0f2fe;
  color: #06b6d4;
}
.game-theme-mixed .game-icon-container {
  background: #ede9fe;
  color: #8b5cf6;
}

.card-bg-decoration {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 100px;
  height: 100px;
  background: currentColor;
  opacity: 0.03;
  border-radius: 50%;
  pointer-events: none;
  z-index: 1;
}

/* ============================================
   GAME AREA
   ============================================ */

.game-area {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.game-header {
  background: white;
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-lg);
  border: 3px solid var(--color-text-primary);
  box-shadow: var(--shadow-md);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.game-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.game-type-icon {
  font-size: var(--font-size-3xl);
}

.game-type-name {
  font-size: var(--font-size-xl);
  font-weight: 900;
}

.game-progress {
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.progress-text {
  font-size: var(--font-size-base);
  font-weight: 700;
  color: var(--color-text-secondary);
}

.progress-bar {
  height: 12px;
  background: #e2e8f0;
  border-radius: var(--border-radius-full);
  overflow: hidden;
  border: 2px solid var(--color-text-primary);
}

.progress-fill {
  height: 100%;
  background: #f43f5e;
  transition: width var(--transition-slow);
}

.btn-exit {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  background: #dc2626;
  color: white;
  border: 3px solid #991b1b;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-lg);
  font-weight: 800;
  cursor: pointer;
  transition: all var(--transition-normal);
  min-height: auto;
}

.btn-exit:hover {
  background: #991b1b;
  transform: scale(1.05);
}

.exit-icon {
  font-size: var(--font-size-xl);
}

/* ============================================
   QUESTION CONTAINER
   ============================================ */

.question-container {
  background: white;
  padding: var(--spacing-3xl);
  border-radius: var(--border-radius-lg);
  border: 3px solid var(--color-text-primary);
  box-shadow: var(--shadow-lg);
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2xl);
}

.instruction-text {
  font-size: var(--font-size-xl);
  font-weight: 700;
  text-align: center;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
}

/* Math Game */
.math-game {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-2xl);
}

.question-text {
  font-size: var(--font-size-4xl);
  font-weight: 900;
  color: var(--color-text-primary);
  text-align: center;
  padding: var(--spacing-xl);
  background: #fff9e6;
  border: 4px solid #d97706;
  border-radius: var(--border-radius-lg);
  min-width: 300px;
}

.answer-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
  width: 100%;
  max-width: 600px;
}

.answer-btn {
  padding: var(--spacing-2xl);
  font-size: var(--font-size-3xl);
  font-weight: 900;
  background: #e0f2fe;
  border: 4px solid #0369a1;
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
  min-height: var(--touch-large);
}

.answer-btn:hover:not(:disabled) {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  background: #bae6fd;
}

.answer-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Memory Game */
.memory-game {
  width: 100%;
}

.memory-numbers {
  display: flex;
  justify-content: center;
  gap: var(--spacing-lg);
  margin: var(--spacing-xl) 0;
}

.memory-number {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-4xl);
  font-weight: 900;
  background: #dbeafe;
  border: 4px solid #3b82f6;
  border-radius: var(--border-radius-md);
}

.timer-display {
  font-size: var(--font-size-3xl);
  font-weight: 900;
  text-align: center;
  color: #dc2626;
  margin-top: var(--spacing-lg);
}

.memory-input-container {
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
  margin: var(--spacing-xl) 0;
}

.memory-input {
  width: 70px;
  height: 70px;
  text-align: center;
  font-size: var(--font-size-3xl);
  font-weight: 900;
  border: 4px solid #cbd5e0;
  border-radius: var(--border-radius-md);
  background: white;
}

.memory-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.3);
}

/* Memory Game Drag & Drop */
.memory-answer-slots {
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
  margin: var(--spacing-xl) 0;
  flex-wrap: wrap;
}

.memory-slot {
  width: 70px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f7fafc;
  border: 3px dashed #cbd5e0;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.memory-slot:hover {
  border-color: #3b82f6;
  background: #ebf8ff;
}

.slot-number {
  font-size: var(--font-size-3xl);
  font-weight: 900;
  color: #2b6cb0;
}

.slot-placeholder {
  font-size: var(--font-size-lg);
  color: #cbd5e0;
  font-weight: 700;
}

.memory-number-bank {
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
  flex-wrap: wrap;
  margin: var(--spacing-lg) 0;
}

.memory-bank-number {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-2xl);
  font-weight: 900;
  background: #dbeafe;
  border: 3px solid #3b82f6;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.memory-bank-number:hover:not(.used) {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  background: #bfdbfe;
}

.memory-bank-number.used {
  opacity: 0.3;
  cursor: default;
  transform: none;
  box-shadow: none;
}

/* Timer Color Classes */
.timer-green {
  color: #10b981 !important;
  font-weight: 900;
}

.timer-orange {
  color: #f59e0b !important;
  font-weight: 900;
  animation: pulse 0.5s ease-in-out infinite;
}

.timer-red {
  color: #ef4444 !important;
  font-weight: 900;
  animation: pulse-intense 0.3s ease-in-out infinite;
  text-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

@keyframes pulse-intense {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
    filter: brightness(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.15);
    filter: brightness(1.2);
  }
}

.reflex-timer,
.card-timer,
.color-timer {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-2xl);
  font-weight: 900;
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(255, 255, 255, 0.9);
  border-radius: var(--border-radius-md);
  border: 3px solid currentColor;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

.card-game-header,
.color-game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: var(--spacing-lg);
}

.reflex-stats {
  display: flex;
  gap: var(--spacing-lg);
  align-items: center;
}

/* Pattern Game */
.pattern-sequence {
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
  margin: var(--spacing-xl) 0;
}

.pattern-item {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-4xl);
  background: white;
  border: 4px solid #cbd5e0;
  border-radius: var(--border-radius-md);
}

.pattern-question {
  background: #fff9e6;
  border-color: #d97706;
  font-size: var(--font-size-3xl);
  font-weight: 900;
}

.pattern-options {
  display: flex;
  justify-content: center;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
}

.pattern-option-btn {
  width: 100px;
  height: 100px;
  font-size: var(--font-size-4xl);
  background: #f8fafc;
  border: 4px solid #cbd5e0;
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.pattern-option-btn:hover:not(:disabled) {
  transform: scale(1.1);
  border-color: #667eea;
  box-shadow: var(--shadow-lg);
}

/* Word Game */
.word-game {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xl);
}

/* Word Hint Box with Meaning */
.word-hint-box {
  width: 100%;
  max-width: 700px;
  background: #e0f2fe;
  border: 3px solid #0369a1;
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-md);
}

.hint-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.hint-meaning {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.7);
  border-radius: var(--border-radius-md);
  margin-top: var(--spacing-md);
}

.hint-icon,
.meaning-icon {
  font-size: var(--font-size-2xl);
  flex-shrink: 0;
}

.hint-icon {
  animation: glow 2s ease-in-out infinite;
}

@keyframes glow {
  0%,
  100% {
    filter: drop-shadow(0 0 5px rgba(251, 191, 36, 0.5));
    transform: scale(1);
  }
  50% {
    filter: drop-shadow(0 0 15px rgba(251, 191, 36, 1));
    transform: scale(1.1);
  }
}

.hint-text {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: #0c4a6e;
  letter-spacing: 0.5px;
}

.meaning-text {
  font-size: var(--font-size-md);
  font-weight: 600;
  color: #0c4a6e;
  line-height: 1.5;
  font-style: italic;
}

/* Word Answer Container with Character Slots */
.word-answer-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
}

.word-groups {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xl);
  justify-content: center;
  align-items: center;
  padding: var(--spacing-lg);
}

.word-group {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--border-radius-md);
  border: 2px dashed #cbd5e0;
}

.char-slot {
  width: 60px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 3px solid #cbd5e0;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
  position: relative;
}

.char-slot.filled {
  background: #ebf8ff;
  border-color: #4299e1;
}

.char-slot.empty:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.char-slot.filled:hover {
  background: #dbeafe;
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.char-value {
  font-size: var(--font-size-2xl);
  font-weight: 900;
  color: #2b6cb0;
}

.char-placeholder {
  font-size: var(--font-size-3xl);
  font-weight: 300;
  color: #cbd5e0;
}

/* ============================================
   FEEDBACK + RESULTS
   ============================================ */

.results-screen {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.results-content {
  width: min(92vw, 620px);
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 4px solid #1f2937;
  border-radius: 28px;
  box-shadow: 0 28px 60px rgba(15, 23, 42, 0.35);
  padding: 28px;
  text-align: center;
}

.results-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 108px;
  height: 108px;
  border-radius: 999px;
  background: linear-gradient(135deg, #fef08a, #f59e0b);
  color: #111827;
  margin-bottom: 10px;
}

.trophy-icon {
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.results-title {
  margin: 4px 0 18px;
  font-size: clamp(1.9rem, 4.8vw, 2.4rem);
  font-weight: 900;
  color: #111827;
}

.results-score {
  margin: 4px auto 20px;
}

.score-circle {
  width: 170px;
  height: 170px;
  border-radius: 999px;
  border: 6px solid #6366f1;
  background: #eef2ff;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-value {
  font-size: 3rem;
  line-height: 1;
  font-weight: 900;
  color: #312e81;
}

.score-total {
  margin-top: 4px;
  font-size: 1.4rem;
  font-weight: 800;
  color: #4f46e5;
}

.score-label {
  margin-top: 10px;
  font-size: 1rem;
  font-weight: 800;
  color: #334155;
}

.results-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 14px 0 14px;
}

.result-stat {
  border: 2px solid #cbd5e1;
  border-radius: 16px;
  padding: 12px;
  background: #fff;
}

.result-stat-icon {
  color: #2563eb;
  margin-bottom: 6px;
}

.result-stat-value {
  font-size: 1.65rem;
  font-weight: 900;
  color: #0f172a;
}

.result-stat-label {
  margin-top: 2px;
  font-size: 0.95rem;
  color: #475569;
  font-weight: 700;
}

.results-message {
  margin: 10px 0 18px;
  padding: 12px 14px;
  border-radius: 14px;
  background: #f1f5f9;
  color: #0f172a;
  font-size: 1.05rem;
  font-weight: 800;
}

.results-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.btn-play-again,
.btn-menu {
  min-width: 170px;
  border-radius: 14px;
  border: 3px solid #1f2937;
  padding: 12px 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 1rem;
  font-weight: 900;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.btn-play-again {
  background: #f59e0b;
  color: #111827;
}

.btn-menu {
  background: #6366f1;
  color: #fff;
}

.btn-play-again:hover,
.btn-menu:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.22);
}

.btn-icon,
.btn-text {
  display: inline-flex;
  align-items: center;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateY(14px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateY(-14px);
}

.bounce-enter-active {
  animation: pop-bounce 0.28s ease;
}

@keyframes pop-bounce {
  0% {
    transform: scale(0.9);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .brain-header {
    flex-direction: column;
    text-align: center;
  }

  .header-content {
    flex-direction: column;
  }

  .game-grid {
    grid-template-columns: 1fr;
  }

  .answer-grid {
    grid-template-columns: 1fr;
  }

  .results-stats {
    flex-direction: column;
  }

  .result-stat {
    max-width: 100%;
  }

  .results-actions {
    flex-direction: column;
  }
}

/* ============================================
   EXIT CONFIRMATION MODAL
   ============================================ */

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--spacing-md);
}

.modal-content {
  background: white;
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-3xl);
  max-width: 450px;
  width: 100%;
  text-align: center;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border: 4px solid var(--color-text-primary);
  animation: modal-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modal-in {
  from {
    transform: scale(0.9) translateY(20px);
    opacity: 0;
  }
  to {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

.modal-icon {
  font-size: 64px;
  margin-bottom: var(--spacing-lg);
  animation: shake 2s ease-in-out infinite;
}

@keyframes shake {
  0%,
  100% {
    transform: rotate(0deg);
  }
  10%,
  30%,
  50%,
  70%,
  90% {
    transform: rotate(-5deg);
  }
  20%,
  40%,
  60%,
  80% {
    transform: rotate(5deg);
  }
}

.modal-title {
  font-size: var(--font-size-2xl);
  font-weight: 900;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
}

.modal-text {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--spacing-2xl);
}

.modal-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
}

.btn-confirm-exit {
  flex: 1;
  padding: var(--spacing-md) var(--spacing-xl);
  background: #ef4444;
  color: white;
  border: 3px solid #991b1b;
  border-radius: var(--border-radius-lg);
  font-weight: 800;
  font-size: var(--font-size-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-confirm-exit:hover {
  background: #dc2626;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.btn-cancel-exit {
  flex: 1;
  padding: var(--spacing-md) var(--spacing-xl);
  background: #f8fafc;
  color: var(--color-text-primary);
  border: 3px solid var(--color-text-primary);
  border-radius: var(--border-radius-lg);
  font-weight: 800;
  font-size: var(--font-size-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel-exit:hover {
  background: #f1f5f9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
