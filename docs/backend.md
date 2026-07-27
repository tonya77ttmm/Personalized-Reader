# Backend Documentation

## Overview

The AI Reader Agent backend is a Python-based REST API built with FastAPI that provides document processing, storage, and AI-powered explanation services. The backend follows a layered architecture with clear separation of concerns between API routes, business logic services, data models, and storage layers.

The system processes text documents by splitting them into manageable pages, storing them with dual persistence (file system + database), and integrating with OpenAI's GPT models through LangChain to provide contextual explanations for selected text.

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs with Python
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library
- **SQLite**: Lightweight, file-based database for document and page storage
- **Pydantic**: Data validation and serialization using Python type annotations
- **LangChain**: Framework for developing applications with language models
- **OpenAI GPT**: Large language model for generating text explanations
- **Uvicorn**: ASGI server for running the FastAPI application

## Application Structure

### Main Application (`main.py`)

The FastAPI application entry point that configures the server, middleware, and routes:

```python
# Core application setup
app = FastAPI(
    title="AI Reader Agent API",
    description="Backend API for AI Reader Agent - personalized reading assistance",
    version="1.0.0"
)

# Database initialization on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Route registration
app.include_router(documents_router)
app.include_router(explanations_router)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Key Features:**

- database initialization on startup
- CORS configuration for frontend integration
- Centralized route management
- Environment-based configuration

### Database Configuration (`database.py`)

Manages SQLAlchemy database connections and session handling:

```python
# SQLite database configuration
DATABASE_URL = f"sqlite:///{DB_DIR}/documents.db"

# Engine with SQLite-specific settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session factory for dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency function for route handlers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Key Features:**

- Automatic database directory creation
- Thread-safe SQLite configuration
- Proper session lifecycle management
- Dependency injection pattern for database access

## API Routes

### Documents API (`/api/documents/`)

Handles document upload, retrieval, and page-based access with comprehensive validation and error handling.

#### POST `/api/documents/`

**Purpose**: Upload and process text documents

**Validation Pipeline**:

1. **File Extension Check**: Only `.txt` files allowed
2. **MIME Type Validation**: Must be `text/plain`
3. **Size Validation**: Maximum 10MB file size
4. **Content Validation**: Valid UTF-8 encoding required
5. **Magic Number Check**: Optional python-magic validation for enhanced security

**Processing Flow**:

```python
# File validation
validate_file(file, content)

# Document processing and storage
document_response = document_service.store_document(content, file.filename)
```

**Response**: `DocumentResponse` with document ID, metadata, and processing confirmation

#### GET `/api/documents/{document_id}/metadata`

**Purpose**: Retrieve document metadata for navigation and display

**Response Fields**:

- `id`: Unique document identifier
- `title`: Document filename or custom title
- `total_pages`: Number of pages after splitting
- `total_words`: Total word count
- `words_per_page`: Configured page size
- `uploaded_at`: Upload timestamp

#### GET `/api/documents/{document_id}/pages/{page_number}`

**Purpose**: Fetch specific document page with context windows

**Validation**:

- Page number must be >= 1
- Page must exist within document bounds
- Document must exist in database

**Response**: `PageDataResponse` with page content, word boundaries, and context windows

#### GET `/api/documents/{document_id}`

**Purpose**: Retrieve complete document information

**Response**: Full document data including content and metadata

### Explanations API (`/api/explanations/`)

Provides AI-powered text explanations using LangChain and OpenAI integration.

#### POST `/api/explanations/`

**Purpose**: Generate contextual explanations for selected text

**Request Validation**:

- Text cannot be empty
- Maximum 1000 characters per request
- Optional context parameter for enhanced explanations

**AI Processing Pipeline**:

```python
# LangChain prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful reading assistant..."),
    ("user", "Explain this text: '{text}'\n\nContext: {context}")
])

# Processing chain
explanation_chain = prompt | model | output_parser

# Generate explanation
explanation = explanation_chain.invoke({
    "text": request.text,
    "context": context
})
```

**Response**: `ExplanationResponse` with explanation, context usage flag, and response time metrics

## Data Models

### Pydantic Models (API Layer)

**Request/Response Models** (`models/document.py`, `models/explanation.py`):

