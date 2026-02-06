# Regulatory Analysis Agent

An autonomous AI agent that analyzes cryptocurrency, blockchain, stablecoin, and digital asset regulations, performs gap analysis, and updates company policies and standards.

## Features

- **Autonomous Web Research**: Uses NewsAPI to fetch relevant regulatory information
- **Regulatory Analysis**: Analyzes regulations across multiple jurisdictions and focus areas
- **Gap Analysis**: Compares regulatory requirements with current company policies to identify gaps
- **Policy Updates**: Generates recommendations and drafts for updating company policies and standards
- **Dynamic Tool Integration**: Easily extendable to incorporate new research tools
- **Structured Reporting**: Synthesizes information into clear, organized reports
- **User-Friendly Interface**: Built with Streamlit for an intuitive user experience
- **Agentic Workflow**: Automates the research process using LangGraph
- **Source Tracking**: Keeps track of all sources for transparency and verification

## Technologies Used

- **LangGraph**: For building the agentic workflow
- **LangChain**: For LLM integration and prompt management
- **Streamlit**: For creating the web interface
- **Python**: The primary programming language
- **DeepSeek**: Large Language Model for analysis and synthesis
- **NewsAPI**: News article search API (optional)

## Installation

### Prerequisites

- Python 3.8 or higher
- API keys for:
  - DeepSeek (required)
  - NewsAPI (optional)

### Setup Steps

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd "Research AI Agent"
   ```

2. **Create Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Required Packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Keys**:
   
   Create a `.env` file in the root directory:
   ```env
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   NEWSAPI_KEY=your_newsapi_key_here
   LLM_MODEL=deepseek-chat
   LLM_TEMPERATURE=0.3
   ```
   
   **Getting API Keys**:
   - DeepSeek: https://platform.deepseek.com/api_keys
   - NewsAPI: https://newsapi.org/ (optional)

5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

   The application will open in your default web browser at `http://localhost:8501`

## Usage

### Basic Workflow

1. **Enter Your Query**: 
   - Type in the regulatory topic you want to analyze (e.g., "stablecoin regulation", "DeFi compliance")
   - Optionally select a jurisdiction to focus on

2. **Provide Current Policies** (Optional):
   - Paste your current company policies, standards, or compliance documents
   - This enables gap analysis

3. **Select Research Tools**:
   - NewsAPI is optional but can provide additional regulatory news
   - Configure in the sidebar

4. **Run Analysis**:
   - Click "Start Analysis"
   - The agent will:
     - Research regulatory requirements
     - Summarize findings
     - Perform gap analysis (if policies provided)
     - Generate policy update recommendations
     - Create a comprehensive report

5. **Review Results**:
   - **Results Tab**: View regulatory summary, gap analysis, and policy updates
   - **Report Tab**: View/download the full markdown report
   - **Sources Tab**: Review all sources used in the analysis

### Example Queries

- "stablecoin regulation in the United States"
- "DeFi compliance requirements"
- "crypto custody regulations"
- "AML/KYC requirements for cryptocurrency exchanges"
- "NFT taxation policies"
- "CBDC regulatory framework"

### Focus Areas

The agent can analyze regulations across multiple areas:
- Cryptocurrency
- Blockchain
- Stablecoin
- Digital Assets
- DeFi
- NFT
- CBDC
- Crypto Exchange
- Crypto Custody
- AML/KYC
- Taxation
- Securities Regulation

### Supported Jurisdictions

**All Countries and Territories** - The app now supports regulatory analysis for all countries worldwide, including:

- All 193 UN Member States
- Special Administrative Regions (Hong Kong, Macau, etc.)
- Territories and Dependencies (Puerto Rico, Guam, British Virgin Islands, etc.)
- Regional Organizations (European Union)
- Disputed Territories and Special Status Regions

You can select any country or jurisdiction from the dropdown menu, or enter a custom jurisdiction name. The app will analyze regulations for any jurisdiction you specify.

## Project Structure

```
.
├── app.py                  # Streamlit application
├── regulatory_agent.py     # Main LangGraph agent
├── research_tools.py       # Research tool integrations
├── gap_analysis.py         # Gap analysis module
├── policy_updater.py       # Policy update module
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .env                  # API keys (create this)
```

## How It Works

1. **Research Phase**: The agent uses multiple research tools to gather information about regulatory requirements
2. **Summarization Phase**: LLM synthesizes research findings into a structured regulatory summary
3. **Gap Analysis Phase**: Compares regulatory requirements with current policies to identify gaps
4. **Policy Update Phase**: Generates recommendations and policy drafts to address identified gaps
5. **Report Generation**: Creates a comprehensive report with all findings, gaps, and recommendations

## Customization

### Adding New Research Tools

Edit `research_tools.py` to add new research sources:

```python
def search_custom_tool(self, query: str) -> List[Dict]:
    # Your custom search implementation
    pass
```

### Modifying Focus Areas

Edit `config.py` to add or modify regulatory focus areas and jurisdictions.

### Changing LLM Model

Update the `LLM_MODEL` in `.env` or `config.py`. Supported DeepSeek models:
- `deepseek-chat` (default) - Supports tool calling and structured output
- `deepseek-chat-32k` - Extended context window
- `deepseek-coder` - Optimized for code generation
- `deepseek-reasoner` - Note: Does not support tool calling or structured output

The agent uses the official `langchain-deepseek` package for DeepSeek integration.

## Troubleshooting

### API Key Issues
- Ensure all API keys are correctly set in `.env`
- Check that API keys have sufficient credits/quota
- Verify API key permissions

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+)

### Research Tool Errors
- Some tools are optional - the agent will work with available tools
- Check API rate limits if you encounter errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]

## Support

For issues, questions, or suggestions, please open an issue on the repository.

## Acknowledgments

Inspired by the Faraday Web Researcher Agent architecture.

