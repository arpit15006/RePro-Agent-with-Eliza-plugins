# 📜 Manuscript Extractor Plugin

An Eliza-compatible plugin that extracts structured metadata from scientific papers in PDF or Markdown format.

## 🎯 Purpose

Converts unstructured research papers into structured knowledge for use in knowledge graphs and scientific analysis pipelines.

## ✨ Features

- **PDF Processing**: Extracts text from PDF files using PyPDF2
- **Markdown Support**: Processes Markdown-formatted papers
- **AI-Powered Extraction**: Uses LLMs (Gemini) for intelligent metadata extraction
- **Structured Output**: Returns JSON-formatted metadata
- **Comprehensive Analysis**: Extracts title, abstract, authors, methods, results, conclusions

## 📥 Input

- Scientific papers (PDF or Markdown)
- Optional: API key for enhanced AI processing
- Optional: Model selection (default: gemini-pro)

## 📤 Output

```json
{
  "title": "Paper title",
  "abstract": "Paper abstract",
  "authors": ["Author 1", "Author 2"],
  "keywords": ["keyword1", "keyword2"],
  "methodology": "Research methodology description",
  "results": "Key findings and results",
  "conclusions": "Paper conclusions",
  "extraction_status": "success"
}
```

## 🚀 Usage

### Command Line
```bash
python main.py --input paper.pdf --output metadata.json --model gemini-pro
```

### Python API
```python
from manuscript_extractor.main import ManuscriptExtractor

extractor = ManuscriptExtractor()
metadata = extractor.extract_metadata("paper.pdf")
```

## 🔧 Dependencies

- PyPDF2>=3.0.0
- google-generativeai>=0.3.0
- pathlib
- json
- logging

## 📋 Requirements

- Python 3.8+
- Optional: Gemini API key for enhanced processing

## 🏷️ Tags

- scientific-research
- metadata-extraction
- pdf-processing
- ai-analysis