```python
class DocumentResponse(BaseModel):
    """Response model for document operations."""
    id: str
    title: str
    metadata: DocumentMetadata
    uploaded_at: datetime
    message: str

class PageDataResponse(BaseModel):
    """Response model for document page endpoint."""
    page_number: int
    content: str
    start_word_index: int
    end_word_index: int
    word_count: int
    context_before: str
    context_after: str

class ExplanationRequest(BaseModel):
    """Request model for text explanation."""
    text: str
    context: Optional[str] = None
```

**Key Features**:

- Automatic validation using Python type hints
- JSON serialization/deserialization
- Optional field support with defaults
- Comprehensive error messages for validation failures

### SQLAlchemy Models (Database Layer)

**Database Models** (`models/db_models.py`):

```python
class Document(Base):
    """Document model for storing document metadata."""
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    total_pages = Column(Integer, nullable=True)
    words_per_page = Column(Integer, default=500)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to pages
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")

class DocumentPage(Base):
    """DocumentPage model for storing individual pages."""
    __tablename__ = "document_pages"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"))
    page_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    start_word_index = Column(Integer, nullable=False)
    end_word_index = Column(Integer, nullable=False)
    context_before = Column(Text, default="")
    context_after = Column(Text, default="")

    # Composite index for efficient querying
    __table_args__ = (
        Index('idx_document_page', 'document_id', 'page_number'),
    )
```

**Key Features**:

- One-to-many relationship between documents and pages
- Cascade deletion for data integrity
- Composite indexing for optimized queries
- Foreign key constraints with proper cleanup

## Business Logic Services

### DocumentService (`services/document_service.py`)

The core service handling document processing, page splitting, and storage operations.

#### Document Processing Pipeline

**1. Content Processing**:

```python
def process_text_content(self, content: bytes, filename: str) -> Dict:
    # Decode UTF-8 content
    text_content = content.decode('utf-8')

    # Calculate metadata
    word_count = len(text_content.split())
    estimated_reading_time = max(1, word_count // 200)  # 200 WPM average

    # Generate preview (first 20 words)
    preview = ' '.join(words[:20]) + ('...' if len(words) > 20 else '')
```

**2. Page Splitting Algorithm**:

```python
def split_document_into_pages(self, content: str, words_per_page: int = 500) -> List[Dict]:
    words = content.split()
    total_words = len(words)
    page_count = math.ceil(total_words / words_per_page)

    for page_num in range(page_count):
        start_word_index = page_num * words_per_page
        end_word_index = min(start_word_index + words_per_page, total_words)

        page_words = words[start_word_index:end_word_index]
        page_content = ' '.join(page_words)
```

**3. Context Window Calculation**:

```python
def calculate_context_windows(self, pages: List[Dict], window_size: int = 100) -> List[Dict]:
    for i, page in enumerate(pages):
        # Previous page context (last N words)
        if i > 0:
            previous_words = pages[i - 1]['content'].split()
            context_words = previous_words[-window_size:]
            page['context_before'] = ' '.join(context_words)

        # Next page context (first N words)
        if i < len(pages) - 1:
            next_words = pages[i + 1]['content'].split()
            context_words = next_words[:window_size]
            page['context_after'] = ' '.join(context_words)
```

#### Storage Strategy

**Dual Storage Implementation**:

- **File System Storage**: Maintains backward compatibility and provides fast content access
- **Database Storage**: Enables structured queries, relationships, and efficient page retrieval

**Storage Process**:

1. Generate unique UUID for document identification
2. Process content and calculate metadata
3. Split document into pages with context windows
4. Store content and metadata files to file system
5. Create database records for document and all pages
6. Use database transactions for atomicity

#### Database Operations

**Document Storage**:

```python
def store_document(self, content: bytes, filename: str, words_per_page: int = 500):
    db = SessionLocal()
    try:
        # Create document record
        db_document = Document(
            id=document_id,
            title=filename,
            content=text_content,
            word_count=processed['word_count'],
            total_pages=len(pages),
            words_per_page=words_per_page
        )
        db.add(db_document)

        # Create page records
        for page in pages:
            db_page = DocumentPage(
                document_id=document_id,
                page_number=page['page_number'],
                content=page['content'],
                context_before=page['context_before'],
                context_after=page['context_after']
            )
            db.add(db_page)

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
```

