"""
Quick deployment script to push project to GitHub and trigger cloud analysis.
Run this script to deploy your analysis to run 24/7 in the cloud.
"""
import subprocess
import os
import sys

def run_command(cmd, check=True):
    """Run a shell command and return output"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if check and result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        return False
    return True

def main():
    print("=" * 60)
    print("CLOUD DEPLOYMENT - Stablecoin Analysis")
    print("=" * 60)
    print()
    
    # Check if git is initialized
    if not os.path.exists(".git"):
        print("📁 Initializing git repository...")
        run_command("git init")
    
    # Check for GitHub CLI
    gh_available = run_command("gh --version", check=False)
    
    print()
    print("📋 SETUP INSTRUCTIONS:")
    print("-" * 60)
    print()
    print("1. Create a GitHub repository:")
    print("   - Go to https://github.com/new")
    print("   - Name it: stablecoin-analysis")
    print("   - Make it PRIVATE (to protect your data)")
    print("   - DON'T initialize with README")
    print()
    print("2. Add your API keys as GitHub Secrets:")
    print("   - Go to: https://github.com/YOUR_USERNAME/stablecoin-analysis/settings/secrets/actions")
    print("   - Add these secrets:")
    print("     • DEEPSEEK_API_KEY")
    print("     • NEWS_API_KEY")
    print("     • LANGSMITH_API_KEY (optional)")
    print()
    print("3. Push your code:")
    print()
    
    # Create .gitignore if it doesn't exist
    gitignore_content = """
# Environment
.env
*.env
venv/
__pycache__/
*.pyc

# IDE
.vscode/
.idea/

# Logs
*.log

# But keep progress files (they're needed for continuation)
!stablecoin_analysis_all_jurisdictions/
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("Commands to run:")
    print("-" * 60)
    print("""
git add .
git commit -m "Stablecoin analysis with cloud deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stablecoin-analysis.git
git push -u origin main
""")
    print("-" * 60)
    print()
    print("4. After pushing, go to GitHub Actions:")
    print("   - Click the 'Actions' tab")
    print("   - Click 'Stablecoin Analysis - All Jurisdictions'")
    print("   - Click 'Run workflow' → 'Run workflow'")
    print()
    print("The analysis will run in the cloud 24/7!")
    print("It auto-saves progress and restarts every 6 hours.")
    print()
    
    response = input("Would you like me to stage all files for commit? (yes/no): ").strip().lower()
    if response == "yes":
        run_command("git add .")
        run_command('git status')
        print()
        print("Files staged! Now run:")
        print('  git commit -m "Stablecoin analysis project"')
        print("  git remote add origin https://github.com/YOUR_USERNAME/stablecoin-analysis.git")
        print("  git push -u origin main")

if __name__ == "__main__":
    main()

