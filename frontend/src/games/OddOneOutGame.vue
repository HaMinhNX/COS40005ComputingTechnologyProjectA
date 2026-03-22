<template>
  <div class="odd-one-out glass-card">
    <div class="instruction">Tìm hình không cùng loại:</div>
    <div class="item-grid">
      <button
        v-for="(item, index) in question?.items"
        :key="index"
        @click="handleAnswer(index)"
        class="item-btn"
        :disabled="answerSubmitted"
      >
        <component :is="item.icon" :size="48" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, markRaw } from 'vue';
import { 
  Apple, Cherry, Coffee, Pizza, IceCream,
  Dog, Cat, Mouse, Bird, Fish, Turtle,
  Car, Bike, Truck, Plane, Bus, Rocket,
  Shirt, Watch, Briefcase, Glasses, Headset, Smartphone,
  Hammer, Wrench, Scissors, Axe,
  Cloud, Sun, Moon, Zap, Snowflake, Flower,
  Heart, Fingerprint, Eye, Footprints
} from 'lucide-vue-next';

const props = defineProps({
  level: { type: Number, default: 0 },
  answerSubmitted: { type: Boolean, default: false }
});

const emit = defineEmits(['submit', 'ready']);

const question = ref(null);
const startTime = ref(0);

const GROUPS = [
  { name: 'Trái cây', icons: [markRaw(Apple), markRaw(Cherry), markRaw(Coffee), markRaw(Pizza), markRaw(IceCream)] },
  { name: 'Động vật', icons: [markRaw(Dog), markRaw(Cat), markRaw(Mouse), markRaw(Bird), markRaw(Fish), markRaw(Turtle)] },
  { name: 'Phương tiện', icons: [markRaw(Car), markRaw(Bike), markRaw(Truck), markRaw(Plane), markRaw(Bus), markRaw(Rocket)] },
  { name: 'Cá nhân', icons: [markRaw(Shirt), markRaw(Watch), markRaw(Briefcase), markRaw(Glasses), markRaw(Headset), markRaw(Smartphone)] },
  { name: 'Công cụ', icons: [markRaw(Hammer), markRaw(Wrench), markRaw(Scissors), markRaw(Axe)] },
  { name: 'Thời tiết', icons: [markRaw(Cloud), markRaw(Sun), markRaw(Moon), markRaw(Zap), markRaw(Snowflake), markRaw(Flower)] },
  { name: 'Cơ thể', icons: [markRaw(Heart), markRaw(Fingerprint), markRaw(Eye), markRaw(Footprints)] }
];

function handleAnswer(index) {
  const timeTaken = Date.now() - startTime.value;
  const isCorrect = index === question.value.oddIndex;
  emit('submit', isCorrect, { timeTaken });
}

function generateQuestion() {
  startTime.value = Date.now();
  
  // Select a main group
  const groupIndex = Math.floor(Math.random() * GROUPS.length);
  const mainGroup = GROUPS[groupIndex];
  
  // Select 3 random icons from main group
  const shuffledMain = [...mainGroup.icons].sort(() => Math.random() - 0.5);
  const items = shuffledMain.slice(0, 3).map(icon => ({ icon }));
  
  // Select 1 icon from a different group
  let otherGroupIndex = Math.floor(Math.random() * GROUPS.length);
  while (otherGroupIndex === groupIndex) {
    otherGroupIndex = Math.floor(Math.random() * GROUPS.length);
  }
  const otherGroup = GROUPS[otherGroupIndex];
  const oddIcon = otherGroup.icons[Math.floor(Math.random() * otherGroup.icons.length)];
  
  // Insert odd icon at random position
  const oddIndex = Math.floor(Math.random() * 4);
  items.splice(oddIndex, 0, { icon: oddIcon });

  question.value = {
    items,
    oddIndex
  };
  
  emit('ready', question.value);
}

watch(() => props.level, () => generateQuestion());
onMounted(() => generateQuestion());
</script>

<style scoped>
.odd-one-out {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  padding: 2.5rem;
  width: 100%;
  max-width: 600px;
}

.instruction {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-text-secondary);
  text-transform: uppercase;
}

.item-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  width: 100%;
}

.item-btn {
  aspect-ratio: 1;
  background: white;
  border: 4px solid var(--color-primary-lighter);
  border-radius: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  color: var(--color-primary);
}

.item-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  background: var(--color-primary-lighter);
  transform: scale(1.05);
  box-shadow: var(--shadow-md);
}

.item-btn:disabled {
  opacity: 0.6;
}
</style>
