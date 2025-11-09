"""Setup configuration for Ready to Start."""

from setuptools import setup, find_packages

setup(
    name="ready-to-start",
    version="0.1.0",
    description="A settings menu navigation puzzle game",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="",
    url="https://github.com/kleer001/ReadyToStart",
    license="MIT",
    packages=find_packages(where=".", include=["src*"]),
    package_dir={"": "."},
    python_requires=">=3.11",
    install_requires=[
        "networkx>=3.1",
        "matplotlib>=3.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "ruff>=0.0.280",
            "pre-commit>=3.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ready-to-start=start:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)
