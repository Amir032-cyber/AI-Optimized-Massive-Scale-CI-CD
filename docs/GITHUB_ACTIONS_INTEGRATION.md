# GitHub Actions Integration Guide

This guide explains how to integrate PTS with GitHub Actions for automatic test selection in your CI/CD pipeline.

## 📋 Prerequisites

- GitHub repository with GitHub Actions enabled
- PTS API key (obtain from your PTS dashboard)
- GitHub Actions workflow file

## 🔑 Setting Up API Key

1. Go to your PTS Dashboard
2. Navigate to "API Keys" section
3. Click "Generate New Key"
4. Copy the key

## 🔐 Adding Secrets to GitHub

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

| Secret Name | Value |
|------------|-------|
| `PTS_API_KEY` | Your PTS API key |
| `PTS_API_URL` | `https://api.pts.example.com` (or your PTS instance URL) |

## 📝 GitHub Actions Workflow

### Basic Setup

Create `.github/workflows/pts-test-selection.yml`:

```yaml
name: PTS Test Selection

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test-selection:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Get changed files
        id: changed-files
        uses: tj-actions/changed-files@v35
        with:
          files: |
            src/**
            tests/**

      - name: Call PTS API for test selection
        id: pts-selection
        env:
          PTS_API_KEY: ${{ secrets.PTS_API_KEY }}
          PTS_API_URL: ${{ secrets.PTS_API_URL }}
        run: |
          CHANGED_FILES="${{ steps.changed-files.outputs.all_changed_files }}"
          
          curl -X POST "$PTS_API_URL/api/v1/predict" \
            -H "Authorization: Bearer $PTS_API_KEY" \
            -H "Content-Type: application/json" \
            -d '{
              "commit_hash": "${{ github.sha }}",
              "repository_url": "${{ github.server_url }}/${{ github.repository }}",
              "changed_files": ["'"${CHANGED_FILES// /\", \"}"'"]
            }' > pts_response.json
          
          echo "response=$(cat pts_response.json)" >> $GITHUB_OUTPUT

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run selected tests
        run: |
          SELECTED_TESTS=$(jq -r '.selected_tests[]' pts_response.json | tr '\n' ' ')
          pytest $SELECTED_TESTS -v
```

### Advanced Setup with Caching

```yaml
name: PTS Test Selection with Caching

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test-selection:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']

    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Get changed files
        id: changed-files
        uses: tj-actions/changed-files@v35

      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Call PTS API
        id: pts
        env:
          PTS_API_KEY: ${{ secrets.PTS_API_KEY }}
          PTS_API_URL: ${{ secrets.PTS_API_URL }}
        run: |
          python scripts/github_integration.py \
            --commit ${{ github.sha }} \
            --repo ${{ github.repository }} \
            --changed-files "${{ steps.changed-files.outputs.all_changed_files }}"

      - name: Run selected tests
        run: |
          pytest $(cat selected_tests.txt) -v --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

## 🔧 Python Integration Script

Create `scripts/github_integration.py`:

```python
#!/usr/bin/env python3

import os
import json
import argparse
import requests
from typing import List

def get_selected_tests(
    commit_hash: str,
    repo_url: str,
    changed_files: List[str]
) -> List[str]:
    """
    Call PTS API to get selected tests.
    """
    api_key = os.getenv("PTS_API_KEY")
    api_url = os.getenv("PTS_API_URL")
    
    if not api_key or not api_url:
        raise ValueError("PTS_API_KEY and PTS_API_URL environment variables are required")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "commit_hash": commit_hash,
        "repository_url": repo_url,
        "changed_files": changed_files
    }
    
    response = requests.post(
        f"{api_url}/api/v1/predict",
        headers=headers,
        json=payload
    )
    
    response.raise_for_status()
    data = response.json()
    
    return data.get("selected_tests", [])

def main():
    parser = argparse.ArgumentParser(description="PTS GitHub Integration")
    parser.add_argument("--commit", required=True, help="Commit hash")
    parser.add_argument("--repo", required=True, help="Repository URL")
    parser.add_argument("--changed-files", required=True, help="Changed files (space-separated)")
    
    args = parser.parse_args()
    
    changed_files = args.changed_files.split()
    
    try:
        selected_tests = get_selected_tests(
            commit_hash=args.commit,
            repo_url=args.repo,
            changed_files=changed_files
        )
        
        # Save selected tests to file
        with open("selected_tests.txt", "w") as f:
            f.write(" ".join(selected_tests))
        
        print(f"Selected {len(selected_tests)} tests")
        for test in selected_tests:
            print(f"  - {test}")
            
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
```

## 📊 Monitoring Results

Add a step to post results as a comment on PRs:

```yaml
- name: Post results comment
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v6
  with:
    script: |
      const fs = require('fs');
      const response = JSON.parse(fs.readFileSync('pts_response.json', 'utf8'));
      
      const comment = `## PTS Test Selection Results
      
      **Tests Selected:** ${response.selected_tests.length}
      **Prediction Time:** ${response.prediction_time_ms.toFixed(2)}ms
      **Model Version:** ${response.model_version}
      
      ### Selected Tests
      \`\`\`
      ${response.selected_tests.join('\n')}
      \`\`\`
      `;
      
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: comment
      });
```

## 🚀 Best Practices

1. **Cache Dependencies**: Use `actions/setup-python@v4` with cache enabled
2. **Fail Fast**: Run selected tests first before full test suite
3. **Monitor Performance**: Track test selection time and accuracy
4. **Error Handling**: Fallback to full test suite if PTS fails
5. **Security**: Use GitHub Secrets for API keys, never commit them

## 🔄 Fallback Strategy

If PTS API is unavailable, run all tests:

```yaml
- name: Run tests (with fallback)
  run: |
    if [ -f selected_tests.txt ]; then
      pytest $(cat selected_tests.txt) -v
    else
      echo "PTS unavailable, running all tests"
      pytest tests/ -v
    fi
```

## 📈 Performance Metrics

Monitor these metrics in your workflow:

- **Test Selection Time**: Time taken by PTS API
- **Test Reduction**: Percentage of tests eliminated
- **Accuracy**: Percentage of bugs caught
- **Pipeline Time**: Total CI/CD execution time

## 🐛 Troubleshooting

### API Key Not Found
```yaml
- name: Verify secrets
  run: |
    if [ -z "${{ secrets.PTS_API_KEY }}" ]; then
      echo "Error: PTS_API_KEY secret not set"
      exit 1
    fi
```

### Network Issues
```yaml
- name: Test API connectivity
  run: |
    curl -I "${{ secrets.PTS_API_URL }}/api/v1/health" \
      -H "Authorization: Bearer ${{ secrets.PTS_API_KEY }}"
```

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PTS API Documentation](../README.md#api-documentation)
- [GitHub Secrets Management](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

For more help, visit our [GitHub Issues](https://github.com/Amir032-cyber/AI-Optimized-Massive-Scale-CI-CD/issues)
