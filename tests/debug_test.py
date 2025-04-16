import pytest
from unittest.mock import Mock, patch
import requests
from ross_cli.cli import install_command

@pytest.fixture
def mock_github_api(mocker):
    """Mock GitHub API responses"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "name": "ross_cli",
        "clone_url": "https://github.com/ResearchOS/ross_cli.git",
        "default_branch": "main"
    }
    mock_response.status_code = 200
    mock_get = mocker.patch('requests.get', return_value=mock_response)
    return mock_get

@pytest.fixture
def mock_git_clone(mocker):
    """Mock Git clone operations"""
    return mocker.patch('git.Repo.clone_from')

def test_install_command_success(mock_github_api, mock_git_clone, tmp_path):
    """Test successful package installation"""
    with patch('os.getcwd', return_value=str(tmp_path)):
        result = install_command("ross_cli")
        
        # Verify GitHub API was called
        mock_github_api.assert_called_once()
        
        # Verify git clone was attempted
        mock_git_clone.assert_called_once()
        
        # Add assertions based on expected behavior
        assert result is None  # Modify based on actual return value

def test_install_command_github_error(mocker, tmp_path):
    """Test installation with GitHub API error"""
    # Mock GitHub API to return an error
    mock_response = Mock()
    mock_response.status_code = 404
    mocker.patch('requests.get', return_value=mock_response)
    
    with patch('os.getcwd', return_value=str(tmp_path)):
        with pytest.raises(Exception) as exc_info:
            install_command("ross_cli")
        assert "GitHub API error" in str(exc_info.value)

def test_install_command_network_error(mocker, tmp_path):
    """Test installation with network error"""
    # Mock network error
    mocker.patch('requests.get', side_effect=requests.exceptions.ConnectionError)
    
    with patch('os.getcwd', return_value=str(tmp_path)):
        with pytest.raises(requests.exceptions.ConnectionError):
            install_command("ross_cli")