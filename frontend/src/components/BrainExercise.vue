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
        <button
          v-for="game in games"
          :key="game.id"
          @click="startGame(game.id)"
          class="game-card"
        >
          <div class="game-icon">
            <component :is="game.icon" :size="32" />
          </div>
          <div class="game-name">{{ game.name }}</div>
          <div class="game-description">{{ game.description }}</div>
          <div class="game-difficulty">
            <span class="difficulty-label">Độ khó:</span>
            <span class="difficulty-stars">
              <Star v-for="i in game.difficulty" :key="i" :size="14" fill="currentColor" />
            </span>
          </div>
        </button>

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
        <div :key="currentQuestion" class="question-container">
          <!-- Math Game -->
          <div v-if="currentSubGame === 'math'" class="math-game">
            <div class="question-text">{{ mathQuestion.question }}</div>
            <div class="answer-grid">
              <button
                v-for="option in mathQuestion.options"
                :key="option"
                @click="submitAnswer(option)"
                class="answer-btn"
                :disabled="answerSubmitted"
              >
                {{ option }}
              </button>
            </div>
          </div>

          <!-- Memory Game -->
          <div v-if="currentSubGame === 'memory'" class="memory-game">
            <div v-if="memoryPhase === 'show'" class="memory-show">
              <div class="instruction-text">Hãy nhớ các số sau:</div>
              <div class="memory-numbers">
                <div v-for="(num, idx) in memorySequence" :key="idx" class="memory-number">
                  {{ num }}
                </div>
              </div>
              <div class="timer-display">{{ memoryTimer }}s</div>
            </div>
            <div v-else-if="memoryPhase === 'recall'" class="memory-recall">
              <div class="instruction-text">Kéo thả các số đúng theo thứ tự:</div>

              <!-- Answer Slots -->
              <div class="memory-answer-slots">
                <div
                  v-for="(slot, idx) in memoryAnswerSlots"
                  :key="idx"
                  class="memory-slot"
                  @click="handleMemorySlotClick(idx)"
                >
                  <span v-if="slot !== null" class="slot-number">{{ slot }}</span>
                  <span v-else class="slot-placeholder">{{ idx + 1 }}</span>
                </div>
              </div>

              <!-- Number Bank (includes correct + decoy numbers) -->
              <div class="memory-number-bank">
                <div
                  v-for="num in memoryNumberBank"
                  :key="num.id"
                  class="memory-bank-number"
                  :class="{ 'used': num.used }"
                  @click="!num.used && handleMemoryBankClick(num)"
                >
                  {{ num.value }}
                </div>
              </div>

              <button @click="submitMemoryAnswer" class="btn-submit" :disabled="!isMemoryAnswerComplete">
                <span class="submit-icon">✓</span>
                <span class="submit-text">Xác nhận</span>
              </button>
            </div>
          </div>

          <!-- Pattern Game -->
          <div v-if="currentSubGame === 'pattern'" class="pattern-game">
            <div class="instruction-text">Chọn hình tiếp theo trong chuỗi:</div>
            <div class="pattern-sequence">
              <div v-for="(shape, idx) in patternSequence" :key="idx" class="pattern-item">
                {{ shape }}
              </div>
              <div class="pattern-item pattern-question">?</div>
            </div>
            <div class="pattern-options">
              <button
                v-for="option in patternOptions"
                :key="option"
                @click="submitAnswer(option)"
                class="pattern-option-btn"
                :disabled="answerSubmitted"
              >
                {{ option }}
              </button>
            </div>
          </div>

          <!-- Word Game -->
          <div v-if="currentSubGame === 'word'" class="word-game">
            <div class="instruction-text">Sắp xếp các chữ cái thành từ có nghĩa:</div>

            <!-- Word Hint (for proverbs) - Now includes meaning -->
            <div v-if="wordHint" class="word-hint-box">
              <div class="hint-row">
                <span class="hint-icon">💡</span>
                <span class="hint-text">{{ wordHint }}</span>
              </div>
              <div v-if="wordMeaning" class="hint-meaning">
                <span class="meaning-icon">📖</span>
                <span class="meaning-text">{{ wordMeaning }}</span>
              </div>
            </div>

            <!-- Answer Area with Individual Boxes -->
            <div class="word-answer-container">
              <!-- Show word groups if it's a multi-word phrase -->
              <div v-if="wordStructure.length > 0" class="word-groups">
                <div v-for="(group, groupIdx) in wordStructure" :key="'group-' + groupIdx" class="word-group">
                  <div
                    v-for="(charSlot, charIdx) in group"
                    :key="'slot-' + groupIdx + '-' + charIdx"
                    class="char-slot"
                    :class="{ 'filled': charSlot.filled, 'empty': !charSlot.filled }"
                    @click="handleCharSlotClick(groupIdx, charIdx)"
                  >
                    <span v-if="charSlot.filled" class="char-value">{{ charSlot.char }}</span>
                    <span v-else class="char-placeholder">_</span>
                  </div>
                </div>
              </div>

              <!-- Fallback for simple words (backward compatibility) -->
              <div v-else class="word-answer-area-simple">
                <div
                  v-for="(tile, idx) in answerTiles"
                  :key="idx"
                  class="word-tile answer-tile"
                  @click="handleAnswerTileClick(idx)"
                >
                  {{ tile.letter }}
                </div>
                <div v-if="answerTiles.length === 0" class="word-placeholder">
                  Chọn chữ cái bên dưới
                </div>
              </div>
            </div>

            <!-- Letter Bank -->
            <div class="word-bank">
              <div
                v-for="tile in wordTiles"
                :key="tile.id"
                class="word-tile bank-tile"
                :class="{ 'used': tile.used }"
                @click="!tile.used && handleWordTileClick(tile)"
              >
                {{ tile.letter }}
              </div>
            </div>

            <button @click="submitAnswer()" class="btn-submit" :disabled="answerSubmitted || !isWordAnswerComplete">
              <span class="submit-icon">✓</span>
              <span class="submit-text">Xác nhận</span>
            </button>
          </div>

          <!-- Color Game -->
          <div v-if="currentSubGame === 'color'" class="color-game">
            <div class="color-game-header">
              <div class="instruction-text" v-if="colorQuestion.type === 'normal'">Vật này màu gì?</div>
              <div class="instruction-text" v-else>Chữ bên dưới có MÀU gì? (Không phải chữ viết gì!)</div>
              <div class="color-timer" :class="colorTimerClass">
                <span class="timer-icon">⏱️</span>
                <span class="timer-value">{{ colorTimeLeft }}s</span>
              </div>
            </div>

            <div class="color-question-item">
              <div v-if="colorQuestion.type === 'normal'" class="color-icon">{{ colorQuestion.icon }}</div>
              <div
                class="color-name"
                :style="{
                  color: colorQuestion.displayColor,
                  fontSize: colorQuestion.type === 'stroop' ? '60px' : '',
                  backgroundColor: colorQuestion.type === 'stroop' ? colorQuestion.backgroundColor : 'transparent',
                  padding: colorQuestion.type === 'stroop' ? '20px 40px' : '0',
                  borderRadius: colorQuestion.type === 'stroop' ? '12px' : '0'
                }"
              >
                {{ colorQuestion.content }}
              </div>
            </div>

            <div class="color-options">
              <button
                v-for="(opt, idx) in colorQuestion.options"
                :key="idx"
                @click="submitAnswer(opt.color)"
                class="color-option-btn"
                :style="{ backgroundColor: opt.bgColor || opt.color }"
                :disabled="answerSubmitted"
              >
                <span :style="{ color: opt.textColor || (opt.color === '#FFFFFF' ? '#000' : '#FFF'), textShadow: opt.textColor ? 'none' : '0 1px 2px rgba(0,0,0,0.5)', fontWeight: '900' }">{{ opt.colorName }}</span>
              </button>
            </div>
          </div>

          <!-- Card Game -->
          <div v-if="currentSubGame === 'card'" class="card-game">
            <div class="card-game-header">
              <div class="instruction-text">Tìm các cặp hình giống nhau:</div>
              <div class="card-timer" :class="cardTimerClass">
                <span class="timer-icon">⏱️</span>
                <span class="timer-value">{{ cardTimeLeft }}s</span>
              </div>
            </div>
            <div class="card-grid" :style="{ gridTemplateColumns: `repeat(${totalPairs > 4 ? 4 : (totalPairs > 2 ? 3 : 2)}, 1fr)` }">
              <div
                v-for="card in cardGrid"
                :key="card.id"
                class="memory-card"
                :class="{ 'is-flipped': card.isFlipped || card.isMatched, 'is-matched': card.isMatched }"
                @click="handleCardClick(card)"
              >
                <div class="card-inner">
                  <div class="card-front">❓</div>
                  <div class="card-back">{{ card.icon }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Reflex Game -->
          <div v-if="currentSubGame === 'reflex'" class="reflex-game">
            <div class="reflex-header">
              <div class="instruction-text">Bấm nhanh vào hình khi nó xuất hiện!</div>
              <div class="reflex-stats">
                <div class="lives-container">
                  <span v-for="i in 3" :key="i" class="heart-icon" :class="{ 'lost': i > lives }">❤️</span>
                </div>
                <div class="reflex-timer" :class="reflexTimerClass">
                  <Timer :size="16" class="timer-icon" />
                  <span class="timer-value">{{ reflexTimeLeft.toFixed(1) }}s</span>
                </div>

              </div>
            </div>
            <div class="reflex-area" @click="handleReflexAreaClick">
              <transition name="pop">
                <button
                  v-if="reflexTarget.visible"
                  class="reflex-target"
                  :style="{ top: reflexTarget.top, left: reflexTarget.left }"
                  @click.stop="handleReflexClick(true)"
                >
                  {{ reflexTarget.icon }}
                </button>
              </transition>
            </div>
          </div>
        </div>
      </transition>

      <!-- Feedback Display -->
      <transition name="bounce">
        <div v-if="showFeedback" class="feedback-display" :class="feedbackClass">
          <div class="feedback-icon">
            <component :is="feedbackIcon" :size="48" />
          </div>
          <div class="feedback-text">{{ feedbackText }}</div>

          <div v-if="showCorrectAnswer" class="correct-answer-display">
            <div class="correct-answer-label">Đáp án đúng:</div>
            <div class="correct-answer-text">{{ correctAnswerDisplay }}</div>
          </div>
        </div>
      </transition>
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
            <button @click="confirmExit" class="btn-confirm-exit">
              Thoát
            </button>
            <button @click="cancelExit" class="btn-cancel-exit">
              Ở lại
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, markRaw } from 'vue';
import { API_BASE_URL } from '../config';
import { 
  Brain, 
  Calculator, 
  Puzzle, 
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
  Timer,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  RotateCcw,
  Home,
  Hash
} from 'lucide-vue-next';



