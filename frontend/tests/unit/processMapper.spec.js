import {
  builderPayloadToNestedRequest,
  normalizeBuilderPayload,
} from '../../src/utils/processMapper'

describe('processMapper process results', () => {
  const payload = {
    processes: [
      {
        key: 'proc-aging',
        name: 'Aging Process',
        order_index: 1,
        result_html:
          '<p><strong>Passed</strong></p><table><tbody><tr><td>PPM</td><td>0</td></tr></tbody></table>',
        lots: [
          {
            client_id: 'lot-aging',
            temp_id: 'lot-aging',
            lot_number: 'LOT-AGING',
            quantity: 10,
          },
        ],
        steps: [
          {
            order_index: 1,
            step_code: 'M100',
            step_label: 'Aging',
            lot_refs: ['lot-aging'],
            results_applicable: false,
          },
        ],
      },
    ],
  }

  it('preserves process-level rich text while normalizing builder data', () => {
    const normalized = normalizeBuilderPayload(payload)

    expect(normalized.processes[0].result_html).toBe(payload.processes[0].result_html)
  })

  it('includes process-level rich text in the nested API request', () => {
    const request = builderPayloadToNestedRequest(payload)

    expect(request.processes[0].result_html).toBe(payload.processes[0].result_html)
  })
})
