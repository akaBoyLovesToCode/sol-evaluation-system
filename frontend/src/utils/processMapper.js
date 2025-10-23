const createClientId = (prefix, index) => `${prefix}-${index + 1}`

const safeInt = (value, fallback = 0) => {
  if (value === undefined || value === null || value === '') return fallback
  const parsed = Number(value)
  if (Number.isNaN(parsed) || !Number.isFinite(parsed)) {
    return fallback
  }
  return Math.trunc(parsed)
}

const clone = (payload) => JSON.parse(JSON.stringify(payload ?? null))

const STEP_CODE_CANONICAL = new Map([
  ['M010', 'M010'],
  ['M031', 'M031'],
  ['M033', 'M033'],
  ['M100', 'M100'],
  ['M111', 'M111'],
  ['M130', 'M130'],
  ['AQL', 'AQL'],
  ['BASIC', 'Basic'],
])

const RESULT_OPTIONAL_CODES = new Set(['M010', 'M033', 'M100'])

export const createEmptyBuilderPayload = () => ({
  processes: [],
  legacy_lot_number: null,
  legacy_quantity: null,
})

const normalizeFailures = (failures = []) => {
  if (!Array.isArray(failures)) return []
  return failures.map((failure, index) => ({
    sequence: safeInt(failure?.sequence, index + 1),
    serial_number: (failure?.serial_number || '').trim() || undefined,
    fail_code_id: failure?.fail_code_id ?? undefined,
    fail_code_text: (failure?.fail_code_text || '').trim().toUpperCase() || '',
    fail_code_name_snapshot: (failure?.fail_code_name_snapshot || '').trim() || undefined,
    analysis_result: (failure?.analysis_result || '').trim() || undefined,
  }))
}

const canonicalStepCode = (value) => {
  const candidate = (value || '').toString().trim().toUpperCase()
  return STEP_CODE_CANONICAL.get(candidate) || candidate
}

const isResultsApplicableDefault = (code) => !RESULT_OPTIONAL_CODES.has((code || '').toUpperCase())

const normalizeProcessLots = (lots = [], processKey = 'proc') => {
  if (!Array.isArray(lots)) lots = []
  const normalized = lots.map((lot, index) => {
    const lotNumber = (lot?.lot_number || '').trim()
    const quantity = safeInt(lot?.quantity, 0)
    const baseId =
      lot?.client_id || lot?.temp_id || lot?.id || createClientId(`${processKey}-lot`, index)
    const clientId = String(baseId)
    return {
      id: lot?.id ?? null,
      temp_id: lot?.temp_id || clientId,
      client_id: clientId,
      lot_number: lotNumber,
      quantity,
    }
  })

  if (!normalized.length) {
    normalized.push({
      id: null,
      temp_id: createClientId(`${processKey}-lot`, 0),
      client_id: createClientId(`${processKey}-lot`, 0),
      lot_number: '',
      quantity: 0,
    })
  }

  const lotAliasMap = new Map()
  normalized.forEach((lot) => {
    lotAliasMap.set(String(lot.client_id), lot.client_id)
    lotAliasMap.set(String(lot.temp_id), lot.client_id)
    if (lot.id !== null && lot.id !== undefined) {
      lotAliasMap.set(String(lot.id), lot.client_id)
    }
  })

  return { lots: normalized, lotAliasMap }
}

