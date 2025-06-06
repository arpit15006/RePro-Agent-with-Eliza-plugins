# 🔁 Reproducibility Assistant Plugin

An Eliza-compatible plugin that analyzes GitHub repositories for scientific reproducibility and generates comprehensive assessment reports.

## 🎯 Purpose

Validates the reproducibility of scientific code repositories by analyzing structure, dependencies, documentation, and execution capabilities.

## ✨ Features

- **Repository Analysis**: Clones and analyzes GitHub repositories
- **Dependency Detection**: Identifies and validates project dependencies
- **Documentation Assessment**: Evaluates README, setup instructions, and documentation quality
- **Code Structure Evaluation**: Analyzes project organization and best practices
- **Reproducibility Scoring**: Generates quantitative reproducibility scores (0.0-1.0)
- **Detailed Reporting**: Provides actionable recommendations for improvement

## 📥 Input

- GitHub repository URL
- Optional: Analysis timeout (default: 300 seconds)

## 📤 Output

```json
{
  "repository_url": "https://github.com/user/repo",
  "reproducibility_score": 0.85,
  "assessment": {
    "has_readme": true,
    "has_requirements": true,
    "has_dockerfile": false,
    "has_tests": true,
    "documentation_quality": "good"
  },
  "recommendations": [
    "Add Dockerfile for containerization",
    "Include environment.yml for conda users"
  ],
  "file_analysis": {
    "total_files": 45,
    "code_files": 23,
    "config_files": 8
  }
}
```

## 🚀 Usage

### Command Line
```bash
python main.py --repo https://github.com/user/repo --output report.json --timeout 300
```

### Python API
```python
from reproducibility_assistant.main import ReproducibilityAssistant

assistant = ReproducibilityAssistant()
report = assistant.assess_repository("https://github.com/user/repo")
```

## 🔧 Dependencies

- requests>=2.28.0
- subprocess
- pathlib
- json
- logging
- tempfile

## 📋 Requirements

- Python 3.8+
- Git (for repository cloning)
- Internet connection

## 🏷️ Tags

- reproducibility
- github-analysis
- code-validation
- scientific-software
