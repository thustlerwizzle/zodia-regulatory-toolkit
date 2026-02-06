# Quick Start Guide

Get up and running with the Regulatory Analysis Agent in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up API Keys

### Option A: Use the setup script
```bash
python setup_env.py
```
Then edit `.env` and add your API keys.

### Option B: Create .env manually
Create a `.env` file in the root directory:

```env
DEEPSEEK_API_KEY=your-deepseek-key-here
NEWSAPI_KEY=your-key-here
LLM_MODEL=deepseek-chat
```

**Minimum Required**: At least `DEEPSEEK_API_KEY` is required. Other APIs are optional but recommended for better results.

## Step 3: Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Step 4: Run Your First Analysis

1. Go to the **Analysis** tab
2. Enter a query like: "stablecoin regulation"
3. Optionally select a jurisdiction (e.g., "United States")
4. Optionally paste your current company policies
5. Click **Start Analysis**

## Example Queries

- "DeFi compliance requirements"
- "crypto custody regulations in Singapore"
- "AML/KYC requirements for cryptocurrency"
- "NFT taxation policies"
- "stablecoin regulation European Union"

## What Happens Next?

The agent will:
1. 🔍 Research regulatory requirements from multiple sources
2. 📋 Summarize key regulatory findings
3. 🔎 Perform gap analysis (if policies provided)
4. 📝 Generate policy update recommendations
5. 📊 Create a comprehensive report

## Viewing Results

- **Results Tab**: See regulatory summary, gaps, and policy updates
- **Report Tab**: View/download the full markdown report
- **Sources Tab**: Review all sources used in the analysis

## Troubleshooting

### "No module named 'X'"
Run: `pip install -r requirements.txt`

### "API key not found"
Make sure your `.env` file exists and contains your API keys

### "DeepSeek API error"
- Check your API key is correct
- Verify you have credits/quota available
- Try a different model in `.env`: `LLM_MODEL=deepseek-chat-32k`
- Make sure `DEEPSEEK_API_KEY` is set correctly in your `.env` file

### Research tools not working
- The agent will work with just DeepSeek
- NewsAPI is optional
- Check API keys if you want to use them

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize focus areas in `config.py`
- Add your own research tools in `research_tools.py`

Happy analyzing! 🚀

