<template>
  <div class="math-game glass-card">
    <div class="question-text">{{ question?.question }}</div>
    <div class="answer-grid">
      <button
        v-for="option in question?.options"
        :key="option"
        @click="handleAnswer(option)"
        class="answer-btn"
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

const question = ref({ question: '', answer: 0, options: [] });
const startTime = ref(0);

function handleAnswer(option) {
  const timeTaken = Date.now() - startTime.value;
  const isCorrect = option === question.value.answer;
  emit('submit', isCorrect, { timeTaken });
}

function generateQuestion() {
  startTime.value = Date.now();
  const level = props.level;
  let num1, num2, num3, answer, questionText;

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
    questionText = `${num1} ${operation} ${num2} = ?`;
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
    questionText = `${num1} ${operation} ${num2} = ?`;
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
      questionText = `${num1} × ${num2} ${op2} ${num3} = ?`;
    } else {
      num1 = Math.floor(Math.random() * 50) + 20;
      num2 = Math.floor(Math.random() * 30) + 10;
      num3 = Math.floor(Math.random() * 20) + 5;
      const first = op1 === '+' ? num1 + num2 : num1 - num2;
      answer = op2 === '+' ? first + num3 : first - num3;
      questionText = `${num1} ${op1} ${num2} ${op2} ${num3} = ?`;
    }
  }
  // Level 9+: Complex multi-step with larger numbers
  else {
    const choice = Math.floor(Math.random() * 3);

    if (choice === 0) {
      const a = Math.floor(Math.random() * 12) + 3;
      const b = Math.floor(Math.random() * 12) + 3;
      const c = Math.floor(Math.random() * 10) + 2;
      const d = Math.floor(Math.random() * 10) + 2;
      answer = (a * b) + (c * d);
      questionText = `(${a} × ${b}) + (${c} × ${d}) = ?`;
    } else if (choice === 1) {
      const a = Math.floor(Math.random() * 20) + 5;
      const b = Math.floor(Math.random() * 20) + 5;
      const c = Math.floor(Math.random() * 8) + 2;
      answer = (a + b) * c;
      questionText = `(${a} + ${b}) × ${c} = ?`;
    } else {
      const a = Math.floor(Math.random() * 15) + 5;
      const b = Math.floor(Math.random() * 12) + 3;
      const c = Math.floor(Math.random() * 10) + 2;
      const d = Math.floor(Math.random() * 8) + 2;
      answer = (a * b) - (c * d);
      questionText = `${a} × ${b} - ${c} × ${d} = ?`;
    }
  }

  // Generate options
  const options = new Set([answer]);
  const range = level < 3 ? 8 : (level < 6 ? 15 : 25);
  while (options.size < 4) {
    const offset = Math.floor(Math.random() * range * 2) - range;
    const option = answer + offset;
    if (option > 0 && option !== answer) options.add(option);
  }

  question.value = {
    question: questionText,
    answer: answer,
    options: Array.from(options).sort(() => Math.random() - 0.5)
  };
  
  emit('ready', question.value);
}

// Re-generate when level changes (new question)
watch(() => props.level, () => {
  generateQuestion();
});

onMounted(() => {
  generateQuestion();
});
</script>

<style scoped>
.math-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
  width: 100%;
  max-width: 600px;
}

.question-text {
  font-size: 3.5rem;
  font-weight: 900;
  color: var(--color-text-primary);
  padding: 2.5rem;
  background: var(--bg-subtle-info);
  border: 4px solid var(--color-info);
  border-radius: 1.5rem;
  width: 100%;
  text-align: center;
  box-shadow: var(--shadow-sm);
}

.answer-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  width: 100%;
}

.answer-btn {
  padding: 1.5rem;
  font-size: 2rem;
  font-weight: 900;
  background: white;
  border: 4px solid var(--color-primary-lighter);
  border-radius: 1.25rem;
  color: var(--color-primary-dark);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: var(--shadow-sm);
}

.answer-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  background: var(--color-primary-lighter);
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.answer-btn:active:not(:disabled) {
  transform: translateY(0);
}

.answer-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