const normalizeProcessSteps = (steps = [], lotAliasMap, quantityMap) => {
  if (!Array.isArray(steps)) steps = []
  return steps.map((step, index) => {
    const rawRefs = Array.isArray(step?.lot_refs) ? step.lot_refs : []
    const mappedRefs = rawRefs.map((ref) => lotAliasMap.get(String(ref)) || null).filter(Boolean)
    const lotRefs = mappedRefs.length ? [...new Set(mappedRefs)] : Array.from(lotAliasMap.values())

    const stepCode = canonicalStepCode(step?.step_code)
    const defaultApplicable = isResultsApplicableDefault(stepCode)
    const resultsApplicable =
      step?.results_applicable === undefined || step?.results_applicable === null
        ? defaultApplicable
        : Boolean(step.results_applicable)

    const normalizedFailures = resultsApplicable ? normalizeFailures(step?.failures) : []
    const rawTotalUnits = step?.total_units
    const rawFailUnits = step?.fail_units
    let totalUnits = null
    let failUnits = null
    let passUnits = null

    if (resultsApplicable) {
      if (rawTotalUnits !== undefined && rawTotalUnits !== null) {
        totalUnits = safeInt(rawTotalUnits, 0)
      }
      if (rawFailUnits !== undefined && rawFailUnits !== null) {
        failUnits = safeInt(rawFailUnits, normalizedFailures.length)
      } else {
        failUnits = normalizedFailures.length
      }
      if (totalUnits !== null && failUnits !== null) {
        passUnits = Math.max(totalUnits - failUnits, 0)
      } else if (step?.pass_units !== undefined && step?.pass_units !== null) {
        passUnits = safeInt(step.pass_units, 0)
      }
    }

    const autoSum = resultsApplicable
      ? lotRefs.reduce((sum, ref) => sum + (quantityMap.get(ref) || 0), 0)
      : 0

    return {
      order_index: safeInt(step?.order_index, index + 1),
      step_code: stepCode,
      step_label: (step?.step_label || '').trim(),
      eval_code: (step?.eval_code || '').trim(),
      lot_refs: lotRefs,
      results_applicable: resultsApplicable,
      total_units: resultsApplicable ? totalUnits : null,
      total_units_manual: resultsApplicable && totalUnits !== null ? totalUnits !== autoSum : false,
      pass_units: resultsApplicable ? passUnits : null,
      fail_units: resultsApplicable ? failUnits : null,
      notes: (step?.notes || '').trim(),
      failures: normalizedFailures,
      metrics: step?.metrics ? clone(step.metrics) : undefined,
    }
  })
}

const normalizeProcesses = (payload) => {
  const incomingProcesses = Array.isArray(payload?.processes) ? payload.processes : []
  const legacyLots = Array.isArray(payload?.lots) ? payload.lots : []
  const legacySteps = Array.isArray(payload?.steps) ? payload.steps : []

  let sourceProcesses = incomingProcesses
  if (!sourceProcesses.length) {
    sourceProcesses = [
      {
        key: payload?.key,
        name: payload?.name,
        order_index: payload?.order_index,
        lots: legacyLots,
        steps: legacySteps,
      },
    ].filter(Boolean)
  }

  return sourceProcesses.map((process, index) => {
    const key = (process?.key || `proc_${index + 1}`).toString()
    const name = (process?.name || process?.process_name || `Process ${index + 1}`).toString()
    const orderIndex = safeInt(process?.order_index ?? process?.process_order_index, index + 1)

    const { lots, lotAliasMap } = normalizeProcessLots(process?.lots, key)
    const quantityMap = new Map(lots.map((lot) => [lot.client_id, Number(lot.quantity) || 0]))
    const steps = normalizeProcessSteps(process?.steps, lotAliasMap, quantityMap)

    return {
      key,
      name,
      order_index: orderIndex,
      lots,
      steps,
    }
  })
}

const legacyLotsFromFields = (rawLotNumber, rawQuantity) => {
  const tokens = (rawLotNumber || '')
    .split(/\r?\n|,|;/)
    .map((entry) => entry.trim())
    .filter(Boolean)

  if (!tokens.length) return []

  const totalQuantity = safeInt(rawQuantity, 0)
  const perLot = tokens.length ? Math.floor(totalQuantity / tokens.length) : 0
  let remainder = totalQuantity - perLot * tokens.length

  return tokens.map((lotNumber, index) => {
    const quantity = totalQuantity > 0 ? perLot + (remainder-- > 0 ? 1 : 0) : 0
    const clientId = createClientId('legacy', index)
    return {
      id: null,
      temp_id: clientId,
      client_id: clientId,
      lot_number: lotNumber,
      quantity,
    }
  })
}

