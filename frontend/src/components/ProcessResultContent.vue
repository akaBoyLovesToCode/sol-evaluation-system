<template>
  <div ref="content"></div>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import { sanitizeRichText } from '../utils/richText'

const props = defineProps({
  html: { type: String, default: '' },
})

const content = ref(null)

const renderContent = () => {
  if (content.value) {
    content.value.innerHTML = sanitizeRichText(props.html)
  }
}

watch(
  () => props.html,
  () => nextTick(renderContent),
)

onMounted(renderContent)
</script>
