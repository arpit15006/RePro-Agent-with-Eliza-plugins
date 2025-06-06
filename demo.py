#!/usr/bin/env python3
"""
RePRO-Agent Demo Script
Demonstrates the complete pipeline with sample data for BioXAI Hackathon submission.
"""

import json
import logging
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run the complete RePRO-Agent demo."""
    
    print("🧬 RePRO-Agent Demo - BioXAI Hackathon Submission")
    print("=" * 60)
    print()
    
    # Check if API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  No GEMINI_API_KEY found in environment.")
        print("   The demo will run with rule-based extraction only.")
        print("   For full LLM-powered functionality, set your API key:")
        print("   export GEMINI_API_KEY='your-key-here'")
        print()
    else:
        print("✅ Gemini API key found - full LLM functionality enabled")
        print()
    
    # Demo parameters
    sample_paper = "sample_paper.md"
    sample_repo = "https://github.com/pytorch/pytorch"  # Well-known repo for demo
    output_dir = "demo_output"
    
    print(f"📄 Sample paper: {sample_paper}")
    print(f"🔗 Sample repository: {sample_repo}")
    print(f"📁 Output directory: {output_dir}")
    print()
    
    # Check if sample paper exists
    if not Path(sample_paper).exists():
        print(f"❌ Sample paper not found: {sample_paper}")
        print("   Please ensure sample_paper.md exists in the current directory.")
        return
    
    try:
        # Import and run pipeline
        from pipeline import ReproAgentPipeline
        
        print("🚀 Starting RePRO-Agent pipeline...")
        print()
        
        # Initialize pipeline
        pipeline = ReproAgentPipeline(work_dir=output_dir)
        
        # Run complete pipeline
        results = pipeline.run_complete_pipeline(
            paper_path=sample_paper,
            repo_url=sample_repo,
            num_hypotheses=5,
            focus_area="deep learning",
            api_key=api_key,
            model="gemini-pro",
            timeout=300
        )
        
        print()
        print("🎉 Demo completed successfully!")
        print("=" * 60)
        print()
        
        # Display results
        print("📊 Generated Files:")
        for file_type, file_path in results.items():
            if Path(file_path).exists():
                size = Path(file_path).stat().st_size
                print(f"  ✅ {file_type}: {file_path} ({size} bytes)")
            else:
                print(f"  ❌ {file_type}: {file_path} (not found)")
        
        print()
        
        # Show sample outputs
        if "hypotheses_file" in results and Path(results["hypotheses_file"]).exists():
            print("🧬 Sample Generated Hypotheses:")
            try:
                with open(results["hypotheses_file"], 'r') as f:
                    hypotheses_data = json.load(f)
                    
                hypotheses = hypotheses_data.get("generated_hypotheses", [])
                for i, hyp in enumerate(hypotheses[:3], 1):  # Show first 3
                    print(f"\n{i}. {hyp.get('hypothesis', 'No hypothesis text')}")
                    print(f"   Feasibility: {hyp.get('feasibility', 'unknown')}")
                    print(f"   Novelty Score: {hyp.get('novelty_score', 'N/A')}")
                    
                if len(hypotheses) > 3:
                    print(f"\n   ... and {len(hypotheses) - 3} more hypotheses")
                    
            except Exception as e:
                print(f"   Error reading hypotheses: {e}")
        
        print()
        
        # Show knowledge graph statistics
        if "graph_file" in results and Path(results["graph_file"]).exists():
            print("📈 Knowledge Graph Statistics:")
            try:
                from knowledge_graph_builder.main import KnowledgeGraphBuilder
                builder = KnowledgeGraphBuilder()
                builder.load_knowledge_graph(results["graph_file"])
                stats = builder.get_statistics()
                
                for key, value in stats.items():
                    print(f"  - {key.replace('_', ' ').title()}: {value}")
                    
            except Exception as e:
                print(f"   Error reading graph statistics: {e}")
        
        print()
        
        # Show reproducibility score
        if "reproducibility_file" in results and Path(results["reproducibility_file"]).exists():
            print("🔍 Reproducibility Assessment:")
            try:
                with open(results["reproducibility_file"], 'r') as f:
                    repro_data = json.load(f)
                    
                score = repro_data.get("reproducibility_score", 0)
                print(f"  - Overall Score: {score:.2f}/1.0")
                
                analysis = repro_data.get("repository_analysis", {})
                print(f"  - Has README: {analysis.get('has_readme', False)}")
                print(f"  - Has Requirements: {analysis.get('has_requirements', False)}")
                print(f"  - Has Dockerfile: {analysis.get('has_dockerfile', False)}")
                
                recommendations = repro_data.get("recommendations", [])
                if recommendations:
                    print(f"  - Recommendations: {len(recommendations)} suggestions")
                    
            except Exception as e:
                print(f"   Error reading reproducibility data: {e}")
        
        print()
        print("🎯 Next Steps:")
        print("  1. Explore the generated files in the output directory")
        print("  2. Try with your own papers and repositories")
        print("  3. Customize focus areas and hypothesis counts")
        print("  4. Use individual plugins for specific tasks")
        print()
        print("📖 For more examples, see EXAMPLES.md")
        print("🐛 Report issues at: https://github.com/yourusername/eliza-repro-hypothesis")
        print()
        print("🏆 Ready for BioXAI Hackathon submission!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