// Props
const props = defineProps({
  userId: String,
  mode: { type: String, default: 'standalone' } // 'standalone' or 'flow'
});

const emit = defineEmits(['completed']);

// API Configuration
const API_URL = API_BASE_URL;

// Game Definitions
const games = [
  {
    id: 'math',
    name: 'Toán Đơn Giản',
    description: 'Tính toán cộng, trừ, nhân, chia',
    icon: markRaw(Calculator),
    difficulty: 1
  },
  {
    id: 'memory',
    name: 'Trí Nhớ Số',
    description: 'Ghi nhớ chuỗi số',
    icon: markRaw(Hash),
    difficulty: 2
  },
  {
    id: 'pattern',
    name: 'Nhận Dạng Mẫu',
    description: 'Tìm quy luật trong chuỗi',
    icon: markRaw(Grid),
    difficulty: 2
  },
  {
    id: 'word',
    name: 'Sắp Xếp Chữ',
    description: 'Ghép chữ thành từ có nghĩa',
    icon: markRaw(Type),
    difficulty: 3
  },
  {
    id: 'color',
    name: 'Màu Sắc Vui Nhộn',
    description: 'Thử thách não bộ với màu sắc',
    icon: markRaw(Palette),
    difficulty: 1
  },
  {
    id: 'card',
    name: 'Lật Hình Ghi Nhớ',
    description: 'Tìm cặp hình giống nhau',
    icon: markRaw(Layers),
    difficulty: 2
  },
  {
    id: 'reflex',
    name: 'Phản Xạ Nhanh',
    description: 'Bắt lấy đồ vật xuất hiện',
    icon: markRaw(Zap),
    difficulty: 3
  },
  {
    id: 'mixed',
    name: 'Tổng Hợp',
    description: 'Thử thách tất cả các kỹ năng',
    icon: markRaw(Shuffle),
    difficulty: 4
  }
];


// State
const activeGame = ref(null);
const currentQuestion = ref(0);
const totalQuestions = ref(10);
const score = ref(0);
const todayScore = ref(0);
const streak = ref(0);
const showFeedback = ref(false);
const feedbackText = ref('');
const feedbackClass = ref('');
const feedbackIcon = ref('');
const answerSubmitted = ref(false);
const showResults = ref(false);
const showExitConfirm = ref(false); // Custom exit modal state

// Game specific states
const lives = ref(3); // For reflex game
const currentSubGame = ref(null); // For mixed mode

// Math Game State
const mathQuestion = ref({ question: '', answer: 0, options: [] });

// Memory Game State
const memoryPhase = ref('show'); // 'show' or 'recall'
const memorySequence = ref([]);
const memoryTimer = ref(5);
const memoryAnswerSlots = ref([]); // User's answer slots
const memoryNumberBank = ref([]); // Available numbers (correct + decoys)
const memorySelectedIndex = ref(null); // Currently selected slot for filling

// Pattern Game State
const patternSequence = ref([]);
const patternOptions = ref([]);
const patternAnswer = ref('');

const scrambledWord = ref('');
const correctWord = ref('');
const wordTiles = ref([]); // Available tiles
const answerTiles = ref([]); // User selected tiles
const wordHint = ref(''); // Hint for word structure
const wordMeaning = ref(''); // Meaning hint for proverbs/idioms
const wordStructure = ref([]); // Structure: array of word groups, each containing char slots
const showCorrectAnswer = ref(false);
const correctAnswerDisplay = ref('');

// Color Game State
const colorQuestion = ref({
  type: 'normal', // 'normal' or 'stroop'
  content: '',
  displayColor: '',
  backgroundColor: '',
  correctAnswer: '',
  options: []
});

// Card Game State
const cardGrid = ref([]);
const flippedCards = ref([]);
const isCheckingMatch = ref(false);
const matchedPairs = ref(0);
const totalPairs = ref(0);
const cardTimeLeft = ref(60);
const cardTimerId = ref(null);

// Color Game Timer
const colorTimeLeft = ref(10);
const colorTimerId = ref(null);

// Reflex Game State
const reflexTarget = ref({ top: '0%', left: '0%', icon: '', visible: false });
const reflexTimerId = ref(null);
const reflexCountdownId = ref(null);
const reflexStartTime = ref(0);
const reflexRoundConfig = ref({ totalTargets: 5, speed: 2000, targetsLeft: 5 });
const reflexScoreInRound = ref(0);
const reflexTimeLeft = ref(0);
const reflexMaxTime = ref(2.0);

// Computed
const currentGameIcon = computed(() => {
  const game = games.find(g => g.id === activeGame.value);
  return game ? game.icon : '';
});

const currentGameName = computed(() => {
  const game = games.find(g => g.id === activeGame.value);
  return game ? game.name : '';
});

const progressPercent = computed(() => {
  return (currentQuestion.value / totalQuestions.value) * 100;
});

const earnedStars = computed(() => {
  const percentage = (score.value / totalQuestions.value) * 100;
  if (percentage >= 90) return 3;
  if (percentage >= 70) return 2;
  if (percentage >= 50) return 1;
  return 0;
});

const resultsMessage = computed(() => {
  const percentage = (score.value / totalQuestions.value) * 100;
  if (percentage >= 90) return 'Xuất sắc! Bạn thật tuyệt vời! 🌟';
  if (percentage >= 70) return 'Rất tốt! Tiếp tục phát huy nhé! 👏';
  if (percentage >= 50) return 'Khá tốt! Hãy cố gắng thêm! 💪';
  return 'Đừng nản chí! Luyện tập nhiều hơn nhé! 🎯';
});

// Timer color classes
const reflexTimerClass = computed(() => {
  const percentage = (reflexTimeLeft.value / reflexMaxTime.value) * 100;
  if (percentage > 60) return 'timer-green';
  if (percentage > 30) return 'timer-orange';
  return 'timer-red';
});

const cardTimerClass = computed(() => {
  // Calculate percentage based on initial time
  const initialTime = currentQuestion.value >= 8 ? 25 : (currentQuestion.value >= 5 ? 30 : (currentQuestion.value >= 2 ? 35 : 40));
  const percentage = (cardTimeLeft.value / initialTime) * 100;
  if (percentage > 50) return 'timer-green';
  if (percentage > 25) return 'timer-orange';
  return 'timer-red';
});

const colorTimerClass = computed(() => {
  const percentage = (colorTimeLeft.value / 10) * 100;
  if (percentage > 60) return 'timer-green';
  if (percentage > 30) return 'timer-orange';
  return 'timer-red';
});

const isMemoryAnswerComplete = computed(() => {
  return memoryAnswerSlots.value.every(slot => slot !== null);
});

const isWordAnswerComplete = computed(() => {
  if (wordStructure.value.length > 0) {
    // Check if all slots are filled
    return wordStructure.value.every(group =>
      group.every(slot => slot.filled)
    );
  } else {
    // Fallback for simple words
    return answerTiles.value.length > 0;
  }
});

// Game Functions
function startGame(gameId) {
  activeGame.value = gameId;
  currentQuestion.value = 0;
  score.value = 0;
  lives.value = 3;
  showResults.value = false;
  generateQuestion();
}

function generateQuestion() {
  answerSubmitted.value = false;

  // Handle Mixed Mode
  let gameType = activeGame.value;
  if (gameType === 'mixed') {
    const subGames = ['math', 'memory', 'pattern', 'word', 'color', 'card', 'reflex'];
    // Avoid repeating the same sub-game immediately if possible
    let nextGame;
    do {
      nextGame = subGames[Math.floor(Math.random() * subGames.length)];
    } while (nextGame === currentSubGame.value && subGames.length > 1);
    currentSubGame.value = nextGame;
    gameType = nextGame;
  } else {
    currentSubGame.value = gameType;
  }

  switch(gameType) {
    case 'math':
      generateMathQuestion();
      break;
    case 'memory':
      generateMemoryQuestion();
      break;
    case 'pattern':
      generatePatternQuestion();
      break;
    case 'word':
      generateWordQuestion();
      break;
    case 'color':
      generateColorQuestion();
      break;
    case 'card':
      generateCardQuestion();
      break;
    case 'reflex':
      generateReflexQuestion();
      break;
  }
}