const normalizeIncomingPayload = (incoming) => {
  const base = createEmptyBuilderPayload()
  if (!incoming || typeof incoming !== 'object') {
    return base
  }

  const processes = normalizeProcesses(incoming)

  return {
    processes,
    legacy_lot_number: incoming.legacy_lot_number ?? null,
    legacy_quantity: incoming.legacy_quantity ?? null,
  }
}

export const cloneBuilderPayload = (payload) => clone(payload ?? createEmptyBuilderPayload())

export const builderPayloadToNestedRequest = (payload) => {
  const normalized = normalizeIncomingPayload(payload)

  const processes = normalized.processes.map((process, index) => {
    const lots = process.lots.map((lot, lotIndex) => {
      const clientId = lot.client_id || createClientId(`proc${index + 1}-lot`, lotIndex)
      return {
        client_id: clientId,
        temp_id: lot.temp_id || clientId,
        lot_number: lot.lot_number,
        quantity: safeInt(lot.quantity, 0),
        ...(lot.id !== undefined && lot.id !== null ? { id: lot.id } : {}),
      }
    })

    const lotIdMap = new Map(lots.map((lot) => [lot.client_id, lot.client_id]))
    const quantityMap = new Map(lots.map((lot) => [lot.client_id, safeInt(lot.quantity, 0)]))

    const steps = process.steps.map((step, stepIndex) => {
      const lotRefs = Array.isArray(step.lot_refs)
        ? step.lot_refs.map((ref) => lotIdMap.get(String(ref)) || null).filter(Boolean)
        : []

      const canonical = canonicalStepCode(step.step_code)
      const resultsApplicable =
        step.results_applicable === undefined || step.results_applicable === null
          ? isResultsApplicableDefault(canonical)
          : step.results_applicable !== false

      const normalizedFailures = resultsApplicable ? normalizeFailures(step.failures) : []
      const failUnits = resultsApplicable
        ? step.fail_units === undefined || step.fail_units === null
          ? normalizedFailures.length
          : safeInt(step.fail_units, normalizedFailures.length)
        : null

      let totalUnits = null
      if (resultsApplicable) {
        if (step.total_units === undefined || step.total_units === null) {
          totalUnits = lotRefs.reduce((sum, ref) => sum + (quantityMap.get(ref) || 0), 0)
        } else {
          totalUnits = safeInt(step.total_units, 0)
        }
      }

      const passUnits =
        resultsApplicable && totalUnits !== null && failUnits !== null
          ? Math.max(totalUnits - failUnits, 0)
          : null

      return {
        order_index: safeInt(step.order_index, stepIndex + 1),
        step_code: canonical,
        step_label: (step.step_label || '').trim() || undefined,
        eval_code: (step.eval_code || '').trim() || null,
        lot_refs: lotRefs,
        results_applicable: resultsApplicable,
        total_units: resultsApplicable ? totalUnits : null,
        total_units_manual:
          resultsApplicable && totalUnits !== null
            ? totalUnits !== lotRefs.reduce((sum, ref) => sum + (quantityMap.get(ref) || 0), 0)
            : false,
        pass_units: resultsApplicable ? passUnits : null,
        fail_units: resultsApplicable ? failUnits : null,
        notes: (step.notes || '').trim() || undefined,
        failures: normalizedFailures,
        ...(step.metrics ? { metrics: clone(step.metrics) } : {}),
      }
    })

    return {
      key: process.key || `proc_${index + 1}`,
      name: process.name || `Process ${index + 1}`,
      order_index: safeInt(process.order_index, index + 1),
      lots,
      steps,
    }
  })

  return {
    processes,
    legacy_lot_number: normalized.legacy_lot_number,
    legacy_quantity: normalized.legacy_quantity,
  }
}

export const normalizeBuilderPayload = (payload) => clone(normalizeIncomingPayload(payload))

