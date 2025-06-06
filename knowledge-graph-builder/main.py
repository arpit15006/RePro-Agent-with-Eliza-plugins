#!/usr/bin/env python3
"""
Knowledge Graph Builder Plugin for Eliza
Builds RDF knowledge graphs from scientific metadata and reproducibility assessments.
"""

import argparse
import json
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from urllib.parse import quote

from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD, DCTERMS, FOAF
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define custom namespaces
SCHEMA = Namespace("https://schema.org/")
REPRO = Namespace("https://reproducibility.org/")
SCIENTIFIC = Namespace("https://scientific.org/")


class KnowledgeGraphBuilder:
    """Build RDF knowledge graphs from scientific data."""
    
    def __init__(self):
        """Initialize the knowledge graph builder."""
        self.graph = Graph()
        self.setup_namespaces()
    
    def setup_namespaces(self):
        """Set up RDF namespaces."""
        self.graph.bind("schema", SCHEMA)
        self.graph.bind("repro", REPRO)
        self.graph.bind("scientific", SCIENTIFIC)
        self.graph.bind("dcterms", DCTERMS)
        self.graph.bind("foaf", FOAF)
    
    def create_uri(self, base: str, identifier: str) -> URIRef:
        """Create a URI from base and identifier."""
        safe_id = quote(str(identifier).replace(" ", "_"), safe="")
        return URIRef(f"{base}{safe_id}")
    
    def add_paper_metadata(self, metadata: Dict[str, Any]) -> URIRef:
        """Add paper metadata to the knowledge graph."""
        # Create paper URI
        if metadata.get("doi"):
            paper_uri = URIRef(f"https://doi.org/{metadata['doi']}")
        elif metadata.get("url"):
            paper_uri = URIRef(metadata["url"])
        else:
            paper_uri = self.create_uri("https://papers.org/", metadata.get("title", str(uuid.uuid4())))
        
        # Add basic paper information
        self.graph.add((paper_uri, RDF.type, SCHEMA.ScholarlyArticle))
        
        if metadata.get("title"):
            self.graph.add((paper_uri, SCHEMA.name, Literal(metadata["title"])))
            self.graph.add((paper_uri, DCTERMS.title, Literal(metadata["title"])))
        
        if metadata.get("abstract"):
            self.graph.add((paper_uri, SCHEMA.abstract, Literal(metadata["abstract"])))
        
        if metadata.get("datePublished"):
            self.graph.add((paper_uri, SCHEMA.datePublished, Literal(metadata["datePublished"], datatype=XSD.date)))
        
        if metadata.get("doi"):
            self.graph.add((paper_uri, SCHEMA.identifier, Literal(metadata["doi"])))
        
        if metadata.get("url"):
            self.graph.add((paper_uri, SCHEMA.url, URIRef(metadata["url"])))
        
        # Add authors
        if metadata.get("author"):
            for author_data in metadata["author"]:
                author_uri = self.add_author(author_data)
                self.graph.add((paper_uri, SCHEMA.author, author_uri))
        
        # Add keywords
        if metadata.get("keywords"):
            for keyword in metadata["keywords"]:
                keyword_uri = self.create_uri("https://keywords.org/", keyword)
                self.graph.add((keyword_uri, RDF.type, SCHEMA.DefinedTerm))
                self.graph.add((keyword_uri, SCHEMA.name, Literal(keyword)))
                self.graph.add((paper_uri, SCHEMA.keywords, keyword_uri))
        
        # Add methodology
        if metadata.get("methodology"):
            method_uri = self.create_uri("https://methods.org/", f"{metadata['title']}_method")
            self.graph.add((method_uri, RDF.type, SCIENTIFIC.Methodology))
            self.graph.add((method_uri, SCHEMA.description, Literal(metadata["methodology"])))
            self.graph.add((paper_uri, SCIENTIFIC.usesMethodology, method_uri))
        
        # Add tools
        if metadata.get("tools"):
            for tool in metadata["tools"]:
                tool_uri = self.add_tool(tool)
                self.graph.add((paper_uri, SCIENTIFIC.usesTool, tool_uri))
        
        # Add datasets
        if metadata.get("datasets"):
            for dataset in metadata["datasets"]:
                dataset_uri = self.add_dataset(dataset)
                self.graph.add((paper_uri, SCIENTIFIC.usesDataset, dataset_uri))
        
        # Add results and conclusions
        if metadata.get("results"):
            result_uri = self.create_uri("https://results.org/", f"{metadata['title']}_results")
            self.graph.add((result_uri, RDF.type, SCIENTIFIC.Results))
            self.graph.add((result_uri, SCHEMA.description, Literal(metadata["results"])))
            self.graph.add((paper_uri, SCIENTIFIC.hasResults, result_uri))
        
        if metadata.get("conclusions"):
            conclusion_uri = self.create_uri("https://conclusions.org/", f"{metadata['title']}_conclusions")
            self.graph.add((conclusion_uri, RDF.type, SCIENTIFIC.Conclusions))
            self.graph.add((conclusion_uri, SCHEMA.description, Literal(metadata["conclusions"])))
            self.graph.add((paper_uri, SCIENTIFIC.hasConclusions, conclusion_uri))
        
        return paper_uri
    
    def add_author(self, author_data: Union[str, Dict[str, Any]]) -> URIRef:
        """Add author information to the knowledge graph."""
        if isinstance(author_data, str):
            author_name = author_data
            author_affiliation = None
        else:
            author_name = author_data.get("name", "Unknown Author")
            author_affiliation = author_data.get("affiliation")
        
        author_uri = self.create_uri("https://authors.org/", author_name)
        self.graph.add((author_uri, RDF.type, SCHEMA.Person))
        self.graph.add((author_uri, FOAF.name, Literal(author_name)))
        self.graph.add((author_uri, SCHEMA.name, Literal(author_name)))
        
        if author_affiliation:
            affiliation_uri = self.create_uri("https://organizations.org/", author_affiliation)
            self.graph.add((affiliation_uri, RDF.type, SCHEMA.Organization))
            self.graph.add((affiliation_uri, SCHEMA.name, Literal(author_affiliation)))
            self.graph.add((author_uri, SCHEMA.affiliation, affiliation_uri))
        
        return author_uri
    
    def add_tool(self, tool_data: Union[str, Dict[str, Any]]) -> URIRef:
        """Add tool information to the knowledge graph."""
        if isinstance(tool_data, str):
            tool_name = tool_data
            tool_url = None
        else:
            tool_name = tool_data.get("name", "Unknown Tool")
            tool_url = tool_data.get("url")
        
        tool_uri = self.create_uri("https://tools.org/", tool_name)
        self.graph.add((tool_uri, RDF.type, SCIENTIFIC.SoftwareTool))
        self.graph.add((tool_uri, SCHEMA.name, Literal(tool_name)))
        
        if tool_url:
            self.graph.add((tool_uri, SCHEMA.url, URIRef(tool_url)))
        
        return tool_uri
    
    def add_dataset(self, dataset_data: Union[str, Dict[str, Any]]) -> URIRef:
        """Add dataset information to the knowledge graph."""
        if isinstance(dataset_data, str):
            dataset_name = dataset_data
            dataset_url = None
        else:
            dataset_name = dataset_data.get("name", "Unknown Dataset")
            dataset_url = dataset_data.get("url")
        
        dataset_uri = self.create_uri("https://datasets.org/", dataset_name)
        self.graph.add((dataset_uri, RDF.type, SCHEMA.Dataset))
        self.graph.add((dataset_uri, SCHEMA.name, Literal(dataset_name)))
        
        if dataset_url:
            self.graph.add((dataset_uri, SCHEMA.url, URIRef(dataset_url)))
        
        return dataset_uri
    
    def add_reproducibility_assessment(self, assessment: Dict[str, Any], paper_uri: Optional[URIRef] = None) -> URIRef:
        """Add reproducibility assessment to the knowledge graph."""
        # Create assessment URI
        repo_url = assessment.get("repository_url", "")
        assessment_uri = self.create_uri("https://assessments.org/", f"assessment_{hash(repo_url)}")
        
        self.graph.add((assessment_uri, RDF.type, REPRO.ReproducibilityAssessment))
        
        # Add basic assessment info
        if assessment.get("assessment_timestamp"):
            self.graph.add((assessment_uri, DCTERMS.created, 
                          Literal(assessment["assessment_timestamp"], datatype=XSD.dateTime)))
        
        if assessment.get("reproducibility_score") is not None:
            self.graph.add((assessment_uri, REPRO.reproducibilityScore, 
                          Literal(assessment["reproducibility_score"], datatype=XSD.float)))
        
        # Add repository information
        if repo_url:
            repo_uri = URIRef(repo_url)
            self.graph.add((repo_uri, RDF.type, SCIENTIFIC.CodeRepository))
            self.graph.add((repo_uri, SCHEMA.url, URIRef(repo_url)))
            self.graph.add((assessment_uri, REPRO.assessesRepository, repo_uri))
            
            # Link to paper if provided
            if paper_uri:
                self.graph.add((paper_uri, SCIENTIFIC.hasCodeRepository, repo_uri))
        
        # Add repository analysis details
        if assessment.get("repository_analysis"):
            analysis = assessment["repository_analysis"]
            
            # Add boolean properties
            for prop in ["has_readme", "has_requirements", "has_dockerfile"]:
                if prop in analysis:
                    predicate = getattr(REPRO, prop.replace("has_", ""))
                    self.graph.add((assessment_uri, predicate, Literal(analysis[prop], datatype=XSD.boolean)))
        
        # Add execution results
        if assessment.get("execution_results"):
            exec_results = assessment["execution_results"]
            if exec_results.get("success_rate") is not None:
                self.graph.add((assessment_uri, REPRO.executionSuccessRate, 
                              Literal(exec_results["success_rate"], datatype=XSD.float)))
        
        # Add recommendations
        if assessment.get("recommendations"):
            for rec in assessment["recommendations"]:
                rec_uri = BNode()
                self.graph.add((rec_uri, RDF.type, REPRO.Recommendation))
                self.graph.add((rec_uri, SCHEMA.description, Literal(rec)))
                self.graph.add((assessment_uri, REPRO.hasRecommendation, rec_uri))
        
        return assessment_uri
    
    def load_and_process_files(self, metadata_file: Optional[str] = None, 
                              reproducibility_file: Optional[str] = None) -> Dict[str, Any]:
        """Load and process input files to build the knowledge graph."""
        results = {"papers_added": 0, "assessments_added": 0}
        paper_uri = None
        
        # Process metadata file
        if metadata_file and Path(metadata_file).exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                paper_uri = self.add_paper_metadata(metadata)
                results["papers_added"] = 1
                logger.info(f"Added paper metadata from {metadata_file}")
            except Exception as e:
                logger.error(f"Error processing metadata file: {e}")
        
        # Process reproducibility file
        if reproducibility_file and Path(reproducibility_file).exists():
            try:
                with open(reproducibility_file, 'r', encoding='utf-8') as f:
                    assessment = json.load(f)
                self.add_reproducibility_assessment(assessment, paper_uri)
                results["assessments_added"] = 1
                logger.info(f"Added reproducibility assessment from {reproducibility_file}")
            except Exception as e:
                logger.error(f"Error processing reproducibility file: {e}")
        
        return results
    
    def save_graph(self, output_path: str, format: str = "turtle"):
        """Save the knowledge graph to a file."""
        try:
            self.graph.serialize(destination=output_path, format=format)
            logger.info(f"Knowledge graph saved to {output_path} in {format} format")
        except Exception as e:
            logger.error(f"Error saving graph: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the knowledge graph."""
        stats = {
            "total_triples": len(self.graph),
            "papers": len(list(self.graph.subjects(RDF.type, SCHEMA.ScholarlyArticle))),
            "authors": len(list(self.graph.subjects(RDF.type, SCHEMA.Person))),
            "tools": len(list(self.graph.subjects(RDF.type, SCIENTIFIC.SoftwareTool))),
            "datasets": len(list(self.graph.subjects(RDF.type, SCHEMA.Dataset))),
            "assessments": len(list(self.graph.subjects(RDF.type, REPRO.ReproducibilityAssessment)))
        }
        return stats


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Build knowledge graph from scientific data")
    parser.add_argument("--metadata", "-m", help="Path to metadata JSON-LD file")
    parser.add_argument("--reproducibility", "-r", help="Path to reproducibility assessment JSON file")
    parser.add_argument("--output", "-o", default="knowledge_graph.ttl", help="Output graph file")
    parser.add_argument("--format", "-f", default="turtle", 
                       choices=["turtle", "ntriples", "rdfxml", "jsonld"],
                       help="Output format")
    
    args = parser.parse_args()
    
    if not args.metadata and not args.reproducibility:
        logger.error("At least one input file (metadata or reproducibility) must be provided")
        sys.exit(1)
    
    try:
        builder = KnowledgeGraphBuilder()
        results = builder.load_and_process_files(args.metadata, args.reproducibility)
        
        # Save the graph
        builder.save_graph(args.output, args.format)
        
        # Print statistics
        stats = builder.get_statistics()
        logger.info(f"Knowledge graph built successfully:")
        logger.info(f"  - Total triples: {stats['total_triples']}")
        logger.info(f"  - Papers: {stats['papers']}")
        logger.info(f"  - Authors: {stats['authors']}")
        logger.info(f"  - Tools: {stats['tools']}")
        logger.info(f"  - Datasets: {stats['datasets']}")
        logger.info(f"  - Assessments: {stats['assessments']}")
        
        print(f"✅ Knowledge graph built: {args.output}")
        print(f"📊 Statistics: {stats['total_triples']} triples, {stats['papers']} papers, {stats['assessments']} assessments")
        
    except Exception as e:
        logger.error(f"Knowledge graph building failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
