import dayjs from 'dayjs'

const TYPE_STYLES = {
  plan: {
    fill: 'bg-slate-500',
    outline: 'border-slate-300',
    label: 'text-slate-600',
    tag: 'bg-slate-100 text-slate-700',
    text: 'text-white',
  },
  eval: {
    fill: 'bg-emerald-500',
    outline: 'border-emerald-300',
    label: 'text-emerald-600',
    tag: 'bg-emerald-100 text-emerald-800',
    text: 'text-white',
  },
  issue: {
    fill: 'bg-red-500',
    outline: 'border-red-300',
    label: 'text-red-600',
    tag: 'bg-red-100 text-red-800',
    text: 'text-white',
  },
  ship: {
    fill: 'bg-blue-500',
    outline: 'border-blue-300',
    label: 'text-blue-600',
    tag: 'bg-blue-100 text-blue-700',
    text: 'text-white',
  },
  risk: {
    fill: 'bg-amber-400',
    outline: 'border-amber-300',
    label: 'text-amber-600',
    tag: 'bg-amber-100 text-amber-700',
    text: 'text-neutral-900',
  },
}

export function daysInMonth(year, month) {
  return dayjs(`${year}-${String(month).padStart(2, '0')}-01`).daysInMonth()
}

export function dateToX(dateISO, startYM, monthWidth) {
  const target = dayjs(dateISO)
  const start = dayjs(`${startYM.year}-${String(startYM.month).padStart(2, '0')}-01`)
  const monthsDiff = target.year() * 12 + target.month() - (start.year() * 12 + start.month())
  const offset = ((target.date() - 1) / daysInMonth(target.year(), target.month() + 1)) * monthWidth

  return monthsDiff * monthWidth + offset
}

export function generateMonths(range) {
  const months = []
  const start = dayjs(`${range.start.year}-${String(range.start.month).padStart(2, '0')}-01`)
  const end = dayjs(`${range.end.year}-${String(range.end.month).padStart(2, '0')}-01`)

  let cursor = start

  while (cursor.isBefore(end) || cursor.isSame(end)) {
    months.push({
      year: cursor.year(),
      month: cursor.month() + 1,
      label: cursor.format('MMM'),
      key: cursor.format('YYYY-MM'),
    })

    cursor = cursor.add(1, 'month')
  }

  return months
}

export function typeToClasses(type) {
  return TYPE_STYLES[type] || TYPE_STYLES.plan
}

export const supportedTypes = Object.keys(TYPE_STYLES)

export function getEventDiameter(monthWidth) {
  const base = 36 * (monthWidth / 160)
  const adjusted = base + 4
  return Math.max(32, Math.min(56, adjusted))
}

export function getOverlapNudge(monthWidth) {
  return getEventDiameter(monthWidth) / 2 + 6
}
