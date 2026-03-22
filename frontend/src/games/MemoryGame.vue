<template>
  <div class="memory-game glass-card">
    <div v-if="phase === 'show'" class="memory-show">
      <div class="instruction-text">Hãy nhớ các số sau:</div>
      <div class="memory-numbers">
        <div v-for="(num, idx) in sequence" :key="idx" class="memory-number">
          {{ num }}
        </div>
      </div>
      <div class="timer-display" :class="timerClass">{{ timer }}s</div>
    </div>
    <div v-else-if="phase === 'recall'" class="memory-recall">
      <div class="instruction-text">Kéo thả các số đúng theo thứ tự:</div>

      <!-- Answer Slots -->
      <div class="memory-answer-slots">
        <div
          v-for="(slot, idx) in answerSlots"
          :key="idx"
          class="memory-slot"
          @click="handleSlotClick(idx)"
        >
          <span v-if="slot !== null" class="slot-number">{{ slot }}</span>
          <span v-else class="slot-placeholder">{{ idx + 1 }}</span>
        </div>
      </div>

      <!-- Number Bank -->
      <div class="memory-number-bank">
        <div
          v-for="num in numberBank"
          :key="num.id"
          class="memory-bank-number"
          :class="{ 'used': num.used }"
          @click="!num.used && handleBankClick(num)"
        >
          {{ num.value }}
        </div>
      </div>

      <button @click="submitAnswer" class="btn-submit" :disabled="!isAnswerComplete">
        <span class="submit-text">Xác nhận</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps({
  level: { type: Number, default: 0 }
});

const emit = defineEmits(['submit']);

const phase = ref('show'); // 'show' or 'recall'
const sequence = ref([]);
const timer = ref(5);
const answerSlots = ref([]);
const numberBank = ref([]);
const startTime = ref(0);

const timerClass = computed(() => {
  if (timer.value <= 2) return 'timer-red';
  if (timer.value <= 4) return 'timer-orange';
  return 'timer-green';
});

const isAnswerComplete = computed(() => {
  return answerSlots.value.every(slot => slot !== null);
});

function generateQuestion() {
  phase.value = 'show';
  const level = props.level;
  const length = 3 + Math.floor(level / 2);

  sequence.value = Array.from({ length }, () => Math.floor(Math.random() * 9) + 1);

  const showTime = Math.max(3, 6 - Math.floor(level / 3));
  timer.value = showTime;

  const interval = setInterval(() => {
    timer.value--;
    if (timer.value <= 0) {
      clearInterval(interval);
      startRecallPhase(length);
    }
  }, 1000);
}

function startRecallPhase(length) {
  phase.value = 'recall';
  startTime.value = Date.now();
  answerSlots.value = Array(length).fill(null);

  const decoyCount = Math.min(length + 2, 6);
  const allNumbers = [...sequence.value];

  while (allNumbers.length < length + decoyCount) {
    const decoy = Math.floor(Math.random() * 9) + 1;
    allNumbers.push(decoy);
  }

  numberBank.value = allNumbers
    .sort(() => Math.random() - 0.5)
    .map((value, id) => ({ id, value, used: false }));
}

function handleBankClick(num) {
  const emptyIndex = answerSlots.value.findIndex(slot => slot === null);
  if (emptyIndex !== -1) {
    answerSlots.value[emptyIndex] = num.value;
    num.used = true;
  }
}

function handleSlotClick(index) {
  const value = answerSlots.value[index];
  if (value !== null) {
    const bankNum = numberBank.value.find(n => n.value === value && n.used);
    if (bankNum) bankNum.used = false;
    answerSlots.value[index] = null;
  }
}

function submitAnswer() {
  const timeTaken = Date.now() - startTime.value;
  const correct = JSON.stringify(answerSlots.value) === JSON.stringify(sequence.value);
  emit('submit', correct, { timeTaken });
}

watch(() => props.level, () => {
  generateQuestion();
});

onMounted(() => {
  generateQuestion();
});
</script>

<style scoped>
.memory-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 100%;
  padding: 2.5rem;
  max-width: 700px;
}

.memory-show, .memory-recall {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.instruction-text {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text-secondary);
  margin-bottom: 2rem;
}

.memory-numbers {
  display: flex;
  gap: 1.25rem;
  margin-bottom: 3rem;
  flex-wrap: wrap;
  justify-content: center;
}

.memory-number {
  width: 5rem;
  height: 5rem;
  background: white;
  border: 4px solid var(--color-primary);
  border-radius: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: 900;
  color: var(--color-primary-dark);
  box-shadow: var(--shadow-md);
  animation: bounceIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.timer-display {
  font-size: 4rem;
  font-weight: 900;
  margin-top: 1rem;
}

.timer-green { color: var(--color-success); }
.timer-orange { color: var(--color-warning); animation: pulse 1s infinite; }
.timer-red { color: var(--color-error); animation: pulse 0.5s infinite; }

.memory-answer-slots {
  display: flex;
  gap: 1.25rem;
  margin-bottom: 3rem;
  flex-wrap: wrap;
  justify-content: center;
}

.memory-slot {
  width: 4.5rem;
  height: 4.5rem;
  background: var(--bg-subtle-primary);
  border: 3px dashed var(--color-primary-light);
  border-radius: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.memory-slot:hover {
  border-color: var(--color-primary);
  background: white;
}

.slot-number {
  font-size: 2.25rem;
  font-weight: 900;
  color: var(--color-primary-dark);
}

.slot-placeholder {
  color: var(--color-text-muted);
  font-weight: 700;
  font-size: 1.25rem;
}

.memory-number-bank {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-bottom: 3rem;
  background: rgba(255, 255, 255, 0.5);
  padding: 1.5rem;
  border-radius: 1.5rem;
  border: 2px solid var(--color-bg-tertiary);
}

.memory-bank-number {
  width: 4rem;
  height: 4rem;
  background: white;
  border: 3px solid var(--color-bg-tertiary);
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: var(--shadow-sm);
}

.memory-bank-number:hover:not(.used) {
  border-color: var(--color-primary);
  background: var(--bg-subtle-primary);
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.memory-bank-number.used {
  opacity: 0.2;
  cursor: not-allowed;
  transform: scale(0.9);
}

.btn-submit {
  padding: 1.25rem 3.5rem;
  background: var(--color-success);
  color: white;
  border: none;
  border-radius: var(--border-radius-full);
  font-size: 1.5rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: var(--shadow-success);
}

.btn-submit:hover:not(:disabled) {
  background: var(--color-success-dark);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(1);
}

@keyframes bounceIn {
  from { opacity: 0; transform: scale(0.3); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
</style>
