<template>
  <div class="pattern-game glass-card">
    <div class="instruction-text">Chọn hình tiếp theo trong chuỗi:</div>
    <div class="pattern-sequence">
      <div v-for="(shape, idx) in sequence" :key="idx" class="pattern-item">
        {{ shape }}
      </div>
      <div class="pattern-item pattern-question">?</div>
    </div>
    <div class="pattern-options">
      <button
        v-for="option in options"
        :key="option"
        @click="handleAnswer(option)"
        class="pattern-option-btn"
        :disabled="answerSubmitted"
      >
        {{ option }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({
  level: { type: Number, default: 0 },
  answerSubmitted: { type: Boolean, default: false }
});

const emit = defineEmits(['submit', 'ready']);

const sequence = ref([]);
const answer = ref('');
const options = ref([]);
const startTime = ref(0);

function handleAnswer(option) {
  const timeTaken = Date.now() - startTime.value;
  const isCorrect = option === answer.value;
  emit('submit', isCorrect, { timeTaken });
}

function generateQuestion() {
  startTime.value = Date.now();
  const patterns = [
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
  sequence.value = pattern.seq;
  answer.value = pattern.answer;
  options.value = pattern.options.sort(() => Math.random() - 0.5);
  
  emit('ready', { answer: answer.value });
}

watch(() => props.level, () => {
  generateQuestion();
});

onMounted(() => {
  generateQuestion();
});
</script>

<style scoped>
.pattern-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2.5rem;
  width: 100%;
  padding: 2.5rem;
  max-width: 700px;
}

.instruction-text {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text-secondary);
}

.pattern-sequence {
  display: flex;
  gap: 1.25rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  justify-content: center;
}

.pattern-item {
  width: 5rem;
  height: 5rem;
  background: white;
  border: 4px solid var(--color-bg-tertiary);
  border-radius: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.75rem;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s;
}

.pattern-question {
  border-color: var(--color-primary);
  color: var(--color-primary);
  font-weight: 900;
  border-style: dashed;
  background: var(--bg-subtle-primary);
}

.pattern-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  width: 100%;
}

.pattern-option-btn {
  padding: 1.5rem;
  font-size: 2.5rem;
  background: white;
  border: 4px solid var(--color-bg-tertiary);
  border-radius: 1.25rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: var(--shadow-sm);
}

.pattern-option-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  background: var(--bg-subtle-primary);
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.pattern-option-btn:active:not(:disabled) {
  transform: translateY(0);
}

.pattern-option-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
