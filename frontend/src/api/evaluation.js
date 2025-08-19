import api from '../utils/api'

export const evaluationAPI = {
  // Get all evaluations with filters
  getEvaluations: async (params = {}) => {
    const response = await api.get('/evaluations', { params })
    return response.data
  },

  // Get single evaluation by ID
  getEvaluation: async (id) => {
    const response = await api.get(`/evaluations/${id}`)
    return response.data
  },

  // Create new evaluation
  createEvaluation: async (data) => {
    const response = await api.post('/evaluations', data)
    return response.data
  },

  // Update evaluation
  updateEvaluation: async (id, data) => {
    const response = await api.put(`/evaluations/${id}`, data)
    return response.data
  },

  // Delete evaluation
  deleteEvaluation: async (id) => {
    const response = await api.delete(`/evaluations/${id}`)
    return response.data
  },

  // Approve evaluation
  approveEvaluation: async (id, data) => {
    const response = await api.post(`/evaluations/${id}/approve`, data)
    return response.data
  },

  // Reject evaluation
  rejectEvaluation: async (id, data) => {
    const response = await api.post(`/evaluations/${id}/reject`, data)
    return response.data
  },

  // Complete evaluation
  completeEvaluation: async (id, data = {}) => {
    const response = await api.post(`/evaluations/${id}/complete`, data)
    return response.data
  },

  // Pause evaluation
  pauseEvaluation: async (id, data = {}) => {
    const response = await api.post(`/evaluations/${id}/pause`, data)
    return response.data
  },

  // Resume evaluation
  resumeEvaluation: async (id, data = {}) => {
    const response = await api.post(`/evaluations/${id}/resume`, data)
    return response.data
  },

  // Cancel evaluation
  cancelEvaluation: async (id, data = {}) => {
    const response = await api.post(`/evaluations/${id}/cancel`, data)
    return response.data
  },

  // Get evaluation statistics
  getEvaluationStats: async (params = {}) => {
    const response = await api.get('/evaluations/stats', { params })
    return response.data
  },

  // Get evaluation results
  getEvaluationResults: async (id) => {
    const response = await api.get(`/evaluations/${id}/results`)
    return response.data
  },

  // Add evaluation result
  addEvaluationResult: async (id, data) => {
    const response = await api.post(`/evaluations/${id}/results`, data)
    return response.data
  },

  // Update evaluation result
  updateEvaluationResult: async (id, resultId, data) => {
    const response = await api.put(`/evaluations/${id}/results/${resultId}`, data)
    return response.data
  },

  // Delete evaluation result
  deleteEvaluationResult: async (id, resultId) => {
    const response = await api.delete(`/evaluations/${id}/results/${resultId}`)
    return response.data
  },

  // Get evaluation details
  getEvaluationDetails: async (id) => {
    const response = await api.get(`/evaluations/${id}/details`)
    return response.data
  },

  // Add evaluation detail
  addEvaluationDetail: async (id, data) => {
    const response = await api.post(`/evaluations/${id}/details`, data)
    return response.data
  },

  // Update evaluation detail
  updateEvaluationDetail: async (id, detailId, data) => {
    const response = await api.put(`/evaluations/${id}/details/${detailId}`, data)
    return response.data
  },

  // Delete evaluation detail
  deleteEvaluationDetail: async (id, detailId) => {
    const response = await api.delete(`/evaluations/${id}/details/${detailId}`)
    return response.data
  },

  // Get evaluation workflow history
  getEvaluationWorkflow: async (id) => {
    const response = await api.get(`/evaluations/${id}/workflow`)
    return response.data
  },

  // Export evaluation data
  exportEvaluation: async (id, format = 'pdf') => {
    const response = await api.get(`/evaluations/${id}/export`, {
      params: { format },
      responseType: 'blob',
    })
    return response.data
  },

  // Bulk export evaluations
  bulkExportEvaluations: async (ids, format = 'excel') => {
    const response = await api.post(
      '/evaluations/bulk-export',
      {
        evaluation_ids: ids,
        format,
      },
      {
        responseType: 'blob',
      },
    )
    return response.data
  },

  // Send mention notification
  sendMention: async (evaluationId, data) => {
    const response = await api.post(`/evaluations/${evaluationId}/mention`, data)
    return response.data
  },

  // Get mentioned users in evaluation
  getMentionedUsers: async (evaluationId) => {
    const response = await api.get(`/evaluations/${evaluationId}/mentions`)
    return response.data
  },

  // Search evaluations
  searchEvaluations: async (query, params = {}) => {
    const response = await api.get('/evaluations/search', {
      params: { q: query, ...params },
    })
    return response.data
  },

  // Get evaluation timeline
  getEvaluationTimeline: async (id) => {
    const response = await api.get(`/evaluations/${id}/timeline`)
    return response.data
  },

  // Add evaluation comment
  addEvaluationComment: async (id, data) => {
    const response = await api.post(`/evaluations/${id}/comments`, data)
    return response.data
  },

  // Get evaluation comments
  getEvaluationComments: async (id) => {
    const response = await api.get(`/evaluations/${id}/comments`)
    return response.data
  },

  // Update evaluation comment
  updateEvaluationComment: async (id, commentId, data) => {
    const response = await api.put(`/evaluations/${id}/comments/${commentId}`, data)
    return response.data
  },

  // Delete evaluation comment
  deleteEvaluationComment: async (id, commentId) => {
    const response = await api.delete(`/evaluations/${id}/comments/${commentId}`)
    return response.data
  },
}
