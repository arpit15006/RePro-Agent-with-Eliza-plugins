#!/usr/bin/env python3
"""
Setup script for RePRO-Agent
Scientific Reproducibility and Hypothesis Generation Pipeline
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r') as f:
        requirements = [
            line.strip() for line in f 
            if line.strip() and not line.startswith('#') and '>=' in line
        ]

setup(
    name="repro-agent",
    version="0.1.0",
    description="Scientific Reproducibility and Hypothesis Generation Pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RePRO-Agent Team",
    author_email="contact@repro-agent.org",
    url="https://github.com/yourusername/eliza-repro-hypothesis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "repro-agent=pipeline:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="scientific-computing reproducibility knowledge-graph hypothesis-generation eliza",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/eliza-repro-hypothesis/issues",
        "Source": "https://github.com/yourusername/eliza-repro-hypothesis",
        "Documentation": "https://github.com/yourusername/eliza-repro-hypothesis/blob/main/README.md",
    },
)
