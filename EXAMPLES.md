# 📚 RePRO-Agent Examples

This document provides comprehensive examples of how to use the RePRO-Agent pipeline for scientific reproducibility assessment and hypothesis generation.

## 🚀 Quick Start Examples

### Example 1: Complete Pipeline with Paper and Repository

```bash
# Process a scientific paper and its associated code repository
python3 pipeline.py \
  --paper "papers/deep_learning_proteins.pdf" \
  --repo "https://github.com/deepmind/alphafold" \
  --num-hypotheses 5 \
  --focus-area "protein structure prediction"
```

### Example 2: Paper Analysis Only

```bash
# Extract metadata from a paper without repository assessment
python3 pipeline.py \
  --paper "papers/machine_learning_review.pdf" \
  --num-hypotheses 3 \
  --focus-area "machine learning"
```

### Example 3: Repository Assessment Only

```bash
# Assess reproducibility of a repository without paper metadata
python3 pipeline.py \
  --repo "https://github.com/pytorch/pytorch" \
  --num-hypotheses 5
```

## 🔧 Individual Plugin Examples

### Manuscript Extractor

```bash
# Extract metadata from PDF
python3 manuscript-extractor/main.py \
  --input "papers/nature_paper.pdf" \
  --output "metadata.json" \
  --model "gpt-4"

# Extract from Markdown
python3 manuscript-extractor/main.py \
  --input "papers/arxiv_paper.md" \
  --output "metadata.json" \
  --model "claude-3-sonnet"

# Use with custom API key
python3 manuscript-extractor/main.py \
  --input "papers/paper.pdf" \
  --api-key "your-api-key-here"
```

### Reproducibility Assistant

```bash
# Assess GitHub repository
python3 reproducibility-assistant/main.py \
  --repo "https://github.com/scikit-learn/scikit-learn" \
  --output "assessment.json"

# Custom timeout for long-running tests
python3 reproducibility-assistant/main.py \
  --repo "https://github.com/tensorflow/tensorflow" \
  --timeout 600 \
  --output "tf_assessment.json"

# Assess private repository (requires authentication)
python3 reproducibility-assistant/main.py \
  --repo "https://github.com/private/repo" \
  --output "private_assessment.json"
```

### Knowledge Graph Builder

```bash
# Build graph from metadata only
python3 knowledge-graph-builder/main.py \
  --metadata "metadata.json" \
  --output "graph.ttl"

# Build graph from both sources
python3 knowledge-graph-builder/main.py \
  --metadata "metadata.json" \
  --reproducibility "assessment.json" \
  --output "complete_graph.ttl"

# Export in different formats
python3 knowledge-graph-builder/main.py \
  --metadata "metadata.json" \
  --format "jsonld" \
  --output "graph.jsonld"
```

### Hypothesis Generator

```bash
# Generate hypotheses from knowledge graph
python3 hypothesis-generator/main.py \
  --graph "graph.ttl" \
  --num-hypotheses 10 \
  --output "hypotheses.json"

# Focus on specific research area
python3 hypothesis-generator/main.py \
  --graph "graph.ttl" \
  --focus-area "computational biology" \
  --num-hypotheses 5

# Use different LLM model
python3 hypothesis-generator/main.py \
  --graph "graph.ttl" \
  --model "claude-3-sonnet" \
  --num-hypotheses 7
```

## 🧬 Scientific Domain Examples

### Bioinformatics Research

```bash
# Process a bioinformatics paper
python3 pipeline.py \
  --paper "papers/genomics_analysis.pdf" \
  --repo "https://github.com/bioinformatics/genomics-toolkit" \
  --focus-area "genomics" \
  --num-hypotheses 8
```

### Machine Learning Research

```bash
# Analyze ML paper and implementation
python3 pipeline.py \
  --paper "papers/transformer_architecture.pdf" \
  --repo "https://github.com/huggingface/transformers" \
  --focus-area "natural language processing" \
  --num-hypotheses 6
```

### Climate Science

```bash
# Process climate modeling research
python3 pipeline.py \
  --paper "papers/climate_model.pdf" \
  --repo "https://github.com/climate/modeling-framework" \
  --focus-area "climate modeling" \
  --num-hypotheses 5
```

## 📊 Output Examples

### Sample Metadata Output

```json
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "title": "Attention Is All You Need",
  "abstract": "The dominant sequence transduction models...",
  "author": [
    {
      "name": "Ashish Vaswani",
      "affiliation": "Google Brain"
    }
  ],
  "tools": ["TensorFlow", "Python", "CUDA"],
  "datasets": [
    {
      "name": "WMT 2014 English-German",
      "url": "http://www.statmt.org/wmt14/"
    }
  ]
}
```

### Sample Reproducibility Report

```json
{
  "repository_url": "https://github.com/tensorflow/tensor2tensor",
  "reproducibility_score": 0.92,
  "repository_analysis": {
    "has_readme": true,
    "has_requirements": true,
    "has_dockerfile": true,
    "main_scripts": ["t2t_trainer.py"]
  },
  "execution_results": {
    "success_rate": 1.0
  },
  "recommendations": [
    "Excellent reproducibility practices"
  ]
}
```

### Sample Generated Hypotheses

