const DEFAULT_EXPORT_PAGE_SIZE = 500

export const fetchAllEvaluationPages = async (
  apiClient,
  params = {},
  pageSize = DEFAULT_EXPORT_PAGE_SIZE,
) => {
  const evaluations = []
  let page = 1

  while (true) {
    const response = await apiClient.get('/evaluations', {
      params: {
        ...params,
        page,
        per_page: pageSize,
      },
    })
    const data = response.data?.data || {}
    const pageEvaluations = Array.isArray(data.evaluations) ? data.evaluations : []

    evaluations.push(...pageEvaluations)

    const total = Number(data.total)
    const pages = Number(data.pages)
    const reachedTotal = Number.isFinite(total) && evaluations.length >= total
    const reachedLastPage = Number.isFinite(pages) && page >= pages

    if (pageEvaluations.length === 0 || reachedTotal || reachedLastPage) {
      break
    }

    page += 1
  }

  return evaluations
}
