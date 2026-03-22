<template>
  <div class="reflex-game glass-card">
    <div class="reflex-header">
      <div class="instruction-text">Bấm nhanh vào hình khi nó xuất hiện!</div>
      <div class="reflex-stats">
        <div class="lives-container">
          <span v-for="i in 3" :key="i" class="heart-icon" :class="{ 'lost': i > lives }">❤️</span>
        </div>
        <div class="reflex-timer" :class="timerClass">
          <Timer :size="18" class="timer-icon" />
          <span class="timer-value">{{ timeLeft.toFixed(1) }}s</span>
        </div>
      </div>
    </div>
    <div class="reflex-area glass-card" @click="handleAreaClick">
      <transition name="pop">
        <button
          v-if="target.visible"
          class="reflex-target"
          :style="{ top: target.top, left: target.left }"
          @click.stop="handleClick(true)"
        >
          {{ target.icon }}
        </button>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { Timer } from 'lucide-vue-next';

const props = defineProps({
  level: { type: Number, default: 0 }
});

const emit = defineEmits(['submit']);

const target = ref({ top: '0%', left: '0%', icon: '', visible: false });
const timeLeft = ref(0);
const lives = ref(3);
const maxTime = ref(2.0);
const scoreInRound = ref(0);
const roundConfig = ref({ totalTargets: 5, speed: 2000, targetsLeft: 5 });
const totalTimeTaken = ref(0);
const spawnTime = ref(0);

const timerId = ref(null);
const countdownId = ref(null);

const timerClass = computed(() => {
  const percentage = (timeLeft.value / maxTime.value) * 100;
  if (percentage > 60) return 'timer-green';
  if (percentage > 30) return 'timer-orange';
  return 'timer-red';
});

function generateQuestion() {
  let total = 5;
  let speed = 2.5;

  if (props.level >= 2) { total = 8; speed = 2.0; }
  if (props.level >= 5) { total = 12; speed = 1.5; }
  if (props.level >= 8) { total = 15; speed = 1.2; }

  roundConfig.value = { totalTargets: total, speed: speed * 1000, targetsLeft: total };
  maxTime.value = speed;
  scoreInRound.value = 0;
  lives.value = 3;
  spawnTarget();
}

function spawnTarget() {
  if (roundConfig.value.targetsLeft <= 0) {
    if (countdownId.value) clearInterval(countdownId.value);
    const passed = scoreInRound.value >= (roundConfig.value.totalTargets * 0.6);
    const avgTime = scoreInRound.value > 0 ? totalTimeTaken.value / scoreInRound.value : 5000;
    emit('submit', passed, { timeTaken: avgTime });
    return;
  }

  target.value.visible = false;
  const icons = ['🦋', '🐝', '🐞', '🦟', '🦗', '🕷️', '🦇', '🦅'];
  
  setTimeout(() => {
    target.value = {
      top: `${Math.floor(Math.random() * 80) + 10}%`,
      left: `${Math.floor(Math.random() * 80) + 10}%`,
      icon: icons[Math.floor(Math.random() * icons.length)],
      visible: true
    };
    spawnTime.value = Date.now();
    timeLeft.value = maxTime.value;
    roundConfig.value.targetsLeft--;

    if (countdownId.value) clearInterval(countdownId.value);
    countdownId.value = setInterval(() => {
      timeLeft.value -= 0.1;
      if (timeLeft.value <= 0) {
        clearInterval(countdownId.value);
        if (target.value.visible) handleClick(false);
      }
    }, 100);

    if (timerId.value) clearTimeout(timerId.value);
    timerId.value = setTimeout(() => {
      if (target.value.visible) handleClick(false);
    }, roundConfig.value.speed);
  }, 500);
}

function handleClick(success) {
  if (!target.value.visible && success) return;
  target.value.visible = false;
  if (timerId.value) clearTimeout(timerId.value);
  if (countdownId.value) clearInterval(countdownId.value);

  if (success) {
    scoreInRound.value++;
    totalTimeTaken.value += (Date.now() - spawnTime.value);
    spawnTarget();
  } else {
    lives.value--;
    if (lives.value <= 0) {
      emit('submit', false);
    } else {
      spawnTarget();
    }
  }
}

function handleAreaClick() {
  if (target.value.visible) handleClick(false);
}

watch(() => props.level, () => {
  generateQuestion();
});

onMounted(() => {
  generateQuestion();
});

onUnmounted(() => {
  if (timerId.value) clearTimeout(timerId.value);
  if (countdownId.value) clearInterval(countdownId.value);
});
</script>

<style scoped>
.reflex-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 100%;
  padding: 2.5rem;
  max-width: 800px;
}

.reflex-header {
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
  max-width: 60%;
}

.reflex-stats {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.lives-container {
  display: flex;
  gap: 0.5rem;
  font-size: 1.75rem;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.heart-icon { transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.heart-icon.lost { filter: grayscale(1); opacity: 0.2; transform: scale(0.8); }

.reflex-timer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  border-radius: var(--border-radius-full);
  font-weight: 900;
  font-size: 1.25rem;
  box-shadow: var(--shadow-sm);
  min-width: 100px;
}

.reflex-area {
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
  background: white;
  border: 4px solid var(--color-bg-tertiary);
  border-radius: 2rem;
  overflow: hidden;
  cursor: crosshair;
  box-shadow: var(--shadow-inner);
}

.reflex-target {
  position: absolute;
  padding: 0;
  margin: 0;
  width: 6rem;
  height: 6rem;
  background: white;
  border: 5px solid var(--color-primary);
  border-radius: 50%;
  box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  cursor: pointer;
  z-index: 10;
  transform: translate(-50%, -50%);
  transition: border-color 0.2s, transform 0.1s;
}

.reflex-target:hover {
  border-color: var(--color-primary-dark);
}

.pop-enter-active { animation: pop-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.pop-leave-active { animation: pop-in 0.2s reverse; }

@keyframes pop-in {
  0% { transform: translate(-50%, -50%) scale(0); }
  100% { transform: translate(-50%, -50%) scale(1); }
}

.timer-green { background: var(--bg-subtle-success); color: var(--color-success-dark); }
.timer-orange { background: var(--bg-subtle-warning); color: var(--color-warning-dark); }
.timer-red { background: var(--bg-subtle-error); color: var(--color-error-dark); }

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
</style>
