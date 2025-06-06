import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export interface PaperAnalysisRequest {
  paper_url?: string
  repo_url?: string
  focus_area?: string
  num_hypotheses?: number
}

export interface JobStatus {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
  results?: any
}

export interface UploadResponse {
  file_id: string
  filename: string
  file_path: string
  size: number
  message: string
}

// API functions
export const apiService = {
  // Health check
  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  },

  // Upload paper file
  async uploadPaper(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/upload-paper', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Start paper analysis
  async analyzePaper(request: PaperAnalysisRequest) {
    const response = await api.post('/analyze-paper', request)
    return response.data
  },

  // Get job status
  async getJobStatus(jobId: string): Promise<JobStatus> {
    const response = await api.get(`/job-status/${jobId}`)
    return response.data
  },

  // Extract metadata from file
  async extractMetadata(filePath: string) {
    const response = await api.get('/extract-metadata', {
      params: { file_path: filePath }
    })
    return response.data
  },

  // Assess reproducibility
  async assessReproducibility(repoUrl: string) {
    const response = await api.get('/assess-reproducibility', {
      params: { repo_url: repoUrl }
    })
    return response.data
  },

  // Build knowledge graph
  async buildKnowledgeGraph(metadata: any, reproducibilityReport?: any) {
    const response = await api.post('/build-knowledge-graph', {
      metadata,
      reproducibility_report: reproducibilityReport
    })
    return response.data
  },

  // Generate hypotheses
  async generateHypotheses(graphData: any[], numHypotheses = 5, focusArea?: string) {
    const response = await api.post('/generate-hypotheses', {
      graph_data: graphData,
      num_hypotheses: numHypotheses,
      focus_area: focusArea
    })
    return response.data
  },

  // Download results
  async downloadResults(jobId: string) {
    const response = await api.get(`/download-results/${jobId}`, {
      responseType: 'blob'
    })
    return response.data
  },
}

export default api
