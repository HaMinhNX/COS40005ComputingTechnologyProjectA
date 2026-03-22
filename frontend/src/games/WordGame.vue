<template>
  <div class="word-game glass-card">
    <div class="instruction-text">Sắp xếp các chữ cái thành từ có nghĩa:</div>

    <!-- Word Hint -->
    <div v-if="hint" class="word-hint-box">
      <div class="hint-row">
        <span class="hint-icon">💡</span>
        <span class="hint-text">{{ hint }}</span>
      </div>
      <div v-if="meaning" class="hint-meaning">
        <span class="meaning-icon">📖</span>
        <span class="meaning-text">{{ meaning }}</span>
      </div>
    </div>

    <!-- Answer Area -->
    <div class="word-answer-container">
      <div v-if="structure.length > 0" class="word-groups">
        <div v-for="(group, groupIdx) in structure" :key="'group-' + groupIdx" class="word-group">
          <div
            v-for="(charSlot, charIdx) in group"
            :key="'slot-' + groupIdx + '-' + charIdx"
            class="char-slot"
            :class="{ 'filled': charSlot.filled, 'empty': !charSlot.filled }"
            @click="handleSlotClick(groupIdx, charIdx)"
          >
            <span v-if="charSlot.filled" class="char-value">{{ charSlot.char }}</span>
            <span v-else class="char-placeholder">_</span>
          </div>
        </div>
      </div>

      <div v-else class="word-answer-area-simple">
        <div
          v-for="(tile, idx) in answerTiles"
          :key="idx"
          class="word-tile answer-tile"
          @click="handleAnswerTileClick(idx)"
        >
          {{ tile.letter }}
        </div>
        <div v-if="answerTiles.length === 0" class="word-placeholder">
          Chọn chữ cái bên dưới
        </div>
      </div>
    </div>

    <!-- Letter Bank -->
    <div class="word-bank">
      <div
        v-for="tile in tiles"
        :key="tile.id"
        class="word-tile bank-tile"
        :class="{ 'used': tile.used }"
        @click="!tile.used && handleTileClick(tile)"
      >
        {{ tile.letter }}
      </div>
    </div>

    <button @click="submitAnswer" class="btn-submit" :disabled="answerSubmitted || !isComplete">
      <span class="submit-text">Xác nhận</span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps({
  level: { type: Number, default: 0 },
  answerSubmitted: { type: Boolean, default: false }
});

const emit = defineEmits(['submit', 'ready']);

const correctWord = ref('');
const tiles = ref([]);
const answerTiles = ref([]);
const hint = ref('');
const meaning = ref('');
const structure = ref([]);
const startTime = ref(0);

const isComplete = computed(() => {
  if (structure.value.length > 0) {
    return structure.value.every(group => group.every(slot => slot.filled));
  }
  return answerTiles.value.length > 0;
});

function generateQuestion() {
  startTime.value = Date.now();
  const level = props.level;
  let wordList;

  if (level < 3) {
    wordList = ['Nhật', 'Tuần', 'Tháng', 'Năm', 'Ngày', 'Máy', 'Bàn', 'Ghế', 'Cửa', 'Nhà', 'Nước', 'Cơm', 'Canh', 'Thịt', 'Cá'];
  } else if (level < 6) {
    wordList = ['Máy bay', 'Ôtô', 'Xe đạp', 'Máy tính', 'Sách vở', 'Bút chì', 'Thước kẻ', 'Áo quần', 'Giày dép'];
  } else if (level < 9) {
    wordList = ['Bệnh viện', 'Trường học', 'Nhà hàng', 'Siêu thị', 'Công viên', 'Sân bay', 'Bến xe'];
  } else {
    const proverbs = [
      { text: 'Có chí thì nên', meaning: 'Khi có quyết tâm và ý chí thì sẽ thành công' },
      { text: 'Đoàn kết là sức mạnh', meaning: 'Khi mọi người đoàn kết với nhau sẽ tạo ra sức mạnh lớn' },
      { text: 'Uống nước nhớ nguồn', meaning: 'Biết ơn công lao của người đi trước' },
      { text: 'Có công mài sắt có ngày nên kim', meaning: 'Chăm chỉ cố gắng sẽ đạt được thành công' },
      { text: 'Trăm hay không bằng một thấy', meaning: 'Nghe nhiều không bằng tự mình trải nghiệm' },
    ];
    const selected = proverbs[Math.floor(Math.random() * proverbs.length)];
    setupWord(selected.text, selected.meaning);
    return;
  }

  const selected = wordList[Math.floor(Math.random() * wordList.length)];
  setupWord(selected);
}

