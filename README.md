# PH Document AI Processor

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Google Document AI](https://img.shields.io/badge/Google%20Document%20AI-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/document-ai)
[![Vercel](https://img.shields.io/badge/Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![Google Sheets](https://img.shields.io/badge/Google%20Sheets-34A853?logo=google-sheets&logoColor=white)](https://www.google.com/sheets/about/)

<p align="center">
   <img width="1654" height="850" alt="Image" src="https://github.com/user-attachments/assets/c3843aa9-49a7-44a0-ac4b-762a03037eb8" />
</p>

This project demonstrates how document data encoding can be automated using **modern AI-driven solutions** to reduce human error and free up time for higher-value tasks.

The current prototype supports **Philippine National ID processing only**. Its document processor is intentionally limited at this stage, but the **architecture is designed to be extensible**. Future updates will introduce additional processors for other **Philippine documents**, such as Certificates of Live Birth and other government-issued IDs.

This repository can also be used as a reference or integrated directly into your own application by following the setup and usage guide provided.

## Project Technologies

- **FastAPI**: Handles API requests, request validation, and server-side logic while keeping secrets and credentials securely on the backend.
- **Google Document AI (Custom Extractor)**: Extracts structured data from documents using a trained AI model tailored to specific document formats.
- **Vercel Serverless Functions** – Hosts the FastAPI backend as serverless functions, enabling scalable, on-demand execution without managing servers.
- **Supabase**: Provides a real-time database and backend services for storing and synchronizing application data.
- **Google Sheets API**: Used as a lightweight data store and reporting layer for extracted document data.

## Features

- ✅ Process **front side** of PH National ID (extracts: unique_id_number, last_name, first_name, middle_name, birth_date, complete_address)
- ✅ Process **rear side** of PH National ID (extracts: issued_date, sex, blood_type, marital_status, place_of_birth)
- ✅ **Auto-detect** mode for PDFs containing both sides
- ✅ Support for images (JPEG, PNG) and PDF files
- ✅ Rate limiting to avoid API abuse
- ✅ Real-time **database connection** through Supabase
- ✅ Real-time **Google Spreadsheet** data insertion

## System Architecture and Flow

<p align="center">
   <img width="1104" height="657" alt="Image" src="https://github.com/user-attachments/assets/e3285eb4-a352-4a96-a4f2-f316727abfe0" />
</p>

1. User access the application and upload a document.
2. The document then goes to the server and pass to Google Cloud Document AI to extract texts.
3. The extracted texts then pass to the server to client to validate by the user.
4. The validated text will be stored in PostgreSQL through Supabase and Google Sheet all in real-time.

## Setup Instructions

### Clone the Repository

```
git clone https://github.com/BenjiBenji20/PH_Documents_AI_Text_Automation.git
cd PH_Documents_AI_Text_Automation
```

### Create and Activate Python Virtual Environment

```
python -m venv venv
source venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

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
- Make sure to change the prefix API url in index.json to your actual domain

### Run the Application

```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python main.py
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### 1. Test Connection
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

### 2. Process Front ID
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

### 3. Process Rear ID
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

### 4. Process Auto-Detect (Recommended)
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

## File Structure

```
├── api/
      ├── main.py          # FastAPI application and endpoints
├── doc/                   # Project documentation
      ├── .pdf/.png..      
├── public/                # Static directory
      ├── index.html       # Static html
      ├── style.css        # Static css
      ├── index.js         # JS to fetch to serverless functions
├── config.py              # Environment configuration
├── schemas.py             # Pydantic models for request/response
├── doc_ai_service.py      # Document AI processing logic
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── vercel.json            # Vercel configuration
└── README.md              # This file
```

This follows Vercel's project route standard.

## Supported File Types

- **Images:** JPEG (.jpg, .jpeg), PNG (.png)
- **Documents:** PDF (.pdf)

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

## Notice

In the future I plan to create another processor to handle more local documents such as certificate of live birth and other document and ID specific in the Philippines.

Having difficulty of finding data to uptrain your Doc AI processor? You can use my synthetic dataset of PH National ID.
Get them in **https://drive.google.com/drive/folders/1SVa5no_zh8FbM9uRLpr5QYJ8rJ0m5eO4?usp=sharing**

### I need a job and of course money!!!
Please email me at **benjicanones6@gmail.com**
