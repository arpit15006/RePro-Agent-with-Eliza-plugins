# 🧬 Hypothesis Generator Plugin

Generates novel research hypotheses using knowledge graph analysis and LLM reasoning, identifying research opportunities and suggesting testable scientific questions.

## Features

- **Graph Pattern Analysis**: Identifies trends, gaps, and opportunities in research data
- **LLM-Powered Generation**: Uses GPT or Claude for intelligent hypothesis creation
- **Network Analysis**: Leverages NetworkX for graph connectivity insights
- **Research Opportunity Detection**: Finds underutilized tools, datasets, and combinations
- **Feasibility Assessment**: Evaluates hypothesis practicality and novelty
- **Comprehensive Reporting**: Provides detailed analysis and recommendations
- **Eliza Compatible**: Follows Eliza plugin specification

## Installation

```bash
cd hypothesis-generator
pip install -r requirements.txt
```

## Configuration

Set your API key as an environment variable:

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic Claude
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## Usage

### Command Line

```bash
# Basic hypothesis generation
python main.py --graph knowledge_graph.ttl

# Generate more hypotheses
python main.py --graph knowledge_graph.ttl --num-hypotheses 10

# Focus on specific research area
python main.py --graph knowledge_graph.ttl --focus-area "machine learning"

# Use different model
python main.py --graph knowledge_graph.ttl --model claude-3-sonnet

# Custom output file
python main.py --graph knowledge_graph.ttl --output research_hypotheses.json
```

### Python API

```python
from main import HypothesisGenerator

# Initialize generator
generator = HypothesisGenerator(api_key="your-key", model="gpt-4")

# Generate comprehensive report
report = generator.generate_research_report(
    graph_file="knowledge_graph.ttl",
    num_hypotheses=5,
    focus_area="computational biology"
)

# Access hypotheses
for hypothesis in report['generated_hypotheses']:
    print(f"Hypothesis: {hypothesis['hypothesis']}")
    print(f"Feasibility: {hypothesis['feasibility']}")
    print(f"Novelty: {hypothesis['novelty_score']}")
```

## Analysis Methods

### Graph Pattern Analysis
- **Entity Counting**: Papers, authors, tools, datasets
- **Relationship Mapping**: Usage patterns and connections
- **Centrality Analysis**: Highly connected entities
- **Gap Identification**: Underutilized resources

### Research Opportunity Detection
- **Tool Combinations**: Unused tool pairings
- **Dataset Reuse**: Underutilized datasets
- **Reproducibility Gaps**: Low-scoring repositories
- **Cross-disciplinary Potential**: Bridge different fields

### Hypothesis Generation Strategies
- **Combinatorial**: Novel tool/dataset combinations
- **Methodological**: Improved research practices
- **Exploratory**: Investigate underexplored areas
- **Validation**: Test existing assumptions

## Output Format

```json
{
  "generation_timestamp": "2024-01-01T12:00:00",
  "source_graph": "knowledge_graph.ttl",
  "focus_area": "machine learning",
  "graph_analysis": {
    "total_triples": 1250,
    "entity_counts": {
      "https://schema.org/ScholarlyArticle": 25,
      "https://schema.org/Person": 50,
      "https://scientific.org/SoftwareTool": 30
    },
    "popular_tools": {
      "TensorFlow": 8,
      "PyTorch": 6,
      "scikit-learn": 5
    },
    "avg_reproducibility_score": 0.72
  },
  "research_opportunities": [
    {
      "type": "tool_combination",
      "description": "Explore combining TensorFlow with PyTorch",
      "rationale": "These popular tools haven't been used together"
    }
  ],
  "generated_hypotheses": [
    {
      "hypothesis": "Combining TensorFlow and PyTorch in a unified framework will improve model development efficiency",
      "rationale": "Both frameworks have complementary strengths that could be leveraged together",
      "methodology": "Develop interoperability layer between frameworks and benchmark performance",
      "required_resources": ["TensorFlow", "PyTorch", "benchmark datasets"],
      "expected_impact": "Reduced development time and improved model performance",
      "feasibility": "medium",
      "novelty_score": 0.8
    }
  ],
  "summary": {
    "total_hypotheses": 5,
    "avg_novelty_score": 0.75,
    "feasibility_distribution": {
      "high": 2,
      "medium": 2,
      "low": 1
    }
  }
}
```

## Hypothesis Categories

### 1. Tool Integration Hypotheses
- Combining underutilized tool pairs
- Cross-platform compatibility studies
- Workflow optimization opportunities

### 2. Dataset Exploration Hypotheses
- Applying new methods to existing datasets
- Cross-dataset validation studies
- Meta-analysis opportunities

### 3. Reproducibility Improvement Hypotheses
- Automated validation frameworks
- Containerization best practices
- Documentation standardization

### 4. Methodological Innovation Hypotheses
- Novel algorithmic approaches
- Hybrid methodology development
- Performance optimization strategies

## SPARQL Integration

The plugin uses SPARQL-like queries internally to analyze the knowledge graph:

```python
# Example internal queries
popular_tools = """
SELECT ?tool (COUNT(?paper) as ?usage_count) WHERE {
  ?paper scientific:usesTool ?tool_uri .
  ?tool_uri schema:name ?tool .
} GROUP BY ?tool ORDER BY DESC(?usage_count)
"""

underused_datasets = """
SELECT ?dataset WHERE {
  ?paper scientific:usesDataset ?dataset_uri .
  ?dataset_uri schema:name ?dataset .
} GROUP BY ?dataset HAVING (COUNT(?paper) = 1)
"""
```

## Integration with Other Plugins

### Input Sources
- **Knowledge Graph Builder**: Provides RDF graph with research metadata
- **Manuscript Extractor**: Contributes paper metadata
- **Reproducibility Assistant**: Provides reproducibility scores

### Workflow Integration
```bash
# Complete pipeline example
python ../manuscript-extractor/main.py --input paper.pdf --output metadata.json
python ../reproducibility-assistant/main.py --repo https://github.com/user/repo --output assessment.json
python ../knowledge-graph-builder/main.py --metadata metadata.json --reproducibility assessment.json --output graph.ttl
python main.py --graph graph.ttl --output hypotheses.json
```

## Advanced Features

### Custom Focus Areas
- Specify research domains for targeted hypothesis generation
- Filter opportunities by field or methodology
- Generate domain-specific insights

### Novelty Scoring
- Assess uniqueness of proposed hypotheses
- Compare against existing research patterns
- Rank hypotheses by innovation potential

### Feasibility Assessment
- Evaluate resource requirements
- Assess technical complexity
- Consider timeline and expertise needs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see [LICENSE](../LICENSE) file for details.
