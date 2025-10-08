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
  ['M031', 'M031'],
  ['M033', 'M033'],
  ['M100', 'M100'],
  ['M111', 'M111'],
  ['M130', 'M130'],
  ['AQL', 'AQL'],
  ['BASIC', 'Basic'],
])

const RESULT_OPTIONAL_CODES = new Set(['M033', 'M100'])

export const createEmptyBuilderPayload = () => ({
  lots: [],
  steps: [],
  legacy_lot_number: null,
  legacy_quantity: null,
})

const combineNotes = (...parts) =>
  parts
    .map((part) => (part || '').trim())
    .filter(Boolean)
    .join('\n\n')

const normalizeLots = (lots = []) => {
  if (!Array.isArray(lots)) return []
  return lots
    .map((lot, index) => {
      const lotNumber = (lot?.lot_number || '').trim()
      const quantity = safeInt(lot?.quantity, 0)
      const id = lot?.id ?? null
      const tempId = String(
        lot?.temp_id || lot?.client_id || lot?.id || createClientId('lot', index),
      )
      const clientId = String(lot?.client_id || tempId)
      return {
        id,
        temp_id: tempId,
        client_id: clientId,
        lot_number: lotNumber,
        quantity,
      }
    })
    .filter((lot) => lot.lot_number)
}

const ensureLotDefaults = (lots) => {
  if (lots.length) return lots
  return [
    {
      id: null,
      temp_id: createClientId('lot', 0),
      client_id: createClientId('lot', 0),
      lot_number: '',
      quantity: 0,
    },
  ]
}

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

const normalizeSteps = (steps = [], lotMap, defaultLotIds, quantityMap) => {
  if (!Array.isArray(steps)) return []
  return steps
    .map((step, index) => {
      const rawRefs = Array.isArray(step?.lot_refs) ? step.lot_refs : []
      const lotRefs = rawRefs.map((ref) => lotMap.get(String(ref)) || null).filter(Boolean)
      const effectiveRefs = lotRefs.length ? [...new Set(lotRefs)] : [...defaultLotIds]

      const rawCode = (step?.step_code || '').trim()
      const canonicalCode = STEP_CODE_CANONICAL.get(rawCode.toUpperCase()) || rawCode.toUpperCase()
      const canonicalUpper = canonicalCode.toUpperCase()
      const defaultResultsApplicable = !RESULT_OPTIONAL_CODES.has(canonicalUpper)
      const resultsApplicable =
        step?.results_applicable === undefined || step?.results_applicable === null
          ? defaultResultsApplicable
          : Boolean(step.results_applicable)

      const totalUnitsValue = step?.total_units
      const failUnitsValue = step?.fail_units
      const passUnitsValue = step?.pass_units
      const autoSum = resultsApplicable
        ? effectiveRefs.reduce((sum, ref) => sum + (quantityMap.get(ref) || 0), 0)
        : 0

      return {
        order_index: safeInt(step?.order_index, index + 1),
        step_code: canonicalCode,
        step_label: (step?.step_label || '').trim(),
        eval_code: (step?.eval_code || '').trim(),
        lot_refs: effectiveRefs,
        results_applicable: resultsApplicable,
        total_units:
          resultsApplicable && totalUnitsValue !== undefined && totalUnitsValue !== null
            ? Number(totalUnitsValue)
            : null,
        total_units_manual:
          resultsApplicable && totalUnitsValue !== undefined && totalUnitsValue !== null
            ? Number(totalUnitsValue) !== autoSum
            : false,
        pass_units:
          resultsApplicable && passUnitsValue !== undefined && passUnitsValue !== null
            ? Number(passUnitsValue)
            : null,
        fail_units:
          resultsApplicable && failUnitsValue !== undefined && failUnitsValue !== null
            ? Number(failUnitsValue)
            : null,
        notes: (step?.notes || '').trim(),
        failures: resultsApplicable ? normalizeFailures(step?.failures) : [],
      }
    })
    .filter((step) => step.step_code || step.step_label || step.failures.length)
}

