import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  FileText, 
  BarChart3, 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  Download,
  RefreshCw,
  ExternalLink,
  GitBranch,
  Users,
  Calendar,
  Tag
} from 'lucide-react'
import { apiService } from '../services/api'
import { useAnalysisStore, AnalysisJob } from '../stores/analysisStore'
import toast from 'react-hot-toast'

const AnalysisPage = () => {
  const { jobId } = useParams()
  const { currentJob, updateJob, setCurrentJob } = useAnalysisStore()
  const [loading, setLoading] = useState(false)
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const hasShownCompletionToastRef = useRef(false)
  const isPollingRef = useRef(false)

  // Cleanup function
  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
      pollingIntervalRef.current = null
    }
    isPollingRef.current = false
  }

  useEffect(() => {
    if (jobId) {
      // Reset completion toast flag for new job
      hasShownCompletionToastRef.current = false

      // Stop any existing polling
      stopPolling()

      // Start polling
      isPollingRef.current = true
      pollJobStatus(jobId)

      // Set up polling for active jobs
      const interval = setInterval(() => {
        if (isPollingRef.current) {
          pollJobStatus(jobId)
        }
      }, 2000)

      pollingIntervalRef.current = interval

      return () => {
        stopPolling()
      }
    }
  }, [jobId])

  const pollJobStatus = async (id: string) => {
    try {
      const status = await apiService.getJobStatus(id)
      const previousStatus = currentJob?.status
      updateJob(id, status)

      if (status.status === 'completed' || status.status === 'failed') {
        stopPolling()
      }

      // Only show toast if status changed and we haven't shown it before
      if (status.status === 'completed' && previousStatus !== 'completed' && !hasShownCompletionToastRef.current) {
        toast.success('Analysis completed!')
        hasShownCompletionToastRef.current = true
      } else if (status.status === 'failed' && previousStatus !== 'failed') {
        toast.error('Analysis failed')
      }
    } catch (error) {
      console.error('Error polling job status:', error)
      stopPolling()
    }
  }

  const downloadResults = async () => {
    if (!currentJob?.job_id) return
    
    try {
      setLoading(true)
      const blob = await apiService.downloadResults(currentJob.job_id)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `repro-agent-results-${currentJob.job_id}.json`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast.success('Results downloaded!')
    } catch (error) {
      console.error('Download error:', error)
      toast.error('Download failed')
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'processing':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-500'
      case 'processing':
        return 'text-blue-500'
      case 'failed':
        return 'text-red-500'
      default:
        return 'text-yellow-500'
    }
  }

  if (!currentJob && jobId) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-foreground mb-2">Analysis Not Found</h2>
        <p className="text-muted-foreground mb-4">
          The analysis job you're looking for doesn't exist or has expired.
        </p>
        <Link
          to="/"
          className="bg-primary text-primary-foreground px-6 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors"
        >
          Start New Analysis
        </Link>
      </div>
    )
  }

  if (!currentJob) {
    return (
      <div className="text-center py-12">
        <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-foreground mb-2">No Analysis Running</h2>
        <p className="text-muted-foreground mb-4">
          Start a new analysis to see results here.
        </p>
        <Link
          to="/"
          className="bg-primary text-primary-foreground px-6 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors"
        >
          Start Analysis
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Analysis Results</h1>
          <p className="text-muted-foreground">Job ID: {currentJob.job_id}</p>
        </div>
        
        <div className="flex items-center gap-3">
          {currentJob.status === 'completed' && (
            <button
              onClick={downloadResults}
              disabled={loading}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <Download className="w-4 h-4" />
              {loading ? 'Downloading...' : 'Download Results'}
            </button>
          )}
        </div>
      </div>

      {/* Status Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-card border border-border rounded-lg p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          {getStatusIcon(currentJob.status)}
          <div>
            <h3 className="text-lg font-semibold text-foreground">
              Analysis Status: <span className={getStatusColor(currentJob.status)}>{currentJob.status}</span>
            </h3>
            <p className="text-sm text-muted-foreground">{currentJob.message}</p>
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="text-foreground">{currentJob.progress}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <motion.div 
              className="bg-primary h-2 rounded-full transition-all duration-300"
              initial={{ width: 0 }}
              animate={{ width: `${currentJob.progress}%` }}
            />
          </div>
        </div>
      </motion.div>

      {/* Results */}
      {currentJob.status === 'completed' && currentJob.results && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Metadata Results */}
          {currentJob.results.metadata && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-card border border-border rounded-lg p-6"
            >
              <div className="flex items-center gap-2 mb-4">
                <FileText className="w-5 h-5 text-blue-500" />
                <h3 className="text-lg font-semibold text-foreground">Paper Metadata</h3>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-foreground mb-2">{currentJob.results.metadata.title}</h4>
                  <p className="text-sm text-muted-foreground line-clamp-3">
                    {currentJob.results.metadata.abstract}
                  </p>
                </div>
                
                {currentJob.results.metadata.author && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Users className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm font-medium text-foreground">Authors</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {currentJob.results.metadata.author.slice(0, 3).map((author: any, index: number) => (
                        <span key={index} className="bg-muted px-2 py-1 rounded text-xs">
                          {typeof author === 'string' ? author : author.name}
                        </span>
                      ))}
                      {currentJob.results.metadata.author.length > 3 && (
                        <span className="text-xs text-muted-foreground">
                          +{currentJob.results.metadata.author.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
                
                {currentJob.results.metadata.keywords && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Tag className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm font-medium text-foreground">Keywords</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {currentJob.results.metadata.keywords.slice(0, 5).map((keyword: string, index: number) => (
                        <span key={index} className="bg-primary/10 text-primary px-2 py-1 rounded text-xs">
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Reproducibility Results */}
          {currentJob.results.reproducibility && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-card border border-border rounded-lg p-6"
            >
              <div className="flex items-center gap-2 mb-4">
                <BarChart3 className="w-5 h-5 text-green-500" />
                <h3 className="text-lg font-semibold text-foreground">Reproducibility Assessment</h3>
              </div>
              
              <div className="space-y-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary mb-2">
                    {(currentJob.results.reproducibility.reproducibility_score * 100).toFixed(0)}%
                  </div>
                  <p className="text-sm text-muted-foreground">Reproducibility Score</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Has README</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Has Requirements</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-yellow-500" />
                    <span>Has Dockerfile</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Has Setup</span>
                  </div>
                </div>
                
                {currentJob.results.reproducibility.recommendations && (
                  <div>
                    <h4 className="font-medium text-foreground mb-2">Recommendations</h4>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {currentJob.results.reproducibility.recommendations.slice(0, 3).map((rec: string, index: number) => (
                        <li key={index} className="flex items-start gap-2">
                          <span className="text-primary">•</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </div>
      )}

      {/* Navigation Links */}
      {currentJob.status === 'completed' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex flex-wrap gap-4 justify-center"
        >
          <Link
            to="/knowledge-graph"
            className="bg-purple-500 text-white px-6 py-3 rounded-lg font-medium hover:bg-purple-600 transition-colors flex items-center gap-2"
          >
            <GitBranch className="w-4 h-4" />
            View Knowledge Graph
          </Link>
          
          <Link
            to="/hypotheses"
            className="bg-yellow-500 text-white px-6 py-3 rounded-lg font-medium hover:bg-yellow-600 transition-colors flex items-center gap-2"
          >
            <FileText className="w-4 h-4" />
            View Hypotheses
          </Link>
        </motion.div>
      )}
    </div>
  )
}

export default AnalysisPage
