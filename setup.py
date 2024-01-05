import re
from setuptools import setup, find_packages


VERSION = '0.0.1'


with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="",
    version=VERSION,
    author="",
    author_email="",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vivarium-collective/vivarium-bayesian-mca",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
    install_requires=[
        # List your package dependencies here
        "process-bigraph",
        "cobra"
    ],
)
