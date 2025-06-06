#!/usr/bin/env python3
"""
Reproducibility Assistant
Assesses code repositories for reproducibility and provides recommendations.
"""

import os
import json
import logging
import requests
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ReproducibilityAssistant:
    """Assess repository reproducibility."""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        
    def assess_repository(self, repo_url: str) -> Dict[str, Any]:
        """Assess a repository for reproducibility."""
        
        try:
            # Parse repository URL
            repo_info = self._parse_repo_url(repo_url)
            
            # Clone or download repository
            repo_path = self._download_repository(repo_url)
            
            # Analyze repository structure
            analysis = self._analyze_repository(repo_path)
            
            # Calculate reproducibility score
            score = self._calculate_reproducibility_score(analysis)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analysis)
            
            # Clean up temporary files
            self._cleanup(repo_path)
            
            return {
                "repository_url": repo_url,
                "repository_info": repo_info,
                "reproducibility_score": score,
                "analysis": analysis,
                "recommendations": recommendations,
                "assessment_date": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error assessing repository: {e}")
            return self._create_fallback_assessment(repo_url, str(e))
    
    def _parse_repo_url(self, repo_url: str) -> Dict[str, str]:
        """Parse repository URL to extract information."""
        
        parsed = urlparse(repo_url)
        
        if 'github.com' in parsed.netloc:
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2:
                return {
                    "platform": "GitHub",
                    "owner": path_parts[0],
                    "name": path_parts[1],
                    "full_name": f"{path_parts[0]}/{path_parts[1]}"
                }
        
        return {
            "platform": "Unknown",
            "url": repo_url
        }
    
    def _download_repository(self, repo_url: str) -> Path:
        """Download repository to temporary directory."""
        
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Try git clone first
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, str(temp_dir / 'repo')],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return temp_dir / 'repo'
            else:
                logger.warning(f"Git clone failed: {result.stderr}")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Git not available or clone timed out")
        
        # Fallback: download as ZIP (for GitHub)
        if 'github.com' in repo_url:
            zip_url = repo_url.replace('github.com', 'github.com').rstrip('/') + '/archive/main.zip'
            try:
                response = requests.get(zip_url, timeout=30)
                if response.status_code == 200:
                    zip_path = temp_dir / 'repo.zip'
                    with open(zip_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Extract ZIP
                    import zipfile
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    # Find extracted directory
                    for item in temp_dir.iterdir():
                        if item.is_dir() and item.name != '__pycache__':
                            return item
                            
            except Exception as e:
                logger.warning(f"ZIP download failed: {e}")
        
        # Create empty directory as fallback
        fallback_dir = temp_dir / 'empty_repo'
        fallback_dir.mkdir()
        return fallback_dir
    
    def _analyze_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze repository structure and files."""
        
        analysis = {
            "files": self._analyze_files(repo_path),
            "structure": self._analyze_structure(repo_path),
            "documentation": self._analyze_documentation(repo_path),
            "dependencies": self._analyze_dependencies(repo_path),
            "testing": self._analyze_testing(repo_path),
            "containerization": self._analyze_containerization(repo_path),
            "ci_cd": self._analyze_ci_cd(repo_path),
            "data": self._analyze_data_availability(repo_path)
        }
        
        return analysis
    
    def _analyze_files(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze file structure."""
        
        files = []
        total_size = 0
        file_types = {}
        
        for file_path in repo_path.rglob('*'):
            if file_path.is_file():
                rel_path = file_path.relative_to(repo_path)
                size = file_path.stat().st_size
                
                files.append({
                    "path": str(rel_path),
                    "size": size,
                    "extension": file_path.suffix.lower()
                })
                
                total_size += size
                ext = file_path.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            "total_files": len(files),
            "total_size": total_size,
            "file_types": file_types,
            "files": files[:100]  # Limit to first 100 files
        }
    
    def _analyze_documentation(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze documentation quality."""
        
        doc_files = []
        readme_exists = False
        license_exists = False
        
        for file_path in repo_path.rglob('*'):
            if file_path.is_file():
                name = file_path.name.lower()
                
                if 'readme' in name:
                    readme_exists = True
                    doc_files.append(str(file_path.relative_to(repo_path)))
                elif 'license' in name:
                    license_exists = True
                    doc_files.append(str(file_path.relative_to(repo_path)))
                elif name.endswith(('.md', '.rst', '.txt')) and any(doc in name for doc in ['doc', 'guide', 'manual']):
                    doc_files.append(str(file_path.relative_to(repo_path)))
        
        return {
            "has_readme": readme_exists,
            "has_license": license_exists,
            "documentation_files": doc_files,
            "documentation_score": self._calculate_doc_score(readme_exists, license_exists, len(doc_files))
        }
    
    def _analyze_dependencies(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze dependency management."""
        
        dependency_files = []
        package_managers = []
        
        # Check for various dependency files
        dep_patterns = {
            'requirements.txt': 'pip',
            'environment.yml': 'conda',
            'Pipfile': 'pipenv',
            'pyproject.toml': 'poetry',
            'package.json': 'npm',
            'Gemfile': 'bundler',
            'pom.xml': 'maven',
            'build.gradle': 'gradle',
            'Cargo.toml': 'cargo'
        }
        
        for pattern, manager in dep_patterns.items():
            matches = list(repo_path.rglob(pattern))
            if matches:
                dependency_files.extend([str(m.relative_to(repo_path)) for m in matches])
                if manager not in package_managers:
                    package_managers.append(manager)
        
        return {
            "has_dependencies": len(dependency_files) > 0,
            "dependency_files": dependency_files,
            "package_managers": package_managers,
            "dependency_score": min(len(dependency_files) * 0.3, 1.0)
        }
    
    def _analyze_testing(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze testing setup."""
        
        test_files = []
        test_frameworks = []
        
        # Look for test files and directories
        for file_path in repo_path.rglob('*'):
            if file_path.is_file():
                name = file_path.name.lower()
                path_str = str(file_path).lower()
                
                if 'test' in name or 'test' in path_str:
                    test_files.append(str(file_path.relative_to(repo_path)))
                    
                    # Detect test frameworks
                    if name.endswith('.py'):
                        content = self._read_file_safe(file_path)
                        if 'pytest' in content:
                            test_frameworks.append('pytest')
                        elif 'unittest' in content:
                            test_frameworks.append('unittest')
        
        return {
            "has_tests": len(test_files) > 0,
            "test_files": test_files[:20],  # Limit output
            "test_frameworks": list(set(test_frameworks)),
            "testing_score": min(len(test_files) * 0.1, 1.0)
        }
    
    def _analyze_containerization(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze containerization setup."""
        
        container_files = []
        
        # Look for container-related files
        container_patterns = ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml', '.dockerignore']
        
        for pattern in container_patterns:
            matches = list(repo_path.rglob(pattern))
            container_files.extend([str(m.relative_to(repo_path)) for m in matches])
        
        return {
            "has_containerization": len(container_files) > 0,
            "container_files": container_files,
            "containerization_score": 1.0 if container_files else 0.0
        }
    
    def _analyze_ci_cd(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze CI/CD setup."""
        
        ci_files = []
        
        # Look for CI/CD files
        ci_patterns = [
            '.github/workflows/*.yml',
            '.github/workflows/*.yaml',
            '.gitlab-ci.yml',
            '.travis.yml',
            'Jenkinsfile',
            '.circleci/config.yml'
        ]
        
        for pattern in ci_patterns:
            matches = list(repo_path.glob(pattern))
            ci_files.extend([str(m.relative_to(repo_path)) for m in matches])
        
        return {
            "has_ci_cd": len(ci_files) > 0,
            "ci_files": ci_files,
            "ci_cd_score": 1.0 if ci_files else 0.0
        }
    
    def _analyze_structure(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze overall repository structure."""
        
        directories = []
        for item in repo_path.rglob('*'):
            if item.is_dir():
                directories.append(str(item.relative_to(repo_path)))
        
        return {
            "total_directories": len(directories),
            "directories": directories[:50],  # Limit output
            "structure_score": min(len(directories) * 0.05, 1.0)
        }
    
    def _analyze_data_availability(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze data availability and management."""
        
        data_files = []
        data_dirs = []
        
        # Look for data-related files and directories
        data_patterns = ['data', 'dataset', 'datasets', 'examples', 'samples']
        
        for pattern in data_patterns:
            matches = list(repo_path.rglob(f'*{pattern}*'))
            for match in matches:
                if match.is_dir():
                    data_dirs.append(str(match.relative_to(repo_path)))
                else:
                    data_files.append(str(match.relative_to(repo_path)))
        
        return {
            "has_data": len(data_files) > 0 or len(data_dirs) > 0,
            "data_files": data_files[:20],
            "data_directories": data_dirs,
            "data_score": 1.0 if (data_files or data_dirs) else 0.0
        }
    
    def _calculate_reproducibility_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall reproducibility score."""
        
        weights = {
            "documentation": 0.25,
            "dependencies": 0.20,
            "testing": 0.15,
            "containerization": 0.15,
            "ci_cd": 0.10,
            "data": 0.10,
            "structure": 0.05
        }
        
        score = 0.0
        for component, weight in weights.items():
            if component in analysis:
                component_score = analysis[component].get(f"{component}_score", 0.0)
                score += component_score * weight
        
        return round(score, 3)
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving reproducibility."""
        
        recommendations = []
        
        # Documentation recommendations
        if not analysis["documentation"]["has_readme"]:
            recommendations.append("Add a comprehensive README file with setup and usage instructions")
        
        if not analysis["documentation"]["has_license"]:
            recommendations.append("Add a license file to clarify usage rights")
        
        # Dependencies recommendations
        if not analysis["dependencies"]["has_dependencies"]:
            recommendations.append("Add dependency management files (requirements.txt, environment.yml, etc.)")
        
        # Testing recommendations
        if not analysis["testing"]["has_tests"]:
            recommendations.append("Add unit tests to verify code functionality")
        
        # Containerization recommendations
        if not analysis["containerization"]["has_containerization"]:
            recommendations.append("Consider adding Docker support for consistent environments")
        
        # CI/CD recommendations
        if not analysis["ci_cd"]["has_ci_cd"]:
            recommendations.append("Set up continuous integration for automated testing")
        
        # Data recommendations
        if not analysis["data"]["has_data"]:
            recommendations.append("Include sample data or clear instructions for data acquisition")
        
        return recommendations
    
    def _calculate_doc_score(self, has_readme: bool, has_license: bool, doc_count: int) -> float:
        """Calculate documentation score."""
        score = 0.0
        if has_readme:
            score += 0.5
        if has_license:
            score += 0.3
        score += min(doc_count * 0.1, 0.2)
        return min(score, 1.0)
    
    def _read_file_safe(self, file_path: Path) -> str:
        """Safely read file content."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            return ""
    
    def _cleanup(self, repo_path: Path):
        """Clean up temporary files."""
        try:
            import shutil
            shutil.rmtree(repo_path.parent)
        except:
            pass
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _create_fallback_assessment(self, repo_url: str, error: str) -> Dict[str, Any]:
        """Create fallback assessment when analysis fails."""
        return {
            "repository_url": repo_url,
            "reproducibility_score": 0.0,
            "error": error,
            "recommendations": [
                "Repository could not be analyzed",
                "Ensure the repository URL is accessible",
                "Check repository permissions"
            ],
            "assessment_date": self._get_timestamp()
        }


def main():
    """CLI interface for reproducibility assistant."""
    import argparse

    parser = argparse.ArgumentParser(description="Assess repository reproducibility")
    parser.add_argument("--repo", "-r", required=True, help="Repository URL")
    parser.add_argument("--output", "-o", required=True, help="Output JSON file path")
    parser.add_argument("--timeout", "-t", type=int, default=300, help="Timeout in seconds")

    args = parser.parse_args()

    try:
        assistant = ReproducibilityAssistant()
        assessment = assistant.assess_repository(args.repo)

        with open(args.output, 'w') as f:
            json.dump(assessment, f, indent=2)

        print(f"✅ Reproducibility assessment completed: {args.output}")
        print(f"📊 Score: {assessment.get('reproducibility_score', 0.0):.3f}")

    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
