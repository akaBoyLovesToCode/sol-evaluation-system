export const createEmptyBuilderPayload = () => ({
  lot_number: '',
  quantity: 0,
  steps: [],
})

const clone = (payload) => JSON.parse(JSON.stringify(payload ?? createEmptyBuilderPayload()))

const combineNotes = (...parts) =>
  parts
    .map((part) => (part || '').trim())
    .filter(Boolean)
    .join('\n\n')

export const evaluationToBuilderPayload = (evaluation) => {
  const payload = createEmptyBuilderPayload()
  if (!evaluation) {
    return payload
  }

  const processes = Array.isArray(evaluation.processes) ? evaluation.processes : []
  if (processes.length > 0) {
    payload.lot_number = processes[0].lot_number || evaluation.evaluation_number || ''
    payload.quantity = processes[0].quantity || 0

    processes.forEach((process, index) => {
      payload.steps.push({
        order_index: index + 1,
        step_code: (process.eval_code || process.title || `STEP_${index + 1}`).toString(),
        step_label: process.title || '',
        eval_code: process.eval_code || '',
        total_units: process.quantity || 0,
        pass_units: process.quantity || 0,
        fail_units: 0,
        notes: combineNotes(
          process.process_description,
          process.manufacturing_test_results,
          process.defect_analysis_results,
          process.aql_result,
        ),
        failures: [],
      })
    })
    return payload
  }

  const legacyText = combineNotes(
    evaluation.legacy_process_text,
    evaluation.process_description,
    evaluation.process_step,
    evaluation.remarks,
  )

  if (legacyText) {
    payload.steps.push({
      order_index: 1,
      step_code: 'LEGACY',
      step_label: 'Legacy',
      eval_code: 'LEGACY',
      total_units: 0,
      pass_units: 0,
      fail_units: 0,
      notes: legacyText,
      failures: [],
    })
  }

  payload.lot_number = evaluation.evaluation_number || payload.lot_number
  return payload
}

export const builderPayloadToNestedRequest = (payload) => {
  const data = clone(payload)
  data.lot_number = (data.lot_number || '').trim()
  data.quantity = Number(data.quantity) || 0
  data.steps = Array.isArray(data.steps)
    ? data.steps
        .map((step, index) => ({
        order_index: step.order_index || index + 1,
        step_code: (step.step_code || '').trim(),
        step_label: (step.step_label || '').trim() || undefined,
        eval_code: (step.eval_code || '').trim(),
        total_units: Number(step.total_units) || 0,
        pass_units: Number(step.pass_units) || 0,
        fail_units: Number(step.fail_units) || 0,
        notes: (step.notes || '').trim() || undefined,
        failures: Array.isArray(step.failures)
          ? step.failures.map((failure, failureIndex) => ({
              sequence: failure.sequence || failureIndex + 1,
              serial_number: (failure.serial_number || '').trim() || undefined,
              fail_code_id: failure.fail_code_id ?? undefined,
              fail_code_text: (failure.fail_code_text || '').trim(),
              fail_code_name_snapshot: (failure.fail_code_name_snapshot || '').trim() || undefined,
              analysis_result: (failure.analysis_result || '').trim() || undefined,
            }))
          : [],
      }))
        .filter((step) => step.step_code && step.eval_code)
    : []
  return data
}

export const hasBuilderSteps = (payload) =>
  Boolean(
    payload &&
      Array.isArray(payload.steps) &&
      payload.steps.some((step) =>
        Boolean(
          step &&
            ((step.step_code && step.step_code.trim()) ||
              (step.eval_code && step.eval_code.trim()) ||
              (Array.isArray(step.failures) && step.failures.some((failure) => failure.fail_code_text))),
        ),
      ),
  )

export const extractLegacyProcessNotes = (evaluation) => {
  const processes = Array.isArray(evaluation?.processes) ? evaluation.processes : []
  if (!processes.length) return []
  return processes
    .map((proc, index) => {
      const content = combineNotes(
        proc.process_description,
        proc.manufacturing_test_results,
        proc.defect_analysis_results,
        proc.aql_result,
      )
      if (!content) return null
      return {
        title: proc.title || proc.eval_code || `Legacy ${index + 1}`,
        content,
      }
    })
    .filter(Boolean)
}

export const cloneBuilderPayload = (payload) => clone(payload)
