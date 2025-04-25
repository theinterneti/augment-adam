"""Setup script for the augment-adam package."""

from setuptools import setup, find_packages

# Read the version from augment_adam/__init__.py
with open("augment_adam/__init__.py", "r", encoding="utf-8") as fh:
    for line in fh:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"\'')
            break

setup(
    name="augment-adam",
    version=version,
    packages=find_packages(),
    install_requires=[
        "faiss-cpu>=1.7.0",  # Use faiss-gpu for GPU support
        "sentence-transformers>=2.2.0",
        "scikit-learn>=1.0.0",
        "numpy>=1.20.0",
        "neo4j>=5.0.0",
        "pydantic>=2.0.0",
        "redis>=4.0.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.20.0",
        "tqdm>=4.65.0",
        "aiohttp>=3.8.0",
        "asyncio>=3.4.3",
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
        ],
        "neo4j": [
            "neo4j>=5.0.0",
        ],
    },
    author="Augment Adam Team",
    author_email="info@augment-adam.com",
    description="An intelligent assistant with advanced memory capabilities",
    long_description="""
    Augment Adam is an intelligent assistant that uses advanced memory systems
    to provide more contextual and personalized responses.

    It features:
    - FAISS-based vector memory for efficient similarity search
    - Neo4j-based graph memory for complex relationships
    - Modular architecture for easy extension
    """,
    long_description_content_type="text/markdown",
    keywords="ai, assistant, memory, faiss, neo4j",
    url="https://github.com/augment-adam/augment-adam",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
