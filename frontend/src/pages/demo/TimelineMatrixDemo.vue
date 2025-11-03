<template>
  <div class="timeline-demo px-6 py-8 space-y-6">
    <div class="flex flex-col gap-3">
      <div class="flex items-center gap-3">
        <h1 class="text-2xl font-semibold text-slate-900">Product Evaluation Timeline</h1>
        <span
          class="uppercase text-xs font-semibold tracking-wide px-2 py-1 rounded-md bg-slate-900 text-white"
        >
          Demo
        </span>
      </div>
      <div
        class="text-sm text-slate-600 bg-slate-100 border border-slate-200 rounded-lg px-4 py-3 w-full max-w-xl"
      >
        Feedback only. All data is mock. Please share comments before we turn this into a real
        feature.
      </div>
    </div>

    <div
      class="bg-white border border-slate-200 rounded-xl shadow-sm px-4 py-5 flex flex-wrap gap-6 items-center"
    >
      <div class="flex items-center gap-3">
        <span class="text-sm font-medium text-slate-600">Zoom</span>
        <el-slider
          v-model="monthWidth"
          :min="120"
          :max="240"
          :step="20"
          :show-tooltip="false"
          class="w-48"
        />
        <span class="text-xs text-slate-500"> {{ monthWidth }} px / month </span>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-sm font-medium text-slate-600">Site</span>
        <el-select v-model="selectedSite" placeholder="All" class="w-40" size="small">
          <el-option label="All Sites" value="" />
          <el-option v-for="site in siteOptions" :key="site" :label="site" :value="site" />
        </el-select>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-sm font-medium text-slate-600">Product</span>
        <el-select v-model="selectedProduct" placeholder="All" class="w-44" size="small">
          <el-option label="All Products" value="" />
          <el-option
            v-for="product in productOptions"
            :key="product"
            :label="product"
            :value="product"
          />
        </el-select>
      </div>
      <div class="flex flex-col gap-2">
        <span class="text-sm font-medium text-slate-600">Types</span>
        <el-checkbox-group v-model="selectedTypes" class="flex flex-wrap gap-3">
          <el-checkbox
            v-for="option in typeOptions"
            :key="option.value"
            :label="option.value"
            size="small"
            border
          >
            <span :class="['font-medium text-xs', option.labelClass]">
              {{ option.label }}
            </span>
          </el-checkbox>
        </el-checkbox-group>
      </div>
    </div>

    <div class="flex flex-wrap gap-3 text-xs">
      <div
        v-for="legend in legendItems"
        :key="legend.type"
        class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-slate-200 bg-white shadow-sm"
      >
        <span
          class="inline-flex h-3 w-3 rounded-full border-2"
          :class="[legend.classes.fill, legend.classes.outline]"
        />
        <span :class="['font-medium', legend.classes.label]">{{ legend.label }}</span>
      </div>
    </div>

    <div v-if="error" class="border border-red-200 bg-red-50 text-red-700 px-4 py-3 rounded-lg">
      {{ error }}
    </div>
    <el-skeleton v-else-if="loading" :rows="5" animated />
    <TimelineMatrix
      v-else
      :rows="filteredRows"
      :timeline-range="timelineRange"
      :month-width="monthWidth"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import TimelineMatrix from '@/components/timeline/TimelineMatrix.vue'
import { fetchTimelineRows } from '@/services/timeline'
import { supportedTypes, typeToClasses } from '@/components/timeline/helpers'
import '@/styles/timeline.css'

const loading = ref(true)
const error = ref('')
const rawRows = ref([])
const timelineRange = ref(null)

const monthWidth = ref(160)

const selectedSite = ref('')
const selectedProduct = ref('')
const selectedTypes = ref([...supportedTypes])

const typeOptions = computed(() =>
  supportedTypes.map((type) => ({
    value: type,
    label: type.charAt(0).toUpperCase() + type.slice(1),
    labelClass: typeToClasses(type).label,
  })),
)

const siteOptions = computed(() => {
  const sites = new Set(rawRows.value.map((row) => row.site))
  return Array.from(sites)
})

const productOptions = computed(() => {
  const rows = selectedSite.value
    ? rawRows.value.filter((row) => row.site === selectedSite.value)
    : rawRows.value

  return Array.from(new Set(rows.map((row) => row.product)))
})

watch(productOptions, (options) => {
  if (selectedProduct.value && !options.includes(selectedProduct.value)) {
    selectedProduct.value = ''
  }
})

watch(
  () => selectedTypes.value.length,
  (length) => {
    if (length === 0) {
      selectedTypes.value = [...supportedTypes]
    }
  },
)

const filteredRows = computed(() => {
  const site = selectedSite.value
  const product = selectedProduct.value
  const types = selectedTypes.value

  return rawRows.value
    .filter((row) => (site ? row.site === site : true))
    .filter((row) => (product ? row.product === product : true))
    .map((row) => ({
      ...row,
      events: row.events.filter((event) => types.includes(event.type)),
    }))
})

const legendItems = computed(() =>
  supportedTypes.map((type) => ({
    type,
    label: type.charAt(0).toUpperCase() + type.slice(1),
    classes: typeToClasses(type),
  })),
)

onMounted(async () => {
  try {
    const { rows, range } = await fetchTimelineRows()
    rawRows.value = rows
    timelineRange.value = range
  } catch (err) {
    error.value = 'Unable to load timeline demo data.'
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script>
