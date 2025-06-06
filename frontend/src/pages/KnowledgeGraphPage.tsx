import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Network, Filter, Download, RefreshCw, Info } from 'lucide-react'
import KnowledgeGraphViewer from '../components/KnowledgeGraphViewer'
import { useAnalysisStore } from '../stores/analysisStore'

const KnowledgeGraphPage = () => {
  const { currentJob } = useAnalysisStore()
  const [graphData, setGraphData] = useState<any[]>([])
  const [filteredData, setFilteredData] = useState<any[]>([])
  const [filters, setFilters] = useState({
    nodeType: 'all',
    searchTerm: ''
  })
  const [stats, setStats] = useState({
    nodes: 0,
    edges: 0,
    papers: 0,
    authors: 0,
    tools: 0,
    datasets: 0
  })

  useEffect(() => {
    // Load graph data from current job or sample data
    if (currentJob?.results?.graph_data) {
      setGraphData(currentJob.results.graph_data)
    } else {
      // Load sample graph data for demo
      loadSampleGraphData()
    }
  }, [currentJob])

  useEffect(() => {
    // Apply filters
    let filtered = graphData
    
    if (filters.nodeType !== 'all') {
      filtered = filtered.filter(item => 
        item.predicate.includes(filters.nodeType) ||
        item.subject.includes(filters.nodeType) ||
        item.object.includes(filters.nodeType)
      )
    }
    
    if (filters.searchTerm) {
      const term = filters.searchTerm.toLowerCase()
      filtered = filtered.filter(item =>
        item.subject.toLowerCase().includes(term) ||
        item.predicate.toLowerCase().includes(term) ||
        item.object.toLowerCase().includes(term)
      )
    }
    
    setFilteredData(filtered)
    calculateStats(filtered)
  }, [graphData, filters])

  const loadSampleGraphData = () => {
    // Sample knowledge graph data for demo
    const sampleData = [
      {
        subject: "https://papers.org/protein-transformer",
        predicate: "https://schema.org/name",
        object: "Deep Learning for Protein Structure Prediction"
      },
      {
        subject: "https://papers.org/protein-transformer",
        predicate: "https://schema.org/author",
        object: "https://authors.org/jane-smith"
      },
      {
        subject: "https://authors.org/jane-smith",
        predicate: "https://schema.org/name",
        object: "Dr. Jane Smith"
      },
      {
        subject: "https://papers.org/protein-transformer",
        predicate: "https://scientific.org/usesTool",
        object: "https://tools.org/pytorch"
      },
      {
        subject: "https://tools.org/pytorch",
        predicate: "https://schema.org/name",
        object: "PyTorch"
      },
      {
        subject: "https://papers.org/protein-transformer",
        predicate: "https://scientific.org/usesDataset",
        object: "https://datasets.org/pdb"
      },
      {
        subject: "https://datasets.org/pdb",
        predicate: "https://schema.org/name",
        object: "Protein Data Bank"
      }
    ]
    
    setGraphData(sampleData)
  }

  const calculateStats = (data: any[]) => {
    const subjects = new Set(data.map(item => item.subject))
    const objects = new Set(data.map(item => item.object))
    const allNodes = new Set([...subjects, ...objects])
    
    const papers = Array.from(allNodes).filter(node => 
      typeof node === 'string' && node.includes('papers.org')
    ).length
    
    const authors = Array.from(allNodes).filter(node => 
      typeof node === 'string' && node.includes('authors.org')
    ).length
    
    const tools = Array.from(allNodes).filter(node => 
      typeof node === 'string' && node.includes('tools.org')
    ).length
    
    const datasets = Array.from(allNodes).filter(node => 
      typeof node === 'string' && node.includes('datasets.org')
    ).length

    setStats({
      nodes: allNodes.size,
      edges: data.length,
      papers,
      authors,
      tools,
      datasets
    })
  }

  const exportGraph = () => {
    const dataStr = JSON.stringify(filteredData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'knowledge-graph.json'
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Knowledge Graph Explorer</h1>
          <p className="text-muted-foreground">
            Interactive visualization of scientific knowledge connections
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={exportGraph}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export Graph
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        {[
          { label: 'Nodes', value: stats.nodes, color: 'text-blue-500' },
          { label: 'Edges', value: stats.edges, color: 'text-green-500' },
          { label: 'Papers', value: stats.papers, color: 'text-purple-500' },
          { label: 'Authors', value: stats.authors, color: 'text-yellow-500' },
          { label: 'Tools', value: stats.tools, color: 'text-red-500' },
          { label: 'Datasets', value: stats.datasets, color: 'text-indigo-500' }
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-card border border-border rounded-lg p-4 text-center"
          >
            <div className={`text-2xl font-bold ${stat.color} mb-1`}>
              {stat.value}
            </div>
            <div className="text-sm text-muted-foreground">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-card border border-border rounded-lg p-4"
      >
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-muted-foreground" />
          <h3 className="text-lg font-semibold text-foreground">Filters</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Node Type
            </label>
            <select
              value={filters.nodeType}
              onChange={(e) => setFilters(prev => ({ ...prev, nodeType: e.target.value }))}
              className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="all">All Types</option>
              <option value="papers">Papers</option>
              <option value="authors">Authors</option>
              <option value="tools">Tools</option>
              <option value="datasets">Datasets</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Search
            </label>
            <input
              type="text"
              value={filters.searchTerm}
              onChange={(e) => setFilters(prev => ({ ...prev, searchTerm: e.target.value }))}
              placeholder="Search nodes and relationships..."
              className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
        </div>
      </motion.div>

      {/* Graph Viewer */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-card border border-border rounded-lg overflow-hidden"
        style={{ height: '600px' }}
      >
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <Network className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold text-foreground">Graph Visualization</h3>
            <div className="ml-auto flex items-center gap-2 text-sm text-muted-foreground">
              <Info className="w-4 h-4" />
              <span>Click and drag to explore • Zoom with mouse wheel</span>
            </div>
          </div>
        </div>
        
        <div className="h-full">
          <KnowledgeGraphViewer data={filteredData} />
        </div>
      </motion.div>

      {/* Graph Data Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-card border border-border rounded-lg overflow-hidden"
      >
        <div className="p-4 border-b border-border">
          <h3 className="text-lg font-semibold text-foreground">Graph Triples</h3>
          <p className="text-sm text-muted-foreground">
            Raw RDF triples showing subject-predicate-object relationships
          </p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-foreground">Subject</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-foreground">Predicate</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-foreground">Object</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredData.slice(0, 20).map((triple, index) => (
                <tr key={index} className="hover:bg-accent/50">
                  <td className="px-4 py-3 text-sm text-foreground truncate max-w-xs">
                    {triple.subject}
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground truncate max-w-xs">
                    {triple.predicate}
                  </td>
                  <td className="px-4 py-3 text-sm text-foreground truncate max-w-xs">
                    {triple.object}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {filteredData.length > 20 && (
            <div className="p-4 text-center text-sm text-muted-foreground">
              Showing 20 of {filteredData.length} triples. Use filters to narrow results.
            </div>
          )}
        </div>
      </motion.div>
    </div>
  )
}

export default KnowledgeGraphPage