const legacyLotsFromFields = (rawLotNumber, rawQuantity) => {
  const lotField = (rawLotNumber || '').trim()
  if (!lotField) {
    return []
  }
  const entries = lotField
    .split(/\r?\n|,|;/)
    .map((entry) => entry.trim())
    .filter(Boolean)

  if (!entries.length) return []

  const totalQuantity = safeInt(rawQuantity, 0)
  const perLot = entries.length ? Math.floor(totalQuantity / entries.length) : 0
  let remainder = totalQuantity - perLot * entries.length

  return entries.map((lotNumber, index) => {
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
    base.lots = ensureLotDefaults([])
    base.steps = []
    return base
  }

  const normalizedLots = ensureLotDefaults(normalizeLots(incoming.lots))
  const lotAliasMap = new Map()
  const defaultLotIds = []
  const lotQuantityMap = new Map()
  normalizedLots.forEach((lot) => {
    lotAliasMap.set(String(lot.client_id), lot.client_id)
    lotAliasMap.set(String(lot.temp_id), lot.client_id)
    if (lot.id !== null && lot.id !== undefined) {
      lotAliasMap.set(String(lot.id), lot.client_id)
    }
    defaultLotIds.push(lot.client_id)
    lotQuantityMap.set(lot.client_id, Number(lot.quantity) || 0)
  })

  const normalizedSteps = normalizeSteps(
    incoming.steps,
    lotAliasMap,
    defaultLotIds,
    lotQuantityMap,
  )

  return {
    lots: normalizedLots,
    steps: normalizedSteps,
    legacy_lot_number: incoming.legacy_lot_number ?? null,
    legacy_quantity: incoming.legacy_quantity ?? null,
  }
}

export const cloneBuilderPayload = (payload) => clone(payload ?? createEmptyBuilderPayload())

export const builderPayloadToNestedRequest = (payload) => {
  const normalized = normalizeIncomingPayload(payload)

  const lotRefMap = new Map()
  const lotQuantityMap = new Map()
  const lots = normalized.lots.map((lot, index) => {
    const tempId = lot.temp_id || lot.client_id || createClientId('lot', index)
    const serialized = {
      temp_id: tempId,
      lot_number: lot.lot_number,
      quantity: safeInt(lot.quantity, 0),
    }
    if (lot.id !== null && lot.id !== undefined) {
      serialized.id = lot.id
    }
    lotRefMap.set(String(lot.client_id), serialized.id ?? serialized.temp_id)
    lotRefMap.set(String(tempId), serialized.id ?? serialized.temp_id)
    if (serialized.id !== undefined) {
      lotRefMap.set(String(serialized.id), serialized.id)
    }
    lotQuantityMap.set(lot.client_id, safeInt(lot.quantity, 0))
    return serialized
  })

  const steps = normalized.steps.map((step, index) => {
    const refs =
      Array.isArray(step.lot_refs) && step.lot_refs.length
        ? [...new Set(step.lot_refs)]
        : lots.map((lot) => lotRefMap.get(String(lot.id ?? lot.temp_id)))
    const mappedRefs = refs.map((ref) => lotRefMap.get(String(ref)) || null).filter(Boolean)

    const canonicalCode =
      STEP_CODE_CANONICAL.get((step.step_code || '').trim().toUpperCase()) ||
      (step.step_code || '').trim()
    const canonicalUpper = (canonicalCode || '').toString().toUpperCase()
    const defaultResultsApplicable = !RESULT_OPTIONAL_CODES.has(canonicalUpper)
    const rawApplicable = step.results_applicable
    const resultsApplicable =
      rawApplicable === undefined || rawApplicable === null
        ? defaultResultsApplicable
        : rawApplicable !== false

    const autoTotal = Array.isArray(step.lot_refs)
      ? step.lot_refs.reduce((sum, ref) => sum + (lotQuantityMap.get(ref) || 0), 0)
      : 0

    let totalUnits = null
    if (resultsApplicable) {
      if (step.total_units === null || step.total_units === undefined) {
        totalUnits = autoTotal
      } else {
        totalUnits = Number(step.total_units)
      }
    }

    const normalizedFailures = resultsApplicable ? normalizeFailures(step.failures) : []
    const failUnits = resultsApplicable ? normalizedFailures.length : null
    const passUnits =
      resultsApplicable && totalUnits !== null && failUnits !== null
        ? Math.max(totalUnits - failUnits, 0)
        : null

    const evalCode = (step.eval_code || '').trim()
    const notes = (step.notes || '').trim()

    return {
      order_index: safeInt(step.order_index, index + 1),
      step_code: canonicalCode,
      step_label: (step.step_label || '').trim() || undefined,
      eval_code: evalCode ? evalCode : null,
      lot_refs: mappedRefs,
      results_applicable: resultsApplicable,
      total_units: resultsApplicable ? totalUnits : null,
      total_units_manual:
        resultsApplicable && totalUnits !== null ? totalUnits !== autoTotal : false,
      pass_units: resultsApplicable ? passUnits : null,
      fail_units: resultsApplicable ? failUnits : null,
      notes: notes || undefined,
      failures: normalizedFailures,
    }
  })

  return {
    lots,
    steps,
    legacy_lot_number: normalized.legacy_lot_number,
    legacy_quantity: normalized.legacy_quantity,
  }
}

export const hasBuilderSteps = (payload) => {
  if (!payload || !Array.isArray(payload.steps)) return false
  return payload.steps.some((step) => {
    if (!step) return false
    const hasPrimary = Boolean((step.step_code || '').trim() || (step.step_label || '').trim())
    const hasEval = Boolean((step.eval_code || '').trim())
    const hasNotes = Boolean((step.notes || '').trim())
    const hasFailures =
      Array.isArray(step.failures) && step.failures.some((failure) => failure?.fail_code_text)
    return hasPrimary || hasEval || hasNotes || hasFailures
  })
}

export const evaluationToBuilderPayload = (evaluation) => {
  const empty = createEmptyBuilderPayload()
  if (!evaluation) return { ...empty, lots: ensureLotDefaults([]) }

  const nestedCandidates = [
    evaluation.nested_process,
    evaluation.nested_process_payload,
    evaluation.process_builder_payload,
    evaluation.nested_payload,
  ]
  const nested = nestedCandidates.find((candidate) => candidate && typeof candidate === 'object')
  if (nested) {
    return normalizeIncomingPayload(nested)
  }

  const lotsFromLegacy = legacyLotsFromFields(
    evaluation.legacy_lot_number || evaluation.lot_number,
    evaluation.legacy_quantity || evaluation.quantity,
  )

  const legacyProcesses = Array.isArray(evaluation.processes) ? evaluation.processes : []

  const lots = lotsFromLegacy.length ? lotsFromLegacy : ensureLotDefaults([])
  const lotIds = lots.map((lot) => lot.client_id)
  const steps = legacyProcesses.map((process, index) => {
    const lotNumber = (process?.lot_number || '').trim()
    const lotMatch = lots.find((lot) => lot.lot_number === lotNumber)
    const lotRef = lotMatch ? [lotMatch.client_id] : [...lotIds]
    const candidateCode = (process?.process_step || process?.eval_code || '').trim()
    const canonicalCode = STEP_CODE_CANONICAL.get(candidateCode.toUpperCase()) || 'Basic'
    const evalCode = (process?.eval_code || '').trim()
    const totalUnits = safeInt(process?.quantity, 0)
    return {
      order_index: index + 1,
      step_code: canonicalCode,
      step_label: (process?.title || '').trim(),
      eval_code: evalCode || null,
      results_applicable: true,
      total_units: totalUnits,
      total_units_manual: false,
      pass_units: totalUnits,
      fail_units: 0,
      notes: combineNotes(
        process?.process_description,
        process?.manufacturing_test_results,
        process?.defect_analysis_results,
        process?.aql_result,
      ),
      lot_refs: lotRef,
      failures: [],
    }
  })

  if (!steps.length) {
    const legacyText = combineNotes(
      evaluation.legacy_process_text,
      evaluation.process_description,
      evaluation.process_step,
      evaluation.remarks,
    )
    if (legacyText) {
      steps.push({
        order_index: 1,
        step_code: 'Basic',
        step_label: 'Legacy',
        eval_code: null,
        results_applicable: true,
        total_units: 0,
        total_units_manual: false,
        pass_units: 0,
        fail_units: 0,
        notes: legacyText,
        lot_refs: [...lotIds],
        failures: [],
      })
    }
  }

  return {
    lots,
    steps,
    legacy_lot_number: evaluation.legacy_lot_number || evaluation.lot_number || null,
    legacy_quantity: evaluation.legacy_quantity || evaluation.quantity || null,
  }
}

export const extractLegacyProcessNotes = (evaluation) => {
  const processes = Array.isArray(evaluation?.processes) ? evaluation.processes : []
  if (!processes.length) return []

  return processes
    .map((process, index) => {
      const content = combineNotes(
        process?.process_description,
        process?.manufacturing_test_results,
        process?.defect_analysis_results,
        process?.aql_result,
      )
      if (!content) return null
      return {
        title: process?.title || process?.eval_code || `Legacy ${index + 1}`,
        content,
      }
    })
    .filter(Boolean)
}

export const normalizeBuilderPayload = (payload) => normalizeIncomingPayload(payload)
