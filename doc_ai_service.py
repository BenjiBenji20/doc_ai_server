from google.cloud import documentai_v1 as documentai
from google.oauth2 import service_account
from google.api_core.client_options import ClientOptions
from typing import Dict, Optional, Tuple
import io
from config import settings
from schemas import FrontNationalIDData, RearNationalIDData, ProcessorType

class DocumentAIService:
    """Service to handle Google Document AI operations"""
    
    def __init__(self):
        """Initialize the Document AI client with credentials from .env"""
        print("Initializing DocumentAIService...")
        credentials_dict = settings.get_credentials_dict()
        self.credentials = service_account.Credentials.from_service_account_info(
            credentials_dict
        )
        print("Credentials loaded successfully")
        
        # Initialize clients for both processors with timeout configuration
        front_options = ClientOptions(api_endpoint=settings.FRONT_NATIONAL_ID_API_ENDPOINT)
        rear_options = ClientOptions(api_endpoint=settings.REAR_NATIONAL_ID_API_ENDPOINT)
        
        print(f"Front API Endpoint: {settings.FRONT_NATIONAL_ID_API_ENDPOINT}")
        print(f"Rear API Endpoint: {settings.REAR_NATIONAL_ID_API_ENDPOINT}")
        
        self.front_client = documentai.DocumentProcessorServiceClient(
            credentials=self.credentials,
            client_options=front_options
        )
        
        self.rear_client = documentai.DocumentProcessorServiceClient(
            credentials=self.credentials,
            client_options=rear_options
        )
        
        # Build processor names
        self.front_processor_name = self.front_client.processor_path(
            settings.DOC_AI_PROJECT_ID,
            settings.PROJECT_LOCATION,
            settings.FRONT_NATIONAL_ID_PROCESSOR_ID
        )
        
        self.rear_processor_name = self.rear_client.processor_path(
            settings.DOC_AI_PROJECT_ID,
            settings.PROJECT_LOCATION,
            settings.REAR_NATIONAL_ID_PROCESSOR_ID
        )
        
        print(f"Front Processor: {self.front_processor_name}")
        print(f"Rear Processor: {self.rear_processor_name}")
        print("DocumentAIService initialized successfully")
    
    def _extract_entities(self, document: documentai.Document) -> Dict[str, str]:
        """Extract entities from Document AI response"""
        entities = {}
        for entity in document.entities:
            # Get the entity type (field name)
            entity_type = entity.type_
            # Get the entity value (text)
            entity_value = entity.mention_text
            entities[entity_type] = entity_value
        return entities
    
    
    def process_document(
        self, 
        file_content: bytes, 
        mime_type: str,
        processor_name: str,
        client: documentai.DocumentProcessorServiceClient
    ) -> documentai.Document:
        """Process a document using specified processor"""
        try:
            # Create the document object
            raw_document = documentai.RawDocument(
                content=file_content,
                mime_type=mime_type
            )
            
            # Configure the process request
            request = documentai.ProcessRequest(
                name=processor_name,
                raw_document=raw_document
            )
            
            # Process the document with timeout
            result = client.process_document(
                request=request,
                timeout=120.0  # 2 minute timeout
            )
            
            return result.document
            
        except TimeoutError as e:
            raise Exception(f"Document AI request timed out after 120 seconds: {str(e)}")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise
    
    
    def process_front_id(self, file_content: bytes, mime_type: str) -> Tuple[FrontNationalIDData, str]:
        """Process front of national ID"""
        document = self.process_document(
            file_content, 
            mime_type, 
            self.front_processor_name,
            self.front_client
        )
        
        entities = self._extract_entities(document)
        front_data = FrontNationalIDData(
            unique_id_number=entities.get("unique_id_number"),
            last_name=entities.get("last_name"),
            first_name=entities.get("first_name"),
            middle_name=entities.get("middle_name"),
            birth_date=entities.get("birth_date"),
            complete_address=entities.get("complete_address")
        )
        
        return front_data, document.text
    
    
    def process_rear_id(self, file_content: bytes, mime_type: str) -> Tuple[RearNationalIDData, str]:
        """Process rear of national ID"""
        document = self.process_document(
            file_content, 
            mime_type, 
            self.rear_processor_name,
            self.rear_client
        )
        
        entities = self._extract_entities(document)
        rear_data = RearNationalIDData(
            issued_date=entities.get("issued_date"),
            sex=entities.get("sex"),
            blood_type=entities.get("blood_type"),
            marital_status=entities.get("marital_status"),
            place_of_birth=entities.get("place_of_birth")
        )
        
        return rear_data, document.text
    
    def process_both_sides(
        self, 
        file_content: bytes, 
        mime_type: str
    ) -> Tuple[Optional[FrontNationalIDData], Optional[RearNationalIDData], ProcessorType, str]:
        """
        Process document with both processors and determine which side(s) are present.
        Returns front_data, rear_data, processor_type, and combined raw text.
        """
        front_data = None
        rear_data = None
        raw_texts = []
        
        # Try processing with front processor
        try:
            front_data, front_text = self.process_front_id(file_content, mime_type)
            raw_texts.append(f"FRONT:\n{front_text}")
        except Exception as e:
            print(f"Front processor failed: {str(e)}")
        
        # Try processing with rear processor
        try:
            rear_data, rear_text = self.process_rear_id(file_content, mime_type)
            raw_texts.append(f"REAR:\n{rear_text}")
        except Exception as e:
            print(f"Rear processor failed: {str(e)}")
        
        # Determine which processor found data
        has_front_data = front_data and front_data.unique_id_number is not None
        has_rear_data = rear_data and rear_data.issued_date is not None
        
        if has_front_data and has_rear_data:
            processor_type = ProcessorType.BOTH
        elif has_front_data:
            processor_type = ProcessorType.FRONT
        elif has_rear_data:
            processor_type = ProcessorType.REAR
        else:
            processor_type = ProcessorType.FRONT  # Default
        
        combined_text = "\n\n".join(raw_texts)
        
        return front_data, rear_data, processor_type, combined_text

# Initialize service as singleton
doc_ai_service = None

def get_doc_ai_service():
    global doc_ai_service
    if doc_ai_service is None:
        doc_ai_service = DocumentAIService()
    return doc_ai_service
