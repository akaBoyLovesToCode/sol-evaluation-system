import { describe, it, expect } from '@jest/globals'
import { buildReliabilitySummary } from '../../src/utils/reliability'

const fakeTranslator = (messages, locale = 'en') => {
  const fn = (key, params = {}) => {
    const template = key.split('.').reduce((obj, part) => obj?.[part], messages)
    if (typeof template !== 'string') {
      throw new Error(`Missing translation for ${key}`)
    }
    return template.replace(/\{\s*(\w+)\s*\}/g, (_, k) => {
      return params[k] !== undefined ? String(params[k]) : `{${k}}`
    })
  }
  fn.locale = locale
  return fn
}

const enMessages = {
  nested: {
    reliability: {
      ppm: '{ppm}ppm ({fail} Fail / {total})',
      r: ', r{r}',
      ci: ', [{low}, {high}]',
      conf: '{conf}% confidence',
    },
  },
}

const zhMessages = {
  nested: {
    reliability: {
      ppm: '{ppm}ppm（{fail} 不良/{total}）',
      r: '，r{r}',
      ci: '，[{low}，{high}]',
      conf: '{conf}% 置信水平',
    },
  },
}

const koMessages = {
  nested: {
    reliability: {
      ppm: '{ppm}ppm({fail} 불량/{total})',
      r: ', r{r}',
      ci: ', [{low}, {high}]',
      conf: '{conf}% 신뢰수준',
    },
  },
}

describe('buildReliabilitySummary', () => {
  it('returns empty string for non reliability step', () => {
    const t = fakeTranslator(enMessages)
    const result = buildReliabilitySummary({ step_code: 'M010' }, t)
    expect(result).toBe('')
  })

  it('returns empty string when total <= 0', () => {
    const t = fakeTranslator(enMessages)
    const result = buildReliabilitySummary(
      { step_code: 'M031', fail_units: 0, total_units: 0 },
      t,
    )
    expect(result).toBe('')
  })

  it('formats english string with CI and confidence', () => {
    const t = fakeTranslator(enMessages)
    const step = {
      step_code: 'M031',
      fail_units: 2,
      total_units: 200,
      metrics: { r: 5000, ci_low_ppm: 0, ci_high_ppm: 968, confidence: 90 },
    }
    const result = buildReliabilitySummary(step, t)
    expect(result).toBe('10000ppm (2 Fail / 200), r5000, [0, 968] @ 90% confidence')
  })

  it('formats chinese string with CI and confidence', () => {
    const t = fakeTranslator(zhMessages)
    const step = {
      step_code: 'M031',
      fail_units: 0,
      total_units: 58,
      metrics: { r: 5000, ci_low_ppm: 0, ci_high_ppm: 968, confidence: '90%' },
    }
    const result = buildReliabilitySummary(step, t)
    expect(result).toBe('0ppm（0 不良/58），r5000，[0，968] @ 90% 置信水平')
  })

  it('formats korean string without CI but with default confidence', () => {
    const t = fakeTranslator(koMessages)
    const step = {
      step_code: 'AQL',
      fail_units: 1,
      total_units: 100,
      metrics: { r: 1234 },
    }
    const result = buildReliabilitySummary(step, t)
    expect(result).toBe('10000ppm(1 불량/100), r1234 @ 90% 신뢰수준')
  })
})
