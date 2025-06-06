#!/usr/bin/env python3
"""
Manuscript Extractor Plugin for Eliza
Extracts structured metadata from scientific papers in PDF or Markdown format.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import fitz  # PyMuPDF
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ManuscriptExtractor:
    """Extract structured metadata from scientific papers."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        """Initialize the extractor with API credentials."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.model = model

        if not self.api_key:
            logger.warning("No API key provided. Using rule-based extraction only.")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from a PDF file."""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_markdown(self, md_path: str) -> str:
        """Extract text content from a Markdown file."""
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading Markdown file: {e}")
            return ""
    
    def create_extraction_prompt(self, text: str) -> str:
        """Create a prompt for LLM-based metadata extraction."""
        return f"""
Extract the following structured metadata from this scientific paper and return it in JSON-LD format:

Required fields:
- @context: "https://schema.org"
- @type: "ScholarlyArticle"
- title: Paper title
- abstract: Abstract text
- author: List of authors with names and affiliations
- datePublished: Publication date if available
- keywords: List of keywords/topics
- methodology: Description of methods used
- tools: List of software tools, libraries, or platforms mentioned
- datasets: List of datasets used (include URLs if available)
- results: Summary of key findings
- conclusions: Main conclusions
- citations: Number of references if countable
- doi: DOI if available
- url: Paper URL if available

Paper text:
{text[:8000]}  # Limit to first 8000 characters to avoid token limits

Return only valid JSON-LD format without any additional text or markdown formatting.
"""
    
    def extract_with_llm(self, text: str) -> Dict[str, Any]:
        """Extract metadata using LLM API."""
        if not self.api_key:
            return self.extract_rule_based(text)
        
        try:
            if "gpt" in self.model.lower():
                return self._extract_with_openai(text)
            elif "claude" in self.model.lower():
                return self._extract_with_anthropic(text)
            elif "gemini" in self.model.lower():
                return self._extract_with_gemini(text)
            else:
                logger.warning(f"Unknown model {self.model}, falling back to rule-based extraction")
                return self.extract_rule_based(text)
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self.extract_rule_based(text)
    
    def _extract_with_openai(self, text: str) -> Dict[str, Any]:
        """Extract using OpenAI API."""
        import openai
        
        client = openai.OpenAI(api_key=self.api_key)
        prompt = self.create_extraction_prompt(text)
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a scientific paper metadata extraction expert. Return only valid JSON-LD."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
    
    def _extract_with_anthropic(self, text: str) -> Dict[str, Any]:
        """Extract using Anthropic Claude API."""
        import anthropic
        
        client = anthropic.Anthropic(api_key=self.api_key)
        prompt = self.create_extraction_prompt(text)
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.content[0].text
        return json.loads(result)

    def _extract_with_gemini(self, text: str) -> Dict[str, Any]:
        """Extract using Google Gemini API."""
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel('gemini-pro')

        prompt = self.create_extraction_prompt(text)

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4000,
            )
        )

        result = response.text
        return json.loads(result)

    def extract_rule_based(self, text: str) -> Dict[str, Any]:
        """Fallback rule-based extraction when no API is available."""
        lines = text.split('\n')
        
        # Basic rule-based extraction
        title = ""
        abstract = ""
        
        # Try to find title (usually first non-empty line or after "Title:")
        for line in lines[:20]:
            line = line.strip()
            if line and not title:
                if len(line) > 10 and len(line) < 200:
                    title = line
                    break
        
        # Try to find abstract
        abstract_start = -1
        for i, line in enumerate(lines):
            if "abstract" in line.lower():
                abstract_start = i
                break
        
        if abstract_start >= 0:
            abstract_lines = []
            for line in lines[abstract_start:abstract_start+20]:
                line = line.strip()
                if line and not line.lower().startswith(('keywords', 'introduction', '1.', 'i.')):
                    abstract_lines.append(line)
                elif abstract_lines:  # Stop if we hit a new section
                    break
            abstract = ' '.join(abstract_lines)
        
        return {
            "@context": "https://schema.org",
            "@type": "ScholarlyArticle",
            "title": title or "Title not found",
            "abstract": abstract or "Abstract not found",
            "author": [],
            "datePublished": "",
            "keywords": [],
            "methodology": "Methodology extraction requires LLM API",
            "tools": [],
            "datasets": [],
            "results": "Results extraction requires LLM API",
            "conclusions": "Conclusions extraction requires LLM API",
            "citations": 0,
            "doi": "",
            "url": "",
            "extraction_method": "rule_based"
        }
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Main method to extract metadata from a paper."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            text = self.extract_text_from_pdf(str(file_path))
        elif file_path.suffix.lower() in ['.md', '.markdown']:
            text = self.extract_text_from_markdown(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        if not text.strip():
            raise ValueError("No text could be extracted from the file")
        
        # Extract metadata
        metadata = self.extract_with_llm(text)
        
        # Add source information
        metadata["source_file"] = str(file_path)
        from datetime import datetime
        metadata["extraction_timestamp"] = datetime.now().isoformat()
        
        return metadata


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Extract metadata from scientific papers")
    parser.add_argument("--input", "-i", required=True, help="Path to input paper (PDF or Markdown)")
    parser.add_argument("--output", "-o", default="metadata.json", help="Output JSON-LD file path")
    parser.add_argument("--model", "-m", default="gpt-4", help="LLM model to use")
    parser.add_argument("--api-key", help="API key (or set OPENAI_API_KEY/ANTHROPIC_API_KEY env var)")
    
    args = parser.parse_args()
    
    try:
        extractor = ManuscriptExtractor(api_key=args.api_key, model=args.model)
        metadata = extractor.extract_metadata(args.input)
        
        # Save output
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metadata extracted successfully and saved to {args.output}")
        print(f"✅ Extraction complete: {args.output}")
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
