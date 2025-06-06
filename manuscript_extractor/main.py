#!/usr/bin/env python3
"""
Manuscript Extractor
Extracts metadata and structured information from scientific papers.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

logger = logging.getLogger(__name__)

class ManuscriptExtractor:
    """Extract metadata from scientific manuscripts."""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from a manuscript file."""
        
        try:
            # Read file content
            content = self._read_file(file_path)
            
            # Extract basic metadata
            metadata = {
                "title": self._extract_title(content),
                "abstract": self._extract_abstract(content),
                "authors": self._extract_authors(content),
                "keywords": self._extract_keywords(content),
                "sections": self._extract_sections(content),
                "references": self._extract_references(content),
                "methodology": self._extract_methodology(content),
                "results": self._extract_results(content),
                "conclusions": self._extract_conclusions(content),
                "file_path": file_path,
                "file_size": os.path.getsize(file_path)
            }
            
            # Use AI for enhanced extraction if API key available
            if self.api_key:
                metadata = self._enhance_with_ai(content, metadata)
                
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return self._create_fallback_metadata(file_path)
    
    def _read_file(self, file_path: str) -> str:
        """Read content from various file formats."""
        
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.pdf':
            return self._read_pdf(file_path)
        elif file_path.suffix.lower() in ['.md', '.txt']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def _read_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            logger.warning("PyPDF2 not available, using fallback text extraction")
            # Fallback: treat as text file
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except:
                return "PDF content could not be extracted"
    
    def _extract_title(self, content: str) -> str:
        """Extract paper title."""
        lines = content.split('\n')
        
        # Look for title patterns
        for line in lines[:20]:  # Check first 20 lines
            line = line.strip()
            if len(line) > 10 and len(line) < 200:
                # Skip common headers
                if not any(skip in line.lower() for skip in ['abstract', 'introduction', 'author', 'email', 'university']):
                    if line and not line.startswith('#'):
                        return line
                    elif line.startswith('# '):
                        return line[2:].strip()
        
        return "Untitled Paper"
    
    def _extract_abstract(self, content: str) -> str:
        """Extract paper abstract."""
        # Look for abstract section
        abstract_match = re.search(r'(?i)abstract\s*:?\s*\n(.*?)(?=\n\s*(?:keywords|introduction|1\.|##))', content, re.DOTALL)
        if abstract_match:
            return abstract_match.group(1).strip()
        
        # Fallback: first paragraph after title
        lines = content.split('\n')
        in_abstract = False
        abstract_lines = []
        
        for line in lines:
            line = line.strip()
            if 'abstract' in line.lower():
                in_abstract = True
                continue
            elif in_abstract and line:
                if any(section in line.lower() for section in ['introduction', 'keywords', '1.', '##']):
                    break
                abstract_lines.append(line)
            elif in_abstract and not line and abstract_lines:
                break
        
        return ' '.join(abstract_lines) if abstract_lines else "Abstract not found"
    
    def _extract_authors(self, content: str) -> List[str]:
        """Extract author names."""
        # Look for author patterns
        author_patterns = [
            r'(?i)authors?\s*:?\s*\n(.*?)(?=\n\s*(?:abstract|affiliation|email))',
            r'(?i)by\s+(.*?)(?=\n)',
            r'(?i)author.*?:\s*(.*?)(?=\n)'
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                authors_text = match.group(1).strip()
                # Split by common separators
                authors = re.split(r'[,;&]|\sand\s', authors_text)
                return [author.strip() for author in authors if author.strip()]
        
        return ["Unknown Author"]
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords."""
        keyword_match = re.search(r'(?i)keywords?\s*:?\s*(.*?)(?=\n\s*(?:introduction|1\.|##))', content, re.DOTALL)
        if keyword_match:
            keywords_text = keyword_match.group(1).strip()
            keywords = re.split(r'[,;]', keywords_text)
            return [kw.strip() for kw in keywords if kw.strip()]
        
        return []
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headers."""
        sections = []
        
        # Look for numbered sections and markdown headers
        section_patterns = [
            r'^\s*(\d+\.?\s+[A-Z][^.\n]*)',
            r'^\s*(#{1,3}\s+[^#\n]+)',
            r'^\s*([A-Z][A-Z\s]{5,30})\s*$'
        ]
        
        for line in content.split('\n'):
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    section = match.group(1).strip()
                    if section not in sections:
                        sections.append(section)
        
        return sections
    
    def _extract_methodology(self, content: str) -> str:
        """Extract methodology section."""
        method_patterns = [
            r'(?i)(methods?|methodology|experimental\s+setup|approach)(.*?)(?=\n\s*(?:\d+\.|##|results|discussion))',
            r'(?i)(##?\s*methods?|##?\s*methodology)(.*?)(?=\n\s*##)'
        ]
        
        for pattern in method_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(2).strip()
        
        return "Methodology not found"
    
    def _extract_results(self, content: str) -> str:
        """Extract results section."""
        result_patterns = [
            r'(?i)(results?|findings)(.*?)(?=\n\s*(?:\d+\.|##|discussion|conclusion))',
            r'(?i)(##?\s*results?)(.*?)(?=\n\s*##)'
        ]
        
        for pattern in result_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(2).strip()
        
        return "Results not found"
    
    def _extract_conclusions(self, content: str) -> str:
        """Extract conclusions section."""
        conclusion_patterns = [
            r'(?i)(conclusions?|summary)(.*?)(?=\n\s*(?:references|acknowledgments|##))',
            r'(?i)(##?\s*conclusions?)(.*?)(?=\n\s*##)'
        ]
        
        for pattern in conclusion_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(2).strip()
        
        return "Conclusions not found"
    
    def _extract_references(self, content: str) -> List[str]:
        """Extract references."""
        # Look for references section
        ref_match = re.search(r'(?i)references?\s*\n(.*?)(?=\n\s*(?:appendix|##|$))', content, re.DOTALL)
        if ref_match:
            ref_text = ref_match.group(1)
            # Split by numbered references
            refs = re.split(r'\n\s*\d+\.', ref_text)
            return [ref.strip() for ref in refs if ref.strip()]
        
        return []
    
    def _enhance_with_ai(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance metadata extraction using AI."""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            Analyze this scientific paper and extract structured metadata. Return a JSON object with the following fields:
            - title: The paper title
            - abstract: The abstract
            - authors: List of author names
            - keywords: List of keywords
            - research_area: The main research domain
            - methodology_type: Type of methodology used
            - key_findings: List of main findings
            - datasets_used: List of datasets mentioned
            - tools_used: List of tools/software mentioned
            
            Paper content:
            {content[:4000]}...
            """
            
            response = model.generate_content(prompt)
            ai_metadata = json.loads(response.text)
            
            # Merge AI results with extracted metadata
            metadata.update(ai_metadata)
            
        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}")
        
        return metadata
    
    def _create_fallback_metadata(self, file_path: str) -> Dict[str, Any]:
        """Create basic metadata when extraction fails."""
        return {
            "title": f"Document: {Path(file_path).name}",
            "abstract": "Could not extract abstract",
            "authors": ["Unknown"],
            "keywords": [],
            "sections": [],
            "references": [],
            "methodology": "Could not extract methodology",
            "results": "Could not extract results",
            "conclusions": "Could not extract conclusions",
            "file_path": file_path,
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "extraction_status": "failed"
        }


def main():
    """CLI interface for manuscript extractor."""
    import argparse

    parser = argparse.ArgumentParser(description="Extract metadata from scientific manuscripts")
    parser.add_argument("--input", "-i", required=True, help="Input file path")
    parser.add_argument("--output", "-o", required=True, help="Output JSON file path")
    parser.add_argument("--model", "-m", default="gemini-pro", help="AI model to use")
    parser.add_argument("--api-key", help="API key for AI services")

    args = parser.parse_args()

    # Set API key if provided
    if args.api_key:
        os.environ['GEMINI_API_KEY'] = args.api_key

    try:
        extractor = ManuscriptExtractor()
        metadata = extractor.extract_metadata(args.input)

        with open(args.output, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Metadata extracted successfully: {args.output}")

    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
