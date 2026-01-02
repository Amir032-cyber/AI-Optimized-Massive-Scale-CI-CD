import pandas as pd
import pytest
from datetime import datetime
from unittest.mock import patch

from pts.data.collector import DataCollector
from pts.data.processor import DataProcessor
from pts.data.validator import DataValidator


@pytest.fixture
def mock_raw_data():
    """Fournit des données brutes factices pour les tests."""
    raw_commits = {
        "commit_hash": [f"hash_{i}" for i in range(10)],
        "author_name": ["Alice", "Bob", "Alice", "Charlie", "Bob", "Alice", "Charlie", "Bob", "Alice", "Charlie"],
        "committed_date": [1672531200 + i * 3600 for i in range(10)], # Timestamps
        "churn": [10, 50, 20, 100, 5, 15, 30, 60, 25, 40],
        "files_changed": [2, 5, 1, 8, 1, 3, 2, 6, 4, 3],
        "message": ["feat: a", "fix: b", "docs: c", "feat: d", "fix: e", "refactor: f", "test: g", "chore: h", "feat: i", "fix: j"],
        "insertions": [5, 25, 10, 50, 2, 7, 15, 30, 12, 20],
        "deletions": [5, 25, 10, 50, 3, 8, 15, 30, 13, 20],
    }
    raw_results = {
        "test_id": [f"test_{i}" for i in range(20)],
        "commit_hash": [f"hash_{i % 10}" for i in range(20)],
        "test_failed": [1 if i % 5 == 0 else 0 for i in range(20)],
    }
    
    return {
        "commit_history": pd.DataFrame(raw_commits),
        "test_results": pd.DataFrame(raw_results),
    }


@patch("pts.data.collector.GitMiner")
def test_data_collector_commit_history(MockGitMiner):
    """Teste la collecte de l'historique des commits."""
    mock_miner = MockGitMiner.return_value
    mock_miner.mine_history.return_value = pd.DataFrame({"commit_hash": ["a", "b"]})
    
    collector = DataCollector(repo_path=".")
    df = collector.collect_commit_history(max_commits=2)
    
    assert len(df) == 2
    assert "commit_hash" in df.columns


def test_data_processor_cleaning(mock_raw_data):
    """Teste le nettoyage et la transformation des données de commits."""
    processor = DataProcessor()
    commit_df = mock_raw_data["commit_history"]
    
    processed_df = processor.clean_and_transform_commits(commit_df)
    
    assert "day_of_week" in processed_df.columns
    assert "hour_of_day" in processed_df.columns
    assert "author_experience" in processed_df.columns
    assert processed_df["author_experience"].max() == 4 # Alice a 4 commits


def test_data_processor_merging(mock_raw_data):
    """Teste la fusion des données de commits et de résultats."""
    processor = DataProcessor()
    commit_df = processor.clean_and_transform_commits(mock_raw_data["commit_history"])
    results_df = mock_raw_data["test_results"]
    
    merged_df = processor.merge_data(commit_df, results_df)
    
    assert len(merged_df) == len(results_df)
    assert "author_name" in merged_df.columns
    assert "test_id" in merged_df.columns
    assert "test_failed" in merged_df.columns


def test_data_validator_valid_data():
    """Teste la validation avec des données valides."""
    required = ["commit_id", "test_id", "test_failed", "churn"]
    validator = DataValidator(required_columns=required)
    
    valid_data = pd.DataFrame({
        "commit_id": ["a", "b"],
        "test_id": ["t1", "t2"],
        "test_failed": [0, 1],
        "churn": [10.0, 20.0],
    })
    
    assert validator.validate(valid_data) is True


def test_data_validator_missing_column():
    """Teste la validation avec une colonne manquante."""
    required = ["commit_id", "test_id", "test_failed", "churn"]
    validator = DataValidator(required_columns=required)
    
    invalid_data = pd.DataFrame({
        "commit_id": ["a", "b"],
        "test_id": ["t1", "t2"],
        "test_failed": [0, 1],
    })
    
    assert validator.validate(invalid_data) is False


def test_data_validator_missing_values():
    """Teste la validation avec des valeurs manquantes."""
    required = ["commit_id", "test_id", "test_failed", "churn"]
    validator = DataValidator(required_columns=required)
    
    invalid_data = pd.DataFrame({
        "commit_id": ["a", None],
        "test_id": ["t1", "t2"],
        "test_failed": [0, 1],
        "churn": [10.0, 20.0],
    })
    
    assert validator.validate(invalid_data) is False
