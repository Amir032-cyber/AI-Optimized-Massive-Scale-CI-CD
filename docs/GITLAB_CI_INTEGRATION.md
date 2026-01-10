# GitLab CI Integration Guide

Complete guide for integrating PTS with GitLab CI/CD pipelines.

## 📋 Prerequisites

- GitLab project with CI/CD enabled
- PTS API key
- `.gitlab-ci.yml` file in repository root

## 🔑 Setting Up API Key

1. Go to your PTS Dashboard
2. Navigate to "API Keys" section
3. Generate a new key and copy it

## 🔐 Adding Variables to GitLab

1. Go to your GitLab project
2. Click **Settings** → **CI/CD** → **Variables**
3. Add the following variables:

| Variable Name | Value | Protected | Masked |
|--------------|-------|-----------|--------|
| `PTS_API_KEY` | Your PTS API key | ✓ | ✓ |
| `PTS_API_URL` | Your PTS API URL | ✓ | ✗ |

## 📝 GitLab CI Configuration

### Basic Setup

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test-selection
  - test
  - report

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

before_script:
  - python --version
  - pip install --upgrade pip
  - pip install -r requirements.txt

test-selection:
  stage: test-selection
  image: python:3.10
  script:
    # Get changed files
    - export CHANGED_FILES=$(git diff --name-only $CI_MERGE_REQUEST_DIFF_BASE_SHA HEAD)
    
    # Call PTS API
    - |
      curl -X POST "$PTS_API_URL/api/v1/predict" \
        -H "Authorization: Bearer $PTS_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
          "commit_hash": "'$CI_COMMIT_SHA'",
          "repository_url": "'$CI_PROJECT_URL'",
          "changed_files": ["'$(echo $CHANGED_FILES | sed 's/ /", "/g')'"]
        }' > pts_response.json
    
    # Extract selected tests
    - cat pts_response.json | jq '.selected_tests[]' > selected_tests.txt
  
  artifacts:
    paths:
      - pts_response.json
      - selected_tests.txt
    expire_in: 1 day
  only:
    - merge_requests
    - main
    - develop

run-selected-tests:
  stage: test
  image: python:3.10
  needs:
    - test-selection
  script:
    - |
      if [ -s selected_tests.txt ]; then
        TESTS=$(cat selected_tests.txt | tr '\n' ' ')
        pytest $TESTS -v --cov=src --cov-report=xml
      else
        echo "No tests selected, running full suite"
        pytest tests/ -v --cov=src --cov-report=xml
      fi
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - htmlcov/
    expire_in: 30 days

test-report:
  stage: report
  image: python:3.10
  needs:
    - test-selection
    - run-selected-tests
  script:
    - |
      echo "## PTS Test Selection Report" > report.md
      echo "" >> report.md
      echo "**Commit:** $CI_COMMIT_SHA" >> report.md
      echo "**Branch:** $CI_COMMIT_BRANCH" >> report.md
      echo "" >> report.md
      echo "### Test Selection Results" >> report.md
      cat pts_response.json | jq . >> report.md
  artifacts:
    paths:
      - report.md
    expire_in: 30 days
  only:
    - merge_requests
```

### Advanced Setup with Multiple Python Versions

```yaml
stages:
  - test-selection
  - test
  - report

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

test-selection:
  stage: test-selection
  image: python:3.10
  script:
    - python scripts/gitlab_integration.py
  artifacts:
    paths:
      - selected_tests.txt
      - pts_response.json
    expire_in: 1 day

test:python3.8:
  stage: test
  image: python:3.8
  needs:
    - test-selection
  script:
    - pip install -r requirements.txt
    - |
      if [ -s selected_tests.txt ]; then
        pytest $(cat selected_tests.txt) -v
      else
        pytest tests/ -v
      fi

test:python3.9:
  stage: test
  image: python:3.9
  needs:
    - test-selection
  script:
    - pip install -r requirements.txt
    - |
      if [ -s selected_tests.txt ]; then
        pytest $(cat selected_tests.txt) -v
      else
        pytest tests/ -v
      fi

test:python3.10:
  stage: test
  image: python:3.10
  needs:
    - test-selection
  script:
    - pip install -r requirements.txt
    - |
      if [ -s selected_tests.txt ]; then
        pytest $(cat selected_tests.txt) -v
      else
        pytest tests/ -v
      fi

test:python3.11:
  stage: test
  image: python:3.11
  needs:
    - test-selection
  script:
    - pip install -r requirements.txt
    - |
      if [ -s selected_tests.txt ]; then
        pytest $(cat selected_tests.txt) -v
      else
        pytest tests/ -v
      fi
