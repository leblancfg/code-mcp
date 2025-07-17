import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.code_mcp.gcf_deployer import GCFDeployer


@pytest.fixture
def deployer():
    return GCFDeployer(project_id="test-project")


def test_deployer_initialization(deployer):
    assert deployer.project_id == "test-project"
    assert deployer.function_name == "code-interpreter"
    assert deployer.region == "us-central1"


def test_check_gcloud_installed(deployer):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        assert deployer.check_gcloud_installed() is True
        mock_run.assert_called_once_with(
            ["gcloud", "--version"],
            capture_output=True,
            text=True
        )


def test_check_gcloud_not_installed(deployer):
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError()
        
        assert deployer.check_gcloud_installed() is False


def test_get_current_project(deployer):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="my-gcp-project\n"
        )
        
        project = deployer.get_current_project()
        assert project == "my-gcp-project"
        
        mock_run.assert_called_once_with(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True
        )


def test_deploy_function(deployer):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        result = deployer.deploy_function()
        assert result is True
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        
        assert call_args[0] == "gcloud"
        assert call_args[1] == "functions"
        assert call_args[2] == "deploy"
        assert call_args[3] == "code-interpreter"
        assert "--runtime=python311" in call_args
        assert "--trigger-http" in call_args
        assert "--allow-unauthenticated" in call_args
        assert "--entry-point=execute_code" in call_args
        assert f"--source={deployer.gcf_source_dir}" in call_args


def test_deploy_function_failure(deployer):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="Deployment failed"
        )
        
        result = deployer.deploy_function()
        assert result is False


def test_get_function_url(deployer):
    expected_url = "https://us-central1-test-project.cloudfunctions.net/code-interpreter"
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=expected_url + "\n"
        )
        
        url = deployer.get_function_url()
        assert url == expected_url
        
        mock_run.assert_called_once_with(
            [
                "gcloud", "functions", "describe", "code-interpreter",
                "--region", "us-central1",
                "--format", "value(httpsTrigger.url)",
                "--project=test-project"
            ],
            capture_output=True,
            text=True
        )


def test_full_deployment_flow(deployer):
    with patch.object(deployer, 'check_gcloud_installed', return_value=True), \
         patch.object(deployer, 'get_current_project', return_value="test-project"), \
         patch.object(deployer, 'deploy_function', return_value=True), \
         patch.object(deployer, 'get_function_url', return_value="https://test.url"):
        
        result = deployer.deploy()
        assert result == {
            "success": True,
            "function_url": "https://test.url",
            "project_id": "test-project"
        }