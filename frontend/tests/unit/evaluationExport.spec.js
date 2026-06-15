import { fetchAllEvaluationPages } from '../../src/utils/evaluationExport'

describe('fetchAllEvaluationPages', () => {
  it('fetches every page while preserving export filters', async () => {
    const apiClient = {
      get: jest
        .fn()
        .mockResolvedValueOnce({
          data: {
            data: {
              evaluations: [{ id: 1 }, { id: 2 }],
              total: 3,
              pages: 2,
            },
          },
        })
        .mockResolvedValueOnce({
          data: {
            data: {
              evaluations: [{ id: 3 }],
              total: 3,
              pages: 2,
            },
          },
        }),
    }

    const evaluations = await fetchAllEvaluationPages(apiClient, { status: 'completed' }, 2)

    expect(evaluations).toEqual([{ id: 1 }, { id: 2 }, { id: 3 }])
    expect(apiClient.get).toHaveBeenNthCalledWith(1, '/evaluations', {
      params: { status: 'completed', page: 1, per_page: 2 },
    })
    expect(apiClient.get).toHaveBeenNthCalledWith(2, '/evaluations', {
      params: { status: 'completed', page: 2, per_page: 2 },
    })
  })

  it('stops after an empty response', async () => {
    const apiClient = {
      get: jest.fn().mockResolvedValue({
        data: {
          data: {
            evaluations: [],
          },
        },
      }),
    }

    await expect(fetchAllEvaluationPages(apiClient)).resolves.toEqual([])
    expect(apiClient.get).toHaveBeenCalledTimes(1)
  })
})
