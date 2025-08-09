import * as echarts from 'echarts'

/**
 * Chart utilities for ECharts integration
 * Provides reusable chart creation and configuration functions
 */

/**
 * Default chart colors
 */
export const DEFAULT_COLORS = [
  '#409EFF', // Primary blue
  '#67C23A', // Success green
  '#E6A23C', // Warning orange
  '#F56C6C', // Danger red
  '#909399', // Info gray
  '#9b59b6', // Purple
  '#1abc9c', // Teal
  '#34495e', // Dark gray
]

/**
 * Common chart configurations
 */
export const CHART_CONFIGS = {
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    borderColor: 'transparent',
    textStyle: {
      color: '#fff',
    },
  },
  legend: {
    textStyle: {
      color: '#606266',
    },
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true,
  },
}

/**
 * Create a pie chart
 * @param {HTMLElement} element - DOM element to render chart
 * @param {Array} data - Chart data array
 * @param {Object} options - Chart configuration options
 * @returns {Object} ECharts instance
 */
export const createPieChart = (element, data, options = {}) => {
  if (!element) {
    console.error('Chart element is required')
    return null
  }

  const chart = echarts.init(element)

  const defaultOptions = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: {
        color: '#606266',
      },
    },
    series: [
      {
        name: options.seriesName || 'Data',
        type: 'pie',
        radius: options.radius || '50%',
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
        itemStyle: {
          borderRadius: 4,
        },
      },
    ],
    color: options.colors || DEFAULT_COLORS,
  }

  const finalOptions = mergeOptions(defaultOptions, options.customOptions || {})
  chart.setOption(finalOptions)

  return chart
}

/**
 * Create a line chart
 * @param {HTMLElement} element - DOM element to render chart
 * @param {Object} data - Chart data with xAxis and series
 * @param {Object} options - Chart configuration options
 * @returns {Object} ECharts instance
 */
export const createLineChart = (element, data, options = {}) => {
  if (!element) {
    console.error('Chart element is required')
    return null
  }

  const chart = echarts.init(element)

  const defaultOptions = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'transparent',
      textStyle: {
        color: '#fff',
      },
    },
    legend: {
      data: data.seriesNames || [],
      textStyle: {
        color: '#606266',
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.xAxis || [],
      axisLabel: {
        color: '#606266',
      },
      axisLine: {
        lineStyle: {
          color: '#DCDFE6',
        },
      },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#606266',
      },
      axisLine: {
        lineStyle: {
          color: '#DCDFE6',
        },
      },
      splitLine: {
        lineStyle: {
          color: '#EBEEF5',
        },
      },
    },
    series: data.series.map((serie, index) => ({
      name: serie.name,
      type: 'line',
      smooth: true,
      data: serie.data,
      itemStyle: {
        color: options.colors ? options.colors[index] : DEFAULT_COLORS[index],
      },
      areaStyle: options.showArea
        ? {
            opacity: 0.3,
          }
        : undefined,
    })),
    color: options.colors || DEFAULT_COLORS,
  }

  const finalOptions = mergeOptions(defaultOptions, options.customOptions || {})
  chart.setOption(finalOptions)

  return chart
}

/**
 * Create a bar chart
 * @param {HTMLElement} element - DOM element to render chart
 * @param {Object} data - Chart data with xAxis and series
 * @param {Object} options - Chart configuration options
 * @returns {Object} ECharts instance
 */
export const createBarChart = (element, data, options = {}) => {
  if (!element) {
    console.error('Chart element is required')
    return null
  }

  const chart = echarts.init(element)

  const defaultOptions = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'transparent',
      textStyle: {
        color: '#fff',
      },
    },
    legend: {
      data: data.seriesNames || [],
      textStyle: {
        color: '#606266',
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: data.xAxis || [],
      axisLabel: {
        color: '#606266',
      },
      axisLine: {
        lineStyle: {
          color: '#DCDFE6',
        },
      },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#606266',
      },
      axisLine: {
        lineStyle: {
          color: '#DCDFE6',
        },
      },
      splitLine: {
        lineStyle: {
          color: '#EBEEF5',
        },
      },
    },
    series: data.series.map((serie, index) => ({
      name: serie.name,
      type: 'bar',
      data: serie.data,
      itemStyle: {
        color: options.colors ? options.colors[index] : DEFAULT_COLORS[index],
        borderRadius: [4, 4, 0, 0],
      },
    })),
    color: options.colors || DEFAULT_COLORS,
  }

  const finalOptions = mergeOptions(defaultOptions, options.customOptions || {})
  chart.setOption(finalOptions)

  return chart
}

/**
 * Make chart responsive
 * @param {Object} chart - ECharts instance
 * @param {HTMLElement} element - Chart container element
 * @returns {Function} Cleanup function
 */
export const makeResponsive = (chart, element) => {
  if (!chart || !element) return () => {}

  const resizeObserver = new ResizeObserver(() => {
    chart.resize()
  })

  resizeObserver.observe(element)

  const handleWindowResize = () => {
    chart.resize()
  }

  window.addEventListener('resize', handleWindowResize)

  return () => {
    resizeObserver.disconnect()
    window.removeEventListener('resize', handleWindowResize)
  }
}

/**
 * Dispose chart and cleanup resources
 * @param {Object} chart - ECharts instance
 * @param {Function} cleanupFn - Cleanup function from makeResponsive
 */
export const disposeChart = (chart, cleanupFn) => {
  if (cleanupFn) {
    cleanupFn()
  }
  if (chart) {
    chart.dispose()
  }
}

/**
 * Deep merge chart options
 * @param {Object} target - Target object
 * @param {Object} source - Source object
 * @returns {Object} Merged object
 */
function mergeOptions(target, source) {
  const result = { ...target }

  for (const key in source) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      if (
        typeof source[key] === 'object' &&
        source[key] !== null &&
        !Array.isArray(source[key])
      ) {
        result[key] = mergeOptions(result[key] || {}, source[key])
      } else {
        result[key] = source[key]
      }
    }
  }

  return result
}

/**
 * Common chart themes
 */
export const CHART_THEMES = {
  default: {
    colors: DEFAULT_COLORS,
    backgroundColor: 'transparent',
  },
  dark: {
    colors: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399'],
    backgroundColor: '#2d3748',
    textColor: '#fff',
  },
  light: {
    colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
    backgroundColor: '#fff',
    textColor: '#333',
  },
}

/**
 * Export utilities for advanced usage
 */
export const chartUtils = {
  /**
   * Convert chart to image
   * @param {Object} chart - ECharts instance
   * @param {Object} options - Export options
   * @returns {String} Base64 image data
   */
  exportToImage: (chart, options = {}) => {
    if (!chart) return null

    return chart.getDataURL({
      type: options.type || 'png',
      pixelRatio: options.pixelRatio || 2,
      backgroundColor: options.backgroundColor || '#fff',
    })
  },

  /**
   * Download chart as image
   * @param {Object} chart - ECharts instance
   * @param {String} filename - Download filename
   * @param {Object} options - Export options
   */
  downloadChart: (chart, filename = 'chart', options = {}) => {
    const dataURL = chartUtils.exportToImage(chart, options)
    if (!dataURL) return

    const link = document.createElement('a')
    link.download = `${filename}.${options.type || 'png'}`
    link.href = dataURL
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  },
}
