from setuptools import setup, find_packages

setup(
    name="ai-cad-automation",
    version="0.1.0",
    description="AI-assisted architectural floor plan generation system",
    author="AI-CAD Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "ezdxf>=1.0.0",
        "openai>=1.0.0",
        "anthropic>=0.3.0",
        "numpy>=1.21.0",
        "shapely>=1.8.0",
        "networkx>=2.8.0",
        "pydantic>=1.8.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5",
        "matplotlib>=3.5.0",
        "redis>=4.0.0",
        "sqlalchemy>=1.4.0",
        "alembic>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)