import { create } from 'zustand'

export interface AnalysisJob {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
  results?: {
    metadata?: any
    reproducibility?: any
    hypotheses?: any
    graph_data?: any
  }
}

interface AnalysisStore {
  currentJob: AnalysisJob | null
  jobs: AnalysisJob[]
  setCurrentJob: (job: AnalysisJob | null) => void
  updateJob: (jobId: string, updates: Partial<AnalysisJob>) => void
  addJob: (job: AnalysisJob) => void
  clearJobs: () => void
}

export const useAnalysisStore = create<AnalysisStore>((set, get) => ({
  currentJob: null,
  jobs: [],
  
  setCurrentJob: (job) => set({ currentJob: job }),
  
  updateJob: (jobId, updates) => {
    const { jobs, currentJob } = get()
    const updatedJobs = jobs.map(job => 
      job.job_id === jobId ? { ...job, ...updates } : job
    )
    
    set({ 
      jobs: updatedJobs,
      currentJob: currentJob?.job_id === jobId 
        ? { ...currentJob, ...updates }
        : currentJob
    })
  },
  
  addJob: (job) => {
    const { jobs } = get()
    set({ 
      jobs: [job, ...jobs],
      currentJob: job
    })
  },
  
  clearJobs: () => set({ jobs: [], currentJob: null }),
}))
