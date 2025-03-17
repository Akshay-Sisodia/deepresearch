from setuptools import setup, find_packages
import os

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="deepresearch",
    version="0.1.0",
    author="Akshay Sisodia",
    author_email="your.email@example.com",
    description="AI-powered research assistant that helps you conduct comprehensive research on any topic",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Akshay-Sisodia/deepresearch",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "deepresearch=scripts.run_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["static/**/*", ".streamlit/**/*"],
    },
)