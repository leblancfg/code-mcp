#!/usr/bin/env python
"""
Script to deploy the Google Cloud Function for code execution.

Usage: python deploy_gcf.py [--project PROJECT_ID]
"""

import argparse
import sys
from src.code_mcp.gcf_deployer import GCFDeployer


def main():
    parser = argparse.ArgumentParser(description="Deploy Code Interpreter Google Cloud Function")
    parser.add_argument(
        "--project",
        help="Google Cloud Project ID (defaults to current gcloud config)",
        default=None
    )
    
    args = parser.parse_args()
    
    deployer = GCFDeployer(project_id=args.project)
    
    print("🚀 Deploying Code Interpreter Cloud Function...")
    
    result = deployer.deploy()
    
    if result["success"]:
        print(f"✅ Successfully deployed!")
        print(f"📍 Function URL: {result['function_url']}")
        print(f"🔧 Project ID: {result['project_id']}")
        print(f"\nTo use with the MCP server, set the environment variable:")
        print(f"export GCF_URL=\"{result['function_url']}\"")
    else:
        print(f"❌ Deployment failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()