function generateMathQuestion() {
  const level = currentQuestion.value;
  let num1, num2, num3, answer, question;

  // Level 0-2: Simple single operations
  if (level < 3) {
    const operations = ['+', '-'];
    const operation = operations[Math.floor(Math.random() * operations.length)];

    if (operation === '+') {
      num1 = Math.floor(Math.random() * 30) + 1;
      num2 = Math.floor(Math.random() * 30) + 1;
      answer = num1 + num2;
    } else {
      num1 = Math.floor(Math.random() * 50) + 20;
      num2 = Math.floor(Math.random() * num1);
      answer = num1 - num2;
    }
    question = `${num1} ${operation} ${num2} = ?`;
  }
  // Level 3-5: Add multiplication and division
  else if (level < 6) {
    const operations = ['+', '-', '×', '÷'];
    const operation = operations[Math.floor(Math.random() * operations.length)];

    if (operation === '+') {
      num1 = Math.floor(Math.random() * 70) + 10;
      num2 = Math.floor(Math.random() * 70) + 10;
      answer = num1 + num2;
    } else if (operation === '-') {
      num1 = Math.floor(Math.random() * 100) + 30;
      num2 = Math.floor(Math.random() * num1);
      answer = num1 - num2;
    } else if (operation === '×') {
      num1 = Math.floor(Math.random() * 12) + 2;
      num2 = Math.floor(Math.random() * 12) + 2;
      answer = num1 * num2;
    } else { // ÷
      num2 = Math.floor(Math.random() * 10) + 2;
      answer = Math.floor(Math.random() * 15) + 1;
      num1 = num2 * answer;
    }
    question = `${num1} ${operation} ${num2} = ?`;
  }
  // Level 6-8: Two-step operations
  else if (level < 9) {
    const op1 = ['+', '-', '×'][Math.floor(Math.random() * 3)];
    const op2 = ['+', '-'][Math.floor(Math.random() * 2)];

    if (op1 === '×') {
      num1 = Math.floor(Math.random() * 10) + 2;
      num2 = Math.floor(Math.random() * 10) + 2;
      num3 = Math.floor(Math.random() * 20) + 5;
      const product = num1 * num2;
      answer = op2 === '+' ? product + num3 : product - num3;
      question = `${num1} × ${num2} ${op2} ${num3} = ?`;
    } else {
      num1 = Math.floor(Math.random() * 50) + 20;
      num2 = Math.floor(Math.random() * 30) + 10;
      num3 = Math.floor(Math.random() * 20) + 5;
      const first = op1 === '+' ? num1 + num2 : num1 - num2;
      answer = op2 === '+' ? first + num3 : first - num3;
      question = `${num1} ${op1} ${num2} ${op2} ${num3} = ?`;
    }
  }
  // Level 9+: Complex multi-step with larger numbers
  else {
    const choice = Math.floor(Math.random() * 3);

    if (choice === 0) {
      // (a × b) + (c × d)
      const a = Math.floor(Math.random() * 12) + 3;
      const b = Math.floor(Math.random() * 12) + 3;
      const c = Math.floor(Math.random() * 10) + 2;
      const d = Math.floor(Math.random() * 10) + 2;
      answer = (a * b) + (c * d);
      question = `(${a} × ${b}) + (${c} × ${d}) = ?`;
    } else if (choice === 1) {
      // (a + b) × c
      const a = Math.floor(Math.random() * 20) + 5;
      const b = Math.floor(Math.random() * 20) + 5;
      const c = Math.floor(Math.random() * 8) + 2;
      answer = (a + b) * c;
      question = `(${a} + ${b}) × ${c} = ?`;
    } else {
      // a × b - c × d
      const a = Math.floor(Math.random() * 15) + 5;
      const b = Math.floor(Math.random() * 12) + 3;
      const c = Math.floor(Math.random() * 10) + 2;
      const d = Math.floor(Math.random() * 8) + 2;
      answer = (a * b) - (c * d);
      question = `${a} × ${b} - ${c} × ${d} = ?`;
    }
  }

  mathQuestion.value.question = question;
  mathQuestion.value.answer = answer;

  // Generate options with appropriate range
  const options = new Set([answer]);
  const range = level < 3 ? 8 : (level < 6 ? 15 : 25);
  while (options.size < 4) {
    const offset = Math.floor(Math.random() * range * 2) - range;
    const option = answer + offset;
    if (option > 0 && option !== answer) options.add(option);
  }

  mathQuestion.value.options = Array.from(options).sort(() => Math.random() - 0.5);
}

function generateMemoryQuestion() {
  memoryPhase.value = 'show';
  const level = currentQuestion.value;
  const length = 3 + Math.floor(level / 2); // Increase difficulty: 3-7 numbers

  memorySequence.value = Array.from({ length }, () => Math.floor(Math.random() * 9) + 1);

  // Show for decreasing time based on level
  const showTime = Math.max(3, 6 - Math.floor(level / 3));
  memoryTimer.value = showTime;

  const interval = setInterval(() => {
    memoryTimer.value--;
    if (memoryTimer.value <= 0) {
      clearInterval(interval);
      memoryPhase.value = 'recall';

      // Initialize answer slots (all empty)
      memoryAnswerSlots.value = Array(length).fill(null);

      // Create number bank with correct numbers + decoys
      const decoyCount = Math.min(length + 2, 6); // Add 2-6 decoy numbers
      const allNumbers = [...memorySequence.value];

      // Add decoy numbers (different from correct ones)
      while (allNumbers.length < length + decoyCount) {
        const decoy = Math.floor(Math.random() * 9) + 1;
        allNumbers.push(decoy);
      }

      // Shuffle and create bank
      memoryNumberBank.value = allNumbers
        .sort(() => Math.random() - 0.5)
        .map((value, id) => ({ id, value, used: false }));

      memorySelectedIndex.value = null;
    }
  }, 1000);
}

// Handle clicking on a number from the bank
function handleMemoryBankClick(num) {
  // Find first empty slot
  const emptyIndex = memoryAnswerSlots.value.findIndex(slot => slot === null);
  if (emptyIndex !== -1) {
    memoryAnswerSlots.value[emptyIndex] = num.value;
    num.used = true;
  }
}

// Handle clicking on an answer slot (to remove number)
function handleMemorySlotClick(index) {
  const value = memoryAnswerSlots.value[index];
  if (value !== null) {
    // Return number to bank
    const bankNum = memoryNumberBank.value.find(n => n.value === value && n.used);
    if (bankNum) bankNum.used = false;
    memoryAnswerSlots.value[index] = null;
  }
}

function submitMemoryAnswer() {
  const userAnswer = memoryAnswerSlots.value;
  const correct = JSON.stringify(userAnswer) === JSON.stringify(memorySequence.value);

  showFeedbackMessage(correct);

  setTimeout(() => {
    nextQuestion();
  }, 800);
}

