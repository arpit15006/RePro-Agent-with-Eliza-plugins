# 🔗 Knowledge Graph Builder Plugin

Builds RDF knowledge graphs from scientific metadata and reproducibility assessments, creating structured semantic representations of research data.

## Features

- **RDF Graph Construction**: Converts JSON-LD metadata to RDF triples
- **Multiple Input Sources**: Processes manuscript metadata and reproducibility assessments
- **Semantic Relationships**: Creates meaningful connections between papers, authors, tools, and datasets
- **Multiple Output Formats**: Supports Turtle, N-Triples, RDF/XML, and JSON-LD
- **SPARQL Ready**: Compatible with SPARQL query engines
- **Eliza Compatible**: Follows Eliza plugin specification

## Installation

```bash
cd knowledge-graph-builder
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Build graph from metadata only
python main.py --metadata paper_metadata.json --output graph.ttl

# Build graph from reproducibility assessment only
python main.py --reproducibility repo_assessment.json --output graph.ttl

# Build graph from both sources
python main.py --metadata paper_metadata.json --reproducibility repo_assessment.json --output graph.ttl

# Specify output format
python main.py --metadata paper_metadata.json --format jsonld --output graph.jsonld
```

### Python API

```python
from main import KnowledgeGraphBuilder

# Initialize builder
builder = KnowledgeGraphBuilder()

# Process files
results = builder.load_and_process_files(
    metadata_file="paper_metadata.json",
    reproducibility_file="repo_assessment.json"
)

# Save graph
builder.save_graph("knowledge_graph.ttl", format="turtle")

# Get statistics
stats = builder.get_statistics()
print(f"Built graph with {stats['total_triples']} triples")
```

## RDF Schema

The knowledge graph uses several ontologies and namespaces:

### Core Namespaces
- **schema**: https://schema.org/ (Schema.org vocabulary)
- **repro**: https://reproducibility.org/ (Custom reproducibility vocabulary)
- **scientific**: https://scientific.org/ (Custom scientific vocabulary)
- **dcterms**: Dublin Core Terms
- **foaf**: Friend of a Friend

### Key Classes

```turtle
# Papers
schema:ScholarlyArticle
  schema:name "Paper Title"
  schema:abstract "Abstract text"
  schema:author <author_uri>
  scientific:usesTool <tool_uri>
  scientific:usesDataset <dataset_uri>

# Authors
schema:Person
  foaf:name "Author Name"
  schema:affiliation <organization_uri>

# Tools
scientific:SoftwareTool
  schema:name "Tool Name"
  schema:url <tool_url>

# Datasets
schema:Dataset
  schema:name "Dataset Name"
  schema:url <dataset_url>

# Reproducibility Assessments
repro:ReproducibilityAssessment
  repro:reproducibilityScore "0.85"^^xsd:float
  repro:assessesRepository <repo_uri>
  repro:hasRecommendation <recommendation_uri>
```

## Example Output

```turtle
@prefix schema: <https://schema.org/> .
@prefix repro: <https://reproducibility.org/> .
@prefix scientific: <https://scientific.org/> .

<https://doi.org/10.1000/182> a schema:ScholarlyArticle ;
    schema:name "Deep Learning for Protein Structure Prediction" ;
    schema:abstract "This paper presents a novel approach..." ;
    schema:author <https://authors.org/John_Doe> ;
    scientific:usesTool <https://tools.org/TensorFlow> ;
    scientific:usesDataset <https://datasets.org/PDB> .

<https://authors.org/John_Doe> a schema:Person ;
    foaf:name "John Doe" ;
    schema:affiliation <https://organizations.org/MIT> .

<https://assessments.org/assessment_12345> a repro:ReproducibilityAssessment ;
    repro:reproducibilityScore "0.85"^^xsd:float ;
    repro:assessesRepository <https://github.com/user/repo> .
```

## SPARQL Queries

Once built, you can query the knowledge graph with SPARQL:

```sparql
# Find all papers by an author
SELECT ?paper ?title WHERE {
  ?paper a schema:ScholarlyArticle ;
         schema:author ?author ;
         schema:name ?title .
  ?author foaf:name "John Doe" .
}

# Find highly reproducible papers
SELECT ?paper ?title ?score WHERE {
  ?paper a schema:ScholarlyArticle ;
         schema:name ?title ;
         scientific:hasCodeRepository ?repo .
  ?assessment repro:assessesRepository ?repo ;
              repro:reproducibilityScore ?score .
  FILTER(?score > 0.8)
}

# Find papers using specific tools
SELECT ?paper ?title ?tool WHERE {
  ?paper a schema:ScholarlyArticle ;
         schema:name ?title ;
         scientific:usesTool ?toolUri .
  ?toolUri schema:name ?tool .
  FILTER(CONTAINS(LCASE(?tool), "tensorflow"))
}
```

## Integration with Other Plugins

This plugin serves as the central data hub:

### Input Sources
- **Manuscript Extractor**: Provides paper metadata in JSON-LD format
- **Reproducibility Assistant**: Provides assessment reports in JSON format

### Output Consumers
- **Hypothesis Generator**: Queries the graph for research insights
- **SPARQL Endpoints**: For advanced querying and analysis
- **Visualization Tools**: For graph exploration

## Advanced Features

### Custom Vocabularies

The plugin defines custom vocabularies for scientific concepts:

```python
# Add custom properties
SCIENTIFIC.usesMethodology
SCIENTIFIC.hasResults
SCIENTIFIC.hasConclusions
REPRO.reproducibilityScore
REPRO.executionSuccessRate
```

### Graph Statistics

```python
stats = builder.get_statistics()
# Returns:
# {
#   "total_triples": 1250,
#   "papers": 10,
#   "authors": 25,
#   "tools": 15,
#   "datasets": 8,
#   "assessments": 10
# }
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see [LICENSE](../LICENSE) file for details.
