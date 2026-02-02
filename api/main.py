from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from doc_ai_service import get_doc_ai_service
from config import settings
from schemas import NationalIDResponse, ProcessorType
from fastapi.middleware.cors import CORSMiddleware
import traceback

doc_ai = APIRouter(prefix="/api/doc-ai", tags=["Document AI"])

@doc_ai.get("/")
async def greet():
    """Health check endpoint"""
    return {
        "message": "Document AI Service is running!", 
        "status": "healthy"
    }


@doc_ai.post("/test-connection")
async def test_connection():
    """
    Test the connection to Google Document AI.
    This endpoint verifies that credentials are properly configured.
    """
    try:
        # Try to access the processor names to verify connection
        front_processor = get_doc_ai_service().front_processor_name
        rear_processor = get_doc_ai_service().rear_processor_name
        
        return {
            "success": True,
            "message": "Successfully connected to Google Document AI",
            "processors": {
                "front": front_processor,
                "rear": rear_processor
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Document AI: {str(e)}"
        )


@doc_ai.post("/process-front", response_model=NationalIDResponse)
async def process_front_id(file: UploadFile = File(...)):
    """
    Process the FRONT side of PH National ID.
    Accepts: image files (JPEG, PNG) or PDF
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Determine MIME type
        mime_type = file.content_type
        if mime_type not in ["image/jpeg", "image/png", "application/pdf"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {mime_type}. Please upload JPEG, PNG, or PDF."
            )
        
        # Process the document
        front_data, raw_text = get_doc_ai_service().process_front_id(file_content, mime_type)
        
        return NationalIDResponse(
            success=True,
            message="Front ID processed successfully",
            processor_used=ProcessorType.FRONT,
            front_data=front_data,
            rear_data=None,
            raw_text=raw_text
        )
        
    except Exception as e:
        error_detail = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing front ID: {str(e)}\n{error_detail}"
        )


@doc_ai.post("/process-rear", response_model=NationalIDResponse)
async def process_rear_id(file: UploadFile = File(...)):
    """
    Process the REAR side of PH National ID.
    Accepts: image files (JPEG, PNG) or PDF
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Determine MIME type
        mime_type = file.content_type
        if mime_type not in ["image/jpeg", "image/png", "application/pdf"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {mime_type}. Please upload JPEG, PNG, or PDF."
            )
        
        # Process the document
        rear_data, raw_text = get_doc_ai_service().process_rear_id(file_content, mime_type)
        
        return NationalIDResponse(
            success=True,
            message="Rear ID processed successfully",
            processor_used=ProcessorType.REAR,
            front_data=None,
            rear_data=rear_data,
            raw_text=raw_text
        )
        
    except Exception as e:
        error_detail = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing rear ID: {str(e)}\n{error_detail}"
        )


@doc_ai.post("/process-auto", response_model=NationalIDResponse)
async def process_auto_detect(file: UploadFile = File(...)):
    """
    Automatically detect and process PH National ID (front, rear, or both).
    
    - If the file contains only the front side, returns front data only
    - If the file contains only the rear side, returns rear data only  
    - If the file (especially PDF) contains both sides, returns both front and rear data
    
    Accepts: image files (JPEG, PNG) or PDF
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Determine MIME type
        mime_type = file.content_type
        if mime_type not in ["image/jpeg", "image/png", "application/pdf"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {mime_type}. Please upload JPEG, PNG, or PDF."
            )
        
        # Process with both processors
        front_data, rear_data, processor_type, raw_text = get_doc_ai_service().process_both_sides(
            file_content, 
            mime_type
        )
        
        # Build message based on what was detected
        if processor_type == ProcessorType.BOTH:
            message = "Both front and rear ID data extracted successfully"
        elif processor_type == ProcessorType.FRONT:
            message = "Front ID data extracted successfully"
        elif processor_type == ProcessorType.REAR:
            message = "Rear ID data extracted successfully"
        else:
            message = "Document processed but no ID data found"
        
        return NationalIDResponse(
            success=True,
            message=message,
            processor_used=processor_type,
            front_data=front_data,
            rear_data=rear_data,
            raw_text=raw_text
        )
        
    except Exception as e:
        error_detail = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing ID: {str(e)}\n{error_detail}"
        )


# Create FastAPI app
app = FastAPI(
    title="Document AI - PH National ID Processor",
    description="FastAPI backend for processing Philippine National ID using Google Document AI",
    version="1.0.0"
)

# CORS Configuration - Allow request from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.DEV_CLIENT_ORIGIN, settings.PROD_CLIENT_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"], # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],  # Allows all headers
  )

# Include router
app.include_router(doc_ai)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Document AI API",
        "endpoints": {
            "health_check": "/api/doc-ai/",
            "test_connection": "/api/doc-ai/test-connection",
            "process_front": "/api/doc-ai/process-front",
            "process_rear": "/api/doc-ai/process-rear",
            "process_auto": "/api/doc-ai/process-auto"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    