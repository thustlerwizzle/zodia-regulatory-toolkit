# Cloud Deployment Guide - Run Analysis 24/7

This guide explains how to run the stablecoin analysis continuously in the cloud, even when your PC is off.

## Option 1: GitHub Actions (Recommended - FREE)

### Setup Steps:

1. **Create a GitHub repository** (if you don't have one):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Add your API keys as GitHub Secrets**:
   - Go to your repository on GitHub
   - Click **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret** and add:
     - `DEEPSEEK_API_KEY` = your DeepSeek API key
     - `NEWS_API_KEY` = your NewsAPI key
     - `LANGSMITH_API_KEY` = your LangSmith API key (optional)

3. **Upload your current progress**:
   ```bash
   git add stablecoin_analysis_all_jurisdictions/
   git commit -m "Upload current progress"
   git push
   ```

4. **Trigger the workflow**:
   - Go to **Actions** tab in your repository
   - Click **Stablecoin Analysis - All Jurisdictions**
   - Click **Run workflow** → **Run workflow**

### How it works:
- Runs for up to 6 hours at a time
- Auto-restarts every 6 hours via schedule
- Saves progress as artifacts between runs
- Completely FREE (2,000 minutes/month on free tier)

---

## Option 2: Render.com (Easy Cloud Hosting)

### Setup:

1. **Create account** at https://render.com

2. **Create a Background Worker**:
   - Click **New** → **Background Worker**
   - Connect your GitHub repository
   - Set **Build Command**: `pip install -r requirements.txt`
   - Set **Start Command**: `python full_stablecoin_analysis_all_jurisdictions.py`

3. **Add Environment Variables**:
   - `DEEPSEEK_API_KEY`
   - `NEWS_API_KEY`
   - `LANGSMITH_API_KEY`

4. **Deploy**

### Pricing:
- Free tier: Limited hours
- Starter: $7/month for always-on

---

## Option 3: Railway.app

### Setup:

1. **Create account** at https://railway.app

2. **New Project** → **Deploy from GitHub**

3. **Add environment variables** in the Variables tab

4. Railway auto-detects Python and runs your app

### Pricing:
- $5 free credit/month
- Pay-as-you-go after that

---

## Option 4: AWS EC2 (Most Reliable)

### Setup:

1. **Launch EC2 instance** (t2.micro is free tier eligible)

2. **SSH into instance**:
   ```bash
   ssh -i your-key.pem ec2-user@your-instance-ip
   ```

3. **Install Python and dependencies**:
   ```bash
   sudo yum install python3 python3-pip git -y
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
   cd YOUR_REPO
   pip3 install -r requirements.txt
   ```

4. **Create .env file**:
   ```bash
   echo "DEEPSEEK_API_KEY=your_key" > .env
   echo "NEWS_API_KEY=your_key" >> .env
   ```

5. **Run with screen** (stays running after disconnect):
   ```bash
   screen -S analysis
   python3 full_stablecoin_analysis_all_jurisdictions.py
   # Press Ctrl+A, then D to detach
   ```

6. **Reconnect later**:
   ```bash
   screen -r analysis
   ```

---

## Quick Start: Push to GitHub and Run

```bash
# Initialize git if needed
git init

# Add all files
git add .
git commit -m "Stablecoin analysis project"

# Create GitHub repo and push
gh repo create stablecoin-analysis --private --source=. --push

# Or manually:
git remote add origin https://github.com/YOUR_USERNAME/stablecoin-analysis.git
git push -u origin main

# Then go to GitHub Actions and trigger the workflow
```

## Monitoring Progress

After deployment, you can:
1. Check GitHub Actions logs in real-time
2. Download progress artifacts from the Actions tab
3. View the summary in `FULL_ANALYSIS_SUMMARY.md`

## Current Progress

Your current progress (110/257 completed) will be preserved when you push to GitHub.
The cloud will continue from where you left off!