```json
{
  "generated_hypotheses": [
    {
      "hypothesis": "Combining transformer architectures with graph neural networks could improve molecular property prediction",
      "rationale": "Both approaches handle different types of structured data effectively",
      "methodology": "Develop hybrid model architecture and benchmark on molecular datasets",
      "required_resources": ["PyTorch", "RDKit", "molecular datasets"],
      "expected_impact": "Improved accuracy in drug discovery applications",
      "feasibility": "medium",
      "novelty_score": 0.85
    }
  ]
}
```

## 🔄 Batch Processing Examples

### Process Multiple Papers

```bash
#!/bin/bash
# Process multiple papers in a directory

for paper in papers/*.pdf; do
    echo "Processing $paper..."
    python3 pipeline.py \
      --paper "$paper" \
      --output-dir "output/$(basename "$paper" .pdf)" \
      --num-hypotheses 3
done
```

### Repository Assessment Batch

```bash
#!/bin/bash
# Assess multiple repositories

repos=(
    "https://github.com/pytorch/pytorch"
    "https://github.com/tensorflow/tensorflow"
    "https://github.com/scikit-learn/scikit-learn"
)

for repo in "${repos[@]}"; do
    repo_name=$(basename "$repo")
    echo "Assessing $repo_name..."
    python3 reproducibility-assistant/main.py \
      --repo "$repo" \
      --output "assessments/${repo_name}_assessment.json"
done
```

## 🐳 Docker Examples

### Run in Docker Container

```bash
# Build Docker image
docker build -t repro-agent .

# Run complete pipeline
docker run -v $(pwd)/papers:/papers -v $(pwd)/output:/output \
  repro-agent \
  --paper /papers/sample.pdf \
  --repo https://github.com/example/repo \
  --output-dir /output
```

## 🔍 Advanced SPARQL Queries

Once you have a knowledge graph, you can query it with SPARQL:

```sparql
# Find papers with high reproducibility scores
PREFIX repro: <https://reproducibility.org/>
PREFIX schema: <https://schema.org/>

SELECT ?paper ?title ?score WHERE {
  ?paper a schema:ScholarlyArticle ;
         schema:name ?title ;
         scientific:hasCodeRepository ?repo .
  ?assessment repro:assessesRepository ?repo ;
              repro:reproducibilityScore ?score .
  FILTER(?score > 0.8)
}
ORDER BY DESC(?score)
```

```sparql
# Find tool combinations that haven't been explored
PREFIX scientific: <https://scientific.org/>
PREFIX schema: <https://schema.org/>

SELECT ?tool1 ?tool2 WHERE {
  ?paper1 scientific:usesTool ?t1 .
  ?paper2 scientific:usesTool ?t2 .
  ?t1 schema:name ?tool1 .
  ?t2 schema:name ?tool2 .
  FILTER(?tool1 != ?tool2)
  FILTER NOT EXISTS {
    ?paper3 scientific:usesTool ?t1 ;
            scientific:usesTool ?t2 .
  }
}
```

## 🚨 Troubleshooting Examples

### Common Issues and Solutions

```bash
# Issue: API rate limits
# Solution: Add delays between requests
python3 pipeline.py --paper paper.pdf --timeout 600

# Issue: Large repositories timeout
# Solution: Increase timeout
python3 reproducibility-assistant/main.py --repo large-repo --timeout 1200

# Issue: Memory issues with large graphs
# Solution: Process in smaller batches
python3 knowledge-graph-builder/main.py --metadata small_batch.json
```

## 📈 Performance Optimization

### Parallel Processing

```python
# Example: Process multiple papers in parallel
import concurrent.futures
from pipeline import ReproAgentPipeline

def process_paper(paper_path):
    pipeline = ReproAgentPipeline(work_dir=f"output/{paper_path.stem}")
    return pipeline.run_complete_pipeline(paper_path=str(paper_path))

papers = list(Path("papers").glob("*.pdf"))

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_paper, papers))
```

## 🎯 Integration Examples

### Jupyter Notebook Integration

```python
# Use in Jupyter notebooks
from pipeline import ReproAgentPipeline
import json

# Initialize pipeline
pipeline = ReproAgentPipeline()

# Process data
results = pipeline.run_complete_pipeline(
    paper_path="research_paper.pdf",
    repo_url="https://github.com/research/code"
)

# Display results
with open(results["hypotheses_file"]) as f:
    hypotheses = json.load(f)
    
for i, hyp in enumerate(hypotheses["generated_hypotheses"]):
    print(f"{i+1}. {hyp['hypothesis']}")
    print(f"   Feasibility: {hyp['feasibility']}")
    print(f"   Novelty: {hyp['novelty_score']}")
    print()
```

## 🔗 API Integration Examples

### REST API Wrapper

```python
# Example Flask API wrapper
from flask import Flask, request, jsonify
from pipeline import ReproAgentPipeline

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_research():
    data = request.json
    pipeline = ReproAgentPipeline()
    
    results = pipeline.run_complete_pipeline(
        paper_path=data.get('paper_path'),
        repo_url=data.get('repo_url'),
        num_hypotheses=data.get('num_hypotheses', 5)
    )
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
```

This comprehensive example collection should help users understand how to effectively use the RePRO-Agent pipeline for their scientific research needs!
