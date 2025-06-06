import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Upload, FileText, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { apiService } from '../services/api'
import { useAnalysisStore } from '../stores/analysisStore'

interface FileUploadProps {
  onUploadComplete?: () => void
}

const FileUpload = ({ onUploadComplete }: FileUploadProps) => {
  const [uploading, setUploading] = useState(false)
  const [repoUrl, setRepoUrl] = useState('')
  const [focusArea, setFocusArea] = useState('')
  const [numHypotheses, setNumHypotheses] = useState(5)
  const navigate = useNavigate()
  const { addJob } = useAnalysisStore()

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setUploading(true)
    
    try {
      // Upload file
      const uploadResult = await apiService.uploadPaper(file)
      toast.success('File uploaded successfully!')

      // Start analysis
      const analysisResult = await apiService.analyzePaper({
        paper_url: uploadResult.file_path,
        repo_url: repoUrl || undefined,
        focus_area: focusArea || undefined,
        num_hypotheses: numHypotheses
      })

      // Add job to store
      addJob({
        job_id: analysisResult.job_id,
        status: 'pending',
        progress: 0,
        message: 'Analysis started'
      })

      toast.success('Analysis started!')
      navigate(`/analysis/${analysisResult.job_id}`)
      onUploadComplete?.()

    } catch (error: any) {
      console.error('Upload/analysis error:', error)
      toast.error(error.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }, [repoUrl, focusArea, numHypotheses, navigate, addJob, onUploadComplete])

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/markdown': ['.md'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
    disabled: uploading
  })

  const handleUrlAnalysis = async () => {
    if (!repoUrl.trim()) {
      toast.error('Please enter a repository URL')
      return
    }

    setUploading(true)
    
    try {
      const analysisResult = await apiService.analyzePaper({
        repo_url: repoUrl,
        focus_area: focusArea || undefined,
        num_hypotheses: numHypotheses
      })

      addJob({
        job_id: analysisResult.job_id,
        status: 'pending',
        progress: 0,
        message: 'Analysis started'
      })

      toast.success('Analysis started!')
      navigate(`/analysis/${analysisResult.job_id}`)
      onUploadComplete?.()

    } catch (error: any) {
      console.error('Analysis error:', error)
      toast.error(error.response?.data?.detail || 'Analysis failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* File Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-primary bg-primary/5' 
            : 'border-border hover:border-primary/50 hover:bg-accent/50'
          }
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          {uploading ? (
            <Loader2 className="w-12 h-12 text-primary mx-auto animate-spin" />
          ) : (
            <Upload className="w-12 h-12 text-muted-foreground mx-auto" />
          )}
          
          <div>
            <p className="text-lg font-medium text-foreground">
              {isDragActive ? 'Drop your paper here' : 'Upload Scientific Paper'}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Drag & drop or click to select • PDF, MD, TXT • Max 50MB
            </p>
          </div>
          
          {fileRejections.length > 0 && (
            <div className="text-sm text-destructive flex items-center gap-2 justify-center">
              <AlertCircle className="w-4 h-4" />
              {fileRejections[0].errors[0].message}
            </div>
          )}
        </div>
      </div>

      {/* Divider */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="bg-background px-2 text-muted-foreground">or analyze repository only</span>
        </div>
      </div>

      {/* Repository URL Input */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            GitHub Repository URL (Optional)
          </label>
          <input
            type="url"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/username/repository"
            className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={uploading}
          />
        </div>

        <button
          onClick={handleUrlAnalysis}
          disabled={uploading || !repoUrl.trim()}
          className="w-full bg-secondary text-secondary-foreground px-4 py-2 rounded-md font-medium hover:bg-secondary/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {uploading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <FileText className="w-4 h-4" />
          )}
          Analyze Repository Only
        </button>
      </div>

      {/* Analysis Options */}
      <div className="space-y-4 pt-4 border-t border-border">
        <h4 className="text-sm font-medium text-foreground">Analysis Options</h4>
        
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Focus Area (Optional)
          </label>
          <input
            type="text"
            value={focusArea}
            onChange={(e) => setFocusArea(e.target.value)}
            placeholder="e.g., machine learning, bioinformatics, climate science"
            className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={uploading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Number of Hypotheses
          </label>
          <select
            value={numHypotheses}
            onChange={(e) => setNumHypotheses(Number(e.target.value))}
            className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={uploading}
          >
            <option value={3}>3 hypotheses</option>
            <option value={5}>5 hypotheses</option>
            <option value={7}>7 hypotheses</option>
            <option value={10}>10 hypotheses</option>
          </select>
        </div>
      </div>

      {/* Supported Formats */}
      <div className="text-xs text-muted-foreground space-y-1">
        <p className="font-medium">Supported formats:</p>
        <div className="flex flex-wrap gap-2">
          <span className="bg-muted px-2 py-1 rounded">PDF</span>
          <span className="bg-muted px-2 py-1 rounded">Markdown</span>
          <span className="bg-muted px-2 py-1 rounded">Plain Text</span>
        </div>
      </div>
    </div>
  )
}

export default FileUpload
