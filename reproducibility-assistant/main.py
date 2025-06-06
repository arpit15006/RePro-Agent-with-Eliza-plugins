#!/usr/bin/env python3
"""
Reproducibility Assistant Plugin for Eliza
Assesses the reproducibility of scientific code repositories.
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import git
import docker
import requests
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ReproducibilityAssistant:
    """Assess reproducibility of scientific code repositories."""
    
    def __init__(self, timeout: int = 300):
        """Initialize the reproducibility assistant."""
        self.timeout = timeout
        self.docker_client = None
        
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.warning(f"Docker not available: {e}")
    
    def clone_repository(self, repo_url: str, target_dir: str) -> bool:
        """Clone a Git repository to the target directory."""
        try:
            git.Repo.clone_from(repo_url, target_dir)
            logger.info(f"Repository cloned successfully to {target_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to clone repository: {e}")
            return False
    
    def analyze_repository_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze the structure and contents of a repository."""
        repo_path = Path(repo_path)
        analysis = {
            "has_readme": False,
            "has_requirements": False,
            "has_dockerfile": False,
            "has_setup_py": False,
            "has_environment_yml": False,
            "python_files": [],
            "jupyter_notebooks": [],
            "data_files": [],
            "config_files": [],
            "main_scripts": []
        }
        
        # Check for common files
        readme_files = list(repo_path.glob("README*")) + list(repo_path.glob("readme*"))
        analysis["has_readme"] = len(readme_files) > 0
        
        requirements_files = list(repo_path.glob("requirements*.txt"))
        analysis["has_requirements"] = len(requirements_files) > 0
        
        analysis["has_dockerfile"] = (repo_path / "Dockerfile").exists()
        analysis["has_setup_py"] = (repo_path / "setup.py").exists()
        analysis["has_environment_yml"] = (repo_path / "environment.yml").exists()
        
        # Find Python files
        for py_file in repo_path.rglob("*.py"):
            if not any(part.startswith('.') for part in py_file.parts):
                analysis["python_files"].append(str(py_file.relative_to(repo_path)))
                
                # Check if it's a main script
                if py_file.name in ["main.py", "run.py", "train.py", "test.py"]:
                    analysis["main_scripts"].append(str(py_file.relative_to(repo_path)))
        
        # Find Jupyter notebooks
        for nb_file in repo_path.rglob("*.ipynb"):
            if not any(part.startswith('.') for part in nb_file.parts):
                analysis["jupyter_notebooks"].append(str(nb_file.relative_to(repo_path)))
        
        # Find data files
        data_extensions = [".csv", ".json", ".xlsx", ".h5", ".pkl", ".npy"]
        for ext in data_extensions:
            for data_file in repo_path.rglob(f"*{ext}"):
                if not any(part.startswith('.') for part in data_file.parts):
                    analysis["data_files"].append(str(data_file.relative_to(repo_path)))
        
        # Find config files
        config_files = list(repo_path.glob("*.yml")) + list(repo_path.glob("*.yaml")) + list(repo_path.glob("*.json"))
        for config_file in config_files:
            analysis["config_files"].append(str(config_file.relative_to(repo_path)))
        
        return analysis
    
    def extract_dependencies(self, repo_path: str) -> List[str]:
        """Extract dependencies from various sources."""
        repo_path = Path(repo_path)
        dependencies = []
        
        # Check requirements.txt
        req_files = list(repo_path.glob("requirements*.txt"))
        for req_file in req_files:
            try:
                with open(req_file, 'r') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    dependencies.extend(deps)
            except Exception as e:
                logger.warning(f"Could not read {req_file}: {e}")
        
        # Check environment.yml
        env_file = repo_path / "environment.yml"
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    env_data = yaml.safe_load(f)
                    if 'dependencies' in env_data:
                        dependencies.extend(env_data['dependencies'])
            except Exception as e:
                logger.warning(f"Could not read environment.yml: {e}")
        
        # Check setup.py
        setup_file = repo_path / "setup.py"
        if setup_file.exists():
            try:
                # This is a simplified approach - in practice, you'd want to parse setup.py more carefully
                with open(setup_file, 'r') as f:
                    content = f.read()
                    if 'install_requires' in content:
                        logger.info("Found install_requires in setup.py (manual parsing needed)")
            except Exception as e:
                logger.warning(f"Could not read setup.py: {e}")
        
        return list(set(dependencies))  # Remove duplicates
    
    def create_dockerfile(self, repo_path: str, dependencies: List[str]) -> str:
        """Create a Dockerfile for the repository."""
        dockerfile_content = f"""
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set default command
CMD ["python", "--version"]
"""
        
        dockerfile_path = Path(repo_path) / "Dockerfile.repro"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        # Create requirements.txt if it doesn't exist
        req_path = Path(repo_path) / "requirements.txt"
        if not req_path.exists() and dependencies:
            with open(req_path, 'w') as f:
                f.write('\n'.join(dependencies))
        
        return str(dockerfile_path)
    
    def test_execution(self, repo_path: str, main_scripts: List[str]) -> Dict[str, Any]:
        """Test execution of main scripts."""
        results = {
            "execution_tests": [],
            "success_rate": 0.0,
            "errors": []
        }
        
        if not main_scripts:
            logger.warning("No main scripts found to test")
            return results
        
        successful_runs = 0
        
        for script in main_scripts:
            script_path = Path(repo_path) / script
            test_result = {
                "script": script,
                "success": False,
                "exit_code": None,
                "stdout": "",
                "stderr": "",
                "execution_time": 0
            }
            
            try:
                start_time = datetime.now()
                
                # Run the script with a timeout
                result = subprocess.run(
                    [sys.executable, str(script_path), "--help"],  # Try help first
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                end_time = datetime.now()
                test_result["execution_time"] = (end_time - start_time).total_seconds()
                test_result["exit_code"] = result.returncode
                test_result["stdout"] = result.stdout[:1000]  # Limit output
                test_result["stderr"] = result.stderr[:1000]
                
                if result.returncode == 0:
                    test_result["success"] = True
                    successful_runs += 1
                
            except subprocess.TimeoutExpired:
                test_result["stderr"] = f"Script execution timed out after {self.timeout} seconds"
                results["errors"].append(f"Timeout: {script}")
            except Exception as e:
                test_result["stderr"] = str(e)
                results["errors"].append(f"Error running {script}: {e}")
            
            results["execution_tests"].append(test_result)
        
        results["success_rate"] = successful_runs / len(main_scripts) if main_scripts else 0.0
        return results
    
    def calculate_reproducibility_score(self, analysis: Dict[str, Any], execution_results: Dict[str, Any]) -> float:
        """Calculate overall reproducibility score."""
        score = 0.0
        max_score = 10.0
        
        # Documentation (2 points)
        if analysis["has_readme"]:
            score += 2.0
        
        # Dependency management (2 points)
        if analysis["has_requirements"] or analysis["has_environment_yml"] or analysis["has_setup_py"]:
            score += 2.0
        
        # Containerization (1 point)
        if analysis["has_dockerfile"]:
            score += 1.0
        
        # Code organization (2 points)
        if analysis["main_scripts"]:
            score += 1.0
        if analysis["python_files"]:
            score += 1.0
        
        # Execution success (3 points)
        score += execution_results["success_rate"] * 3.0
        
        return min(score / max_score, 1.0)
    
    def assess_repository(self, repo_url: str) -> Dict[str, Any]:
        """Main method to assess repository reproducibility."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repo"
            
            # Clone repository
            if not self.clone_repository(repo_url, str(repo_path)):
                return {
                    "error": "Failed to clone repository",
                    "reproducibility_score": 0.0
                }
            
            # Analyze structure
            analysis = self.analyze_repository_structure(str(repo_path))
            
            # Extract dependencies
            dependencies = self.extract_dependencies(str(repo_path))
            
            # Test execution
            execution_results = self.test_execution(str(repo_path), analysis["main_scripts"])
            
            # Calculate score
            score = self.calculate_reproducibility_score(analysis, execution_results)
            
            # Create comprehensive report
            report = {
                "repository_url": repo_url,
                "assessment_timestamp": datetime.now().isoformat(),
                "reproducibility_score": score,
                "repository_analysis": analysis,
                "dependencies": dependencies,
                "execution_results": execution_results,
                "recommendations": self.generate_recommendations(analysis, execution_results)
            }
            
            return report
    
    def generate_recommendations(self, analysis: Dict[str, Any], execution_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving reproducibility."""
        recommendations = []
        
        if not analysis["has_readme"]:
            recommendations.append("Add a comprehensive README.md with usage instructions")
        
        if not analysis["has_requirements"]:
            recommendations.append("Add requirements.txt or environment.yml for dependency management")
        
        if not analysis["has_dockerfile"]:
            recommendations.append("Consider adding a Dockerfile for containerized execution")
        
        if not analysis["main_scripts"]:
            recommendations.append("Add clear entry point scripts (main.py, run.py, etc.)")
        
        if execution_results["success_rate"] < 1.0:
            recommendations.append("Fix execution errors in main scripts")
        
        if not analysis["data_files"] and not any("data" in f for f in analysis["config_files"]):
            recommendations.append("Document data requirements and provide sample data")
        
        return recommendations


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Assess repository reproducibility")
    parser.add_argument("--repo", "-r", required=True, help="GitHub repository URL")
    parser.add_argument("--output", "-o", default="reproducibility_report.json", help="Output report file")
    parser.add_argument("--timeout", "-t", type=int, default=300, help="Execution timeout in seconds")
    
    args = parser.parse_args()
    
    try:
        assistant = ReproducibilityAssistant(timeout=args.timeout)
        report = assistant.assess_repository(args.repo)
        
        # Save report
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        score = report.get("reproducibility_score", 0.0)
        logger.info(f"Assessment complete. Reproducibility score: {score:.2f}")
        print(f"✅ Assessment complete: {args.output}")
        print(f"📊 Reproducibility Score: {score:.2f}/1.0")
        
        if "recommendations" in report and report["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"  - {rec}")
        
    except Exception as e:
        logger.error(f"Assessment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