function generatePatternQuestion() {
  const patterns = [
    // Original patterns (15)
    { seq: ['🔴', '🔵', '🔴', '🔵'], answer: '🔴', options: ['🔴', '🔵', '🟢', '🟡'] },
    { seq: ['⭐', '⭐', '🌙', '⭐', '⭐'], answer: '🌙', options: ['⭐', '🌙', '☀️', '🌟'] },
    { seq: ['🍎', '🍊', '🍎', '🍊'], answer: '🍎', options: ['🍎', '🍊', '🍋', '🍇'] },
    { seq: ['🐶', '🐱', '🐶', '🐱'], answer: '🐶', options: ['🐶', '🐱', '🐭', '🐹'] },
    { seq: ['🌸', '🌸', '🌸', '🌺', '🌸', '🌸', '🌸'], answer: '🌺', options: ['🌸', '🌺', '🌻', '🌹'] },
    { seq: ['🔵', '🟢', '🔵', '🟢'], answer: '🔵', options: ['🔵', '🟢', '🔴', '🟡'] },
    { seq: ['🌙', '☀️', '🌙', '☀️'], answer: '🌙', options: ['🌙', '☀️', '⭐', '🌟'] },
    { seq: ['🍕', '🍔', '🍕', '🍔'], answer: '🍕', options: ['🍕', '🍔', '🍟', '🌭'] },
    { seq: ['🚗', '🚗', '🚙', '🚗', '🚗'], answer: '🚙', options: ['🚗', '🚙', '🚕', '🚌'] },
    { seq: ['❤️', '💙', '💚', '❤️', '💙'], answer: '💚', options: ['❤️', '💙', '💚', '💛'] },
    { seq: ['🎵', '🎶', '🎵', '🎶'], answer: '🎵', options: ['🎵', '🎶', '🎼', '🎹'] },
    { seq: ['🏀', '⚽', '🏀', '⚽'], answer: '🏀', options: ['🏀', '⚽', '🏈', '⚾'] },
    { seq: ['🌞', '🌞', '🌝', '🌞', '🌞'], answer: '🌝', options: ['🌞', '🌝', '🌛', '🌜'] },
    { seq: ['🎈', '🎁', '🎈', '🎁'], answer: '🎈', options: ['🎈', '🎁', '🎀', '🎊'] },
    { seq: ['🍓', '🍓', '🍇', '🍓', '🍓'], answer: '🍇', options: ['🍓', '🍇', '🍉', '🍌'] },

    // New patterns (20 more)
    { seq: ['🌻', '🌻', '🌹', '🌻', '🌻', '🌹'], answer: '🌻', options: ['🌻', '🌹', '🌷', '🌺'] },
    { seq: ['🦁', '🐯', '🦁', '🐯', '🦁'], answer: '🐯', options: ['🦁', '🐯', '🐻', '🐼'] },
    { seq: ['🍌', '🍌', '🍌', '🍎', '🍌', '🍌', '🍌'], answer: '🍎', options: ['🍌', '🍎', '🍊', '🍇'] },
    { seq: ['🎯', '🎲', '🎯', '🎲'], answer: '🎯', options: ['🎯', '🎲', '🎰', '🎮'] },
    { seq: ['🌊', '🌊', '🏔️', '🌊', '🌊'], answer: '🏔️', options: ['🌊', '🏔️', '🏝️', '🏖️'] },
    { seq: ['🦋', '🐝', '🦋', '🐝', '🦋'], answer: '🐝', options: ['🦋', '🐝', '🐞', '🦗'] },
    { seq: ['🎨', '🎨', '🎨', '🖌️', '🎨', '🎨', '🎨'], answer: '🖌️', options: ['🎨', '🖌️', '🖍️', '✏️'] },
    { seq: ['🌈', '☁️', '🌈', '☁️'], answer: '🌈', options: ['🌈', '☁️', '⛅', '🌤️'] },
    { seq: ['🎸', '🎹', '🎸', '🎹', '🎸'], answer: '🎹', options: ['🎸', '🎹', '🎺', '🎻'] },
    { seq: ['🍰', '🍰', '🧁', '🍰', '🍰', '🧁'], answer: '🍰', options: ['🍰', '🧁', '🎂', '🍪'] },
    { seq: ['🚀', '🛸', '🚀', '🛸'], answer: '🚀', options: ['🚀', '🛸', '🛩️', '✈️'] },
    { seq: ['📚', '📚', '📚', '📖', '📚', '📚', '📚'], answer: '📖', options: ['📚', '📖', '📝', '📄'] },
    { seq: ['🌟', '💫', '🌟', '💫', '🌟'], answer: '💫', options: ['🌟', '💫', '✨', '⭐'] },
    { seq: ['🏆', '🥇', '🏆', '🥇'], answer: '🏆', options: ['🏆', '🥇', '🥈', '🥉'] },
    { seq: ['🎭', '🎭', '🎪', '🎭', '🎭', '🎪'], answer: '🎭', options: ['🎭', '🎪', '🎬', '🎤'] },
    { seq: ['🌺', '🌼', '🌺', '🌼', '🌺'], answer: '🌼', options: ['🌺', '🌼', '🌻', '🌷'] },
    { seq: ['🍦', '🍦', '🍦', '🍨', '🍦', '🍦', '🍦'], answer: '🍨', options: ['🍦', '🍨', '🧊', '🍧'] },
    { seq: ['🎃', '👻', '🎃', '👻'], answer: '🎃', options: ['🎃', '👻', '🦇', '🕷️'] },
    { seq: ['🌴', '🌴', '🌲', '🌴', '🌴', '🌲'], answer: '🌴', options: ['🌴', '🌲', '🌳', '🎄'] },
    { seq: ['🔔', '🔔', '🔔', '🎺', '🔔', '🔔', '🔔'], answer: '🎺', options: ['🔔', '🎺', '📯', '🎷'] },
  ];

  const pattern = patterns[Math.floor(Math.random() * patterns.length)];
  patternSequence.value = pattern.seq;
  patternAnswer.value = pattern.answer;
  patternOptions.value = pattern.options.sort(() => Math.random() - 0.5);
}

function generateWordQuestion() {
  const level = currentQuestion.value;

  let wordList;
  let meanings = {}; // Map of word -> meaning

  // Level 0-2: Simple words
  if (level < 3) {
    wordList = [
      'Nhật', 'Tuần', 'Tháng', 'Năm', 'Ngày',
      'Máy', 'Bàn', 'Ghế', 'Cửa', 'Nhà',
      'Nước', 'Cơm', 'Canh', 'Thịt', 'Cá',
      'Mẹ', 'Bố', 'Con', 'Anh', 'Em',
      'Hoa', 'Cây', 'Lá', 'Xe', 'Tàu',
      // 20 more simple words
      'Sách', 'Vở', 'Bút', 'Thước', 'Túi',
      'Áo', 'Quần', 'Mũ', 'Giày', 'Tất',
      'Trời', 'Đất', 'Mây', 'Mưa', 'Gió',
      'Sông', 'Núi', 'Rừng', 'Biển', 'Đồi',
      'Tim', 'Gan', 'Phổi', 'Thận', 'Dạ'
    ];
    wordHint.value = '';
    wordMeaning.value = '';
  }
  // Level 3-5: Compound words
  else if (level < 6) {
    wordList = [
      'Máy bay', 'Ôtô', 'Xe đạp', 'Máy tính',
      'Sách vở', 'Bút chì', 'Thước kẻ',
      'Áo quần', 'Giày dép', 'Mũ nón',
      'Trời mưa', 'Nắng gió', 'Mây trời',
      'Rừng núi', 'Biển cả', 'Sông suối',
      'Tim phổi', 'Gan dạ', 'Thận gan',
      'Hoa quả', 'Rau củ', 'Thịt cá',
      // 20 more compound words
      'Bàn ghế', 'Cửa sổ', 'Nhà cửa', 'Đường phố',
      'Xe máy', 'Tàu hoả', 'Máy móc', 'Công cụ',
      'Bút mực', 'Giấy bút', 'Bảng đen', 'Phấn trắng',
      'Áo dài', 'Quần áo', 'Nón lá', 'Dép lào',
      'Mưa gió', 'Nắng mưa', 'Sương mù', 'Gió bão',
      'Sông nước', 'Núi rừng', 'Đồi núi', 'Biển trời'
    ];
    wordHint.value = '';
    wordMeaning.value = '';
  }
  // Level 6-8: Longer compound words and simple idioms
  else if (level < 9) {
    wordList = [
      'Bệnh viện', 'Trường học', 'Nhà hàng',
      'Siêu thị', 'Công viên', 'Sân bay',
      'Bến xe', 'Nhà ga', 'Bưu điện',
      'Ngân hàng', 'Chợ bán', 'Phố phố',
      'Mặt trời', 'Mặt trăng', 'Ngôi sao',
      'Đại dương', 'Đồi núi', 'Thác nước',
      'Cỏ cây', 'Hoa lá', 'Rừng rậm',
      // 20 more longer phrases
      'Bệnh nhân', 'Bác sĩ', 'Y tá', 'Thuốc men',
      'Học sinh', 'Giáo viên', 'Lớp học', 'Bài tập',
      'Khách hàng', 'Nhân viên', 'Quản lý', 'Giám đốc',
      'Gia đình', 'Bạn bè', 'Hàng xóm', 'Người thân',
      'Thời tiết', 'Khí hậu', 'Nhiệt độ', 'Độ ẩm',
      'Phong cảnh', 'Cảnh đẹp', 'Thiên nhiên', 'Môi trường'
    ];
    wordHint.value = '';
    wordMeaning.value = '';
  }
  // Level 9+: Proverbs and idioms (Thành ngữ, tục ngữ) with meanings
  else {
    const proverbsWithMeanings = [
      { text: 'Có chí thì nên', meaning: 'Khi có quyết tâm và ý chí thì sẽ thành công' },
      { text: 'Đoàn kết là sức mạnh', meaning: 'Khi mọi người đoàn kết với nhau sẽ tạo ra sức mạnh lớn' },
      { text: 'Học thầy không tạy học bạn', meaning: 'Học hỏi từ bạn bè cũng quan trọng như học từ thầy cô' },
      { text: 'Uống nước nhớ nguồn', meaning: 'Biết ơn công lao của người đi trước' },
      { text: 'Một giọt máu đào hơn ao nước lã', meaning: 'Tình ruột thịt quý giá hơn tình bạn bè' },
      { text: 'Lành gạo là lành canh', meaning: 'Nguyên liệu tốt thì món ăn mới ngon' },
      { text: 'Có công mài sắt có ngày nên kim', meaning: 'Chăm chỉ cố gắng sẽ đạt được thành công' },
      { text: 'Tránh vỏ dưa gặp vỏ dừa', meaning: 'Tránh cái này lại gặp cái khác cũng khó khăn như vậy' },
      { text: 'Tiền nào của nấy', meaning: 'Trả tiền bao nhiêu thì được hàng hóa chất lượng tương ứng' },
      { text: 'Thương cho roi cho vọt', meaning: 'Yêu thương con cái phải biết dạy dỗ nghiêm khắc' },
      { text: 'Mặt nước mắt cá', meaning: 'Vẻ mặt không biểu lộ cảm xúc' },
      { text: 'Nước đổ lá môn', meaning: 'Lời nói không có tác dụng, không được lắng nghe' },
      { text: 'Cái khôn cái khờ', meaning: 'Người khôn ngoan biết cách ứng xử linh hoạt' },
      { text: 'Trong cói ngoài nhung', meaning: 'Bên trong giản dị nhưng bên ngoài sang trọng' },
      { text: 'Trăm hay không bằng một thấy', meaning: 'Nghe nhiều không bằng tự mình trải nghiệm' },
      // 20 more proverbs
      { text: 'Ăn quả nhớ kẻ trồng cây', meaning: 'Biết ơn người đã giúp đỡ mình' },
      { text: 'Không thầy đố mày làm nên', meaning: 'Không có thầy dạy thì khó thành công' },
      { text: 'Học ăn học nói học gói học mở', meaning: 'Phải học cách ứng xử trong mọi hoàn cảnh' },
      { text: 'Một cây làm chẳng nên non', meaning: 'Một mình không thể làm được việc lớn' },
      { text: 'Ba cây chụm lại nên hòn núi cao', meaning: 'Đoàn kết sẽ tạo ra sức mạnh lớn' },
      { text: 'Gần mực thì đen gần đèn thì rạng', meaning: 'Gần ai thì học theo người đó' },
      { text: 'Chớ thấy sóng cả mà ngã tay chèo', meaning: 'Đừng bỏ cuộc khi gặp khó khăn' },
      { text: 'Ở hiền gặp lành', meaning: 'Sống tốt sẽ gặp điều tốt lành' },
      { text: 'Gieo gió gặt bão', meaning: 'Làm xấu sẽ nhận hậu quả xấu' },
      { text: 'Công cha như núi Thái Sơn', meaning: 'Công lao cha mẹ rất lớn lao' },
      { text: 'Nghĩa mẹ như nước trong nguồn', meaning: 'Tình mẹ vô bờ bến' },
      { text: 'Xa mặt cách lòng', meaning: 'Lâu không gặp thì tình cảm phai nhạt' },
      { text: 'Tốt gỗ hơn tốt nước sơn', meaning: 'Bản chất tốt quan trọng hơn vẻ ngoài' },
      { text: 'Đói cho sạch rách cho thơm', meaning: 'Nghèo nhưng phải giữ danh dự' },
      { text: 'Thất bại là mẹ thành công', meaning: 'Từ thất bại rút kinh nghiệm để thành công' },
      { text: 'Học hành là bổn phận', meaning: 'Học tập là nhiệm vụ quan trọng' },
      { text: 'Lời nói chẳng mất tiền mua', meaning: 'Nói lời tốt không tốn kém gì' },
      { text: 'Lá lành đùm lá rách', meaning: 'Người tốt giúp đỡ người khó khăn' },
      { text: 'Ăn mày mà đòi xôi gấc', meaning: 'Yêu cầu quá cao so với hoàn cảnh' },
      { text: 'Ăn miếng trả miếng', meaning: 'Đáp trả lại những gì người khác làm' }
    ];

    const selected = proverbsWithMeanings[Math.floor(Math.random() * proverbsWithMeanings.length)];
    correctWord.value = selected.text;
    wordMeaning.value = selected.meaning;

    // Generate hint
    const words = correctWord.value.split(' ');
    const wordLengths = words.map(w => `${w.length} chữ`);
    wordHint.value = `${words.length} từ (${wordLengths.join(', ')})`;

    // Create word structure with individual character slots
    wordStructure.value = words.map(word =>
      word.split('').map(char => ({ char: '', filled: false, correctChar: char }))
    );

    // Scramble the word (remove spaces first, then scramble)
    const lettersOnly = correctWord.value.replace(/ /g, '').split('');
    for (let i = lettersOnly.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [lettersOnly[i], lettersOnly[j]] = [lettersOnly[j], lettersOnly[i]];
    }

    scrambledWord.value = lettersOnly.join(' ');

    // Create tiles (without spaces)
    wordTiles.value = lettersOnly.map((l, i) => ({ id: i, letter: l, used: false }));
    answerTiles.value = [];
    return;
  }

  // For simple words (level < 9)
  correctWord.value = wordList[Math.floor(Math.random() * wordList.length)];
  wordMeaning.value = '';

  // Check if it's a multi-word phrase
  if (correctWord.value.includes(' ')) {
    const words = correctWord.value.split(' ');
    wordHint.value = `${words.length} từ`;

    // Create word structure with individual character slots
    wordStructure.value = words.map(word =>
      word.split('').map(char => ({ char: '', filled: false, correctChar: char }))
    );
  } else {
    wordHint.value = '';
    wordStructure.value = []; // Use simple mode
  }

  // Scramble the word (remove spaces first, then scramble)
  const lettersOnly = correctWord.value.replace(/ /g, '').split('');
  for (let i = lettersOnly.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [lettersOnly[i], lettersOnly[j]] = [lettersOnly[j], lettersOnly[i]];
  }

  scrambledWord.value = lettersOnly.join(' ');

  // Create tiles (without spaces)
  wordTiles.value = lettersOnly.map((l, i) => ({ id: i, letter: l, used: false }));
  answerTiles.value = [];
}

