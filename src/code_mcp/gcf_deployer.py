import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class GCFDeployer:
    def __init__(self, project_id=None):
        self.project_id = project_id
        self.function_name = "code-interpreter"
        self.region = "us-central1"
        self.gcf_source_dir = Path(__file__).parent.parent.parent / "gcf"
    
    def check_gcloud_installed(self) -> bool:
        try:
            print("🔍 Checking for gcloud CLI...")
            subprocess.run(["gcloud", "--version"], capture_output=True, text=True)
            print("✅ gcloud CLI found")
            return True
        except FileNotFoundError:
            logger.error("gcloud CLI not found. Please install Google Cloud SDK.")
            return False
    
    def get_current_project(self) -> str:
        print("🔍 Getting current GCP project...")
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            project = result.stdout.strip()
            print(f"📋 Current project: {project}")
            return project
        print("⚠️  No default project set")
        return None
    
    def deploy_function(self) -> bool:
        cmd = [
            "gcloud", "functions", "deploy", self.function_name,
            "--runtime=python311",
            "--trigger-http",
            "--allow-unauthenticated",
            "--entry-point=execute_code",
            f"--source={self.gcf_source_dir}",
            f"--region={self.region}",
            "--timeout=60s",
            "--memory=256MB"
        ]
        
        if self.project_id:
            cmd.append(f"--project={self.project_id}")
        
        logger.info(f"Deploying function with command: {' '.join(cmd)}")
        print(f"⏳ Deploying function (this may take 1-2 minutes)...")
        
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            logger.info("Function deployed successfully")
            return True
        else:
            logger.error(f"Deployment failed: {result.stderr}")
            return False
    
    def get_function_url(self) -> str:
        cmd = [
            "gcloud", "functions", "describe", self.function_name,
            "--region", self.region,
            "--format", "value(httpsTrigger.url)"
        ]
        
        if self.project_id:
            cmd.append(f"--project={self.project_id}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    
    def deploy(self) -> dict:
        if not self.check_gcloud_installed():
            return {"success": False, "error": "gcloud CLI not installed"}
        
        if not self.project_id:
            self.project_id = self.get_current_project()
            if not self.project_id:
                return {"success": False, "error": "No GCP project configured"}
        
        logger.info(f"Using GCP project: {self.project_id}")
        
        if not self.deploy_function():
            return {"success": False, "error": "Function deployment failed"}
        
        function_url = self.get_function_url()
        if not function_url:
            return {"success": False, "error": "Could not retrieve function URL"}
        
        return {
            "success": True,
            "function_url": function_url,
            "project_id": self.project_id
        }