#!/usr/bin/env python3
"""
RePRO-Agent Pipeline
Complete pipeline for scientific reproducibility assessment and hypothesis generation.
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ReproAgentPipeline:
    """Complete RePRO-Agent pipeline orchestrator."""
    
    def __init__(self, work_dir: str = "output"):
        """Initialize the pipeline."""
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
        
        # Plugin paths
        # Get the correct base path (parent directory if running from backend)
        base_path = Path.cwd()
        if base_path.name == "backend":
            base_path = base_path.parent

        self.plugins = {
            "manuscript_extractor": base_path / "manuscript_extractor/main.py",
            "reproducibility_assistant": base_path / "reproducibility_assistant/main.py",
            "knowledge_graph_builder": base_path / "knowledge_graph_builder/main.py",
            "hypothesis_generator": base_path / "hypothesis_generator/main.py"
        }
        
        # Verify plugins exist
        for name, path in self.plugins.items():
            if not path.exists():
                raise FileNotFoundError(f"Plugin not found: {path}")
    
    def run_plugin(self, plugin_name: str, args: list) -> Dict[str, Any]:
        """Run a specific plugin with given arguments."""
        plugin_path = self.plugins[plugin_name]
        cmd = [sys.executable, str(plugin_path)] + args
        
        logger.info(f"Running {plugin_name}: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"{plugin_name} completed successfully")
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"{plugin_name} failed: {e}")
            return {
                "success": False,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "returncode": e.returncode,
                "error": str(e)
            }
    
    def extract_manuscript_metadata(self, paper_path: str,
                                  api_key: Optional[str] = None,
                                  model: str = "gemini-pro") -> str:
        """Extract metadata from a scientific paper."""
        output_path = self.work_dir / "metadata.json"
        
        args = [
            "--input", paper_path,
            "--output", str(output_path),
            "--model", model
        ]
        
        if api_key:
            args.extend(["--api-key", api_key])
        
        result = self.run_plugin("manuscript_extractor", args)
        
        if not result["success"]:
            raise RuntimeError(f"Manuscript extraction failed: {result['error']}")
        
        return str(output_path)
    
    def assess_reproducibility(self, repo_url: str, timeout: int = 300) -> str:
        """Assess reproducibility of a code repository."""
        output_path = self.work_dir / "reproducibility_report.json"
        
        args = [
            "--repo", repo_url,
            "--output", str(output_path),
            "--timeout", str(timeout)
        ]
        
        result = self.run_plugin("reproducibility_assistant", args)
        
        if not result["success"]:
            raise RuntimeError(f"Reproducibility assessment failed: {result['error']}")
        
        return str(output_path)
    
    def build_knowledge_graph(self, metadata_file: Optional[str] = None,
                            reproducibility_file: Optional[str] = None,
                            output_format: str = "turtle") -> str:
        """Build knowledge graph from extracted data."""
        output_path = self.work_dir / f"knowledge_graph.{output_format.replace('turtle', 'ttl')}"
        
        args = [
            "--output", str(output_path),
            "--format", output_format
        ]
        
        if metadata_file:
            args.extend(["--metadata", metadata_file])
        
        if reproducibility_file:
            args.extend(["--reproducibility", reproducibility_file])
        
        result = self.run_plugin("knowledge_graph_builder", args)
        
        if not result["success"]:
            raise RuntimeError(f"Knowledge graph building failed: {result['error']}")
        
        return str(output_path)
    
    def generate_hypotheses(self, graph_file: str,
                          num_hypotheses: int = 5,
                          focus_area: Optional[str] = None,
                          api_key: Optional[str] = None,
                          model: str = "gemini-pro") -> str:
        """Generate research hypotheses from knowledge graph."""
        output_path = self.work_dir / "hypotheses.json"
        
        args = [
            "--graph", graph_file,
            "--output", str(output_path),
            "--num-hypotheses", str(num_hypotheses),
            "--model", model
        ]
        
        if focus_area:
            args.extend(["--focus-area", focus_area])
        
        if api_key:
            args.extend(["--api-key", api_key])
        
        result = self.run_plugin("hypothesis_generator", args)
        
        if not result["success"]:
            raise RuntimeError(f"Hypothesis generation failed: {result['error']}")
        
        return str(output_path)
    
    def run_complete_pipeline(self, paper_path: Optional[str] = None,
                            repo_url: Optional[str] = None,
                            num_hypotheses: int = 5,
                            focus_area: Optional[str] = None,
                            api_key: Optional[str] = None,
                            model: str = "gemini-pro",
                            timeout: int = 300) -> Dict[str, str]:
        """Run the complete RePRO-Agent pipeline."""
        
        if not paper_path and not repo_url:
            raise ValueError("At least one of paper_path or repo_url must be provided")
        
        logger.info("Starting RePRO-Agent pipeline...")
        results = {}
        
        # Step 1: Extract manuscript metadata (if paper provided)
        metadata_file = None
        if paper_path:
            logger.info("Step 1: Extracting manuscript metadata...")
            metadata_file = self.extract_manuscript_metadata(paper_path, api_key, model)
            results["metadata_file"] = metadata_file
            logger.info(f"✅ Metadata extracted: {metadata_file}")
        
        # Step 2: Assess reproducibility (if repo provided)
        reproducibility_file = None
        if repo_url:
            logger.info("Step 2: Assessing reproducibility...")
            reproducibility_file = self.assess_reproducibility(repo_url, timeout)
            results["reproducibility_file"] = reproducibility_file
            logger.info(f"✅ Reproducibility assessed: {reproducibility_file}")
        
        # Step 3: Build knowledge graph
        logger.info("Step 3: Building knowledge graph...")
        graph_file = self.build_knowledge_graph(metadata_file, reproducibility_file)
        results["graph_file"] = graph_file
        logger.info(f"✅ Knowledge graph built: {graph_file}")
        
        # Step 4: Generate hypotheses
        logger.info("Step 4: Generating research hypotheses...")
        hypotheses_file = self.generate_hypotheses(
            graph_file, num_hypotheses, focus_area, api_key, model
        )
        results["hypotheses_file"] = hypotheses_file
        logger.info(f"✅ Hypotheses generated: {hypotheses_file}")
        
        # Create summary report
        summary_file = self.create_summary_report(results)
        results["summary_file"] = summary_file
        
        logger.info("🎉 Pipeline completed successfully!")
        return results
    
    def create_summary_report(self, results: Dict[str, str]) -> str:
        """Create a summary report of the pipeline execution."""
        summary_path = self.work_dir / "pipeline_summary.json"
        
        summary = {
            "pipeline": "RePRO-Agent",
            "version": "0.1.0",
            "execution_timestamp": datetime.now().isoformat(),
            "output_files": results,
            "description": "Complete scientific reproducibility assessment and hypothesis generation pipeline"
        }
        
        # Add file statistics if available
        for file_type, file_path in results.items():
            if Path(file_path).exists():
                summary[f"{file_type}_size"] = Path(file_path).stat().st_size
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return str(summary_path)


def main():
    """Main CLI interface for the pipeline."""
    parser = argparse.ArgumentParser(description="RePRO-Agent: Scientific Reproducibility and Hypothesis Generation Pipeline")
    
    # Input options
    parser.add_argument("--paper", "-p", help="Path to scientific paper (PDF or Markdown)")
    parser.add_argument("--repo", "-r", help="GitHub repository URL")
    
    # Output options
    parser.add_argument("--output-dir", "-o", default="output", help="Output directory")
    parser.add_argument("--num-hypotheses", "-n", type=int, default=5, help="Number of hypotheses to generate")
    parser.add_argument("--focus-area", "-f", help="Focus area for hypothesis generation")
    
    # API options
    parser.add_argument("--api-key", help="API key for LLM services")
    parser.add_argument("--model", "-m", default="gemini-pro", help="LLM model to use")
    
    # Execution options
    parser.add_argument("--timeout", "-t", type=int, default=300, help="Timeout for reproducibility assessment")
    
    args = parser.parse_args()
    
    if not args.paper and not args.repo:
        parser.error("At least one of --paper or --repo must be provided")
    
    try:
        # Initialize pipeline
        pipeline = ReproAgentPipeline(work_dir=args.output_dir)
        
        # Run complete pipeline
        results = pipeline.run_complete_pipeline(
            paper_path=args.paper,
            repo_url=args.repo,
            num_hypotheses=args.num_hypotheses,
            focus_area=args.focus_area,
            api_key=args.api_key,
            model=args.model,
            timeout=args.timeout
        )
        
        # Print results
        print("\n🎉 RePRO-Agent Pipeline Completed Successfully!")
        print(f"📁 Output directory: {args.output_dir}")
        print("\n📄 Generated files:")
        for file_type, file_path in results.items():
            print(f"  - {file_type}: {file_path}")
        
        # Print summary if hypotheses were generated
        if "hypotheses_file" in results:
            try:
                with open(results["hypotheses_file"], 'r') as f:
                    hypotheses_data = json.load(f)
                    num_hyp = len(hypotheses_data.get("generated_hypotheses", []))
                    avg_novelty = hypotheses_data.get("summary", {}).get("avg_novelty_score", 0)
                    print(f"\n🧬 Generated {num_hyp} hypotheses with average novelty score: {avg_novelty:.2f}")
            except Exception as e:
                logger.warning(f"Could not read hypotheses summary: {e}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
