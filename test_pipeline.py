#!/usr/bin/env python3
"""
Test script for RePRO-Agent pipeline
Validates all components and provides example usage.
"""

import json
import logging
import tempfile
from pathlib import Path
from pipeline import ReproAgentPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_sample_metadata():
    """Create sample metadata for testing."""
    return {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "title": "Deep Learning for Protein Structure Prediction",
        "abstract": "This paper presents a novel deep learning approach for predicting protein structures using transformer architectures.",
        "author": [
            {
                "name": "Dr. Jane Smith",
                "affiliation": "MIT Computer Science"
            },
            {
                "name": "Prof. John Doe", 
                "affiliation": "Stanford University"
            }
        ],
        "datePublished": "2024-01-15",
        "keywords": ["deep learning", "protein structure", "transformers", "bioinformatics"],
        "methodology": "We developed a transformer-based neural network trained on the Protein Data Bank (PDB) dataset. The model uses attention mechanisms to capture long-range dependencies in amino acid sequences.",
        "tools": ["PyTorch", "TensorFlow", "AlphaFold", "PyMOL"],
        "datasets": [
            {
                "name": "Protein Data Bank (PDB)",
                "url": "https://www.rcsb.org/"
            },
            {
                "name": "UniProt",
                "url": "https://www.uniprot.org/"
            }
        ],
        "results": "Our model achieved 95% accuracy on the CASP14 benchmark, outperforming previous methods by 12%. The model successfully predicted structures for 1,000 novel proteins.",
        "conclusions": "Transformer architectures show significant promise for protein structure prediction. Future work should explore multi-modal approaches combining sequence and structural data.",
        "citations": 42,
        "doi": "10.1038/s41586-2024-12345",
        "url": "https://www.nature.com/articles/s41586-2024-12345"
    }


def create_sample_reproducibility_report():
    """Create sample reproducibility report for testing."""
    return {
        "repository_url": "https://github.com/example/protein-structure-prediction",
        "assessment_timestamp": "2024-01-20T10:30:00",
        "reproducibility_score": 0.85,
        "repository_analysis": {
            "has_readme": True,
            "has_requirements": True,
            "has_dockerfile": False,
            "has_setup_py": True,
            "has_environment_yml": True,
            "python_files": ["main.py", "model.py", "utils.py", "train.py"],
            "jupyter_notebooks": ["analysis.ipynb", "visualization.ipynb"],
            "data_files": ["sample_data.csv"],
            "config_files": ["config.yaml"],
            "main_scripts": ["main.py", "train.py"]
        },
        "dependencies": [
            "torch>=1.12.0",
            "numpy>=1.21.0",
            "pandas>=1.3.0",
            "biopython>=1.79"
        ],
        "execution_results": {
            "execution_tests": [
                {
                    "script": "main.py",
                    "success": True,
                    "exit_code": 0,
                    "stdout": "Model loaded successfully\nPrediction completed",
                    "stderr": "",
                    "execution_time": 15.2
                }
            ],
            "success_rate": 1.0,
            "errors": []
        },
        "recommendations": [
            "Consider adding a Dockerfile for containerized execution",
            "Add more comprehensive unit tests"
        ]
    }