function handleWordTileClick(tile) {
  if (answerSubmitted.value) return;

  // New structure mode
  if (wordStructure.value.length > 0) {
    // Find first empty slot
    for (let groupIdx = 0; groupIdx < wordStructure.value.length; groupIdx++) {
      for (let charIdx = 0; charIdx < wordStructure.value[groupIdx].length; charIdx++) {
        const slot = wordStructure.value[groupIdx][charIdx];
        if (!slot.filled) {
          slot.char = tile.letter;
          slot.filled = true;
          slot.tileId = tile.id; // Track which tile is used
          tile.used = true;
          return;
        }
      }
    }
  } else {
    // Old simple mode
    tile.used = true;
    answerTiles.value.push({ ...tile });
  }
}

function handleCharSlotClick(groupIdx, charIdx) {
  if (answerSubmitted.value) return;

  const slot = wordStructure.value[groupIdx][charIdx];
  if (slot.filled) {
    // Return character to bank
    const tile = wordTiles.value.find(t => t.id === slot.tileId);
    if (tile) tile.used = false;

    slot.char = '';
    slot.filled = false;
    slot.tileId = null;
  }
}

function handleAnswerTileClick(index) {
  if (answerSubmitted.value) return;

  // Return to bank (old simple mode)
  const tile = answerTiles.value[index];
  const originalTile = wordTiles.value.find(t => t.id === tile.id);
  if (originalTile) originalTile.used = false;

  answerTiles.value.splice(index, 1);
}

function generateColorQuestion() {
  // Updated color list with distinct yellow and orange
  const items = [
    { name: 'Quả Táo', color: '#EF4444', icon: '🍎', colorName: 'Đỏ' },
    { name: 'Quả Chuối', color: '#FFEB3B', icon: '🍌', colorName: 'Vàng' },
    { name: 'Cái Lá', color: '#10B981', icon: '🍃', colorName: 'Xanh Lá' },
    { name: 'Quả Nho', color: '#8B5CF6', icon: '🍇', colorName: 'Tím' },
    { name: 'Cà Rốt', color: '#FF9800', icon: '🥕', colorName: 'Cam' },
    { name: 'Than Đá', color: '#1F2937', icon: '🌑', colorName: 'Đen' },
    { name: 'Tuyết', color: '#FFFFFF', icon: '❄️', colorName: 'Trắng' },
    { name: 'Hoa Hồng', color: '#EC4899', icon: '🌹', colorName: 'Hồng' },
    { name: 'Sô cô la', color: '#78350F', icon: '🍫', colorName: 'Nâu' },
    { name: 'Biển', color: '#3B82F6', icon: '🌊', colorName: 'Xanh Dương' },
    { name: 'Lửa', color: '#EF4444', icon: '🔥', colorName: 'Đỏ' },
    { name: 'Cỏ', color: '#10B981', icon: '🌱', colorName: 'Xanh Lá' },
    { name: 'Mặt Trời', color: '#FFEB3B', icon: '☀️', colorName: 'Vàng' }
  ];

  // Start timer
  colorTimeLeft.value = 10;
  if (colorTimerId.value) clearInterval(colorTimerId.value);
  colorTimerId.value = setInterval(() => {
    colorTimeLeft.value--;
    if (colorTimeLeft.value <= 0) {
      clearInterval(colorTimerId.value);
      // Time's up - auto submit wrong answer
      if (!answerSubmitted.value) {
        submitAnswer(null);
      }
    }
  }, 1000);

  // 50% chance of Stroop Effect question (Text color != Meaning)
  const isStroop = Math.random() < 0.5;

  if (isStroop) {
    // Stroop Mode
    const color1 = items[Math.floor(Math.random() * items.length)];
    let color2 = items[Math.floor(Math.random() * items.length)];
    while (color1.colorName === color2.colorName) {
      color2 = items[Math.floor(Math.random() * items.length)];
    }

    // Pick a random background color different from both
    let bgColor = items[Math.floor(Math.random() * items.length)];
    while (bgColor.colorName === color1.colorName || bgColor.colorName === color2.colorName) {
      bgColor = items[Math.floor(Math.random() * items.length)];
    }

    // Question: What color is the TEXT? (Text says "RED" but is colored BLUE)
    colorQuestion.value = {
      type: 'stroop',
      content: color1.colorName, // Text says "RED"
      displayColor: color2.color, // Color is BLUE
      backgroundColor: bgColor.color + '40', // Semi-transparent background
      correctAnswer: color2.color, // Answer is BLUE
      options: []
    };

    // Generate options (colors) with brain-teasing backgrounds
    const options = [color2]; // Correct answer
    while (options.length < 4) {
      const randomItem = items[Math.floor(Math.random() * items.length)];
      if (!options.find(o => o.color === randomItem.color)) {
        options.push(randomItem);
      }
    }

    // Add contrasting background colors to each option
    colorQuestion.value.options = options.map(opt => {
      // Find a different color for background that contrasts well
      let bgOpt;
      let attempts = 0;
      do {
        bgOpt = items[Math.floor(Math.random() * items.length)];
        attempts++;
      } while (bgOpt.colorName === opt.colorName && attempts < 10);

      // Determine text color for readability
      const textColor = getContrastColor(bgOpt.color);

      return {
        ...opt,
        bgColor: bgOpt.color,
        textColor: textColor
      };
    }).sort(() => Math.random() - 0.5);

  } else {
    // Normal Mode
    const item = items[Math.floor(Math.random() * items.length)];
    colorQuestion.value = {
      type: 'normal',
      content: item.name,
      icon: item.icon,
      displayColor: 'black',
      correctAnswer: item.color,
      options: []
    };

    // Generate options with brain-teasing backgrounds
    const options = [item];
    while (options.length < 4) {
      const randomItem = items[Math.floor(Math.random() * items.length)];
      if (!options.find(o => o.color === randomItem.color)) {
        options.push(randomItem);
      }
    }

    // Add contrasting background colors to each option
    colorQuestion.value.options = options.map(opt => {
      // Find a different color for background that contrasts well
      let bgOpt;
      let attempts = 0;
      do {
        bgOpt = items[Math.floor(Math.random() * items.length)];
        attempts++;
      } while (bgOpt.colorName === opt.colorName && attempts < 10);

      // Determine text color for readability
      const textColor = getContrastColor(bgOpt.color);

      return {
        ...opt,
        bgColor: bgOpt.color,
        textColor: textColor
      };
    }).sort(() => Math.random() - 0.5);
  }
}

