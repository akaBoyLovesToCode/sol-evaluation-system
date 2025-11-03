<template>
  <div
    class="timeline-matrix border border-slate-200 bg-white shadow-sm rounded-xl overflow-hidden"
  >
    <div class="flex">
      <div class="flex-shrink-0 bg-white border-r border-slate-200">
        <div class="sticky top-0 z-20 bg-white border-b border-slate-200">
          <div
            class="grid grid-cols-5 text-[11px] uppercase tracking-wide text-slate-500 font-semibold"
          >
            <div class="px-4 py-3">Site</div>
            <div class="px-4 py-3">I/F</div>
            <div class="px-4 py-3">Product</div>
            <div class="px-4 py-3">Ctrl</div>
            <div class="px-4 py-3">Nand</div>
          </div>
        </div>
        <div>
          <div
            v-for="row in positionedRows"
            :key="row.rowKey"
            class="grid grid-cols-5 border-b border-slate-100 text-sm text-slate-700"
            :style="{ height: `${rowHeight}px` }"
          >
            <div class="px-4 flex items-center font-semibold text-slate-700">
              {{ row.site }}
            </div>
            <div class="px-4 flex items-center text-slate-600">
              {{ row.iface }}
            </div>
            <div class="px-4 flex items-center text-slate-700">
              {{ row.product }}
            </div>
            <div class="px-4 flex items-center text-slate-600">
              {{ row.ctrl }}
            </div>
            <div class="px-4 flex items-center text-slate-600">
              {{ row.nand }}
            </div>
          </div>
        </div>
      </div>
      <div class="flex-1 overflow-x-auto">
        <div
          class="relative"
          :style="{
            minWidth: `${Math.max(timelineWidth, 0)}px`,
          }"
        >
          <div class="sticky top-0 z-20 bg-white border-b border-slate-200">
            <div class="flex">
              <div
                v-for="group in monthGroups"
                :key="group.year"
                class="border-r border-slate-200 last:border-r-0"
                :style="{ width: `${group.months.length * monthWidth}px` }"
              >
                <div class="px-4 pt-3 pb-2 text-sm font-semibold text-slate-600">
                  {{ group.year }}
                </div>
                <div class="flex border-t border-slate-100">
                  <div
                    v-for="month in group.months"
                    :key="month.key"
                    class="text-center text-xs font-medium text-slate-500 py-2 border-r border-slate-100 last:border-r-0"
                    :style="{ width: `${monthWidth}px` }"
                  >
                    {{ month.label }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="timeline-grid" :style="gridStyles">
            <div
              v-for="row in positionedRows"
              :key="`${row.rowKey}-timeline`"
              class="relative border-b border-slate-200"
              :style="{ height: `${rowHeight}px` }"
            >
              <div class="timeline-events h-full w-full">
                <EventDot
                  v-for="event in row.events"
                  :key="event.id"
                  :event="event"
                  :left="event.left"
                  :classes="event.classes"
                  :month-width="monthWidth"
                />
              </div>
            </div>
            <div
              v-if="todayLeft !== null"
              class="timeline-today-line"
              :style="{ left: `${todayLeft}px` }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import dayjs from 'dayjs'
import EventDot from './EventDot.vue'
import {
  dateToX,
  generateMonths,
  typeToClasses,
  getOverlapNudge,
} from './helpers'

const props = defineProps({
  rows: {
    type: Array,
    default: () => [],
  },
  timelineRange: {
    type: Object,
    required: true,
  },
  monthWidth: {
    type: Number,
    required: true,
  },
})

const rowHeight = 88

const months = computed(() => {
  if (!props.timelineRange) {
    return []
  }
  return generateMonths(props.timelineRange)
})

const timelineWidth = computed(() => months.value.length * props.monthWidth)

const gridStyles = computed(() => ({
  '--month-width': `${props.monthWidth}px`,
  '--timeline-width': `${timelineWidth.value}px`,
  width: `${Math.max(timelineWidth.value, 0)}px`,
}))

const monthGroups = computed(() => {
  const groups = []
  let current = null

  months.value.forEach((month) => {
    if (!current || current.year !== month.year) {
      current = {
        year: month.year,
        months: [],
      }
      groups.push(current)
    }

    current.months.push(month)
  })

  return groups
})

const positionedRows = computed(() => {
  if (!props.timelineRange) {
    return []
  }

  return props.rows.map((row, index) => {
    const dayUsage = {}
    const overlapNudge = getOverlapNudge(props.monthWidth)
    const events = (row.events || []).map((event) => {
      const left = dateToX(event.date, props.timelineRange.start, props.monthWidth)
      const offsetIndex = dayUsage[event.date] || 0
      dayUsage[event.date] = offsetIndex + 1

      return {
        ...event,
        left: left + offsetIndex * overlapNudge,
        offsetIndex,
        classes: typeToClasses(event.type),
      }
    })

    return {
      ...row,
      events,
      rowKey: `${row.product}-${row.site}-${index}`,
    }
  })
})

const todayLeft = computed(() => {
  if (!props.timelineRange || months.value.length === 0) {
    return null
  }

  const today = dayjs()
  const start = dayjs(
    `${props.timelineRange.start.year}-${String(props.timelineRange.start.month).padStart(2, '0')}-01`,
  )
  const end = dayjs(
    `${props.timelineRange.end.year}-${String(props.timelineRange.end.month).padStart(2, '0')}-01`,
  ).endOf('month')

  if (today.isBefore(start) || today.isAfter(end)) {
    return null
  }

  return dateToX(today.format('YYYY-MM-DD'), props.timelineRange.start, props.monthWidth)
})

defineExpose({
  rowHeight,
  timelineWidth,
})
</script>
