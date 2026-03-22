<template>
  <div class="category-game glass-card">
    <div class="item-display">
      <div class="item-card animate-pop">
        <component :is="question?.item.icon" v-if="question?.item.icon" :size="80" class="item-icon" />
        <div class="item-name">{{ question?.item.name }}</div>
      </div>
    </div>

    <div class="category-grid">
      <button
        v-for="cat in question?.categories"
        :key="cat.id"
        @click="handleAnswer(cat.id)"
        class="category-btn"
        :disabled="answerSubmitted"
      >
        <component :is="cat.icon" :size="24" />
        <span>{{ cat.name }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, markRaw } from 'vue';
import { 
  Apple, Car, Dog, Shirt, 
  Utensils, Bike, Cat,
  Cherry, Truck, Watch,
  Coffee, Pizza, Sandwich, IceCream,
  Bus, Train, Plane, Rocket,
  Bird, Fish, Mouse, Turtle,
  Lamp, Sofa, Bed, Tv,
  Trees, Flower, Cloud, Sun,
  Beef, Milk, Flame
} from 'lucide-vue-next';

const props = defineProps({
  level: { type: Number, default: 0 },
  answerSubmitted: { type: Boolean, default: false }
});

const emit = defineEmits(['submit', 'ready']);

const question = ref(null);
const startTime = ref(0);

// ... (existing categories)
const CATEGORIES = {
  food: { name: 'Thực phẩm', icon: markRaw(Utensils) },
  vehicle: { name: 'Phương tiện', icon: markRaw(Car) },
  animal: { name: 'Động vật', icon: markRaw(Dog) },
  clothing: { name: 'Trang phục', icon: markRaw(Shirt) },
  furniture: { name: 'Nội thất', icon: markRaw(Sofa) },
  nature: { name: 'Tự nhiên', icon: markRaw(Trees) }
};

const ITEMS = [
  { name: 'Táo', category: 'food', icon: markRaw(Apple) },
  { name: 'Anh đào', category: 'food', icon: markRaw(Cherry) },
  { name: 'Cà phê', category: 'food', icon: markRaw(Coffee) },
  { name: 'Pizza', category: 'food', icon: markRaw(Pizza) },
  { name: 'Bánh mì', category: 'food', icon: markRaw(Sandwich) },
  { name: 'Kem', category: 'food', icon: markRaw(IceCream) },
  { name: 'Thịt bò', category: 'food', icon: markRaw(Beef) },
  { name: 'Sữa', category: 'food', icon: markRaw(Milk) },
  { name: 'Xe hơi', category: 'vehicle', icon: markRaw(Car) },
  { name: 'Xe tải', category: 'vehicle', icon: markRaw(Truck) },
  { name: 'Xe buýt', category: 'vehicle', icon: markRaw(Bus) },
  { name: 'Tàu hỏa', category: 'vehicle', icon: markRaw(Train) },
  { name: 'Máy bay', category: 'vehicle', icon: markRaw(Plane) },
  { name: 'Tên lửa', category: 'vehicle', icon: markRaw(Rocket) },
  { name: 'Xe đạp', category: 'vehicle', icon: markRaw(Bike) },
  { name: 'Chó', category: 'animal', icon: markRaw(Dog) },
  { name: 'Mèo', category: 'animal', icon: markRaw(Cat) },
  { name: 'Chim', category: 'animal', icon: markRaw(Bird) },
  { name: 'Cá', category: 'animal', icon: markRaw(Fish) },
  { name: 'Chuột', category: 'animal', icon: markRaw(Mouse) },
  { name: 'Rùa', category: 'animal', icon: markRaw(Turtle) },
  { name: 'Áo thun', category: 'clothing', icon: markRaw(Shirt) },
  { name: 'Đồng hồ', category: 'clothing', icon: markRaw(Watch) },
  { name: 'Sofa', category: 'furniture', icon: markRaw(Sofa) },
  { name: 'Giường', category: 'furniture', icon: markRaw(Bed) },
  { name: 'Đèn', category: 'furniture', icon: markRaw(Lamp) },
  { name: 'Ti vi', category: 'furniture', icon: markRaw(Tv) },
  { name: 'Cây', category: 'nature', icon: markRaw(Trees) },
  { name: 'Hoa', category: 'nature', icon: markRaw(Flower) },
  { name: 'Mây', category: 'nature', icon: markRaw(Cloud) },
  { name: 'Mặt trời', category: 'nature', icon: markRaw(Sun) },
  { name: 'Ngọn lửa', category: 'nature', icon: markRaw(Flame) }
];

function handleAnswer(categoryId) {
  const timeTaken = Date.now() - startTime.value;
  const isCorrect = categoryId === question.value.item.category;
  emit('submit', isCorrect, { timeTaken });
}

function generateQuestion() {
  startTime.value = Date.now();
  
  // Select a random item
  const randomItem = ITEMS[Math.floor(Math.random() * ITEMS.length)];
  
  // Select 2 categories (one correct, one incorrect)
  const catKeys = Object.keys(CATEGORIES);
  const correctCat = randomItem.category;
  let wrongCat = catKeys[Math.floor(Math.random() * catKeys.length)];
  while (wrongCat === correctCat) {
    wrongCat = catKeys[Math.floor(Math.random() * catKeys.length)];
  }

  const selectedCategories = [
    { id: correctCat, ...CATEGORIES[correctCat] },
    { id: wrongCat, ...CATEGORIES[wrongCat] }
  ].sort(() => Math.random() - 0.5);

  question.value = {
    item: randomItem,
    categories: selectedCategories
  };
  
  emit('ready', question.value);
}

watch(() => props.level, () => generateQuestion());
onMounted(() => generateQuestion());
</script>

<style scoped>
.category-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3rem;
  padding: 2.5rem;
  width: 100%;
  max-width: 600px;
}

.item-display {
  perspective: 1000px;
}

.item-card {
  background: white;
  border: 6px solid var(--color-primary-lighter);
  border-radius: 2.5rem;
  padding: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  box-shadow: var(--shadow-lg);
  min-width: 250px;
}

.item-icon {
  color: var(--color-primary);
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
}

.item-name {
  font-size: 2.5rem;
  font-weight: 900;
  color: var(--color-text-primary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  width: 100%;
}

.category-btn {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  background: white;
  border: 4px solid var(--color-primary-lighter);
  border-radius: 1.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.category-btn span {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--color-text-secondary);
}

.category-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  background: var(--color-primary-lighter);
  transform: translateY(-6px);
  box-shadow: var(--shadow-md);
}

.category-btn:disabled {
  opacity: 0.6;
}

@keyframes pop {
  0% { transform: scale(0.8); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
.animate-pop {
  animation: pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
</style>
