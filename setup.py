from setuptools import setup, find_packages

setup(
    name="pts",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Dépendances de production listées dans requirements.txt ou pyproject.toml
        # Pour la simplicité, on se base sur pyproject.toml
    ],
    author="AI Development Assistant",
    author_email="ai-assistant@pts.dev",
    description="Enterprise-Grade CI/CD Optimization with Machine Learning",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Amir032-cyber/AI-Optimized-Massive-Scale-CI-CD",
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
)
