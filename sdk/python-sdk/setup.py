"""Setup configuration for Python SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="agentchain-trust-sdk",
    version="1.0.0",
    author="Alwin",
    author_email="support@agentchain.ai",
    description="Python SDK for AgentChain Trust Layer API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alwin123098/Agentchainv2",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "async": ["aiohttp>=3.8.0"],
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentchain-trust=agentchain_trust_sdk.cli:main",
        ],
    },
)