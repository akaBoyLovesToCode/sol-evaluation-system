const RELIABILITY_CODES = new Set(['M031', 'M111', 'M130', 'AQL'])

const pickDefined = (...values) => {
  for (const value of values) {
    if (value !== undefined && value !== null && value !== '') {
      return value
    }
  }
  return undefined
}

const toNumber = (value, fallback = null) => {
  if (value === undefined || value === null || value === '') {
    return fallback
  }
  const normalized = typeof value === 'string' ? value.replace(/,/g, '') : value
  const num = Number(normalized)
  return Number.isFinite(num) ? num : fallback
}

export const isReliabilityStep = (code) => {
  if (!code) return false
  return RELIABILITY_CODES.has(String(code).toUpperCase())
}

export const buildReliabilitySummary = (step, translate) => {
  if (!isReliabilityStep(step?.step_code)) {
    return ''
  }

  const reliabilityMetrics =
    step?.metrics?.reliability ?? step?.reliability ?? step?.metrics ?? {}

  const fail =
    toNumber(pickDefined(step?.fail_units, reliabilityMetrics.fail), 0) ?? 0

  const total =
    toNumber(
      pickDefined(
        step?.test_units,
        step?.total_units,
        reliabilityMetrics.total,
        step?.metrics?.test_units,
      ),
      0,
    ) ?? 0

  if (!Number.isFinite(total) || total <= 0) {
    return ''
  }

  const ppmRaw = pickDefined(reliabilityMetrics.ppm)
  const ppmCandidate = toNumber(ppmRaw)
  const ppm = Number.isFinite(ppmCandidate)
    ? Math.round(ppmCandidate)
    : Math.round((fail / total) * 1_000_000)

  if (!Number.isFinite(ppm)) {
    return ''
  }

  const r = pickDefined(reliabilityMetrics.r, step?.r)

  const ciLow = toNumber(
    pickDefined(
      reliabilityMetrics.ciLow,
      reliabilityMetrics.ci_low,
      reliabilityMetrics.ciLowPpm,
      reliabilityMetrics.ci_low_ppm,
      step?.ciLow,
      step?.ci_low,
    ),
  )
  const ciHigh = toNumber(
    pickDefined(
      reliabilityMetrics.ciHigh,
      reliabilityMetrics.ci_high,
      reliabilityMetrics.ciHighPpm,
      reliabilityMetrics.ci_high_ppm,
      step?.ciHigh,
      step?.ci_high,
    ),
  )
  let conf = pickDefined(
    reliabilityMetrics.conf,
    reliabilityMetrics.confidence,
    reliabilityMetrics.confidence_level,
    step?.conf,
  )
  conf = toNumber(conf !== undefined ? String(conf).replace('%', '') : undefined, 90) ?? 90

  const parts = []
  parts.push(translate('nested.reliability.ppm', { ppm, fail, total }))

  if (r !== undefined && r !== null && `${r}`.trim() !== '') {
    parts.push(translate('nested.reliability.r', { r }))
  }

  if (Number.isFinite(ciLow) && Number.isFinite(ciHigh)) {
    parts.push(
      translate('nested.reliability.ci', {
        low: Math.round(ciLow),
        high: Math.round(ciHigh),
      }),
    )
  }

  const confSuffix = translate('nested.reliability.conf', { conf })
  parts.push(` @ ${confSuffix}`)

  return parts.join('')
}

export const stepLabelForPath = (step, newStepLabel = '') => {
  const code = step?.step_code
  const label = code || newStepLabel
  if (!label) {
    return ''
  }

  const evalCode =
    step?.eval_code ?? step?.eval ?? step?.metadata?.eval ?? step?.metrics?.eval_code

  if (evalCode) {
    return `${label}(${evalCode})`
  }

  return label
}

export default {
  isReliabilityStep,
  buildReliabilitySummary,
  stepLabelForPath,
}