```

## 🔧 Python Integration Script

Create `scripts/gitlab_integration.py`:

```python
#!/usr/bin/env python3

import os
import json
import requests
import subprocess
from typing import List

def get_changed_files() -> List[str]:
    """Get list of changed files in the merge request."""
    try:
        # For merge requests
        base_sha = os.getenv("CI_MERGE_REQUEST_DIFF_BASE_SHA")
        head_sha = os.getenv("CI_COMMIT_SHA")
        
        if base_sha and head_sha:
            result = subprocess.run(
                ["git", "diff", "--name-only", base_sha, head_sha],
                capture_output=True,
                text=True
            )
            return result.stdout.strip().split('\n')
    except Exception as e:
        print(f"Error getting changed files: {e}")
    
    return []

def get_selected_tests() -> List[str]:
    """Call PTS API to get selected tests."""
    api_key = os.getenv("PTS_API_KEY")
    api_url = os.getenv("PTS_API_URL")
    commit_sha = os.getenv("CI_COMMIT_SHA")
    project_url = os.getenv("CI_PROJECT_URL")
    
    if not api_key or not api_url:
        raise ValueError("PTS_API_KEY and PTS_API_URL variables are required")
    
    changed_files = get_changed_files()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "commit_hash": commit_sha,
        "repository_url": project_url,
        "changed_files": changed_files
    }
    
    response = requests.post(
        f"{api_url}/api/v1/predict",
        headers=headers,
        json=payload
    )
    
    response.raise_for_status()
    data = response.json()
    
    # Save response
    with open("pts_response.json", "w") as f:
        json.dump(data, f, indent=2)
    
    return data.get("selected_tests", [])

def main():
    try:
        selected_tests = get_selected_tests()
        
        # Save selected tests
        with open("selected_tests.txt", "w") as f:
            for test in selected_tests:
                f.write(f"{test}\n")
        
        print(f"Selected {len(selected_tests)} tests")
        for test in selected_tests:
            print(f"  - {test}")
            
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
```

## 📊 Merge Request Integration

Add to `.gitlab-ci.yml` to post results as MR comments:

```yaml
report:
  stage: report
  image: python:3.10
  needs:
    - test-selection
  script:
    - |
      python -c "
      import json
      import os
      
      with open('pts_response.json', 'r') as f:
          data = json.load(f)
      
      comment = f'''## PTS Test Selection Results
      
      **Tests Selected:** {len(data['selected_tests'])}
      **Prediction Time:** {data['prediction_time_ms']:.2f}ms
      **Model Version:** {data['model_version']}
      
      ### Selected Tests
      \`\`\`
      {chr(10).join(data['selected_tests'])}
      \`\`\`
      '''
      
      # Write to file for GitLab to post
      with open('mr_comment.txt', 'w') as f:
          f.write(comment)
      "
  artifacts:
    paths:
      - mr_comment.txt
    expire_in: 1 day
  only:
    - merge_requests
```

## 🚀 Best Practices

1. **Use `needs` keyword**: Ensure test-selection runs before tests
2. **Cache dependencies**: Speed up pipeline execution
3. **Set timeouts**: Prevent hanging jobs
4. **Use artifacts**: Share data between jobs
5. **Error handling**: Fallback to full test suite if PTS fails

## 🔄 Fallback Strategy

```yaml
run-tests:
  stage: test
  script:
    - |
      if [ -s selected_tests.txt ]; then
        echo "Running selected tests..."
        pytest $(cat selected_tests.txt) -v
      else
        echo "Fallback: Running full test suite"
        pytest tests/ -v
      fi
  retry:
    max: 2
    when:
      - runner_system_failure
      - stuck_or_timeout_failure
```

## 📈 Performance Optimization

```yaml
test:
  stage: test
  parallel: 4  # Run tests in parallel
  script:
    - pytest tests/ -v --dist=loadscope -n auto
  timeout: 30 minutes
```

## 🐛 Troubleshooting

### API Key Not Found
```yaml
test-selection:
  script:
    - |
      if [ -z "$PTS_API_KEY" ]; then
        echo "Error: PTS_API_KEY not set"
        exit 1
      fi
```

### Network Issues
```yaml
test-selection:
  retry:
    max: 3
    when:
      - api_failure
      - runner_system_failure
```

## 📚 Additional Resources

- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [GitLab CI Variables](https://docs.gitlab.com/ee/ci/variables/)
- [PTS API Documentation](../README.md)

---

For support, visit our [GitHub Issues](https://github.com/Amir032-cyber/AI-Optimized-Massive-Scale-CI-CD/issues)