// Helper function to get contrasting text color
function getContrastColor(hexColor) {
  // Convert hex to RGB
  const r = parseInt(hexColor.slice(1, 3), 16);
  const g = parseInt(hexColor.slice(3, 5), 16);
  const b = parseInt(hexColor.slice(5, 7), 16);

  // Calculate luminance
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

  // Return black or white based on luminance
  return luminance > 0.5 ? '#000000' : '#FFFFFF';
}

function generateCardQuestion() {
  flippedCards.value = [];
  isCheckingMatch.value = false;
  matchedPairs.value = 0;

  // Dynamic difficulty: Increase pairs and reduce time based on question number
  // Q1-2: 2 pairs (4 cards), 40s
  // Q3-5: 3 pairs (6 cards), 35s
  // Q6-8: 4 pairs (8 cards), 30s
  // Q9+: 6 pairs (12 cards), 25s
  let pairCount = 2;
  let timeLimit = 40;

  if (currentQuestion.value >= 2) { pairCount = 3; timeLimit = 35; }
  if (currentQuestion.value >= 5) { pairCount = 4; timeLimit = 30; }
  if (currentQuestion.value >= 8) { pairCount = 6; timeLimit = 25; }

  totalPairs.value = pairCount;
  cardTimeLeft.value = timeLimit;

  const icons = ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐸', '🐙', '🦄', '🦋', '🐝', '🐞'];
  const selectedIcons = icons.sort(() => Math.random() - 0.5).slice(0, pairCount);

  const cards = [...selectedIcons, ...selectedIcons]
    .sort(() => Math.random() - 0.5)
    .map((icon, index) => ({
      id: index,
      icon,
      isFlipped: false,
      isMatched: false
    }));

  cardGrid.value = cards;

  // Start countdown timer
  if (cardTimerId.value) clearInterval(cardTimerId.value);
  cardTimerId.value = setInterval(() => {
    cardTimeLeft.value--;
    if (cardTimeLeft.value <= 0) {
      clearInterval(cardTimerId.value);
      // Time's up - fail the round
      showFeedbackMessage(false);
      setTimeout(nextQuestion, 800);
    }
  }, 1000);
}

function handleCardClick(card) {
  if (isCheckingMatch.value || card.isFlipped || card.isMatched) return;

  card.isFlipped = true;
  flippedCards.value.push(card);

  if (flippedCards.value.length === 2) {
    isCheckingMatch.value = true;
    const [card1, card2] = flippedCards.value;

    if (card1.icon === card2.icon) {
      // Match!
      setTimeout(() => {
        card1.isMatched = true;
        card2.isMatched = true;
        flippedCards.value = [];
        isCheckingMatch.value = false;
        matchedPairs.value++;

        if (matchedPairs.value === totalPairs.value) {
          // Clear timer on completion
          if (cardTimerId.value) clearInterval(cardTimerId.value);
          showFeedbackMessage(true);
          setTimeout(nextQuestion, 800);
        }
      }, 500);
    } else {
      // No match
      setTimeout(() => {
        card1.isFlipped = false;
        card2.isFlipped = false;
        flippedCards.value = [];
        isCheckingMatch.value = false;
      }, 1000);
    }
  }
}

function generateReflexQuestion() {
  // Configure round based on progress
  // Q1-2: 5 targets, 2.5s per target
  // Q3-5: 8 targets, 2.0s per target
  // Q6-8: 12 targets, 1.5s per target
  // Q9+: 15 targets, 1.2s per target

  let total = 5;
  let maxTime = 2.5;

  if (currentQuestion.value >= 2) { total = 8; maxTime = 2.0; }
  if (currentQuestion.value >= 5) { total = 12; maxTime = 1.5; }
  if (currentQuestion.value >= 8) { total = 15; maxTime = 1.2; }

  reflexRoundConfig.value = {
    totalTargets: total,
    speed: maxTime * 1000,
    targetsLeft: total
  };

  reflexMaxTime.value = maxTime;
  reflexScoreInRound.value = 0;
  spawnReflexTarget();
}

function spawnReflexTarget() {
  if (reflexRoundConfig.value.targetsLeft <= 0) {
    // Round finished
    if (reflexCountdownId.value) clearInterval(reflexCountdownId.value);
    const passed = reflexScoreInRound.value >= (reflexRoundConfig.value.totalTargets * 0.6); // Need 60% to pass
    showFeedbackMessage(passed);
    setTimeout(nextQuestion, 1000);
    return;
  }

  reflexTarget.value.visible = false;

  const icons = ['🦋', '🐝', '🐞', '🦟', '🦗', '🕷️', '🦇', '🦅'];
  const icon = icons[Math.floor(Math.random() * icons.length)];

  // Small delay before next target
  setTimeout(() => {
    const top = Math.floor(Math.random() * 80) + 10; // 10% to 90%
    const left = Math.floor(Math.random() * 80) + 10;

    reflexTarget.value = {
      top: `${top}%`,
      left: `${left}%`,
      icon: icon,
      visible: true
    };
    reflexStartTime.value = Date.now();
    reflexTimeLeft.value = reflexMaxTime.value;
    reflexRoundConfig.value.targetsLeft--;

    // Start countdown timer with color changes
    if (reflexCountdownId.value) clearInterval(reflexCountdownId.value);
    reflexCountdownId.value = setInterval(() => {
      reflexTimeLeft.value -= 0.1;
      if (reflexTimeLeft.value <= 0) {
        clearInterval(reflexCountdownId.value);
        if (reflexTarget.value.visible) {
          handleReflexClick(false); // Missed - time ran out
        }
      }
    }, 100);

    // Set timeout for "missed"
    if (reflexTimerId.value) clearTimeout(reflexTimerId.value);
    reflexTimerId.value = setTimeout(() => {
      if (reflexTarget.value.visible) {
        handleReflexClick(false); // Missed
      }
    }, reflexRoundConfig.value.speed);
  }, 500);
}

function handleReflexClick(success) {
  if (!reflexTarget.value.visible && success) return;

  reflexTarget.value.visible = false;
  if (reflexTimerId.value) clearTimeout(reflexTimerId.value);
  if (reflexCountdownId.value) clearInterval(reflexCountdownId.value);

  if (success) {
    reflexScoreInRound.value++;
    spawnReflexTarget();
  } else {
    // Missed
    lives.value--;
    if (lives.value <= 0) {
      // Fail the round immediately
      showFeedbackMessage(false);
      setTimeout(nextQuestion, 800);
    } else {
      spawnReflexTarget();
    }
  }
}

// Handle clicking outside the target (miss click)
function handleReflexAreaClick() {
  if (reflexTarget.value.visible) {
    // Clicked on the area but missed the target
    handleReflexClick(false);
  }
}

function submitAnswer(answer) {
  if (answerSubmitted.value) return;

  answerSubmitted.value = true;
  let correct = false;

  // Use currentSubGame for mixed mode, otherwise use activeGame
  const gameType = currentSubGame.value || activeGame.value;

  switch(gameType) {
    case 'math':
      correct = answer === mathQuestion.value.answer;
      break;
    case 'pattern':
      correct = answer === patternAnswer.value;
      break;
    case 'word':
      let userAnswer;
      if (wordStructure.value.length > 0) {
        // New structure mode - collect characters from slots
        userAnswer = wordStructure.value
          .map(group => group.map(slot => slot.char).join(''))
          .join(' ');
      } else {
        // Old simple mode
        userAnswer = answerTiles.value.map(t => t.letter).join('');
      }
      const normalizedUserAnswer = userAnswer.toLowerCase().replace(/ /g, '');
      const normalizedCorrectWord = correctWord.value.toLowerCase().replace(/ /g, '');
      correct = normalizedUserAnswer === normalizedCorrectWord;
      if (!correct) {
        correctAnswerDisplay.value = correctWord.value;
      }
      break;
    case 'color':
      correct = answer === colorQuestion.value.correctAnswer;
      break;
    case 'reflex':
      // Reflex logic is handled in handleReflexClick
      correct = answer === true;
      break;
  }

  showFeedbackMessage(correct);

  // Clear color timer if it's a color game
  if (gameType === 'color' && colorTimerId.value) {
    clearInterval(colorTimerId.value);
  }

  setTimeout(() => {
    nextQuestion();
  }, 800); // Reduced from 1000ms to 800ms for faster feedback
}

