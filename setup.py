"""Setup script for the augment-adam package."""

import os
import re
from setuptools import setup, find_packages

# Read the version from pyproject.toml
with open("pyproject.toml", "r", encoding="utf-8") as fh:
    version_match = re.search(r'version = "([^"]+)"', fh.read())
    if version_match:
        version = version_match.group(1)
    else:
        version = "0.1.0"  # Default version if not found

setup(
    name="augment-adam",
    version=version,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.9,<3.12",
    install_requires=[
        "faiss-cpu>=1.7.0",  # Use faiss-gpu for GPU support
        "sentence-transformers>=2.2.0",
        "scikit-learn>=1.0.0",
        "numpy>=1.20.0",
        "pydantic>=2.0.0",
        "redis>=4.0.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.20.0",
        "tqdm>=4.65.0",
        "aiohttp>=3.8.0",
        "asyncio>=3.4.3",
        "rich>=13.7.0",
        "typer>=0.9.0",
        "psutil>=5.9.0",
        "pyyaml>=6.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "dspy-ai>=2.6.18",
        "chromadb>=0.4.22",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=1.3.0",
            "pre-commit>=3.5.0",
            "ruff>=0.1.6",
        ],
        "neo4j": [
            "neo4j>=5.0.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings>=0.20.0",
            "mkdocs-jupyter>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "augment-adam=augment_adam.cli:app",
        ],
    },
    author="Augment Adam Team",
    author_email="info@augment-adam.com",
    description="An intelligent assistant with advanced memory capabilities",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="ai, assistant, memory, faiss, neo4j, vector, graph, embedding",
    url="https://github.com/theinterneti/augment-adam",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="MIT",
)