export const hasBuilderSteps = (payload) => {
  if (!payload || !Array.isArray(payload.processes)) return false
  return payload.processes.some((process) => {
    if (!process || !Array.isArray(process.steps)) return false
    return process.steps.some((step) => {
      if (!step) return false
      const hasPrimary = Boolean((step.step_code || '').trim() || (step.step_label || '').trim())
      const hasEval = Boolean((step.eval_code || '').trim())
      const hasNotes = Boolean((step.notes || '').trim())
      const hasFailures =
        Array.isArray(step.failures) && step.failures.some((failure) => failure?.fail_code_text)
      return hasPrimary || hasEval || hasNotes || hasFailures
    })
  })
}

export const evaluationToBuilderPayload = (evaluation) => {
  const empty = createEmptyBuilderPayload()
  if (!evaluation) return clone(empty)

  const nested =
    evaluation.nested_process_payload ||
    evaluation.nested_process ||
    evaluation.process_builder_payload
  if (nested) {
    return normalizeIncomingPayload(nested)
  }

  const lotsFromLegacy = legacyLotsFromFields(
    evaluation.legacy_lot_number || evaluation.lot_number,
    evaluation.legacy_quantity || evaluation.quantity,
  )

  const legacyProcesses = Array.isArray(evaluation.processes) ? evaluation.processes : []

  if (!legacyProcesses.length) {
    return {
      processes: [
        {
          key: 'proc_1',
          name: 'Process 1',
          order_index: 1,
          lots: lotsFromLegacy.length
            ? lotsFromLegacy
            : [
                {
                  id: null,
                  temp_id: createClientId('lot', 0),
                  client_id: createClientId('lot', 0),
                  lot_number: '',
                  quantity: 0,
                },
              ],
          steps: [],
        },
      ],
      legacy_lot_number: evaluation.legacy_lot_number || evaluation.lot_number || null,
      legacy_quantity: evaluation.legacy_quantity || evaluation.quantity || null,
    }
  }

  const lots = lotsFromLegacy.length
    ? lotsFromLegacy
    : [
        {
          id: null,
          temp_id: createClientId('lot', 0),
          client_id: createClientId('lot', 0),
          lot_number: '',
          quantity: 0,
        },
      ]

  const lotMap = new Map(lots.map((lot) => [lot.client_id, lot.client_id]))

  const steps = legacyProcesses.map((process, index) => {
    const candidateCode = (process?.process_step || process?.eval_code || '').trim()
    const canonicalCode = STEP_CODE_CANONICAL.get(candidateCode.toUpperCase()) || 'Basic'
    const totalUnits = safeInt(process?.quantity, 0)
    return {
      order_index: index + 1,
      step_code: canonicalCode,
      step_label: (process?.title || '').trim(),
      eval_code: (process?.eval_code || '').trim() || null,
      results_applicable: true,
      total_units: totalUnits,
      total_units_manual: false,
      pass_units: totalUnits,
      fail_units: 0,
      notes: (process?.process_description || '').trim(),
      lot_refs: [...lotMap.values()],
      failures: [],
    }
  })

  return {
    processes: [
      {
        key: 'proc_1',
        name: evaluation.process_name || 'Process 1',
        order_index: 1,
        lots,
        steps,
      },
    ],
    legacy_lot_number: evaluation.legacy_lot_number || evaluation.lot_number || null,
    legacy_quantity: evaluation.legacy_quantity || evaluation.quantity || null,
  }
}

export const cloneBuilderPayloadWithDefaults = (payload) => {
  const normalized = normalizeIncomingPayload(payload)
  return clone(normalized)
}

export const extractLegacyProcessNotes = (evaluation) => {
  const processes = Array.isArray(evaluation?.processes) ? evaluation.processes : []
  if (!processes.length) return []

  return processes
    .map((process) => ({
      lot_number: process?.lot_number,
      description: (process?.process_description || '').trim(),
    }))
    .filter((entry) => entry.description)
}