def test_knowledge_graph_builder():
    """Test the knowledge graph builder with sample data."""
    logger.info("Testing Knowledge Graph Builder...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample input files
        metadata_file = temp_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(create_sample_metadata(), f, indent=2)
        
        reproducibility_file = temp_path / "reproducibility.json"
        with open(reproducibility_file, 'w') as f:
            json.dump(create_sample_reproducibility_report(), f, indent=2)
        
        # Test knowledge graph builder
        from knowledge_graph_builder.main import KnowledgeGraphBuilder
        
        builder = KnowledgeGraphBuilder()
        results = builder.load_and_process_files(
            str(metadata_file), 
            str(reproducibility_file)
        )
        
        # Save graph
        graph_file = temp_path / "test_graph.ttl"
        builder.save_graph(str(graph_file))
        
        # Get statistics
        stats = builder.get_statistics()
        
        logger.info(f"✅ Knowledge Graph Builder test passed")
        logger.info(f"   - Papers added: {results['papers_added']}")
        logger.info(f"   - Assessments added: {results['assessments_added']}")
        logger.info(f"   - Total triples: {stats['total_triples']}")
        
        return str(graph_file)


def test_hypothesis_generator(graph_file):
    """Test the hypothesis generator with sample graph."""
    logger.info("Testing Hypothesis Generator...")
    
    from hypothesis_generator.main import HypothesisGenerator
    
    generator = HypothesisGenerator()
    generator.load_knowledge_graph(graph_file)
    
    # Analyze graph patterns
    analysis = generator.analyze_graph_patterns()
    
    # Find opportunities
    opportunities = generator.find_research_opportunities(analysis)
    
    # Generate hypotheses (rule-based since no API key)
    hypotheses = generator._generate_rule_based_hypotheses(analysis, opportunities, 3)
    
    logger.info(f"✅ Hypothesis Generator test passed")
    logger.info(f"   - Graph entities: {len(analysis['entity_counts'])}")
    logger.info(f"   - Opportunities found: {len(opportunities)}")
    logger.info(f"   - Hypotheses generated: {len(hypotheses)}")
    
    if hypotheses:
        logger.info(f"   - Example hypothesis: {hypotheses[0]['hypothesis'][:100]}...")
    
    return hypotheses


def test_complete_pipeline():
    """Test the complete pipeline with sample data."""
    logger.info("Testing Complete Pipeline...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample metadata file (simulating manuscript extractor output)
        metadata_file = temp_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(create_sample_metadata(), f, indent=2)
        
        # Create sample reproducibility file (simulating reproducibility assistant output)
        reproducibility_file = temp_path / "reproducibility.json"
        with open(reproducibility_file, 'w') as f:
            json.dump(create_sample_reproducibility_report(), f, indent=2)
        
        # Initialize pipeline
        pipeline = ReproAgentPipeline(work_dir=str(temp_path))
        
        # Test knowledge graph building
        graph_file = pipeline.build_knowledge_graph(
            str(metadata_file), 
            str(reproducibility_file)
        )
        
        # Test hypothesis generation
        hypotheses_file = pipeline.generate_hypotheses(
            graph_file, 
            num_hypotheses=3
        )
        
        # Create summary
        results = {
            "metadata_file": str(metadata_file),
            "reproducibility_file": str(reproducibility_file),
            "graph_file": graph_file,
            "hypotheses_file": hypotheses_file
        }
        
        summary_file = pipeline.create_summary_report(results)
        
        logger.info(f"✅ Complete Pipeline test passed")
        logger.info(f"   - All files created successfully")
        logger.info(f"   - Summary: {summary_file}")
        
        # Print sample results
        if Path(hypotheses_file).exists():
            with open(hypotheses_file, 'r') as f:
                hypotheses_data = json.load(f)
                num_hyp = len(hypotheses_data.get("generated_hypotheses", []))
                logger.info(f"   - Generated {num_hyp} hypotheses")


def run_all_tests():
    """Run all tests."""
    logger.info("🧪 Starting RePRO-Agent Pipeline Tests")
    logger.info("=" * 50)
    
    try:
        # Test 1: Knowledge Graph Builder
        graph_file = test_knowledge_graph_builder()
        
        # Test 2: Hypothesis Generator
        test_hypothesis_generator(graph_file)
        
        # Test 3: Complete Pipeline
        test_complete_pipeline()
        
        logger.info("=" * 50)
        logger.info("🎉 All tests passed successfully!")
        logger.info("")
        logger.info("✅ Your RePRO-Agent installation is working correctly.")
        logger.info("📖 See README.md for usage examples.")
        logger.info("🚀 Ready to process real scientific papers!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        logger.error("Please check your installation and try again.")
        raise


if __name__ == "__main__":
    run_all_tests()
