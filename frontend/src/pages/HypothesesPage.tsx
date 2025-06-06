import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Lightbulb, 
  TrendingUp, 
  Clock, 
  Target, 
  Star, 
  Download,
  Filter,
  Search,
  ChevronDown,
  ChevronUp,
  ExternalLink
} from 'lucide-react'
import { useAnalysisStore } from '../stores/analysisStore'

interface Hypothesis {
  hypothesis: string
  rationale: string
  methodology: string
  required_resources: string[]
  expected_impact: string
  feasibility: 'high' | 'medium' | 'low'
  novelty_score: number
}

const HypothesesPage = () => {
  const { currentJob } = useAnalysisStore()
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([])
  const [filteredHypotheses, setFilteredHypotheses] = useState<Hypothesis[]>([])
  const [filters, setFilters] = useState({
    feasibility: 'all',
    minNovelty: 0,
    searchTerm: ''
  })
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set())
  const [sortBy, setSortBy] = useState<'novelty' | 'feasibility'>('novelty')

  useEffect(() => {
    // Load hypotheses from current job or sample data
    if (currentJob?.results?.hypotheses?.generated_hypotheses) {
      setHypotheses(currentJob.results.hypotheses.generated_hypotheses)
    } else {
      // Load sample hypotheses for demo
      loadSampleHypotheses()
    }
  }, [currentJob])

  useEffect(() => {
    // Apply filters and sorting
    let filtered = hypotheses

    // Filter by feasibility
    if (filters.feasibility !== 'all') {
      filtered = filtered.filter(h => h.feasibility === filters.feasibility)
    }

    // Filter by novelty score
    filtered = filtered.filter(h => h.novelty_score >= filters.minNovelty)

    // Filter by search term
    if (filters.searchTerm) {
      const term = filters.searchTerm.toLowerCase()
      filtered = filtered.filter(h =>
        h.hypothesis.toLowerCase().includes(term) ||
        h.rationale.toLowerCase().includes(term) ||
        h.methodology.toLowerCase().includes(term) ||
        h.expected_impact.toLowerCase().includes(term)
      )
    }

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'novelty') {
        return b.novelty_score - a.novelty_score
      } else {
        const feasibilityOrder = { high: 3, medium: 2, low: 1 }
        return feasibilityOrder[b.feasibility] - feasibilityOrder[a.feasibility]
      }
    })

    setFilteredHypotheses(filtered)
  }, [hypotheses, filters, sortBy])

  const loadSampleHypotheses = () => {
    const sampleHypotheses: Hypothesis[] = [
      {
        hypothesis: "Combining transformer architectures with graph neural networks could improve molecular property prediction accuracy by 15-20%",
        rationale: "Both approaches handle different types of structured data effectively - transformers for sequences and GNNs for molecular graphs",
        methodology: "Develop hybrid model architecture that processes molecular SMILES strings with transformers and molecular graphs with GNNs, then fuses representations",
        required_resources: ["PyTorch", "RDKit", "molecular datasets", "GPU compute"],
        expected_impact: "Improved accuracy in drug discovery applications, faster lead compound identification",
        feasibility: "medium",
        novelty_score: 0.85
      },
      {
        hypothesis: "Multi-modal protein structure prediction using both sequence and experimental constraints could achieve sub-angstrom accuracy",
        rationale: "Current methods rely primarily on sequence data, but incorporating experimental constraints from NMR or cryo-EM could significantly improve predictions",
        methodology: "Integrate experimental distance constraints and secondary structure information into transformer-based protein folding models",
        required_resources: ["AlphaFold", "experimental structure databases", "constraint optimization algorithms"],
        expected_impact: "Revolutionary improvement in protein structure prediction for drug design and protein engineering",
        feasibility: "high",
        novelty_score: 0.92
      },
      {
        hypothesis: "Federated learning approaches could enable privacy-preserving analysis of sensitive medical datasets across institutions",
        rationale: "Many valuable medical datasets cannot be shared due to privacy concerns, but federated learning allows model training without data sharing",
        methodology: "Implement differential privacy mechanisms in federated learning frameworks for multi-institutional medical research",
        required_resources: ["federated learning frameworks", "differential privacy libraries", "institutional partnerships"],
        expected_impact: "Enable large-scale medical research while preserving patient privacy",
        feasibility: "medium",
        novelty_score: 0.78
      },
      {
        hypothesis: "Quantum-enhanced machine learning algorithms could solve NP-hard optimization problems in computational biology",
        rationale: "Quantum computers show promise for certain optimization problems that are intractable for classical computers",
        methodology: "Develop quantum approximate optimization algorithms (QAOA) for protein folding and drug discovery problems",
        required_resources: ["quantum computing platforms", "quantum algorithm expertise", "hybrid classical-quantum frameworks"],
        expected_impact: "Breakthrough solutions for previously unsolvable computational biology problems",
        feasibility: "low",
        novelty_score: 0.95
      },
      {
        hypothesis: "Automated reproducibility assessment tools could improve scientific research quality by identifying non-reproducible studies",
        rationale: "Many published studies cannot be reproduced, but manual assessment is time-consuming and subjective",
        methodology: "Develop AI systems that automatically assess code quality, data availability, and experimental design reproducibility",
        required_resources: ["code analysis tools", "statistical validation frameworks", "large corpus of scientific papers"],
        expected_impact: "Improved scientific rigor and faster identification of reliable research",
        feasibility: "high",
        novelty_score: 0.72
      }
    ]
    
    setHypotheses(sampleHypotheses)
  }

  const toggleExpanded = (index: number) => {
    const newExpanded = new Set(expandedCards)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedCards(newExpanded)
  }

  const getFeasibilityColor = (feasibility: string) => {
    switch (feasibility) {
      case 'high': return 'text-green-500 bg-green-500/10'
      case 'medium': return 'text-yellow-500 bg-yellow-500/10'
      case 'low': return 'text-red-500 bg-red-500/10'
      default: return 'text-gray-500 bg-gray-500/10'
    }
  }

  const getNoveltyStars = (score: number) => {
    const stars = Math.round(score * 5)
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${i < stars ? 'text-yellow-500 fill-current' : 'text-gray-300'}`}
      />
    ))
  }

  const exportHypotheses = () => {
    const dataStr = JSON.stringify(filteredHypotheses, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'research-hypotheses.json'
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Research Hypotheses</h1>
          <p className="text-muted-foreground">
            AI-generated research questions and experimental suggestions
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={exportHypotheses}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export Hypotheses
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { 
            label: 'Total Hypotheses', 
            value: hypotheses.length, 
            icon: Lightbulb,
            color: 'text-blue-500'
          },
          { 
            label: 'High Feasibility', 
            value: hypotheses.filter(h => h.feasibility === 'high').length, 
            icon: Target,
            color: 'text-green-500'
          },
          { 
            label: 'Avg Novelty Score', 
            value: hypotheses.length ? (hypotheses.reduce((sum, h) => sum + h.novelty_score, 0) / hypotheses.length).toFixed(2) : '0', 
            icon: TrendingUp,
            color: 'text-purple-500'
          },
          { 
            label: 'High Impact', 
            value: hypotheses.filter(h => h.expected_impact.toLowerCase().includes('breakthrough') || h.expected_impact.toLowerCase().includes('revolutionary')).length, 
            icon: Star,
            color: 'text-yellow-500'
          }
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-card border border-border rounded-lg p-4"
          >
            <div className="flex items-center gap-3">
              <stat.icon className={`w-8 h-8 ${stat.color}`} />
              <div>
                <div className="text-2xl font-bold text-foreground">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Filters and Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-card border border-border rounded-lg p-4"
      >
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-muted-foreground" />
          <h3 className="text-lg font-semibold text-foreground">Filters & Search</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Feasibility
            </label>
            <select
              value={filters.feasibility}
              onChange={(e) => setFilters(prev => ({ ...prev, feasibility: e.target.value }))}
              className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="all">All Levels</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Min Novelty Score
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={filters.minNovelty}
              onChange={(e) => setFilters(prev => ({ ...prev, minNovelty: parseFloat(e.target.value) }))}
              className="w-full"
            />
            <div className="text-xs text-muted-foreground mt-1">{filters.minNovelty.toFixed(1)}</div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Sort By
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'novelty' | 'feasibility')}
              className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="novelty">Novelty Score</option>
              <option value="feasibility">Feasibility</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Search
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                value={filters.searchTerm}
                onChange={(e) => setFilters(prev => ({ ...prev, searchTerm: e.target.value }))}
                placeholder="Search hypotheses..."
                className="w-full pl-10 pr-3 py-2 border border-border rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Hypotheses List */}
      <div className="space-y-4">
        {filteredHypotheses.map((hypothesis, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + index * 0.1 }}
            className="bg-card border border-border rounded-lg overflow-hidden"
          >
            <div className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between gap-4 mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    {hypothesis.hypothesis}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {hypothesis.rationale}
                  </p>
                </div>
                
                <div className="flex flex-col items-end gap-2">
                  <div className="flex items-center gap-1">
                    {getNoveltyStars(hypothesis.novelty_score)}
                    <span className="text-sm text-muted-foreground ml-2">
                      {hypothesis.novelty_score.toFixed(2)}
                    </span>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getFeasibilityColor(hypothesis.feasibility)}`}>
                    {hypothesis.feasibility} feasibility
                  </span>
                </div>
              </div>

              {/* Expandable Content */}
              {expandedCards.has(index) && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-4 pt-4 border-t border-border"
                >
                  <div>
                    <h4 className="font-medium text-foreground mb-2">Methodology</h4>
                    <p className="text-sm text-muted-foreground">{hypothesis.methodology}</p>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-foreground mb-2">Required Resources</h4>
                    <div className="flex flex-wrap gap-2">
                      {hypothesis.required_resources.map((resource, idx) => (
                        <span key={idx} className="bg-muted px-2 py-1 rounded text-xs">
                          {resource}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-foreground mb-2">Expected Impact</h4>
                    <p className="text-sm text-muted-foreground">{hypothesis.expected_impact}</p>
                  </div>
                </motion.div>
              )}

              {/* Toggle Button */}
              <button
                onClick={() => toggleExpanded(index)}
                className="w-full mt-4 flex items-center justify-center gap-2 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {expandedCards.has(index) ? (
                  <>
                    <ChevronUp className="w-4 h-4" />
                    Show Less
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-4 h-4" />
                    Show Details
                  </>
                )}
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      {filteredHypotheses.length === 0 && (
        <div className="text-center py-12">
          <Lightbulb className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-foreground mb-2">No Hypotheses Found</h3>
          <p className="text-muted-foreground">
            Try adjusting your filters or complete an analysis to generate hypotheses.
          </p>
        </div>
      )}
    </div>
  )
}

export default HypothesesPage
