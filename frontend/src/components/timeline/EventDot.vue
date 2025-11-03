<template>
  <el-tooltip
    placement="top"
    effect="light"
    :content="tooltipContent"
    popper-class="max-w-xs"
    :show-after="120"
  >
    <template v-if="isInsidePlacement">
      <div
        class="timeline-event absolute top-1/2 -translate-y-1/2 -translate-x-1/2 flex flex-col items-center justify-center rounded-full border-2 transition-transform duration-150 ease-out ring-2 ring-white shadow-sm hover:scale-105"
        :class="[classes.fill, classes.outline, textClass]"
        :style="[positionStyles, sizeStyles]"
      >
        <div class="flex flex-col items-center justify-center leading-tight gap-0.5 uppercase">
          <span
            class="font-semibold tracking-wide"
            :style="[dateStyle, textShadowStyle]"
          >
            {{ dateLabel }}
          </span>
          <span
            class="font-medium"
            :style="[customerStyle, textShadowStyle]"
          >
            {{ customerLabel }}
          </span>
        </div>
      </div>
    </template>
    <template v-else>
      <div
        class="timeline-event absolute top-1/2 -translate-y-1/2 -translate-x-1/2 flex flex-col items-center text-xs font-medium text-gray-600 gap-1"
        :style="[positionStyles, outsideWrapperSize]"
      >
        <span class="timeline-event-label text-xs text-slate-500 uppercase tracking-wide">
          {{ dateLabel }}
        </span>
        <div
          class="rounded-full border-2 ring-2 ring-white shadow-sm transition-transform duration-150 ease-out hover:scale-105 flex items-center justify-center"
          :class="[classes.fill, classes.outline, textClass]"
          :style="sizeStyles"
        >
          <span
            class="font-semibold uppercase"
            :style="[dateStyle, textShadowStyle]"
          >
            {{ dateLabel }}
          </span>
        </div>
        <span class="timeline-event-label text-xs text-slate-700 uppercase">
          {{ customerLabel }}
        </span>
      </div>
    </template>
  </el-tooltip>
</template>

<script setup>
import { computed } from 'vue'
import dayjs from 'dayjs'
import { getEventDiameter } from './helpers'

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
  left: {
    type: Number,
    required: true,
  },
  classes: {
    type: Object,
    required: true,
  },
  monthWidth: {
    type: Number,
    required: true,
  },
  labelPlacement: {
    type: String,
    default: 'inside',
    validator: (value) => ['inside', 'outside'].includes(value),
  },
})

const diameter = computed(() => getEventDiameter(props.monthWidth))
const positionStyles = computed(() => ({
  left: `${props.left}px`,
}))

const sizeStyles = computed(() => ({
  width: `${diameter.value}px`,
  height: `${diameter.value}px`,
}))

const outsideWrapperSize = computed(() => ({
  width: `${diameter.value}px`,
}))

const dateLabel = computed(() => dayjs(props.event.date).format('MM/DD'))
const customerLabel = computed(() => props.event.customer.slice(0, 6).toUpperCase())
const textClass = computed(() => props.classes?.text || 'text-white')

const isInsidePlacement = computed(() => props.labelPlacement !== 'outside')
const isCompact = computed(() => props.monthWidth < 140)

const dateStyle = computed(() => ({
  fontSize: `${isCompact.value ? 10 : 11}px`,
}))

const customerStyle = computed(() => ({
  fontSize: `${isCompact.value ? 9 : 10}px`,
}))

const textShadowStyle = computed(() =>
  textClass.value.includes('text-white')
    ? { textShadow: '0 1px 2px rgba(15, 23, 42, 0.45)' }
    : {}
)

const tooltipContent = computed(() => {
  const details = [
    `${dayjs(props.event.date).format('MMM D, YYYY')}`,
    `Customer: ${props.event.customer}`,
    `Type: ${props.event.type.toUpperCase()}`,
  ]

  if (props.event.note) {
    details.push(`Note: ${props.event.note}`)
  }

  return details.join(' • ')
})
</script>
