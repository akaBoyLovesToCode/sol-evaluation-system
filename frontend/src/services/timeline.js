import { rows, timelineRange } from '@/mocks/timeline'

export function fetchTimelineRows() {
  return Promise.resolve({
    rows,
    range: timelineRange,
  })
}
