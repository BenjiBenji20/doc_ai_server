# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Your .env File
Copy your existing credentials to a `.env` file in the project root. Make sure it includes:

```env
# Your Google Service Account credentials
type=service_account
project_id=...
private_key_id=...
private_key="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email=...
client_id=
auth_uri=
token_uri=
auth_provider_x509_cert_url=
client_x509_cert_url=
universe_domain=

# Your Document AI settings
DOC_AI_PROJECT_ID=...
PROJECT_LOCATION=...
FRONT_NATIONAL_ID_API_ENDPOINT=...
FRONT_NATIONAL_ID_PROCESSOR_ID=...
REAR_NATIONAL_ID_API_ENDPOINT=...
REAR_NATIONAL_ID_PROCESSOR_ID=...
```

### Step 3: Run the Server
```bash
uvicorn main:app --reload
```

Server will start at: `http://localhost:8000`

### Step 4: Test Connection in Postman

**First Test - Verify Connection:**
- Method: `POST`
- URL: `http://localhost:8000/api/doc-ai/test-connection`
- Click Send
- ✅ You should see: `"success": true`

**Second Test - Process a Document:**
- Method: `POST`  
- URL: `http://localhost:8000/api/doc-ai/process-auto`
- Body → form-data
- Key: `file` (select "File" type)
- Value: Choose your PH National ID image/PDF
- Click Send
- ✅ You should see extracted data in the response!

## 📋 Available Endpoints

| Endpoint | Purpose | When to Use |
|----------|---------|-------------|
| `/api/doc-ai/test-connection` | Test credentials | First step - verify setup |
| `/api/doc-ai/process-front` | Front side only | Single front image |
| `/api/doc-ai/process-rear` | Rear side only | Single rear image |
| `/api/doc-ai/process-auto` | Auto-detect | **Recommended** - handles all cases |

## 🎯 Recommended Workflow

1. **Test Connection** → Verify your credentials work
2. **Use process-auto** → Let the system detect which side(s) are present
3. **Check the response** → Look at `processor_used` to see what was detected:
   - `"front"` = Only front data found
   - `"rear"` = Only rear data found  
   - `"both"` = Both sides detected (usually PDFs with 2 pages)

## 📥 Import Postman Collection

For even faster testing, import the included Postman collection:
1. Open Postman
2. Click "Import"
3. Select `PH_National_ID_DocumentAI.postman_collection.json`
4. All endpoints are ready to test!

## ⚠️ Common Issues

**"Module not found"**
→ Run: `pip install -r requirements.txt`

**"Failed to connect"**
→ Double-check your `.env` credentials

**"No data extracted"**
→ Ensure image quality is good and using the correct ID side

## 📚 Need More Details?

See the full [README.md](README.md) for:
- Complete API documentation
- Detailed response examples
- Troubleshooting guide
- Production deployment tips