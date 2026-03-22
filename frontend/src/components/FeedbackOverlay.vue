<template>
  <transition name="feedback-fade">
    <div v-if="show" class="feedback-overlay" :class="tierClass">
      <div class="feedback-content">
        <div class="feedback-icon-wrapper">
          <component :is="icon" :size="80" class="feedback-icon" />
          <div v-if="tier === 'excellent'" class="confetti-particles">
            <div v-for="n in 12" :key="n" class="particle"></div>
          </div>
        </div>
        <h2 class="feedback-title">{{ title }}</h2>
        <p class="feedback-message">{{ message }}</p>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed, markRaw } from 'vue';
import { Trophy, Star, CheckCircle2 } from 'lucide-vue-next';

const props = defineProps({
  show: Boolean,
  tier: {
    type: String,
    default: 'normal', // 'excellent', 'good', 'normal'
    validator: (v) => ['excellent', 'good', 'normal'].includes(v)
  }
});

const tierClass = computed(() => `tier-${props.tier}`);

const icon = computed(() => {
  if (props.tier === 'excellent') return markRaw(Trophy);
  if (props.tier === 'good') return markRaw(Star);
  return markRaw(CheckCircle2);
});

const title = computed(() => {
  if (props.tier === 'excellent') return 'XUẤT SẮC!';
  if (props.tier === 'good') return 'RẤT TỐT!';
  return 'CHÍNH XÁC!';
});

const message = computed(() => {
  if (props.tier === 'excellent') return 'Bạn thật tuyệt vời! 🌟';
  if (props.tier === 'good') return 'Tiếp tục phát huy nhé! 👏';
  return 'Làm tốt lắm! 💪';
});
</script>

<style scoped>
.feedback-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: var(--border-radius-lg);
  pointer-events: none;
}

.feedback-content {
  text-align: center;
  padding: 2rem;
  border-radius: 2rem;
  background: white;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
  border: 4px solid currentColor;
  transform: scale(0.9);
  animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

.feedback-icon-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 1rem;
}

.feedback-icon {
  filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.2));
}

.feedback-title {
  font-size: 3rem;
  font-weight: 900;
  margin: 0;
  letter-spacing: 2px;
}

.feedback-message {
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 0.5rem;
  opacity: 0.9;
}

/* Tier Specific Styles */
.tier-excellent {
  color: #F59E0B; /* Amber/Gold */
}
.tier-excellent .feedback-content {
  border-color: #F59E0B;
  background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%);
}

.tier-good {
  color: #10B981; /* Emerald */
}
.tier-good .feedback-content {
  border-color: #10B981;
  background: linear-gradient(135deg, #ECFDF5 0%, #FFFFFF 100%);
}

.tier-normal {
  color: #3B82F6; /* Blue */
}
.tier-normal .feedback-content {
  border-color: #3B82F6;
  background: linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 100%);
}

/* Animations */
@keyframes popIn {
  from { opacity: 0; transform: scale(0.8) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.feedback-fade-enter-active, .feedback-fade-leave-active {
  transition: all 0.4s ease;
}
.feedback-fade-enter-from, .feedback-fade-leave-to {
  opacity: 0;
  transform: scale(1.1);
}

/* Confetti Effect for Excellent */
.confetti-particles {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
}

.particle {
  position: absolute;
  width: 10px;
  height: 10px;
  background: #F59E0B;
  border-radius: 2px;
  animation: explode 1s ease-out forwards;
}

@keyframes explode {
  0% { transform: translate(0, 0) rotate(0); opacity: 1; }
  100% { transform: translate(var(--dx), var(--dy)) rotate(var(--dr)); opacity: 0; }
}

/* Dynamic particle values */
.particle:nth-child(1) { --dx: -80px; --dy: -80px; --dr: 45deg; animation-delay: 0.1s; background: #FCD34D; }
.particle:nth-child(2) { --dx: 80px; --dy: -90px; --dr: -30deg; animation-delay: 0.05s; background: #6366F1; }
.particle:nth-child(3) { --dx: -60px; --dy: 90px; --dr: 120deg; animation-delay: 0.15s; background: #10B981; }
.particle:nth-child(4) { --dx: 90px; --dy: 60px; --dr: 200deg; animation-delay: 0s; background: #F43F5E; }
.particle:nth-child(5) { --dx: -100px; --dy: 0px; --dr: 90deg; animation-delay: 0.2s; background: #8B5CF6; }
.particle:nth-child(6) { --dx: 100px; --dy: 0px; --dr: -45deg; animation-delay: 0.1s; background: #0EA5E9; }
.particle:nth-child(7) { --dx: -40px; --dy: -100px; --dr: 30deg; animation-delay: 0.05s; }
.particle:nth-child(8) { --dx: 40px; --dy: -100px; --dr: -60deg; animation-delay: 0.15s; }
.particle:nth-child(9) { --dx: -40px; --dy: 100px; --dr: 180deg; animation-delay: 0s; }
.particle:nth-child(10) { --dx: 40px; --dy: 100px; --dr: 75deg; animation-delay: 0.2s; }
.particle:nth-child(11) { --dx: 0px; --dy: -110px; --dr: 0deg; animation-delay: 0.1s; }
.particle:nth-child(12) { --dx: 0px; --dy: 110px; --dr: 15deg; animation-delay: 0.05s; }
</style>
