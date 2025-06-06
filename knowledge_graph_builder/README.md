# 🔗 Knowledge Graph Builder Plugin

An Eliza-compatible plugin that builds semantic knowledge graphs from scientific metadata and reproducibility reports using RDF standards.

## 🎯 Purpose

Converts structured outputs from manuscript extraction and reproducibility assessment into semantic knowledge graphs for advanced analysis and hypothesis generation.

## ✨ Features

- **RDF Triple Generation**: Creates semantic triples from structured data
- **Multiple Input Sources**: Processes metadata and reproducibility reports
- **Format Support**: Outputs in Turtle, JSON-LD, and XML formats
- **Semantic Relationships**: Maps scientific concepts and relationships
- **Graph Statistics**: Provides detailed statistics about generated graphs
- **Standards Compliance**: Uses schema.org and scientific ontologies

## 📥 Input

- Metadata JSON file (from manuscript extractor)
- Reproducibility report JSON file
- Optional: Output format specification

## 📤 Output

### RDF Graph (Turtle format)
```turtle
@prefix schema: <https://schema.org/> .
@prefix scientific: <https://scientific.org/> .

<https://papers.org/paper1> a schema:ScholarlyArticle ;
    schema:name "Deep Learning for Protein Structure" ;
    schema:author <https://authors.org/jane-smith> ;
    scientific:usesTool <https://tools.org/pytorch> .
```

### Statistics
```json
{
  "total_triples": 156,
  "total_papers": 1,
  "total_authors": 3,
  "total_tools": 5,
  "total_datasets": 2
}
```

## 🚀 Usage

### Command Line
```bash
python main.py --metadata metadata.json --reproducibility report.json --output graph.ttl --format turtle
```

### Python API
```python
from knowledge_graph_builder.main import KnowledgeGraphBuilder

builder = KnowledgeGraphBuilder()
results = builder.load_and_process_files("metadata.json", "report.json")
builder.save_graph("output.ttl", "turtle")
```

## 🔧 Dependencies

- rdflib>=6.0.0
- json
- logging
- pathlib
- urllib.parse

## 📋 Requirements

- Python 3.8+
- Input data from manuscript extractor or reproducibility assistant

## 🏷️ Tags

- knowledge-graphs
- rdf
- semantic-web
- data-integration
