<template>
  <div class="color-game glass-card">
    <div class="color-game-header">
      <div v-if="question.type === 'normal'" class="instruction-text">Vật này màu gì?</div>
      <div v-else class="instruction-text">Chữ bên dưới có MÀU gì?</div>
      <div class="color-timer" :class="timerClass">
        <span class="timer-icon">⏱️</span>
        <span class="timer-value">{{ timeLeft }}s</span>
      </div>
    </div>

    <div class="color-question-item">
      <div v-if="question.type === 'normal'" class="color-icon">{{ question.icon }}</div>
      <div
        class="color-name"
        :style="{
          color: question.displayColor,
          fontSize: question.type === 'stroop' ? '60px' : '',
          backgroundColor: question.type === 'stroop' ? question.backgroundColor : 'transparent',
          padding: question.type === 'stroop' ? '20px 40px' : '0',
          borderRadius: question.type === 'stroop' ? '12px' : '0'
        }"
      >
        {{ question.content }}
      </div>
    </div>

    <div class="color-options">
      <button
        v-for="(opt, idx) in question.options"
        :key="idx"
        @click="submitAnswer(opt.color)"
        class="color-option-btn"
        :style="{ backgroundColor: opt.bgColor || opt.color }"
        :disabled="answerSubmitted"
      >
        <span :style="{ color: opt.textColor || (opt.color === '#FFFFFF' ? '#000' : '#FFF'), fontWeight: '900' }">{{ opt.colorName }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  level: { type: Number, default: 0 },
  answerSubmitted: { type: Boolean, default: false }
});

const emit = defineEmits(['submit']);

const timeLeft = ref(10);
const timerId = ref(null);
const question = ref({
  type: 'normal',
  content: '',
  displayColor: '',
  backgroundColor: '',
  correctAnswer: '',
  options: []
});
const startTime = ref(0);

const timerClass = computed(() => {
  const percentage = (timeLeft.value / 10) * 100;
  if (percentage > 60) return 'timer-green';
  if (percentage > 30) return 'timer-orange';
  return 'timer-red';
});

function getContrastColor(hexColor) {
  const r = parseInt(hexColor.slice(1, 3), 16);
  const g = parseInt(hexColor.slice(3, 5), 16);
  const b = parseInt(hexColor.slice(5, 7), 16);
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5 ? '#000000' : '#FFFFFF';
}

function generateQuestion() {
  startTime.value = Date.now();
  const items = [
    { name: 'Quả Táo', color: '#EF4444', icon: '🍎', colorName: 'Đỏ' },
    { name: 'Quả Chuối', color: '#FFEB3B', icon: '🍌', colorName: 'Vàng' },
    { name: 'Cái Lá', color: '#10B981', icon: '🍃', colorName: 'Xanh Lá' },
    { name: 'Quả Nho', color: '#8B5CF6', icon: '🍇', colorName: 'Tím' },
    { name: 'Cà Rốt', color: '#FF9800', icon: '🥕', colorName: 'Cam' },
    { name: 'Than Đá', color: '#1F2937', icon: '🌑', colorName: 'Đen' },
    { name: 'Tuyết', color: '#FFFFFF', icon: '❄️', colorName: 'Trắng' },
    { name: 'Hoa Hồng', color: '#EC4899', icon: '🌹', colorName: 'Hồng' },
    { name: 'Biển', color: '#3B82F6', icon: '🌊', colorName: 'Xanh Dương' }
  ];

  timeLeft.value = 10;
  if (timerId.value) clearInterval(timerId.value);
  timerId.value = setInterval(() => {
    timeLeft.value--;
    if (timeLeft.value <= 0) {
      clearInterval(timerId.value);
      if (!props.answerSubmitted) emit('submit', null);
    }
  }, 1000);

  const isStroop = Math.random() < 0.5;

  if (isStroop) {
    const color1 = items[Math.floor(Math.random() * items.length)];
    let color2 = items[Math.floor(Math.random() * items.length)];
    while (color1.colorName === color2.colorName) {
      color2 = items[Math.floor(Math.random() * items.length)];
    }

    let bgColor = items[Math.floor(Math.random() * items.length)];
    while (bgColor.colorName === color1.colorName || bgColor.colorName === color2.colorName) {
      bgColor = items[Math.floor(Math.random() * items.length)];
    }

    question.value = {
      type: 'stroop',
      content: color1.colorName,
      displayColor: color2.color,
      backgroundColor: bgColor.color + '40',
      correctAnswer: color2.color,
      options: []
    };

    const qOptions = [color2];
    while (qOptions.length < 4) {
      const rnd = items[Math.floor(Math.random() * items.length)];
      if (!qOptions.find(o => o.color === rnd.color)) qOptions.push(rnd);
    }

    question.value.options = qOptions.map(opt => {
      let bgOpt;
      let attempts = 0;
      do {
        bgOpt = items[Math.floor(Math.random() * items.length)];
        attempts++;
      } while (bgOpt.colorName === opt.colorName && attempts < 10);
      return { ...opt, bgColor: bgOpt.color, textColor: getContrastColor(bgOpt.color) };
    }).sort(() => Math.random() - 0.5);

  } else {
    const item = items[Math.floor(Math.random() * items.length)];
    question.value = {
      type: 'normal',
      content: item.name,
      icon: item.icon,
      displayColor: 'black',
      correctAnswer: item.color,
      options: []
    };

    const qOptions = [item];
    while (qOptions.length < 4) {
      const rnd = items[Math.floor(Math.random() * items.length)];
      if (!qOptions.find(o => o.color === rnd.color)) qOptions.push(rnd);
    }

    question.value.options = qOptions.map(opt => {
      let bgOpt;
      let attempts = 0;
      do {
        bgOpt = items[Math.floor(Math.random() * items.length)];
        attempts++;
      } while (bgOpt.colorName === opt.colorName && attempts < 10);
      return { ...opt, bgColor: bgOpt.color, textColor: getContrastColor(bgOpt.color) };
    }).sort(() => Math.random() - 0.5);
  }
}

function submitAnswer(color) {
  const timeTaken = Date.now() - startTime.value;
  if (timerId.value) clearInterval(timerId.value);
  emit('submit', color === question.value.correctAnswer, { timeTaken });
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
.color-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2.5rem;
  width: 100%;
  padding: 2.5rem;
  max-width: 700px;
}

.color-game-header {
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
  max-width: 70%;
}

.color-timer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  border-radius: var(--border-radius-full);
  font-weight: 900;
  font-size: 1.25rem;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s;
}

.timer-green { background: var(--bg-subtle-success); color: var(--color-success-dark); }
.timer-orange { background: var(--bg-subtle-warning); color: var(--color-warning-dark); animation: pulse 1s infinite; }
.timer-red { background: var(--bg-subtle-error); color: var(--color-error-dark); animation: pulse 0.5s infinite; }

.color-question-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;
  background: white;
  border-radius: 2rem;
  box-shadow: var(--shadow-md);
  width: 100%;
}

.color-icon { font-size: 6rem; filter: drop-shadow(0 4px 10px rgba(0,0,0,0.1)); }
.color-name { font-size: 4rem; font-weight: 900; text-align: center; line-height: 1.2; }

.color-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  width: 100%;
}

.color-option-btn {
  padding: 1.75rem;
  font-size: 1.75rem;
  border: 4px solid rgba(0, 0, 0, 0.05);
  border-radius: 1.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}

.color-option-btn:hover:not(:disabled) {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(0, 0, 0, 0.1);
}

.color-option-btn:active:not(:disabled) {
  transform: translateY(0);
}

.color-option-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  filter: grayscale(0.5);
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
</style>
