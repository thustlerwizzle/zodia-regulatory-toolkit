# Live Regulatory Monitoring Guide

## How to Verify Live Tracking is Active

### 1. **Visual Indicators in the GUI**

When monitoring is active, you'll see:

- **Status Label**: Shows "🟢 Monitoring: ACTIVE (checking every X hours)" in green
- **Dashboard Info**: Displays "📊 Tracking: X jurisdictions × Y topics = Z regulations"
- **Last Check Time**: Updates automatically showing when the last check was performed

### 2. **Monitoring Dashboard**

Click the **"📊 Open Monitoring Dashboard"** button to open a dedicated dashboard that shows:

- **Real-time Activity Log**: See live updates as regulations are being checked
- **Current Status**: Active/Inactive monitoring status
- **Statistics**: Number of jurisdictions, topics, and total regulations being tracked
- **Last Update Time**: When the last check completed

### 3. **Activity Logs**

The monitoring service logs all activity to:
- **Console Output**: When running from command line, you'll see:
  ```
  [2024-01-15 10:30:00] Starting regulatory monitoring cycle...
  Monitoring: United States - cryptocurrency
  Monitoring: United States - blockchain
  ...
  ✅ No regulatory changes detected
  Next check in 24 hours...
  ```

### 4. **Data Files Created**

When monitoring is active, you'll see files being created in:

- **`regulatory_data/`**: Contains snapshots of all regulations
  - Format: `{Jurisdiction}_{Topic}.json`
  - Example: `United_States_cryptocurrency.json`

- **`regulatory_data/revisions/`**: Contains revision history when changes are detected
  - Format: `revision_{Jurisdiction}_{Topic}_{Timestamp}.json`

- **`regulatory_data/notifications/`**: Contains notification files when changes are detected
  - Format: `notification_{Timestamp}.md`

### 5. **What's Being Tracked**

The system tracks **ALL** of the following:

#### Jurisdictions (10 total):
- United States
- European Union
- United Kingdom
- Singapore
- Japan
- Switzerland
- United Arab Emirates
- Hong Kong
- Australia
- Canada

#### Regulatory Topics (12 total):
- cryptocurrency
- blockchain
- stablecoin
- digital assets
- DeFi
- NFT
- CBDC
- crypto exchange
- crypto custody
- AML/KYC
- taxation
- securities regulation

#### Total Regulations Tracked: **120** (10 jurisdictions × 12 topics)

### 6. **How to Test Monitoring**

1. **Start Monitoring**:
   - Click "▶️ Start Monitoring" in the GUI
   - Set interval (e.g., 24 hours for daily checks)

2. **Run Immediate Check**:
   - Click "🔄 Check Now" to run a check immediately
   - Watch the results panel for detailed output

3. **View Activity**:
   - Open the Monitoring Dashboard
   - Watch the activity log in real-time
   - See which jurisdictions and topics are being checked

4. **Check Files**:
   - Navigate to `regulatory_data/` folder
   - You should see JSON files for each jurisdiction-topic combination
   - Files are updated on each check

### 7. **Verification Checklist**

✅ **Monitoring Status**: Shows "ACTIVE" in green  
✅ **Dashboard**: Shows tracking statistics (120 regulations)  
✅ **Activity Log**: Shows real-time checking activity  
✅ **Data Files**: JSON files created/updated in `regulatory_data/`  
✅ **Last Check Time**: Updates after each monitoring cycle  
✅ **Notifications**: Created when changes are detected  
✅ **Revisions**: Created when changes are detected  

### 8. **Troubleshooting**

If monitoring doesn't appear to be working:

1. **Check API Keys**: Run `python deploy.py` to verify all API keys are set
2. **Check Console**: Look for error messages in the console/terminal
3. **Check Files**: Verify files are being created in `regulatory_data/`
4. **Manual Test**: Click "🔄 Check Now" to trigger an immediate check
5. **View Logs**: Check the activity log in the Monitoring Dashboard

### 9. **Monitoring Frequency**

- **Default**: Every 24 hours
- **Configurable**: Set any interval from 1 hour to 168 hours (1 week)
- **Immediate**: Can run checks on-demand using "Check Now"

### 10. **What Happens When Changes Are Detected**

1. **Change Detection**: System compares new data with previous snapshots
2. **Revision Created**: Detailed revision file saved to `regulatory_data/revisions/`
3. **Notification Generated**: Markdown notification file created
4. **Policies Updated**: Automatic policy updates applied
5. **Alert Shown**: GUI shows warning message with change count

---

**The system is actively tracking 120 regulations across 10 jurisdictions and 12 topics, checking for changes automatically at your specified interval!**

