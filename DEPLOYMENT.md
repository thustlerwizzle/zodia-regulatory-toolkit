# Deployment Guide

## Pre-Deployment Checklist

Run the deployment check script:
```bash
python deploy.py
```

This will verify:
- ✅ API keys are configured
- ✅ Required dependencies are installed
- ✅ Application is ready to run

## Deployment Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Ensure your `.env` file contains:
```env
DEEPSEEK_API_KEY=your_key_here
LANGSMITH_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here  # Optional
```

### 3. Run the Application

**GUI Mode (Recommended):**
```bash
python gui_agent.py
```

**Command Line Mode:**
```bash
python run_agent.py
```

## Features Available After Deployment

### ✅ File Upload Support
- Upload PDF, DOCX, TXT, MD, Excel, CSV files
- No size limitations
- Multiple files supported
- Automatic text extraction

### ✅ Live Regulatory Monitoring
- Tracks regulations across all jurisdictions
- Monitors: cryptocurrency, blockchain, stablecoin, digital assets, DeFi, NFT, etc.
- Automatic change detection
- Revision tracking
- Notification system

### ✅ Automatic Policy Updates
- Detects regulatory changes
- Automatically updates policies
- Saves to Desktop/Regulatory_Policies/
- Tracks all revisions

### ✅ Change Notifications
- Creates notification files when changes detected
- Stores in `regulatory_data/notifications/`
- View from GUI: "View Notifications" button

### ✅ Revision History
- Tracks all regulatory changes
- Stores in `regulatory_data/revisions/`
- View from GUI: "View Revisions" button

## Monitoring Setup

1. **Start Monitoring:**
   - Click "▶️ Start Monitoring" in GUI
   - Set interval (default: 24 hours)
   - Monitoring runs in background

2. **Manual Check:**
   - Click "🔄 Check Now" for immediate check

3. **View Results:**
   - "📬 View Notifications" - See change notifications
   - "📋 View Revisions" - See revision history

## File Structure After Deployment

```
.
├── regulatory_data/
│   ├── revisions/          # All regulatory change revisions
│   ├── notifications/      # Change notifications
│   └── *.json             # Regulatory snapshots
├── Desktop/
│   └── Regulatory_Policies/  # Auto-generated policy files
└── regulatory_report_*.md    # Analysis reports
```

## API Keys Required

- **DEEPSEEK_API_KEY** (Required) - For LLM analysis
- **LANGSMITH_API_KEY** (Optional) - For tracing
- **NEWSAPI_KEY** (Optional) - For news research

## Troubleshooting

### API Keys Not Working
- Check `.env` file exists
- Verify keys are correct (no extra spaces)
- Ensure keys have sufficient credits

### Monitoring Not Starting
- Ensure agent is initialized
- Check API keys are set
- Verify no errors in console

### File Upload Issues
- Ensure file types are supported
- Check file is not corrupted
- Try smaller files first

## Production Deployment

For production deployment:

1. Set environment variables in your deployment platform
2. Ensure `.env` file is properly configured
3. Run `python deploy.py` to verify setup
4. Start monitoring service
5. Set up automated backups of `regulatory_data/` folder

## Support

For issues or questions, check:
- `regulatory_data/notifications/` for error notifications
- Console output for detailed error messages
- Revision history for tracking changes