function showFeedbackMessage(correct) {
  if (correct) {
    score.value++;
    feedbackIcon.value = markRaw(CheckCircle2);
    feedbackText.value = 'Chính xác! Tuyệt vời!';
    feedbackClass.value = 'feedback-correct';
    showCorrectAnswer.value = false;
  } else {
    feedbackIcon.value = markRaw(AlertCircle);
    feedbackText.value = 'Chưa đúng, cố gắng lần sau nhé!';
    feedbackClass.value = 'feedback-incorrect';
    showCorrectAnswer.value = true;
  }


  showFeedback.value = true;

  // Log to database
  logExerciseAttempt(correct);
}

function nextQuestion() {
  showFeedback.value = false;
  showCorrectAnswer.value = false;
  correctAnswerDisplay.value = '';
  currentQuestion.value++;

  if (currentQuestion.value >= totalQuestions.value) {
    endGame();
  } else {
    generateQuestion();
  }
}

function endGame() {
  showResults.value = true;
  activeGame.value = null;

  // Update today's score
  todayScore.value += score.value;

  // Log completion to database
  logGameCompletion();
}

function handleFinish() {
  if (props.mode === 'flow') {
    emit('completed', { score: score.value, total: totalQuestions.value });
  } else {
    backToMenu();
  }
}

function playAgain() {
  const lastGame = activeGame.value;
  showResults.value = false;
  startGame(lastGame || 'math');
}

function backToMenu() {
  showResults.value = false;
  activeGame.value = null;
}

function exitGame() {
  showExitConfirm.value = true;
}

function confirmExit() {
  showExitConfirm.value = false;
  // Reset all game state
  activeGame.value = null;
  currentSubGame.value = null;
  showResults.value = false;
  showFeedback.value = false;
  currentQuestion.value = 0;
  score.value = 0;
  answerSubmitted.value = false;

  // Reset game-specific state
  memoryPhase.value = 'show';
  memoryAnswerSlots.value = [];
  memoryNumberBank.value = [];
  answerTiles.value = [];
  if (reflexTimerId.value) clearTimeout(reflexTimerId.value);
  if (reflexCountdownId.value) clearInterval(reflexCountdownId.value);
  if (cardTimerId.value) clearInterval(cardTimerId.value);
  if (colorTimerId.value) clearInterval(colorTimerId.value);
}

function cancelExit() {
  showExitConfirm.value = false;
}

// Database Functions
async function logExerciseAttempt(isCorrect) {
  try {
    await fetch(`${API_URL}/brain-exercise/submit`, {

      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: props.userId,
        exercise_type: activeGame.value,
        is_correct: isCorrect,
        question_number: currentQuestion.value + 1
      })
    });
  } catch (error) {
    console.error('Error logging attempt:', error);
  }
}

async function logGameCompletion() {
  try {
    await fetch(`${API_URL}/brain-exercise/complete`, {

      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: props.userId,
        exercise_type: activeGame.value,
        score: score.value,
        total_questions: totalQuestions.value
      })
    });
  } catch (error) {
    console.error('Error logging completion:', error);
  }
}

async function loadUserStats() {
  try {
    const response = await fetch(`${API_URL}/brain-exercise/stats/${props.userId}`);

    if (response.ok) {
      const data = await response.json();
      todayScore.value = data.today_score || 0;
      streak.value = data.streak || 0;
    }
  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

// Lifecycle
onMounted(() => {
  if (props.userId) {
    loadUserStats();
  }
});
</script>

<style scoped>
.brain-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

/* ============================================
   HEADER
   ============================================ */

.brain-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  color: white;
  padding: var(--spacing-2xl);
  border-radius: var(--border-radius-xl);
  border: 5px solid transparent;
  border-image: linear-gradient(90deg, #F093FB, #F5576C, #FFE66D) 1;
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
  color: #FFE66D;
}

.header-subtitle {
  font-size: var(--font-size-xl);
  margin: 0;
  opacity: 0.95;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  color: #FFF5E1;
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
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-lg);
}

.game-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-2xl);
  background: linear-gradient(135deg, #F7FAFC 0%, #EDF2F7 100%);
  border: 3px solid #CBD5E0;
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
  min-height: 280px;
}

.game-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-xl);
  border-color: #F093FB;
  background: linear-gradient(135deg, #FFFFFF 0%, #F7FAFC 100%);
}

.game-icon {
  font-size: 80px;
}

.game-name {
  font-size: var(--font-size-xl);
  font-weight: 900;
  text-align: center;
  color: var(--color-text-primary);
}