function setupWord(text, wordMeaning = '') {
  correctWord.value = text;
  meaning.value = wordMeaning;
  
  const words = text.split(' ');
  if (words.length > 1 || text.length > 5) {
    hint.value = wordMeaning ? `${words.length} từ` : '';
    structure.value = words.map(word =>
      word.split('').map(char => ({ char: '', filled: false, correctChar: char }))
    );
  } else {
    hint.value = '';
    structure.value = [];
  }

  const lettersOnly = text.replace(/ /g, '').split('');
  for (let i = lettersOnly.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [lettersOnly[i], lettersOnly[j]] = [lettersOnly[j], lettersOnly[i]];
  }

  tiles.value = lettersOnly.map((l, i) => ({ id: i, letter: l, used: false }));
  answerTiles.value = [];
  
  emit('ready', { correctWord: correctWord.value });
}

function handleTileClick(tile) {
  if (props.answerSubmitted) return;

  if (structure.value.length > 0) {
    for (let gIdx = 0; gIdx < structure.value.length; gIdx++) {
      for (let cIdx = 0; cIdx < structure.value[gIdx].length; cIdx++) {
        const slot = structure.value[gIdx][cIdx];
        if (!slot.filled) {
          slot.char = tile.letter;
          slot.filled = true;
          slot.tileId = tile.id;
          tile.used = true;
          return;
        }
      }
    }
  } else {
    tile.used = true;
    answerTiles.value.push({ ...tile });
  }
}

function handleSlotClick(gIdx, cIdx) {
  if (props.answerSubmitted) return;
  const slot = structure.value[gIdx][cIdx];
  if (slot.filled) {
    const tile = tiles.value.find(t => t.id === slot.tileId);
    if (tile) tile.used = false;
    slot.char = '';
    slot.filled = false;
  }
}

function handleAnswerTileClick(index) {
  if (props.answerSubmitted) return;
  const tile = answerTiles.value[index];
  const orig = tiles.value.find(t => t.id === tile.id);
  if (orig) orig.used = false;
  answerTiles.value.splice(index, 1);
}

function submitAnswer() {
  const timeTaken = Date.now() - startTime.value;
  let userAnswer;
  if (structure.value.length > 0) {
    userAnswer = structure.value.map(g => g.map(s => s.char).join('')).join(' ');
  } else {
    userAnswer = answerTiles.value.map(t => t.letter).join('');
  }
  
  const correct = userAnswer.toLowerCase().replace(/ /g, '') === correctWord.value.toLowerCase().replace(/ /g, '');
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
.word-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 100%;
  padding: 2.5rem;
  max-width: 800px;
}

.instruction-text {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text-secondary);
}

.word-hint-box {
  background: var(--bg-subtle-warning);
  border: 3px solid var(--color-warning);
  border-radius: 1.5rem;
  padding: 1.5rem;
  width: 100%;
  box-shadow: var(--shadow-sm);
}

.hint-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.hint-text {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--color-warning-dark);
}

.hint-meaning {
  border-top: 1px solid var(--color-warning-light);
  padding-top: 0.75rem;
  font-style: italic;
  font-size: 1.1rem;
  color: var(--color-warning-dark);
  opacity: 0.8;
}

.word-answer-container {
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 1rem 0;
}

.word-groups {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  justify-content: center;
}

.word-group {
  display: flex;
  gap: 0.75rem;
}

.char-slot {
  width: 3.5rem;
  height: 4.5rem;
  background: var(--bg-subtle-primary);
  border: 3px dashed var(--color-primary-light);
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 2rem;
  font-weight: 900;
  transition: all 0.3s;
}

.char-slot.filled {
  border-style: solid;
  border-color: var(--color-primary);
  background: white;
  color: var(--color-primary-dark);
  box-shadow: var(--shadow-sm);
  transform: translateY(-2px);
}

.word-answer-area-simple {
  display: flex;
  gap: 0.75rem;
  min-height: 5.5rem;
  background: var(--bg-subtle-primary);
  border: 3px dashed var(--color-primary-light);
  border-radius: 1.5rem;
  padding: 1rem;
  width: 100%;
  justify-content: center;
  align-items: center;
}

.word-tile {
  width: 3.5rem;
  height: 4.5rem;
  background: white;
  border: 3px solid var(--color-bg-tertiary);
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 900;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: var(--shadow-sm);
}

.bank-tile:hover:not(.used) {
  border-color: var(--color-primary);
  background: var(--bg-subtle-primary);
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.bank-tile.used {
  opacity: 0.2;
  cursor: not-allowed;
  transform: scale(0.9);
}

.word-bank {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin: 2rem 0;
  background: rgba(255, 255, 255, 0.5);
  padding: 1.5rem;
  border-radius: 2rem;
  border: 2px solid var(--color-bg-tertiary);
}

.btn-submit {
  padding: 1.25rem 4rem;
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
</style>