**Page Retrieval**:

```python
def get_document_page(self, document_id: str, page_number: int):
    db = SessionLocal()
    try:
        # Verify document exists
        db_document = db.query(Document).filter(Document.id == document_id).first()

        # Validate page bounds
        if page_number < 1 or page_number > db_document.total_pages:
            return None

        # Query specific page
        db_page = db.query(DocumentPage).filter(
            DocumentPage.document_id == document_id,
            DocumentPage.page_number == page_number
        ).first()
    finally:
        db.close()
```

## AI Integration

### LangChain Setup

**Model Configuration**:

```python
# OpenAI model initialization
model = ChatOpenAI(
    temperature=0,        # Deterministic responses
    model="gpt-4.1-mini", # Cost-effective model choice
)

# Output parser for clean text responses
output_parser = StrOutputParser()
```

**Prompt Engineering**:

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful reading assistant. Explain words, idioms, or technical terms based on the context. Keep explanations clear, concise, and under 5 words if possible."),
    ("user", "Explain this text: '{text}'\n\nContext: {context}")
])

# Processing chain
explanation_chain = prompt | model | output_parser
```

**Key Design Decisions**:

- **Temperature 0**: Ensures consistent, deterministic explanations
- **Concise Responses**: Optimized for quick understanding (under 5 words when possible)
- **Context Integration**: Uses surrounding text for better explanations
- **Error Handling**: Graceful fallbacks for API failures

### Performance Optimization

**Response Time Tracking**:

```python
start_time = time.time()
explanation = explanation_chain.invoke({"text": request.text, "context": context})
response_time = int((time.time() - start_time) * 1000)
```

**Input Validation**:

- Maximum 1000 characters per request to prevent timeouts
- Empty text validation
- Context length optimization

## Database Schema

### Tables and Relationships

**Documents Table**:

- **Primary Key**: `id` (UUID string)
- **Content Storage**: Full document text for backward compatibility
- **Metadata Fields**: word count, reading time, language detection
- **Pagination Fields**: total pages, words per page configuration
- **Timestamps**: Upload tracking for analytics

**Document Pages Table**:

- **Composite Key**: `document_id` + `page_number`
- **Content Segmentation**: Individual page content with word boundaries
- **Context Windows**: Previous and next page context for AI explanations
- **Performance Indexing**: Optimized for page retrieval queries

**Indexing Strategy**:

```sql
-- Composite index for efficient page queries
CREATE INDEX idx_document_page ON document_pages (document_id, page_number);

-- Primary key indexes automatically created
CREATE INDEX ix_documents_id ON documents (id);
CREATE INDEX ix_document_pages_id ON document_pages (id);
```

### Data Integrity

**Foreign Key Constraints**:

- `document_pages.document_id` → `documents.id` with CASCADE DELETE
- Ensures automatic cleanup when documents are deleted
- Maintains referential integrity across tables

**Validation Rules**:

- Document IDs must be valid UUIDs
- Page numbers must be positive integers
- Word indices must be non-negative and properly ordered
- Content fields cannot be null or empty

## Error Handling（以下System Design暂时不看）

### API Error Standards

**HTTP Status Code Usage**:

- `400 Bad Request`: Invalid input data, validation failures
- `404 Not Found`: Document or page not found
- `413 Request Entity Too Large`: File size exceeds limits
- `500 Internal Server Error`: Unexpected server errors

**Error Response Format**:

```python
class ErrorResponse(BaseModel):
    error: str        # Error type/category
    detail: str       # Human-readable description
    status_code: int  # HTTP status code
```

### Validation Error Handling

**File Upload Validation**:

```python
def validate_file(file: UploadFile, content: bytes) -> None:
    # File extension validation
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not supported")

    # MIME type validation
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Size validation
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    # UTF-8 encoding validation
    try:
        content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must contain valid UTF-8 text")
```

**Database Error Handling**:

```python
try:
    db.commit()
except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")
finally:
    db.close()
