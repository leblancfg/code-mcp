import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from gcf.main import execute_code


@pytest.fixture
def app():
    app = Flask(__name__)
    return app


class MockRequest:
    def __init__(self, json_data):
        self.json_data = json_data
    
    def get_json(self):
        return self.json_data


def test_execute_code_python(app):
    request = MockRequest({
        "code": "print('Hello, World!')",
        "language": "python"
    })
    
    with app.app_context():
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout="Hello, World!\n",
                stderr="",
                returncode=0
            )
            
            response, status_code = execute_code(request)
            
            assert response.json == {
                "stdout": "Hello, World!\n",
                "stderr": "",
                "exitCode": 0
            }
            assert status_code == 200
            
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0][0] == "python"
            assert call_args[0][0][1] == "-c"
            assert call_args[0][0][2] == "print('Hello, World!')"


def test_execute_code_javascript(app):
    request = MockRequest({
        "code": "console.log(6 * 7)",
        "language": "javascript"
    })
    
    with app.app_context():
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout="42\n",
                stderr="",
                returncode=0
            )
            
            response, status_code = execute_code(request)
            
            assert response.json == {
                "stdout": "42\n",
                "stderr": "",
                "exitCode": 0
            }
            assert status_code == 200
            
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0][0] == "node"
            assert call_args[0][0][1] == "-e"
            assert call_args[0][0][2] == "console.log(6 * 7)"


def test_execute_code_bash(app):
    request = MockRequest({
        "code": "echo 'Hello from Bash'",
        "language": "bash"
    })
    
    with app.app_context():
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout="Hello from Bash\n",
                stderr="",
                returncode=0
            )
            
            response, status_code = execute_code(request)
            
            assert response.json == {
                "stdout": "Hello from Bash\n",
                "stderr": "",
                "exitCode": 0
            }
            assert status_code == 200
            
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0][0] == "bash"
            assert call_args[0][0][1] == "-c"
            assert call_args[0][0][2] == "echo 'Hello from Bash'"


def test_execute_code_with_error(app):
    request = MockRequest({
        "code": "print('unclosed",
        "language": "python"
    })
    
    with app.app_context():
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout="",
                stderr="SyntaxError: EOL while scanning string literal\n",
                returncode=1
            )
            
            response, status_code = execute_code(request)
            
            assert response.json == {
                "stdout": "",
                "stderr": "SyntaxError: EOL while scanning string literal\n",
                "exitCode": 1
            }
            assert status_code == 200


def test_execute_code_timeout(app):
    request = MockRequest({
        "code": "import time; time.sleep(100)",
        "language": "python"
    })
    
    with app.app_context():
        with patch('subprocess.run') as mock_run:
            import subprocess
            mock_run.side_effect = subprocess.TimeoutExpired(cmd=['python'], timeout=30)
            
            response, status_code = execute_code(request)
            
            assert response.json == {
                "stdout": "",
                "stderr": "Code execution timed out after 30 seconds",
                "exitCode": -1
            }
            assert status_code == 200


def test_execute_code_unsupported_language(app):
    request = MockRequest({
        "code": "some code",
        "language": "unsupported"
    })
    
    with app.app_context():
        response, status_code = execute_code(request)
        
        assert response.json == {
            "error": "Unsupported language: unsupported"
        }
        assert status_code == 400


def test_execute_code_missing_code(app):
    request = MockRequest({
        "language": "python"
    })
    
    with app.app_context():
        response, status_code = execute_code(request)
        
        assert response.json == {
            "error": "Missing required field: code"
        }
        assert status_code == 400


def test_execute_code_missing_language(app):
    request = MockRequest({
        "code": "print('test')"
    })
    
    with app.app_context():
        response, status_code = execute_code(request)
        
        assert response.json == {
            "error": "Missing required field: language"
        }
        assert status_code == 400