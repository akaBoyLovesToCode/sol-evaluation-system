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

const LOG_GAMMA_COEFF = [
  76.1800917295, -86.5053203294, 24.0140982408, -1.23173957245, 1.208650973866179e-3,
  -5.395239384953e-6,
]

const logGamma = (xx) => {
  // Lanczos approximation for log gamma to support incomplete beta
  let x = xx
  let y = xx
  let tmp = x + 5.5
  tmp -= (x + 0.5) * Math.log(tmp)
  let ser = 1.000000000190015
  for (let j = 0; j < LOG_GAMMA_COEFF.length; j += 1) {
    y += 1
    ser += LOG_GAMMA_COEFF[j] / y
  }
  return -tmp + Math.log((Math.sqrt(2 * Math.PI) * ser) / x)
}

const betacf = (a, b, x) => {
  // Continued fraction for incomplete beta (from Numerical Recipes)
  const MAX_ITER = 200
  const EPS = 3e-7
  const FPMIN = 1e-30
  let qab = a + b
  let qap = a + 1
  let qam = a - 1
  let c = 1
  let d = 1 - (qab * x) / qap
  if (Math.abs(d) < FPMIN) d = FPMIN
  d = 1 / d
  let h = d
  for (let m = 1; m <= MAX_ITER; m += 1) {
    const m2 = 2 * m
    let aa = (m * (b - m) * x) / ((qam + m2) * (a + m2))
    d = 1 + aa * d
    if (Math.abs(d) < FPMIN) d = FPMIN
    c = 1 + aa / c
    if (Math.abs(c) < FPMIN) c = FPMIN
    d = 1 / d
    h *= d * c
    aa = (-(a + m) * (qab + m) * x) / ((a + m2) * (qap + m2))
    d = 1 + aa * d
    if (Math.abs(d) < FPMIN) d = FPMIN
    c = 1 + aa / c
    if (Math.abs(c) < FPMIN) c = FPMIN
    d = 1 / d
    const del = d * c
    h *= del
    if (Math.abs(del - 1.0) < EPS) break
  }
  return h
}

const regularizedIncompleteBeta = (a, b, x) => {
  if (x <= 0) return 0
  if (x >= 1) return 1
  const bt = Math.exp(
    logGamma(a + b) - logGamma(a) - logGamma(b) + a * Math.log(x) + b * Math.log(1 - x),
  )
  const symm = x < (a + 1) / (a + b + 2)
  if (symm) {
    return (bt * betacf(a, b, x)) / a
  }
  return 1 - (bt * betacf(b, a, 1 - x)) / b
}

const fCdf = (x, d1, d2) => {
  const a = d1 / 2
  const b = d2 / 2
  const xx = (d1 * x) / (d1 * x + d2)
  return regularizedIncompleteBeta(a, b, xx)
}

const fQuantile = (p, d1, d2) => {
  // Simple bisection using CDF
  if (p <= 0) return 0
  if (p >= 1) return Number.POSITIVE_INFINITY
  let lo = 0
  let hi = 1
  // Expand upper bound until CDF >= p
  while (fCdf(hi, d1, d2) < p) {
    hi *= 2
    if (hi > 1e6) break
  }
  for (let i = 0; i < 100; i += 1) {
    const mid = (lo + hi) / 2
    const cdf = fCdf(mid, d1, d2)
    if (Math.abs(cdf - p) < 1e-7) {
      return mid
    }
    if (cdf < p) lo = mid
    else hi = mid
  }
  return (lo + hi) / 2
}

const clopperPearsonPpm = (fail, total, confLevel = 0.9) => {
  const alpha = 1 - confLevel
  const tail = alpha / 2
  let lower = 0
  let upper = 1

  if (fail === 0) {
    lower = 0
  } else {
    const fLower = fQuantile(tail, 2 * (total - fail + 1), 2 * fail)
    lower = fail / (fail + (total - fail + 1) * fLower)
  }

  if (fail === total) {
    upper = 1
  } else {
    const fUpper = fQuantile(1 - tail, 2 * (fail + 1), 2 * (total - fail))
    upper = ((fail + 1) * fUpper) / (total - fail + (fail + 1) * fUpper)
  }

  return {
    lower_ppm: Math.round(lower * 1_000_000),
    upper_ppm: Math.round(upper * 1_000_000),
  }
}

export const buildReliabilitySummary = (step, translate) => {
  if (!isReliabilityStep(step?.step_code)) {
    return ''
  }

  const reliabilityMetrics = step?.metrics?.reliability ?? step?.reliability ?? step?.metrics ?? {}

  const fail = toNumber(pickDefined(step?.fail_units, reliabilityMetrics.fail), 0) ?? 0

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

  const observedPpm = Math.round((fail / total) * 1_000_000)
  const resolutionPpm = Math.round((1 / total) * 1_000_000)

  const { lower_ppm: lowerPpm, upper_ppm: upperPpm } = clopperPearsonPpm(fail, total, 0.9)

  const failLabel = translate('nested.reliability.failLabel')
  const ratio = `${fail}${fail > 0 ? ` ${failLabel}` : ''}/${total}`
  const confidenceLabel = translate('nested.reliability.confidenceLabel')

  return `${observedPpm}ppm(${ratio}, r${resolutionPpm},[${lowerPpm}, ${upperPpm}] @${90}% ${confidenceLabel})`
}

export const buildTotalsSummary = (step, translate) => {
  const total =
    toNumber(pickDefined(step?.total_units, step?.test_units, step?.metrics?.test_units), 0) ?? 0
  const pass = toNumber(step?.pass_units, 0) ?? 0
  const fail = toNumber(step?.fail_units, 0) ?? 0

  return translate('nested.summary.totals', {
    total,
    pass,
    fail,
  })
}

export const stepLabelForPath = (step, newStepLabel = '') => {
  const code = step?.step_code
  const label = code || newStepLabel
  if (!label) {
    return ''
  }

  const evalCode = step?.eval_code ?? step?.eval ?? step?.metadata?.eval ?? step?.metrics?.eval_code

  if (evalCode) {
    return `${label}(${evalCode})`
  }

  return label
}

export default {
  isReliabilityStep,
  buildReliabilitySummary,
  buildTotalsSummary,
  stepLabelForPath,
}
