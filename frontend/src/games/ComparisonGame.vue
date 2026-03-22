<template>
  <div class="comparison-game glass-card">
    <div class="comparison-display">
      <div class="side left-side">
        <div class="side-content">{{ question?.leftSide.text }}</div>
        <div v-if="question?.leftSide.hint" class="side-hint">{{ question?.leftSide.hint }}</div>
      </div>
      <div class="operator-placeholder">?</div>
      <div class="side right-side">
        <div class="side-content">{{ question?.rightSide.text }}</div>
        <div v-if="question?.rightSide.hint" class="side-hint">{{ question?.rightSide.hint }}</div>
      </div>
    </div>

    <div class="answer-grid">
      <button
        v-for="op in operators"
        :key="op.value"
        @click="handleAnswer(op.value)"
        class="answer-btn"
        :disabled="answerSubmitted"
      >
        {{ op.label }}
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

const question = ref(null);
const startTime = ref(0);
const operators = [
  { label: '>', value: '>' },
  { label: '=', value: '=' },
  { label: '<', value: '<' }
];

function handleAnswer(value) {
  const timeTaken = Date.now() - startTime.value;
  const isCorrect = value === question.value.answer;
  emit('submit', isCorrect, { timeTaken });
}

function generateQuestion() {
  startTime.value = Date.now();
  const level = props.level;
  
  let leftVal, rightVal, leftText, rightText;
  
  if (level < 2) {
    // Simple number comparison
    leftVal = Math.floor(Math.random() * 50) + 1;
    rightVal = Math.floor(Math.random() * 50) + 1;
    leftText = leftVal.toString();
    rightText = rightVal.toString();
  } else if (level < 5) {
    // Expression vs Number
    const op = Math.random() > 0.5 ? '+' : '-';
    const n1 = Math.floor(Math.random() * 20) + 5;
    const n2 = Math.floor(Math.random() * 20) + 1;
    leftVal = op === '+' ? n1 + n2 : n1 - n2;
    leftText = `${n1} ${op} ${n2}`;
    
    rightVal = Math.floor(Math.random() * 30) + 5;
    rightText = rightVal.toString();
  } else {
    // Expression vs Expression
    const ops = ['+', '-', '×'];
    const op1 = ops[Math.floor(Math.random() * 2)];
    const op2 = ops[Math.floor(Math.random() * (level > 7 ? 3 : 2))];
    
    const a = Math.floor(Math.random() * 15) + 5;
    const b = Math.floor(Math.random() * 10) + 2;
    leftVal = op1 === '+' ? a + b : (op1 === '-' ? a - b : a * b);
    leftText = `${a} ${op1} ${b}`;
    
    const c = Math.floor(Math.random() * 15) + 5;
    const d = Math.floor(Math.random() * 10) + 2;
    rightVal = op2 === '+' ? c + d : (op2 === '-' ? c - d : c * d);
    rightText = `${c} ${op2} ${d}`;
  }

  // Ensure some cases are equal
  if (Math.random() < 0.2) {
    rightVal = leftVal;
    // If it was supposed to be a number, update rightText
    if (level < 5 && rightText !== rightVal.toString()) {
        rightText = rightVal.toString();
    } else if (level >= 5) {
        // Just make them numerically equal even if text differs
    }
  }

  let answer = '=';
  if (leftVal > rightVal) answer = '>';
  else if (leftVal < rightVal) answer = '<';

  question.value = {
    leftSide: { text: leftText },
    rightSide: { text: rightText },
    answer: answer
  };
  
  emit('ready', question.value);
}

watch(() => props.level, () => generateQuestion());
onMounted(() => generateQuestion());
</script>

<style scoped>
.comparison-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2.5rem;
  padding: 2.5rem;
  width: 100%;
  max-width: 800px;
}

.comparison-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  width: 100%;
}

.side {
  flex: 1;
  background: white;
  border: 4px solid var(--color-primary-lighter);
  border-radius: 2rem;
  padding: 2.5rem 1.5rem;
  text-align: center;
  box-shadow: var(--shadow-sm);
  min-height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  transition: all 0.3s ease;
}

.side-content {
  font-size: 3rem;
  font-weight: 900;
  color: var(--color-text-primary);
}

.operator-placeholder {
  font-size: 4rem;
  font-weight: 900;
  color: var(--color-primary);
  background: var(--color-primary-lighter);
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset var(--shadow-sm);
}

.answer-grid {
  display: flex;
  gap: 1.5rem;
  width: 100%;
  justify-content: center;
}

.answer-btn {
  flex: 1;
  max-width: 120px;
  padding: 1.5rem 0;
  font-size: 2.5rem;
  font-weight: 900;
  background: white;
  border: 4px solid var(--color-primary-lighter);
  border-radius: 1.5rem;
  color: var(--color-primary-dark);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: var(--shadow-sm);
}

.answer-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  background: var(--color-primary-lighter);
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}

.answer-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .comparison-display {
    flex-direction: column;
    gap: 1rem;
  }
  .operator-placeholder {
    transform: rotate(90deg);
  }
}
</style>
