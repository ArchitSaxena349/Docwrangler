# 🚀 LLM Insurance Webhook API - Ready for Testing

## 📍 **Your Webhook URL**
**Check the LocalTunnel window** for your public URL. It will look like:
```
https://abc-123-def.loca.lt
```

## 🎯 **Quick Test**
Replace `[YOUR-URL]` with your actual LocalTunnel URL:

```bash
# Health check
curl https://[YOUR-URL]/webhook/health

# Insurance claim test
curl -X POST https://[YOUR-URL]/webhook/insurance-claim \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "TEST-001",
    "age": 46,
    "gender": "male",
    "procedure": "knee surgery",
    "location": "Pune",
    "policy_duration": "3 months",
    "claim_amount": 50000
  }'
```

## 📋 **Available Endpoints**

### 1. Health Check
- **URL**: `https://[YOUR-URL]/webhook/health`
- **Method**: GET
- **Purpose**: Verify webhook is working

### 2. Insurance Claim Processing
- **URL**: `https://[YOUR-URL]/webhook/insurance-claim`
- **Method**: POST
- **Purpose**: Process insurance claims with AI analysis

**Example Request:**
```json
{
  "claim_id": "CLM-2024-001",
  "age": 46,
  "gender": "male",
  "procedure": "knee surgery",
  "location": "Pune",
  "policy_duration": "3 months",
  "claim_amount": 50000
}
```

**Example Response:**
```json
{
  "claim_id": "CLM-2024-001",
  "status": "processed",
  "decision": "approved",
  "approved": true,
  "coverage_amount": 50000,
  "justification": "Surgery procedures are covered. knee surgery approved for 46-year-old male in Pune.",
  "confidence_score": 0.90,
  "processing_time_seconds": 2.1
}
```

### 3. Natural Language Query
- **URL**: `https://[YOUR-URL]/webhook/query`
- **Method**: POST
- **Purpose**: Process natural language insurance questions

**Example Request:**
```json
{
  "query": "46-year-old male, knee surgery, 3-month policy",
  "context": {"user_id": "test123"}
}
```

**Example Response:**
```json
{
  "status": "success",
  "query": "46-year-old male, knee surgery, 3-month policy",
  "decision": "approved",
  "justification": "Medical procedure is typically covered under standard health insurance policies",
  "confidence": 0.85,
  "amount": 50000,
  "processing_time": 1.5
}
```

## 🌐 **Web Testing Interface**
Open `webhook_test_page.html` in a browser to test the API with a simple web interface.

## 🔧 **Technical Details**
- **CORS**: Enabled for web integration
- **Authentication**: None (for testing)
- **Content-Type**: application/json
- **Timeout**: 30 seconds
- **Data Source**: 6 real insurance policies (Bajaj, HDFC, ICICI, etc.)

## 🎉 **What This API Does**
- Analyzes insurance claims using AI
- Processes natural language queries about insurance
- Returns decisions (approved/rejected/pending)
- Provides confidence scores and justifications
- References specific policy clauses
- Handles multiple insurance policy types

## 📞 **Support**
The webhook processes real insurance data from 6 different policies and uses AI to make intelligent decisions about coverage, waiting periods, and claim approvals.

---
**Ready to integrate!** 🚀