.game-description {
  font-size: var(--font-size-base);
  text-align: center;
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.game-difficulty {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-top: auto;
}

.difficulty-label {
  font-size: var(--font-size-sm);
  font-weight: 700;
  color: var(--color-text-secondary);
}

.difficulty-stars {
  font-size: var(--font-size-lg);
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
  background: #E2E8F0;
  border-radius: var(--border-radius-full);
  overflow: hidden;
  border: 2px solid var(--color-text-primary);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #F093FB 0%, #F5576C 100%);
  transition: width var(--transition-slow);
}

.btn-exit {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  background: #DC2626;
  color: white;
  border: 3px solid #991B1B;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-lg);
  font-weight: 800;
  cursor: pointer;
  transition: all var(--transition-normal);
  min-height: auto;
}

.btn-exit:hover {
  background: #991B1B;
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
  background: linear-gradient(135deg, #FFF9E6 0%, #FEF3C7 100%);
  border: 4px solid #D97706;
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
  background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
  border: 4px solid #0369A1;
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
  min-height: var(--touch-large);
}

.answer-btn:hover:not(:disabled) {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  background: linear-gradient(135deg, #BAE6FD 0%, #7DD3FC 100%);
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
  background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
  border: 4px solid #3B82F6;
  border-radius: var(--border-radius-md);
}

.timer-display {
  font-size: var(--font-size-3xl);
  font-weight: 900;
  text-align: center;
  color: #DC2626;
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
  border: 4px solid #CBD5E0;
  border-radius: var(--border-radius-md);
  background: white;
}

.memory-input:focus {
  border-color: #3B82F6;
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
  background: #F7FAFC;
  border: 3px dashed #CBD5E0;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.memory-slot:hover {
  border-color: #3B82F6;
  background: #EBF8FF;
}

.slot-number {
  font-size: var(--font-size-3xl);
  font-weight: 900;
  color: #2B6CB0;
}

.slot-placeholder {
  font-size: var(--font-size-lg);
  color: #CBD5E0;
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
  background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
  border: 3px solid #3B82F6;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.memory-bank-number:hover:not(.used) {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  background: linear-gradient(135deg, #BFDBFE 0%, #93C5FD 100%);
}

.memory-bank-number.used {
  opacity: 0.3;
  cursor: default;
  transform: none;
  box-shadow: none;
}

/* Timer Color Classes */
.timer-green {
  color: #10B981 !important;
  font-weight: 900;
}

.timer-orange {
  color: #F59E0B !important;
  font-weight: 900;
  animation: pulse 0.5s ease-in-out infinite;
}

.timer-red {
  color: #EF4444 !important;
  font-weight: 900;
  animation: pulse-intense 0.3s ease-in-out infinite;
  text-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

@keyframes pulse-intense {
  0%, 100% {
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

.reflex-timer, .card-timer, .color-timer {
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

.card-game-header, .color-game-header {
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
  border: 4px solid #CBD5E0;
  border-radius: var(--border-radius-md);
}

.pattern-question {
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border-color: #D97706;
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
  background: linear-gradient(135deg, #F7FAFC 0%, #EDF2F7 100%);
  border: 4px solid #CBD5E0;
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.pattern-option-btn:hover:not(:disabled) {
  transform: scale(1.1);
  border-color: #667EEA;
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
  background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
  border: 3px solid #0369A1;
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

.hint-icon, .meaning-icon {
  font-size: var(--font-size-2xl);
  flex-shrink: 0;
}

.hint-icon {
  animation: glow 2s ease-in-out infinite;
}

@keyframes glow {
  0%, 100% {
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
  color: #0C4A6E;
  letter-spacing: 0.5px;
}

.meaning-text {
  font-size: var(--font-size-md);
  font-weight: 600;
  color: #0C4A6E;
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
  border: 2px dashed #CBD5E0;
}

.char-slot {
  width: 60px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 3px solid #CBD5E0;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
  position: relative;
}

.char-slot.filled {
  background: linear-gradient(135deg, #EBF8FF 0%, #DBEAFE 100%);
  border-color: #4299E1;
}

.char-slot.empty:hover {
  border-color: #667EEA;
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.char-slot.filled:hover {
  background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.char-value {
  font-size: var(--font-size-2xl);
  font-weight: 900;
  color: #2B6CB0;
}

.char-placeholder {
  font-size: var(--font-size-3xl);
  font-weight: 300;
  color: #CBD5E0;
}

/* Old Simple Mode Fallback */
.word-answer-area-simple {
  min-height: 80px;
  width: 100%;
  max-width: 600px;
  background: #F7FAFC;
  border: 3px dashed #CBD5E0;
  border-radius: var(--border-radius-lg);
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  justify-content: center;
  align-items: center;
  margin-bottom: var(--spacing-xl);
}

.word-hint {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
  border: 3px solid #0369A1;
  border-radius: var(--border-radius-lg);
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: #0C4A6E;
  box-shadow: var(--shadow-sm);
}

.scrambled-word {
  font-size: var(--font-size-4xl);
  font-weight: 900;
  letter-spacing: 8px;
  padding: var(--spacing-xl) var(--spacing-2xl);
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border: 4px solid #D97706;
  border-radius: var(--border-radius-lg);
}

.word-input {
  width: 100%;
  max-width: 500px;
  padding: var(--spacing-xl);
  font-size: var(--font-size-2xl);
  font-weight: 700;
  text-align: center;
  text-transform: uppercase;
  border: 4px solid #CBD5E0;
  border-radius: var(--border-radius-md);
}

.word-input:focus {
  border-color: #3B82F6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.3);
}

/* Word Game Tiles */
.word-placeholder {
  color: var(--color-text-secondary);
  font-style: italic;
  font-size: var(--font-size-lg);
}

.word-bank {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  justify-content: center;
  max-width: 700px;
  padding: var(--spacing-lg);
  background: rgba(248, 250, 252, 0.8);
  border-radius: var(--border-radius-lg);
}

.word-tile {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-2xl);
  font-weight: 900;
  background: white;
  border: 3px solid #CBD5E0;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.word-tile:hover:not(.used) {
  transform: translateY(-4px);
  border-color: #667EEA;
  box-shadow: var(--shadow-md);
}

.bank-tile.used {
  opacity: 0.3;
  cursor: default;
  transform: none;
  box-shadow: none;
}

.answer-tile {
  background: #EBF8FF;
  border-color: #4299E1;
  color: #2B6CB0;
}

/* Color Game */
.color-game {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xl);
}

.color-question-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xl);
  background: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
}

.color-icon {
  font-size: 120px;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
}

.color-name {
  font-size: var(--font-size-2xl);
  font-weight: 900;
  color: var(--color-text-primary);
}

.color-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
  width: 100%;
  max-width: 600px;
}

.color-option-btn {
  height: 100px;
  border-radius: var(--border-radius-lg);
  border: 4px solid rgba(0,0,0,0.1);
  font-size: var(--font-size-xl);
  font-weight: 900;
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  align-items: center;
  justify-content: center;
  text-transform: uppercase;
}

.color-option-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: var(--shadow-lg);
  border-color: rgba(0,0,0,0.2);
}

/* Card Game */
.card-game {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.card-grid {
  display: grid;
  gap: var(--spacing-md);
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.memory-card {
  aspect-ratio: 3/4;
  perspective: 1000px;
  cursor: pointer;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.memory-card.is-flipped .card-inner {
  transform: rotateY(180deg);
}

.card-front, .card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-4xl);
  border: 3px solid #CBD5E0;
  box-shadow: var(--shadow-sm);
}

.card-front {
  background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
  color: white;
}

.card-back {
  background: white;
  transform: rotateY(180deg);
}

.memory-card.is-matched .card-back {
  background: #D1FAE5;
  border-color: #10B981;
}

/* Reflex Game */
.reflex-game {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.reflex-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.lives-container {
  display: flex;
  gap: var(--spacing-sm);
}

.heart-icon {
  font-size: var(--font-size-2xl);
  transition: all 0.3s;
}

.heart-icon.lost {
  filter: grayscale(100%);
  opacity: 0.3;
  transform: scale(0.8);
}

.reflex-area {
  position: relative;
  width: 100%;
  height: 400px;
  background: #F0F9FF;
  border: 3px dashed #BAE6FD;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  cursor: crosshair;
}

.reflex-target {
  position: absolute;
  width: 80px;
  height: 80px;
  font-size: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: none;
  border-radius: 50%;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  cursor: pointer;
  transform: translate(-50%, -50%);
  transition: transform 0.1s;
}

.reflex-target:active {
  transform: translate(-50%, -50%) scale(0.9);
}

.pop-enter-active {
  animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.pop-leave-active {
  transition: opacity 0.2s;
}

.pop-leave-to {
  opacity: 0;
}

@keyframes popIn {
  0% { transform: translate(-50%, -50%) scale(0); }
  100% { transform: translate(-50%, -50%) scale(1); }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
}

.modal-content {
  background: white;
  padding: var(--spacing-2xl);
  border-radius: var(--border-radius-xl);
  width: 90%;
  max-width: 400px;
  text-align: center;
  box-shadow: var(--shadow-2xl);
  animation: bounceIn 0.4s;
}

.modal-icon {
  font-size: 60px;
  margin-bottom: var(--spacing-md);
}

.modal-title {
  font-size: var(--font-size-2xl);
  font-weight: 900;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}

.modal-text {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xl);
}

.modal-actions {
  display: flex;
  gap: var(--spacing-md);
}

.btn-confirm-exit, .btn-cancel-exit {
  flex: 1;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  font-weight: 700;
  font-size: var(--font-size-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.btn-confirm-exit {
  background: #EF4444;
  color: white;
  border: none;
}

.btn-confirm-exit:hover {
  background: #DC2626;
}

.btn-cancel-exit {
  background: #E5E7EB;
  color: var(--color-text-primary);
  border: none;
}

.btn-cancel-exit:hover {
  background: #D1D5DB;
}

/* Submit Button */
.btn-submit {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg) var(--spacing-2xl);
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: white;
  border: 4px solid #047857;
  border-radius: var(--border-radius-lg);
  font-size: var(--font-size-xl);
  font-weight: 900;
  cursor: pointer;
  transition: all var(--transition-normal);
  min-height: var(--touch-comfortable);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  filter: brightness(1.1);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-icon {
  font-size: var(--font-size-2xl);
}

/* ============================================
   FEEDBACK DISPLAY
   ============================================ */

.feedback-display {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  padding: var(--spacing-3xl);
  border-radius: var(--border-radius-xl);
  border: 6px solid;
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
  min-width: 400px;
}

.feedback-correct {
  background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
  border-color: #047857;
  color: #065F46;
}

.feedback-incorrect {
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border-color: #D97706;
  color: #92400E;
}

.feedback-icon {
  font-size: 100px;
}

.feedback-text {
  font-size: var(--font-size-3xl);
  font-weight: 900;
  text-align: center;
}

.correct-answer-display {
  margin-top: var(--spacing-md);
  padding: var(--spacing-lg);
  background: rgba(255, 255, 255, 0.9);
  border-radius: var(--border-radius-md);
  border: 3px solid #DC2626;
  width: 100%;
}

.correct-answer-label {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: #991B1B;
  margin-bottom: var(--spacing-sm);
  text-align: center;
}

.correct-answer-text {
  font-size: var(--font-size-2xl);
  font-weight: 900;
  color: #DC2626;
  text-align: center;
  letter-spacing: 1px;
}

/* ============================================
   RESULTS SCREEN
   ============================================ */

.results-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: var(--spacing-xl);
}

.results-content {
  background: white;
  padding: var(--spacing-3xl);
  border-radius: var(--border-radius-xl);
  border: 6px solid var(--color-text-primary);
  box-shadow: var(--shadow-xl);
  max-width: 700px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xl);
}

.results-icon {
  font-size: 120px;
  animation: bounce 1s ease-in-out infinite;
}

.results-title {
  font-size: var(--font-size-4xl);
  font-weight: 900;
  margin: 0;
  color: var(--color-text-primary);
}

.results-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
}

.score-circle {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: linear-gradient(135deg, #F093FB 0%, #F5576C 100%);
  border: 8px solid #E91E63;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: var(--shadow-xl);
}

.score-value {
  font-size: 80px;
  font-weight: 900;
  line-height: 1;
}

.score-total {
  font-size: var(--font-size-xl);
  font-weight: 700;
}

.score-label {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-text-secondary);
}

.results-stats {
  display: flex;
  gap: var(--spacing-2xl);
  width: 100%;
  justify-content: center;
}

.result-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, #F7FAFC 0%, #EDF2F7 100%);
  border: 3px solid #CBD5E0;
  border-radius: var(--border-radius-md);
  flex: 1;
  max-width: 200px;
}

.result-stat-icon {
  font-size: var(--font-size-3xl);
}

.result-stat-value {
  font-size: var(--font-size-3xl);
  font-weight: 900;
  color: var(--color-text-primary);
}

.result-stat-label {
  font-size: var(--font-size-sm);
  font-weight: 700;
  color: var(--color-text-secondary);
  text-align: center;
}

.results-message {
  font-size: var(--font-size-xl);
  font-weight: 700;
  text-align: center;
  color: var(--color-text-secondary);
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, #FFF9E6 0%, #FEF3C7 100%);
  border-radius: var(--border-radius-md);
  border: 3px solid #D97706;
}

.results-actions {
  display: flex;
  gap: var(--spacing-lg);
  width: 100%;
}

.btn-play-again,
.btn-menu {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg) var(--spacing-xl);
  font-size: var(--font-size-xl);
  font-weight: 900;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  min-height: var(--touch-comfortable);
}

.btn-play-again {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: white;
  border: 4px solid #047857;
}

.btn-play-again:hover {
  filter: brightness(1.1);
  transform: translateY(-2px);
}

.btn-menu {
  background: white;
  color: var(--color-text-primary);
  border: 4px solid var(--color-text-primary);
}

.btn-menu:hover {
  background: var(--color-bg-secondary);
  transform: translateY(-2px);
}

/* ============================================
   TRANSITIONS
   ============================================ */

.slide-enter-active,
.slide-leave-active {
  transition: all var(--transition-normal);
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.bounce-enter-active {
  animation: bounceIn 0.6s;
}

.bounce-leave-active {
  animation: bounceOut 0.4s;
}

/* ============================================
   RESPONSIVE
   ============================================ */

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
</style>

