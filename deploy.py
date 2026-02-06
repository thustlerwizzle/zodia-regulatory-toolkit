"""
Deployment script to ensure API keys are properly configured
"""
import os
from pathlib import Path
from dotenv import load_dotenv


def check_deployment_ready():
    """Check if the application is ready for deployment"""
    load_dotenv()
    
    issues = []
    warnings = []
    
    # Check required API keys
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not deepseek_key:
        issues.append("❌ DEEPSEEK_API_KEY is missing (REQUIRED)")
    else:
        print("✅ DEEPSEEK_API_KEY is set")
    
    # Check optional API keys
    newsapi_key = os.getenv("NEWSAPI_KEY", "")
    if not newsapi_key:
        warnings.append("⚠️  NEWSAPI_KEY is not set (optional, but recommended)")
    else:
        print("✅ NEWSAPI_KEY is set")
    
    langsmith_key = os.getenv("LANGSMITH_API_KEY", "")
    if not langsmith_key:
        warnings.append("⚠️  LANGSMITH_API_KEY is not set (optional, for tracing)")
    else:
        print("✅ LANGSMITH_API_KEY is set")
    
    # Check .env file exists
    if not Path(".env").exists():
        issues.append("❌ .env file not found")
    else:
        print("✅ .env file exists")
    
    # Print summary
    print("\n" + "="*50)
    print("DEPLOYMENT READINESS CHECK")
    print("="*50)
    
    if issues:
        print("\n🚨 CRITICAL ISSUES (must fix):")
        for issue in issues:
            print(f"  {issue}")
    
    if warnings:
        print("\n⚠️  WARNINGS (optional but recommended):")
        for warning in warnings:
            print(f"  {warning}")
    
    if not issues:
        print("\n✅ Application is ready for deployment!")
        print("\nTo run:")
        print("  python gui_agent.py")
        return True
    else:
        print("\n❌ Please fix the issues above before deployment")
        return False


if __name__ == "__main__":
    check_deployment_ready()

