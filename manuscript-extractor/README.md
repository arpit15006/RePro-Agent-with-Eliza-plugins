# 📜 Manuscript Extractor Plugin

Extracts structured metadata from scientific papers in PDF or Markdown format using LLM-powered analysis.

## Features

- **Multi-format Support**: Handles PDF and Markdown files
- **LLM Integration**: Uses OpenAI GPT or Anthropic Claude for intelligent extraction
- **Fallback Processing**: Rule-based extraction when no API key is available
- **JSON-LD Output**: Structured metadata in standard format
- **Eliza Compatible**: Follows Eliza plugin specification

## Installation

```bash
cd manuscript-extractor
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

Or create a `.env` file:
```
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

## Usage

### Command Line

```bash
# Basic usage
python main.py --input paper.pdf --output metadata.json

# Specify model
python main.py --input paper.pdf --output metadata.json --model gpt-4

# Use Anthropic Claude
python main.py --input paper.md --output metadata.json --model claude-3-sonnet

# Provide API key directly
python main.py --input paper.pdf --api-key your-key-here
```

### Python API

```python
from main import ManuscriptExtractor

# Initialize extractor
extractor = ManuscriptExtractor(api_key="your-key", model="gpt-4")

# Extract metadata
metadata = extractor.extract_metadata("paper.pdf")

# Save to file
import json
with open("metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
```

## Output Format

The plugin outputs JSON-LD structured data:

```json
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "title": "Paper Title",
  "abstract": "Paper abstract...",
  "author": [
    {
      "name": "Author Name",
      "affiliation": "Institution"
    }
  ],
  "datePublished": "2024-01-01",
  "keywords": ["keyword1", "keyword2"],
  "methodology": "Description of methods...",
  "tools": ["Python", "TensorFlow", "scikit-learn"],
  "datasets": [
    {
      "name": "Dataset Name",
      "url": "https://example.com/dataset"
    }
  ],
  "results": "Summary of findings...",
  "conclusions": "Main conclusions...",
  "citations": 42,
  "doi": "10.1000/182",
  "url": "https://example.com/paper",
  "source_file": "paper.pdf",
  "extraction_timestamp": "2024-01-01T12:00:00"
}
```

## Supported Models

- **OpenAI**: gpt-4, gpt-3.5-turbo
- **Anthropic**: claude-3-sonnet, claude-3-haiku

## Error Handling

- Falls back to rule-based extraction if LLM API fails
- Handles various PDF formats and encodings
- Provides detailed error messages and logging

## Integration with Other Plugins

The JSON-LD output is designed to be consumed by:
- Knowledge Graph Builder Plugin
- Reproducibility Assistant Plugin
- Hypothesis Generator Plugin

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see [LICENSE](../LICENSE) file for details.
