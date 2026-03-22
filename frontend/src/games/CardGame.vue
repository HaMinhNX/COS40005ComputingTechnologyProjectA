<template>
  <div class="card-game glass-card">
    <div class="card-game-header">
      <div class="instruction-text">Tìm các cặp hình giống nhau:</div>
      <div class="card-timer" :class="timerClass">
        <span class="timer-icon">⏱️</span>
        <span class="timer-value">{{ timeLeft }}s</span>
      </div>
    </div>
    <div class="card-grid" :style="{ gridTemplateColumns: `repeat(${gridCols}, 1fr)` }">
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
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  level: { type: Number, default: 0 }
});

const emit = defineEmits(['submit']);

const cardGrid = ref([]);
const flippedCards = ref([]);
const isCheckingMatch = ref(false);
const matchedPairs = ref(0);
const totalPairs = ref(0);
const timeLeft = ref(60);
const timerId = ref(null);
const startTime = ref(0);
const initialTimeLimit = ref(40);

const gridCols = computed(() => {
  if (totalPairs.value > 4) return 4;
  if (totalPairs.value > 2) return 3;
  return 2;
});

const timerClass = computed(() => {
  const initialTime = props.level >= 8 ? 25 : (props.level >= 5 ? 30 : (props.level >= 2 ? 35 : 40));
  const percentage = (timeLeft.value / initialTime) * 100;
  if (percentage > 50) return 'timer-green';
  if (percentage > 25) return 'timer-orange';
  return 'timer-red';
});

function generateQuestion() {
  flippedCards.value = [];
  isCheckingMatch.value = false;
  matchedPairs.value = 0;

  let pairCount = 2;
  let timeLimit = 40;

  if (props.level >= 2) { pairCount = 3; timeLimit = 35; }
  if (props.level >= 5) { pairCount = 4; timeLimit = 30; }
  if (props.level >= 8) { pairCount = 6; timeLimit = 25; }

  totalPairs.value = pairCount;
  timeLeft.value = timeLimit;
  initialTimeLimit.value = timeLimit;
  startTime.value = Date.now();

  const icons = ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐸', '🐙', '🦄', '🦋', '🐝', '🐞'];
  const selectedIcons = icons.sort(() => Math.random() - 0.5).slice(0, pairCount);

  cardGrid.value = [...selectedIcons, ...selectedIcons]
    .sort(() => Math.random() - 0.5)
    .map((icon, index) => ({
      id: index,
      icon,
      isFlipped: false,
      isMatched: false
    }));

  if (timerId.value) clearInterval(timerId.value);
  timerId.value = setInterval(() => {
    timeLeft.value--;
    if (timeLeft.value <= 0) {
      clearInterval(timerId.value);
      emit('submit', false);
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
      setTimeout(() => {
        card1.isMatched = true;
        card2.isMatched = true;
        flippedCards.value = [];
        isCheckingMatch.value = false;
        matchedPairs.value++;

        if (matchedPairs.value === totalPairs.value) {
          if (timerId.value) clearInterval(timerId.value);
          // For CardGame, excellence is about relative time left
          const performanceRatio = timeLeft.value / initialTimeLimit.value;
          const tierOptions = { timeTaken: performanceRatio > 0.5 ? 1000 : 3000 };
          emit('submit', true, tierOptions);
        }
      }, 500);
    } else {
      setTimeout(() => {
        card1.isFlipped = false;
        card2.isFlipped = false;
        flippedCards.value = [];
        isCheckingMatch.value = false;
      }, 1000);
    }
  }
}

watch(() => props.level, () => {
  generateQuestion();
});

onMounted(() => {
  generateQuestion();
});

onUnmounted(() => {
  if (timerId.value) clearInterval(timerId.value);
});
</script>

<style scoped>
.card-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 100%;
  padding: 2.5rem;
  max-width: 700px;
}

.card-game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 1rem;
}

.instruction-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-secondary);
}

.card-timer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  border-radius: var(--border-radius-full);
  font-weight: 900;
  font-size: 1.25rem;
  box-shadow: var(--shadow-sm);
}

.timer-green { background: var(--bg-subtle-success); color: var(--color-success-dark); }
.timer-orange { background: var(--bg-subtle-warning); color: var(--color-warning-dark); animation: pulse 1s infinite; }
.timer-red { background: var(--bg-subtle-error); color: var(--color-error-dark); animation: pulse 0.5s infinite; }

.card-grid {
  display: grid;
  gap: 1.25rem;
  width: 100%;
  max-width: 600px;
  background: rgba(255, 255, 255, 0.3);
  padding: 1.5rem;
  border-radius: 2rem;
  border: 4px solid var(--color-bg-tertiary);
}

.memory-card {
  aspect-ratio: 1;
  perspective: 1000px;
  cursor: pointer;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
}

.is-flipped .card-inner { transform: rotateY(180deg); }

.card-front, .card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  border-radius: 1.25rem;
  box-shadow: var(--shadow-md);
  border: 4px solid white;
}

.card-front {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
}

.card-back {
  background: white;
  border-color: var(--color-primary);
  transform: rotateY(180deg);
}

.is-matched .card-back {
  border-color: var(--color-success);
  background: var(--bg-subtle-success);
  animation: matchPulse 0.5s ease-out;
}

@keyframes matchPulse {
  0% { transform: rotateY(180deg) scale(1); }
  50% { transform: rotateY(180deg) scale(1.1); }
  100% { transform: rotateY(180deg) scale(1); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
</style>
