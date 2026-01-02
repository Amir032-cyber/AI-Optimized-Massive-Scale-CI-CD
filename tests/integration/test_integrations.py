import pytest
from unittest.mock import patch, MagicMock
import requests

from pts.integrations.github import GitHubIntegration
from pts.integrations.gitlab import GitLabIntegration
from pts.integrations.jenkins import JenkinsIntegration


@pytest.fixture
def mock_requests_get():
    """Mock la fonction requests.get pour simuler les réponses d'API."""
    with patch("requests.get") as mock_get:
        yield mock_get


# --- Tests GitHubIntegration ---

def test_github_get_commit_details_success(mock_requests_get):
    """Teste la récupération réussie des détails d'un commit GitHub."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "sha": "abc1234",
        "commit": {
            "author": {"name": "Test User", "date": "2023-01-01T00:00:00Z"},
            "message": "feat: new feature",
        },
        "files": [
            {"filename": "file1.py"},
            {"filename": "file2.py"},
        ],
    }
    mock_requests_get.return_value = mock_response
    
    integration = GitHubIntegration(token="fake_token", repo_owner="owner", repo_name="repo")
    details = integration.get_commit_details("abc1234")
    
    assert details is not None
    assert details["sha"] == "abc1234"
    assert "file1.py" in details["changed_files"]
    assert len(details["changed_files"]) == 2


def test_github_get_commit_details_failure(mock_requests_get):
    """Teste la récupération échouée des détails d'un commit GitHub."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_requests_get.return_value = mock_response
    
    integration = GitHubIntegration(token="fake_token", repo_owner="owner", repo_name="repo")
    details = integration.get_commit_details("nonexistent_sha")
    
    assert details is None


# --- Tests GitLabIntegration ---

def test_gitlab_get_commit_details_success(mock_requests_get):
    """Teste la récupération réussie des détails d'un commit GitLab."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "def5678",
        "author_name": "GitLab User",
        "committed_date": "2023-01-01T00:00:00.000Z",
        "message": "fix: bug fix",
    }
    mock_requests_get.return_value = mock_response
    
    integration = GitLabIntegration(private_token="fake_token", project_id=123)
    details = integration.get_commit_details("def5678")
    
    assert details is not None
    assert details["id"] == "def5678"


# --- Tests JenkinsIntegration ---

def test_jenkins_get_job_info_success(mock_requests_get):
    """Teste la récupération réussie des informations d'un job Jenkins."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "build-job",
        "lastBuild": {"number": 10},
    }
    mock_requests_get.return_value = mock_response
    
    integration = JenkinsIntegration(base_url="http://jenkins.local", username="user", api_token="token")
    info = integration.get_job_info("build-job")
    
    assert info is not None
    assert info["name"] == "build-job"
