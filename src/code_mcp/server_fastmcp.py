import os
import logging
import asyncio
import requests
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP("code-interpreter")

# Global GCF URL
GCF_URL = os.getenv("GCF_URL")


@mcp.tool()
async def run_code(code: str, language: str) -> str:
    """
    Execute code in a sandboxed environment using Google Cloud Functions.
    
    Args:
        code: The code to execute
        language: Programming language (python, javascript, bash)
    
    Returns:
        The output from code execution
    """
    global GCF_URL
    
    if not GCF_URL:
        # Try to deploy if not configured
        from .gcf_deployer import GCFDeployer
        deployer = GCFDeployer()
        deployment = deployer.deploy()
        if deployment["success"]:
            GCF_URL = deployment["function_url"]
            logger.info(f"GCF deployed at: {GCF_URL}")
        else:
            raise RuntimeError("GCF_URL not configured and deployment failed")
    
    # Call GCF
    loop = asyncio.get_event_loop()
    
    def make_request():
        return requests.post(
            GCF_URL,
            json={"code": code, "language": language},
            timeout=35
        )
    
    try:
        response = await loop.run_in_executor(None, make_request)
        response.raise_for_status()
        result = response.json()
        
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")
        exit_code = result.get("exitCode", 0)
        
        output = stdout
        if stderr:
            output += f"\n\nErrors:\n{stderr}"
        if exit_code != 0:
            output += f"\n\nExit code: {exit_code}"
        
        return output.strip()
    except Exception as e:
        logger.error(f"Error calling GCF: {str(e)}")
        raise


def main():
    """Entry point for the MCP server"""
    if not GCF_URL:
        logger.warning("GCF_URL not set, will attempt to deploy on first use")
    mcp.run()


if __name__ == "__main__":
    main()