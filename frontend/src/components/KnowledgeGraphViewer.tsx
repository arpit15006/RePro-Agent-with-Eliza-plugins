import { useEffect, useRef } from 'react'
import cytoscape from 'cytoscape'
import coseBilkent from 'cytoscape-cose-bilkent'

// Register the layout
cytoscape.use(coseBilkent)

interface KnowledgeGraphViewerProps {
  data: Array<{
    subject: string
    predicate: string
    object: string
  }>
}

const KnowledgeGraphViewer = ({ data }: KnowledgeGraphViewerProps) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const cyRef = useRef<cytoscape.Core | null>(null)

  useEffect(() => {
    if (!containerRef.current || !data.length) return

    // Clean up previous instance
    if (cyRef.current) {
      cyRef.current.destroy()
    }

    // Process data into nodes and edges
    const nodes = new Map()
    const edges: any[] = []

    data.forEach((triple, index) => {
      const { subject, predicate, object } = triple

      // Add subject node
      if (!nodes.has(subject)) {
        nodes.set(subject, {
          data: {
            id: subject,
            label: getNodeLabel(subject),
            type: getNodeType(subject)
          }
        })
      }

      // Add object node (if it's a URI)
      if (object.startsWith('http') && !nodes.has(object)) {
        nodes.set(object, {
          data: {
            id: object,
            label: getNodeLabel(object),
            type: getNodeType(object)
          }
        })
      }

      // Add edge (only for URI objects)
      if (object.startsWith('http')) {
        edges.push({
          data: {
            id: `edge-${index}`,
            source: subject,
            target: object,
            label: getPredicateLabel(predicate),
            predicate: predicate
          }
        })
      }
    })

    // Initialize Cytoscape
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: [
        ...Array.from(nodes.values()),
        ...edges
      ],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': (ele: any) => getNodeColor(ele.data('type')),
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            'font-weight': 'bold',
            'color': '#ffffff',
            'text-outline-width': 2,
            'text-outline-color': '#000000',
            'width': 60,
            'height': 60,
            'border-width': 2,
            'border-color': '#ffffff',
            'text-wrap': 'wrap',
            'text-max-width': '80px'
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'border-color': '#3b82f6'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#64748b',
            'target-arrow-color': '#64748b',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'color': '#1e293b',
            'text-background-color': '#ffffff',
            'text-background-opacity': 0.8,
            'text-background-padding': '2px',
            'edge-text-rotation': 'autorotate'
          }
        },
        {
          selector: 'edge:selected',
          style: {
            'line-color': '#3b82f6',
            'target-arrow-color': '#3b82f6',
            'width': 3
          }
        }
      ],
      layout: {
        name: 'cose-bilkent',
        animate: true,
        animationDuration: 1000,
        fit: true,
        padding: 50,
        nodeRepulsion: 4500,
        idealEdgeLength: 100,
        edgeElasticity: 0.45,
        nestingFactor: 0.1,
        gravity: 0.25,
        numIter: 2500,
        tile: true,
        tilingPaddingVertical: 10,
        tilingPaddingHorizontal: 10
      },
      minZoom: 0.1,
      maxZoom: 3,
      wheelSensitivity: 0.2
    })

    // Add event listeners
    cyRef.current.on('tap', 'node', (evt) => {
      const node = evt.target
      console.log('Node clicked:', node.data())
      
      // Highlight connected nodes
      const connectedEdges = node.connectedEdges()
      const connectedNodes = connectedEdges.connectedNodes()
      
      cyRef.current?.elements().removeClass('highlighted')
      node.addClass('highlighted')
      connectedNodes.addClass('highlighted')
      connectedEdges.addClass('highlighted')
    })

    cyRef.current.on('tap', 'edge', (evt) => {
      const edge = evt.target
      console.log('Edge clicked:', edge.data())
    })

    cyRef.current.on('tap', (evt) => {
      if (evt.target === cyRef.current) {
        // Clicked on background, remove highlights
        cyRef.current?.elements().removeClass('highlighted')
      }
    })

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy()
        cyRef.current = null
      }
    }
  }, [data])

  const getNodeLabel = (uri: string): string => {
    // Extract meaningful label from URI
    const parts = uri.split('/')
    const lastPart = parts[parts.length - 1]
    
    // Convert kebab-case or snake_case to readable format
    return lastPart
      .replace(/[-_]/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .trim()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
      .substring(0, 20) // Limit length
  }

  const getPredicateLabel = (predicate: string): string => {
    // Extract meaningful label from predicate URI
    const parts = predicate.split('/')
    const lastPart = parts[parts.length - 1]
    
    return lastPart
      .replace(/([A-Z])/g, ' $1')
      .trim()
      .toLowerCase()
  }

  const getNodeType = (uri: string): string => {
    if (uri.includes('papers.org')) return 'paper'
    if (uri.includes('authors.org')) return 'author'
    if (uri.includes('tools.org')) return 'tool'
    if (uri.includes('datasets.org')) return 'dataset'
    if (uri.includes('organizations.org')) return 'organization'
    if (uri.includes('keywords.org')) return 'keyword'
    return 'unknown'
  }

  const getNodeColor = (type: string): string => {
    const colors = {
      paper: '#3b82f6',      // blue
      author: '#10b981',     // green
      tool: '#f59e0b',       // yellow
      dataset: '#8b5cf6',    // purple
      organization: '#ef4444', // red
      keyword: '#06b6d4',    // cyan
      unknown: '#6b7280'     // gray
    }
    return colors[type as keyof typeof colors] || colors.unknown
  }

  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <div className="text-center">
          <div className="text-4xl mb-4">🕸️</div>
          <p>No graph data available</p>
          <p className="text-sm mt-2">Complete an analysis to see the knowledge graph</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative w-full h-full">
      <div ref={containerRef} className="w-full h-full cytoscape-container" />
      
      {/* Legend */}
      <div className="absolute top-4 right-4 bg-background/90 backdrop-blur-sm border border-border rounded-lg p-3 text-xs">
        <h4 className="font-semibold mb-2">Node Types</h4>
        <div className="space-y-1">
          {[
            { type: 'paper', color: '#3b82f6', label: 'Papers' },
            { type: 'author', color: '#10b981', label: 'Authors' },
            { type: 'tool', color: '#f59e0b', label: 'Tools' },
            { type: 'dataset', color: '#8b5cf6', label: 'Datasets' },
            { type: 'organization', color: '#ef4444', label: 'Organizations' },
            { type: 'keyword', color: '#06b6d4', label: 'Keywords' }
          ].map(({ type, color, label }) => (
            <div key={type} className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: color }}
              />
              <span>{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Controls */}
      <div className="absolute bottom-4 left-4 bg-background/90 backdrop-blur-sm border border-border rounded-lg p-2">
        <div className="flex gap-2">
          <button
            onClick={() => cyRef.current?.fit()}
            className="px-3 py-1 bg-primary text-primary-foreground rounded text-xs hover:bg-primary/90 transition-colors"
          >
            Fit
          </button>
          <button
            onClick={() => cyRef.current?.center()}
            className="px-3 py-1 bg-secondary text-secondary-foreground rounded text-xs hover:bg-secondary/90 transition-colors"
          >
            Center
          </button>
        </div>
      </div>
    </div>
  )
}

export default KnowledgeGraphViewer
