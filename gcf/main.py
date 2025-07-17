import subprocess
import json
import logging
from flask import jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TIMEOUT = 30
SUPPORTED_LANGUAGES = {
    "python": ["python", "-c"],
    "javascript": ["node", "-e"],
    "bash": ["bash", "-c"]
}


def execute_code(request):
    try:
        request_json = request.get_json()
        
        if not request_json:
            return jsonify({"error": "Invalid request body"}), 400
        
        code = request_json.get("code")
        language = request_json.get("language")
        
        if not code:
            return jsonify({"error": "Missing required field: code"}), 400
        
        if not language:
            return jsonify({"error": "Missing required field: language"}), 400
        
        if language not in SUPPORTED_LANGUAGES:
            return jsonify({"error": f"Unsupported language: {language}"}), 400
        
        cmd = SUPPORTED_LANGUAGES[language] + [code]
        
        logger.info(f"Executing {language} code")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=TIMEOUT
            )
            
            return jsonify({
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exitCode": result.returncode
            }), 200
            
        except subprocess.TimeoutExpired:
            return jsonify({
                "stdout": "",
                "stderr": f"Code execution timed out after {TIMEOUT} seconds",
                "exitCode": -1
            }), 200
        
        except Exception as e:
            logger.error(f"Execution error: {str(e)}")
            return jsonify({
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "exitCode": -1
            }), 200
    
    except Exception as e:
        logger.error(f"Request handling error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500