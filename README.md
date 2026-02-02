# PH National ID Document AI Processor

FastAPI backend for processing Philippine National ID using Google Document AI with custom trained processors.

## Features

- ✅ Process **front side** of PH National ID (extracts: unique_id_number, last_name, first_name, middle_name, birth_date, complete_address)
- ✅ Process **rear side** of PH National ID (extracts: issued_date, sex, blood_type, marital_status, place_of_birth)
- ✅ **Auto-detect** mode for PDFs containing both sides
- ✅ Support for images (JPEG, PNG) and PDF files
- ✅ Connection testing endpoint

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory with your Google Cloud credentials:

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

**Important Notes:**
- Make sure your `private_key` value includes the quotes and proper newline characters (`\n`)
- Replace all placeholder values with your actual Google Cloud credentials

### 3. Run the Application

```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python main.py
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### 1. Health Check
**GET** `/api/doc-ai/`

Test if the service is running.

```bash
curl http://localhost:8000/api/doc-ai/
```

### 2. Test Connection
**POST** `/api/doc-ai/test-connection`

Verify that Google Document AI credentials are properly configured.

**Postman Setup:**
- Method: `POST`
- URL: `http://localhost:8000/api/doc-ai/test-connection`
- No body required

**Expected Response:**
```json
{
  "success": true,
  "message": "Successfully connected to Google Document AI",
  "processors": {
    "front": "projects/.../processors/...",
    "rear": "projects/.../processors/..."
  }
}
```

### 3. Process Front ID
**POST** `/api/doc-ai/process-front`

Process only the front side of PH National ID.

**Postman Setup:**
- Method: `POST`
- URL: `http://localhost:8000/api/doc-ai/process-front`
- Body: `form-data`
  - Key: `file` (type: File)
  - Value: Select your image/PDF file

**Expected Response:**
```json
{
  "success": true,
  "message": "Front ID processed successfully",
  "processor_used": "front",
  "front_data": {
    "unique_id_number": "1234-5678-9012",
    "last_name": "DELA CRUZ",
    "first_name": "JUAN",
    "middle_name": "SANTOS",
    "birth_date": "01/15/1990",
    "complete_address": "123 Main St, Manila"
  },
  "rear_data": null,
  "raw_text": "..."
}
```

### 4. Process Rear ID
**POST** `/api/doc-ai/process-rear`

Process only the rear side of PH National ID.

**Postman Setup:**
- Method: `POST`
- URL: `http://localhost:8000/api/doc-ai/process-rear`
- Body: `form-data`
  - Key: `file` (type: File)
  - Value: Select your image/PDF file

**Expected Response:**
```json
{
  "success": true,
  "message": "Rear ID processed successfully",
  "processor_used": "rear",
  "front_data": null,
  "rear_data": {
    "issued_date": "01/15/2022",
    "sex": "M",
    "blood_type": "O+",
    "marital_status": "SINGLE",
    "place_of_birth": "MANILA"
  },
  "raw_text": "..."
}
```

### 5. Process Auto-Detect (Recommended)
**POST** `/api/doc-ai/process-auto`

Automatically detect and process front, rear, or both sides.

**Postman Setup:**
- Method: `POST`
- URL: `http://localhost:8000/api/doc-ai/process-auto`
- Body: `form-data`
  - Key: `file` (type: File)
  - Value: Select your image/PDF file

**Use Cases:**
- Single image of **front only** → Returns front_data only
- Single image of **rear only** → Returns rear_data only
- PDF with **both pages** → Returns both front_data and rear_data

**Expected Response (Both Sides):**
```json
{
  "success": true,
  "message": "Both front and rear ID data extracted successfully",
  "processor_used": "both",
  "front_data": {
    "unique_id_number": "1234-5678-9012",
    "last_name": "DELA CRUZ",
    "first_name": "JUAN",
    "middle_name": "SANTOS",
    "birth_date": "01/15/1990",
    "complete_address": "123 Main St, Manila"
  },
  "rear_data": {
    "issued_date": "01/15/2022",
    "sex": "M",
    "blood_type": "O+",
    "marital_status": "SINGLE",
    "place_of_birth": "MANILA"
  },
  "raw_text": "..."
}
```

## Testing with Postman

### Step-by-Step Testing Guide

1. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

2. **Test connection first:**
   - Create a new request in Postman
   - Method: POST
   - URL: `http://localhost:8000/api/doc-ai/test-connection`
   - Click "Send"
   - You should see a success message with processor information

3. **Test with a file:**
   - Create a new request
   - Method: POST
   - URL: `http://localhost:8000/api/doc-ai/process-auto` (recommended) or specific endpoint
   - Go to "Body" tab
   - Select "form-data"
   - Add a key named `file` with type "File"
   - Click "Select Files" and choose your National ID image or PDF
   - Click "Send"

4. **Check the response:**
   - Look for `"success": true`
   - Verify extracted data in `front_data` and/or `rear_data`
   - Check `raw_text` for debugging if needed

## File Structure

```
.
├── main.py                 # FastAPI application and endpoints
├── config.py              # Environment configuration
├── models.py              # Pydantic models for request/response
├── doc_ai_service.py      # Document AI processing logic
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .env.example          # Example environment file
└── README.md             # This file
```

## Supported File Types

- **Images:** JPEG (.jpg, .jpeg), PNG (.png)
- **Documents:** PDF (.pdf)

## Error Handling

The API returns detailed error messages when:
- Invalid file type is uploaded
- Document AI processing fails
- Connection to Google Cloud fails
- Missing or invalid credentials

Example error response:
```json
{
  "detail": "Error processing ID: [error details]"
}
```

## Tips for Best Results

1. **Image Quality:** Use high-resolution, clear images
2. **Orientation:** Ensure the ID is properly oriented
3. **Lighting:** Good lighting improves extraction accuracy
4. **PDF Format:** For PDFs with both sides, each side should be on a separate page

## Troubleshooting

### "Failed to connect to Document AI"
- Check that all credentials in `.env` are correct
- Verify that your service account has Document AI permissions
- Ensure processor IDs are correct

### "No data extracted"
- Check image quality
- Verify the correct side of ID is being processed
- Check that processors are properly trained

### "Module not found"
- Run `pip install -r requirements.txt`
- Ensure you're in the correct virtual environment
