<template>
  <div class="shadow-match glass-card">
    <div class="target-display">
      <div class="target-card">
        <component :is="question?.target.icon" :size="100" class="target-icon" />
      </div>
    </div>

    <div class="option-grid">
      <button
        v-for="(option, index) in question?.options"
        :key="index"
        @click="handleAnswer(index)"
        class="option-btn"
        :disabled="answerSubmitted"
      >
        <component :is="option.icon" :size="60" class="shadow-icon" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, markRaw } from 'vue';
import { 
  Heart, Star, Cloud, Moon, 
  Sun, Music, Bell, Ghost,
  Gift, Trophy, Anchor, Target,
  Flame, Zap, Snowflake, Flower, Trees,
  Bird, Fish, Mouse, Coffee, Pizza,
  Bus, Train, Plane, Rocket,
  Lamp, Sofa, Bed, Tv
} from 'lucide-vue-next';

const props = defineProps({
  level: { type: Number, default: 0 },
  answerSubmitted: { type: Boolean, default: false }
});

const emit = defineEmits(['submit', 'ready']);

const question = ref(null);
const startTime = ref(0);

const ICONS = [
  markRaw(Heart), markRaw(Star), markRaw(Cloud), markRaw(Moon),
  markRaw(Sun), markRaw(Music), markRaw(Bell), markRaw(Ghost),
  markRaw(Gift), markRaw(Trophy), markRaw(Anchor), markRaw(Target),
  markRaw(Flame), markRaw(Zap), markRaw(Snowflake), markRaw(Flower), markRaw(Trees),
  markRaw(Bird), markRaw(Fish), markRaw(Mouse), markRaw(Coffee), markRaw(Pizza),
  markRaw(Bus), markRaw(Train), markRaw(Plane), markRaw(Rocket),
  markRaw(Lamp), markRaw(Sofa), markRaw(Bed), markRaw(Tv)
];

function handleAnswer(index) {
  const timeTaken = Date.now() - startTime.value;
  const isCorrect = index === question.value.correctIndex;
  emit('submit', isCorrect, { timeTaken });
}

function generateQuestion() {
  startTime.value = Date.now();
  
  const shuffled = [...ICONS].sort(() => Math.random() - 0.5);
  const target = { icon: shuffled[0] };
  const options = shuffled.slice(0, 4).map(icon => ({ icon }));
  
  // Shuffle options and track correct index
  const finalOptions = [...options].sort(() => Math.random() - 0.5);
  const newCorrectIndex = finalOptions.findIndex(o => o.icon === target.icon);

  question.value = {
    target,
    options: finalOptions,
    correctIndex: newCorrectIndex
  };
  
  emit('ready', question.value);
}

watch(() => props.level, () => generateQuestion());
onMounted(() => generateQuestion());
</script>

<style scoped>
.shadow-match {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3rem;
  padding: 2.5rem;
  width: 100%;
  max-width: 600px;
}

.target-card {
  background: white;
  border: 6px solid var(--color-primary-lighter);
  border-radius: 2.5rem;
  padding: 3rem;
  box-shadow: var(--shadow-lg);
}

.target-icon {
  color: #3B82F6;
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
}

.option-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  width: 100%;
}

.option-btn {
  aspect-ratio: 1;
  background: white;
  border: 4px solid var(--color-primary-lighter);
  border-radius: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.shadow-icon {
  color: #1E293B; /* Dark gray to look like a shadow */
  filter: grayscale(1) brightness(0.2);
}

.option-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  background: var(--color-primary-lighter);
  transform: scale(1.05);
}

.option-btn:disabled {
  opacity: 0.6;
}
</style>
