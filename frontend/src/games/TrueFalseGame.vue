<template>
  <div class="true-false-game glass-card">
    <div class="statement-card shadow-xl">
      <div class="statement-text">{{ question?.text }}</div>
    </div>

    <div class="action-buttons">
      <button @click="handleAnswer(true)" class="btn-true" :disabled="answerSubmitted">
        <CheckCircle :size="32" />
        <span>ĐÚNG</span>
      </button>
      <button @click="handleAnswer(false)" class="btn-false" :disabled="answerSubmitted">
        <XCircle :size="32" />
        <span>SAI</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { CheckCircle, XCircle } from 'lucide-vue-next';

const props = defineProps({
  level: { type: Number, default: 0 },
  answerSubmitted: { type: Boolean, default: false }
});

const emit = defineEmits(['submit', 'ready']);

const question = ref(null);
const startTime = ref(0);

function handleAnswer(value) {
  const timeTaken = Date.now() - startTime.value;
  const isCorrect = value === question.value.answer;
  emit('submit', isCorrect, { timeTaken });
}

function generateQuestion() {
  startTime.value = Date.now();
  const level = props.level;
  
  let text = '';
  let answer = true;
  
  const type = Math.floor(Math.random() * (level > 4 ? 3 : 2));
  
  if (type === 0) {
    // Math fact (random operation)
    const n1 = Math.floor(Math.random() * 30) + 1;
    const n2 = Math.floor(Math.random() * 30) + 1;
    const op = Math.random() > 0.5 ? '+' : '-';
    answer = Math.random() > 0.5;
    let result = op === '+' ? n1 + n2 : n1 - n2;
    if (!answer) result += (Math.random() > 0.5 ? 1 : -1) * (Math.floor(Math.random() * 5) + 1);
    text = `${n1} ${op} ${n2} = ${result}`;
  } else if (type === 1) {
    // General Knowledge / Logic
    const facts = [
      { t: "Bầu trời có màu xanh", a: true },
      { t: "Nước sôi ở 100 độ C", a: true },
      { t: "Con chó có 5 chân", a: false },
      { t: "Mặt trời mọc ở hướng Tây", a: false },
      { t: "Chim biết bay", a: true },
      { t: "Cá sống dưới nước", a: true },
      { t: "Quả chuối có màu tím", a: false },
      { t: "Sữa có màu trắng", a: true },
      { t: "Con người có 3 mắt", a: false },
      { t: "Mùa đông thường lạnh", a: true },
      { t: "1 giờ có 100 phút", a: false },
      { t: "Trái đất hình vuông", a: false },
      { t: "Lửa thì nóng", a: true },
      { t: "Băng thì lạnh", a: true },
      { t: "Con mèo kêu gâu gâu", a: false },
      { t: "Hình vuông có 4 cạnh", a: true },
      { t: "Vịt biết bơi", a: true },
      { t: "Xe hơi có cánh để bay", a: false },
      { t: "Ngựa có 4 chân", a: true },
      { t: "Cây xanh nhờ ánh sáng", a: true }
    ];
    const item = facts[Math.floor(Math.random() * facts.length)];
    text = item.t;
    answer = item.a;
  } else {
    // Relationship / Antonym Logic
    const logicQueries = [
      { t: "Mẹ của bố là bà nội", a: true },
      { t: "Bố của mẹ là ông ngoại", a: true },
      { t: "Con của cô là em họ", a: true },
      { t: "Anh trai của bố là bác", a: true },
      { t: "Lạnh trái ngược với nóng", a: true },
      { t: "Cao trái ngược với thấp", a: true },
      { t: "To trái ngược với lớn", a: false },
      { t: "Nhanh trái ngược với chậm", a: true },
      { t: "Sáng trái ngược với đêm", a: true },
      { t: "Đỏ trái ngược với xanh", a: false }
    ];
    const item = logicQueries[Math.floor(Math.random() * logicQueries.length)];
    text = item.t;
    answer = item.a;
  }

  question.value = { text, answer };
  emit('ready', question.value);
}

watch(() => props.level, () => generateQuestion());
onMounted(() => generateQuestion());
</script>

<style scoped>
.true-false-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3rem;
  padding: 2.5rem;
  width: 100%;
  max-width: 600px;
}

.statement-card {
  background: white;
  border: 6px solid var(--color-primary-lighter);
  border-radius: 2.5rem;
  padding: 4rem 2rem;
  width: 100%;
  text-align: center;
}

.statement-text {
  font-size: 2.5rem;
  font-weight: 900;
  color: var(--color-text-primary);
  line-height: 1.3;
}

.action-buttons {
  display: flex;
  gap: 2rem;
  width: 100%;
}

.btn-true, .btn-false {
  flex: 1;
  padding: 1.5rem;
  border-radius: 2rem;
  font-weight: 900;
  font-size: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 4px solid transparent;
}

.btn-true {
  background: #ECFDF5;
  color: #059669;
  border-color: #A7F3D0;
}

.btn-true:hover:not(:disabled) {
  background: #D1FAE5;
  transform: translateY(-8px);
  box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.2);
}

.btn-false {
  background: #FEF2F2;
  color: #DC2626;
  border-color: #FECACA;
}

.btn-false:hover:not(:disabled) {
  background: #FEE2E2;
  transform: translateY(-8px);
  box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.2);
}

.btn-true:disabled, .btn-false:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
