# 🔁 Reproducibility Assistant Plugin

Assesses the reproducibility of scientific code repositories by analyzing structure, dependencies, and execution success.

## Features

- **Repository Analysis**: Examines code structure, documentation, and dependencies
- **Execution Testing**: Tests main scripts for successful execution
- **Docker Integration**: Can containerize repositories for isolated testing
- **Scoring System**: Provides quantitative reproducibility scores (0.0-1.0)
- **Recommendations**: Suggests improvements for better reproducibility
- **Eliza Compatible**: Follows Eliza plugin specification

## Installation

```bash
cd reproducibility-assistant
pip install -r requirements.txt
```

### Docker Support (Optional)

For full functionality including containerized testing:

```bash
# Install Docker
# On Ubuntu/Debian:
sudo apt-get install docker.io

# Add user to docker group
sudo usermod -aG docker $USER
```

## Usage

### Command Line

```bash
# Basic assessment
python main.py --repo https://github.com/user/repo

# Custom output file
python main.py --repo https://github.com/user/repo --output my_report.json

# Custom timeout for script execution
python main.py --repo https://github.com/user/repo --timeout 600
```

### Python API

```python
from main import ReproducibilityAssistant

# Initialize assistant
assistant = ReproducibilityAssistant(timeout=300)

# Assess repository
report = assistant.assess_repository("https://github.com/user/repo")

# Print score
print(f"Reproducibility Score: {report['reproducibility_score']:.2f}")
```

## Assessment Criteria

The reproducibility score (0.0-1.0) is calculated based on:

### Documentation (20%)
- ✅ README.md file exists
- ✅ Clear usage instructions

### Dependency Management (20%)
- ✅ requirements.txt, environment.yml, or setup.py
- ✅ Version specifications

### Containerization (10%)
- ✅ Dockerfile present
- ✅ Container builds successfully

### Code Organization (20%)
- ✅ Clear entry point scripts (main.py, run.py, etc.)
- ✅ Organized Python modules

### Execution Success (30%)
- ✅ Main scripts run without errors
- ✅ Help/usage information available
- ✅ No missing dependencies

## Output Format

```json
{
  "repository_url": "https://github.com/user/repo",
  "assessment_timestamp": "2024-01-01T12:00:00",
  "reproducibility_score": 0.85,
  "repository_analysis": {
    "has_readme": true,
    "has_requirements": true,
    "has_dockerfile": false,
    "python_files": ["main.py", "utils.py"],
    "main_scripts": ["main.py"],
    "data_files": ["data.csv"]
  },
  "dependencies": ["numpy>=1.20.0", "pandas>=1.3.0"],
  "execution_results": {
    "execution_tests": [
      {
        "script": "main.py",
        "success": true,
        "exit_code": 0,
        "execution_time": 2.5
      }
    ],
    "success_rate": 1.0
  },
  "recommendations": [
    "Consider adding a Dockerfile for containerized execution"
  ]
}
```

## Common Issues and Solutions

### Git Clone Failures
- Ensure repository URL is correct and accessible
- Check network connectivity
- Verify repository is public or provide authentication

### Docker Issues
- Ensure Docker daemon is running
- Check user permissions for Docker access
- Verify Docker installation

### Execution Timeouts
- Increase timeout value for long-running scripts
- Check for infinite loops or blocking operations
- Consider testing with smaller datasets

## Integration with Other Plugins

This plugin works with:
- **Manuscript Extractor**: Links papers to their code repositories
- **Knowledge Graph Builder**: Stores reproducibility scores as graph properties
- **Hypothesis Generator**: Uses reproducibility data for research suggestions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see [LICENSE](../LICENSE) file for details.