```

### AI Service Error Handling

**OpenAI API Integration**:

- Timeout handling for slow responses
- Rate limit detection and backoff
- Graceful degradation when AI service is unavailable
- Input validation to prevent API abuse

**Error Recovery Strategies**:

- Automatic retry with exponential backoff
- Fallback responses for critical failures
- Comprehensive logging for debugging
- User-friendly error messages

## Performance Optimizations

### Database Performance

**Query Optimization**:

- Composite indexes on frequently queried columns
- Efficient JOIN operations between documents and pages
- Pagination support for large document collections
- Connection pooling for concurrent requests

**Memory Management**:

- Lazy loading of document content
- Efficient page-based content retrieval
- Proper session cleanup to prevent memory leaks
- Optimized SQLAlchemy query patterns

### Storage Performance

**File System Operations**:

- Organized directory structure for fast file access
- UUID-based naming to prevent conflicts
- Separate content and metadata storage for flexibility
- Atomic file operations to prevent corruption

**Caching Strategies**:

- Database connection pooling
- Prepared statement caching
- Metadata caching for frequently accessed documents
- Context window pre-calculation for faster page loads

### AI Service Performance

**Request Optimization**:

- Input length validation to prevent timeouts
- Efficient prompt templates for faster processing
- Response time monitoring and alerting
- Batch processing capabilities for multiple requests

**Resource Management**:

- Connection reuse for OpenAI API calls
- Request queuing to prevent rate limit violations
- Memory-efficient text processing
- Asynchronous processing where applicable

## Security Considerations

### Input Validation

**File Upload Security**:

- Strict MIME type validation using multiple methods
- File size limits to prevent resource exhaustion
- Content scanning for malicious patterns
- UTF-8 encoding validation to prevent injection attacks

**API Input Sanitization**:

- Pydantic model validation for all requests
- SQL injection prevention through ORM usage
- XSS prevention in text content handling
- Path traversal protection in file operations

### Data Security

**Storage Security**:

- Secure file permissions on document storage
- Database access controls and authentication
- Encrypted connections for external API calls
- Proper cleanup of temporary files

**Privacy Protection**:

- No logging of sensitive document content
- Secure handling of AI API responses
- Data retention policies for uploaded documents
- User consent mechanisms for AI processing

### API Security

**Access Control**:

- CORS configuration for frontend integration
- Rate limiting to prevent API abuse
- Input validation on all endpoints
- Proper error handling to prevent information leakage

**Authentication Framework**:

- Prepared for future authentication implementation
- Session management infrastructure
- Role-based access control foundations
- Audit logging capabilities

## Deployment and Configuration

### Environment Configuration

**Required Environment Variables**:

```bash
FRONTEND_URL=http://localhost:3000    # CORS configuration
OPENAI_API_KEY=your_api_key_here     # AI service authentication
DATABASE_URL=sqlite:///storage/database/documents.db  # Database connection
```

**Optional Configuration**:

```bash
MAX_FILE_SIZE=10485760               # 10MB default
WORDS_PER_PAGE=500                   # Default page size
CONTEXT_WINDOW_SIZE=100              # Context words per page
```

### Database Migration

**Initial Setup**:

```python
# Automatic table creation on startup
def init_db():
    Base.metadata.create_all(bind=engine)
```

**Migration Strategy**:

- SQLAlchemy Alembic integration for schema changes
- Backward compatibility with file-based storage
- Data migration scripts for version upgrades
- Rollback procedures for failed migrations

### Production Deployment

**Server Configuration**:

```bash
# Production server with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# With SSL and production settings
uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

**Performance Tuning**:

- Worker process scaling based on CPU cores
- Database connection pool sizing
- File system optimization for document storage
- Memory limits and garbage collection tuning

## Monitoring and Logging

### Application Monitoring

**Health Check Endpoint**:

```python
@app.get("/")
async def root():
    return {"message": "AI Reader Agent API is running"}
```

**Performance Metrics**:

- Response time tracking for AI explanations
- Database query performance monitoring
- File upload success/failure rates
- API endpoint usage statistics

### Error Logging

**Structured Logging**:

- Request/response logging for debugging
- Error stack traces for troubleshooting
- Performance bottleneck identification
- Security event logging

**Log Management**:

- Centralized logging for production environments
- Log rotation and retention policies
- Error alerting and notification systems
- Performance dashboard integration

This comprehensive backend documentation provides complete coverage of the AI Reader Agent's server-side architecture, implementation details, and operational considerations. The documentation serves as both a reference for current developers and an onboarding guide for new team members joining the project.
