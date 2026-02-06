"""
Helper script to set up environment variables
"""
import os
import sys


def create_env_file():
    """Create .env file with template"""
    env_template = """# API Keys
# Get your API keys from:
# - DeepSeek: https://platform.deepseek.com/api_keys
# - NewsAPI: https://newsapi.org/ (optional)

DEEPSEEK_API_KEY=
LANGSMITH_API_KEY=
NEWSAPI_KEY=

# LLM Configuration
LLM_MODEL=deepseek-chat
LLM_TEMPERATURE=0.3

# Research Configuration
MAX_SEARCH_RESULTS=10
MAX_NEWS_ARTICLES=20
"""
    
    if os.path.exists(".env"):
        response = input(".env file already exists. Overwrite? (y/n): ")
        if response.lower() != "y":
            print("Cancelled.")
            return
    
    with open(".env", "w") as f:
        f.write(env_template)
    
    print("✅ Created .env file")
    print("📝 Please edit .env and add your API keys")


if __name__ == "__main__":
    create_env_file()

