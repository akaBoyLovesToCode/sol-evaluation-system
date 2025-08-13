<template>
  <div
    ref="containerRef"
    :class="['animated-container', animationType, { 'is-visible': isVisible }]"
    :style="{ animationDelay: delay }"
  >
    <slot />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'fadeInUp',
    validator: (value) => ['fadeInUp', 'fadeInLeft', 'fadeInRight'].includes(value),
  },
  delay: {
    type: String,
    default: '0s',
  },
  duration: {
    type: String,
    default: '0.6s',
  },
})

const containerRef = ref()
const isVisible = ref(false)

const animationType = `fade-in-${props.type.replace('fadeIn', '').toLowerCase()}`

onMounted(async () => {
  await nextTick()
  // 使用 requestAnimationFrame 确保在下一帧开始动画
  requestAnimationFrame(() => {
    isVisible.value = true
  })
})
</script>

<style scoped>
.animated-container {
  opacity: 0;
  transition: none;
}

.animated-container.fade-in-up {
  transform: translateY(30px);
}

.animated-container.fade-in-left {
  transform: translateX(-30px);
}

.animated-container.fade-in-right {
  transform: translateX(30px);
}

.animated-container.is-visible {
  opacity: 1;
  transform: translate(0, 0);
  transition: all v-bind(duration) cubic-bezier(0.25, 0.46, 0.45, 0.94);
  transition-delay: v-bind(delay);
}
</style>
