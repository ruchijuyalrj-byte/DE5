# Library Data Pipeline

![Teaching](https://img.shields.io/badge/module-DE5M5-blue)
![Python Version](https://img.shields.io/badge/python-3.9--3.12-blue.svg)

![Open Issues](https://img.shields.io/github/issues/YOUR_USERNAME/YOUR_REPO)
![Open PRs](https://img.shields.io/github/issues-pr/YOUR_USERNAME/YOUR_REPO)
![Last Commit](https://img.shields.io/github/last-commit/YOUR_USERNAME/YOUR_REPO)
![CI Pipeline Badge](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)

<mark>*Replace `YOUR_USERNAME/YOUR_REPO` with your details*</mark>

## Project Overview
[TODO: Describe the library's data quality problem]

## Architecture
[TODO: Add architecture diagram]

See [docs/architecture/](docs/architecture/) for details.

## Setup

### Git

At a prompt copy and paste the following 2 lines:

```sh
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

### Local Development
```bash
# Clone this repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Confirm the Python 3 version
python --version

# Install dev dependencies (includes test tools, linting, docs)
pip install -r requirements_dev.txt

# Install the package in editable mode
pip install -e .

# Run tests
pytest

# Run tests with a coverage report
pytest --cov=src --cov-report=term-missing

# Run tests with an HTML coverage report
pytest --cov=src --cov-report=html

# Run the pipeline
python -m data_processing.run_pipeline

# To push new code to GitHub
git status
git add .
git commit -m "New changes"
git push
```

## Project Structure
[TODO: Document your folder structure]

## Data Sources
[TODO: Describe the data files]

## Testing
[TODO: Document your testing approach]

Current coverage: [TODO: Add coverage badge]

## CI/CD
This project uses GitHub Actions for continuous integration.

See [.github/workflows/ci.yml](.github/workflows/ci.yml)

## Deployment to Fabric
[TODO: Document Fabric deployment process]

## Team
[TODO: Add team members]
