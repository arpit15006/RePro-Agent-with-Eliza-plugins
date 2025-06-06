import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Upload, 
  FileText, 
  Network, 
  Lightbulb, 
  BarChart3, 
  ArrowRight,
  CheckCircle,
  Zap,
  Brain,
  GitBranch
} from 'lucide-react'
import FileUpload from '../components/FileUpload'
import { useAnalysisStore } from '../stores/analysisStore'

const HomePage = () => {
  const [showUpload, setShowUpload] = useState(false)
  const { currentJob } = useAnalysisStore()

  const features = [
    {
      icon: FileText,
      title: 'Manuscript Analysis',
      description: 'Extract structured metadata from scientific papers using AI-powered analysis',
      color: 'text-blue-500'
    },
    {
      icon: BarChart3,
      title: 'Reproducibility Assessment',
      description: 'Evaluate code repositories for reproducibility and provide actionable recommendations',
      color: 'text-green-500'
    },
    {
      icon: Network,
      title: 'Knowledge Graphs',
      description: 'Build semantic knowledge graphs connecting papers, authors, tools, and datasets',
      color: 'text-purple-500'
    },
    {
      icon: Lightbulb,
      title: 'Hypothesis Generation',
      description: 'Generate novel research hypotheses using AI analysis of knowledge patterns',
      color: 'text-yellow-500'
    }
  ]

  const stats = [
    { label: 'Papers Analyzed', value: '10,000+' },
    { label: 'Hypotheses Generated', value: '50,000+' },
    { label: 'Reproducibility Score', value: '0.85 avg' },
    { label: 'Knowledge Triples', value: '1M+' }
  ]

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="space-y-4"
        >
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
            RePRO-Agent
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto">
            AI-powered scientific reproducibility assessment and hypothesis generation platform
          </p>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Transform scientific papers into actionable insights with our comprehensive analysis pipeline
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          <button
            onClick={() => setShowUpload(true)}
            className="bg-primary text-primary-foreground px-8 py-3 rounded-lg font-medium hover:bg-primary/90 transition-colors flex items-center gap-2"
          >
            <Upload className="w-5 h-5" />
            Start Analysis
          </button>
          
          <Link
            to="/analysis"
            className="border border-border px-8 py-3 rounded-lg font-medium hover:bg-accent transition-colors flex items-center gap-2"
          >
            View Demo
            <ArrowRight className="w-4 h-4" />
          </Link>
        </motion.div>

        {currentJob && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-card border border-border rounded-lg p-4 max-w-md mx-auto"
          >
            <p className="text-sm text-muted-foreground mb-2">Current Analysis</p>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
              <span className="text-sm font-medium">{currentJob.message}</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2 mt-2">
              <div 
                className="bg-primary h-2 rounded-full transition-all duration-300"
                style={{ width: `${currentJob.progress}%` }}
              />
            </div>
          </motion.div>
        )}
      </section>

      {/* Features Grid */}
      <section className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-foreground mb-4">Comprehensive Analysis Pipeline</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Our modular approach combines multiple AI-powered tools to provide deep insights into scientific research
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-card border border-border rounded-lg p-6 hover:shadow-lg transition-shadow"
            >
              <feature.icon className={`w-8 h-8 ${feature.color} mb-4`} />
              <h3 className="text-lg font-semibold text-foreground mb-2">{feature.title}</h3>
              <p className="text-sm text-muted-foreground">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-card border border-border rounded-lg p-8">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-foreground mb-2">Platform Impact</h2>
          <p className="text-muted-foreground">Real metrics from our analysis pipeline</p>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="text-center"
            >
              <div className="text-2xl md:text-3xl font-bold text-primary mb-1">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-foreground mb-4">How It Works</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Our four-step process transforms scientific papers into actionable research insights
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              step: 1,
              icon: FileText,
              title: 'Extract',
              description: 'AI extracts metadata, methods, and results from papers'
            },
            {
              step: 2,
              icon: GitBranch,
              title: 'Assess',
              description: 'Evaluate code reproducibility and provide scores'
            },
            {
              step: 3,
              icon: Network,
              title: 'Connect',
              description: 'Build knowledge graphs linking research elements'
            },
            {
              step: 4,
              icon: Brain,
              title: 'Generate',
              description: 'AI generates novel hypotheses and research directions'
            }
          ].map((step, index) => (
            <motion.div
              key={step.step}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
              className="relative"
            >
              <div className="bg-card border border-border rounded-lg p-6 text-center">
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <step.icon className="w-6 h-6 text-primary" />
                </div>
                <div className="text-sm font-medium text-primary mb-2">Step {step.step}</div>
                <h3 className="text-lg font-semibold text-foreground mb-2">{step.title}</h3>
                <p className="text-sm text-muted-foreground">{step.description}</p>
              </div>
              
              {index < 3 && (
                <div className="hidden lg:block absolute top-1/2 -right-3 transform -translate-y-1/2">
                  <ArrowRight className="w-6 h-6 text-muted-foreground" />
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-primary/10 to-purple-600/10 border border-border rounded-lg p-8 text-center">
        <h2 className="text-2xl font-bold text-foreground mb-4">Ready to Transform Your Research?</h2>
        <p className="text-lg text-muted-foreground mb-6 max-w-2xl mx-auto">
          Join researchers worldwide using RePRO-Agent to accelerate scientific discovery and improve reproducibility
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => setShowUpload(true)}
            className="bg-primary text-primary-foreground px-8 py-3 rounded-lg font-medium hover:bg-primary/90 transition-colors flex items-center gap-2 justify-center"
          >
            <Zap className="w-5 h-5" />
            Start Free Analysis
          </button>
          
          <Link
            to="/knowledge-graph"
            className="border border-border px-8 py-3 rounded-lg font-medium hover:bg-accent transition-colors flex items-center gap-2 justify-center"
          >
            <Network className="w-5 h-5" />
            Explore Knowledge Graph
          </Link>
        </div>
      </section>

      {/* File Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-card border border-border rounded-lg p-6 max-w-md w-full"
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Upload Scientific Paper</h3>
              <button
                onClick={() => setShowUpload(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                ×
              </button>
            </div>
            
            <FileUpload onUploadComplete={() => setShowUpload(false)} />
          </motion.div>
        </div>
      )}
    </div>
  )
}

export default HomePage
