# System Architecture Documentation

## 1. Overview

**AI Reader Agent** is a web application that helps users read text documents with AI-powered explanations. Users can upload a document, navigate through pages, and select text to get context-aware explanations from AI.

The system follows a **three-layer architecture**:  

1. **Frontend** – Handles user interface and interactions  
2. **Backend** – Manages documents, AI requests, and business logic  
3. **Data Layer** – Stores document content, metadata, and communicates with external AI services  

> Think of it as a stack: Frontend talks to Backend, which talks to Data and AI services.

---

## 2. Architecture Diagram

```	
Overall
    UI--> API
    API --> DB
    API --> AI

```
```
Frontend Layer (React TypeScript)
        UI
        ?Router[React Router]
        ?Services[Frontend Services]
        ?Cache[Page Cache Manager]
```
```
Backend Layer (Python FastAPI)"
        API
        Services
        Models
        Database
        Storage
       无 Middleware[CORS & Validation]
    

   

    UI --> Router
    UI --> Services
    Services --> Cache
    Services --> API
    API --> BL
    BL --> Models
    BL --> SQLite
    BL --> FileSystem
    BL --> OpenAI

```

## Three-Tier Architecture

### 1. Frontend Layer (Presentation Tier)


- **DocumentViewer**: Main reading interface with page navigation and text selection
- **FileUpload**: Secure document upload with validation
- **Layout**: Application shell and navigation structure
- **PageFetcher**: Handles API communication with retry logic
- **PageCacheManager**: Implements intelligent page caching with LRU eviction

### 2. Backend Layer (Business Logic Tier)

The backend is built with Python FastAPI, providing a high-performance REST API with automatic documentation and validation.

#### API Structure

- **Documents API** (`/api/documents/`): Document upload, metadata, and page retrieval
- **Explanations API** (`/api/explanations/`): AI-powered text explanations
- **DocumentService**: Core document processing, page splitting, and storage management

### 3. Data Layer (Persistence Tier)

The data layer implements a hybrid storage strategy combining structured database storage with file system storage for optimal performance.

#### Storage Systems

- **SQLite Database**: Structured storage for document metadata and pages
- **File Storage**: Document content and metadata files for backward compatibility


## Component Relationships and Data Flow

### Document Upload Flow

```mermaid
sequenceDiagram
    participant User
    participant FileUpload
    participant DocumentsAPI
    participant DocumentService
    participant Database
    participant FileSystem

    User->>FileUpload: Upload text file
    FileUpload->>DocumentsAPI: POST /api/documents/
    DocumentsAPI->>DocumentService: store_document()
    DocumentService->>DocumentService: Process & split into pages
    DocumentService->>Database: Store document & pages
    DocumentService->>FileSystem: Store content & metadata
    DocumentService->>DocumentsAPI: Return DocumentResponse
    DocumentsAPI->>FileUpload: Document metadata
    FileUpload->>User: Upload success
```

### Document Reading Flow

```mermaid
sequenceDiagram
    participant User
    participant DocumentViewer
    participant PageFetcher
    participant PageCache
    participant DocumentsAPI
    participant Database

    User->>DocumentViewer: Navigate to document
    DocumentViewer->>PageFetcher: fetchMetadata()
    PageFetcher->>DocumentsAPI: GET /documents/{id}/metadata
    DocumentsAPI->>Database: Query document metadata
    Database->>DocumentsAPI: Return metadata
    DocumentsAPI->>PageFetcher: DocumentMetadata
    PageFetcher->>DocumentViewer: Metadata with total pages

    DocumentViewer->>PageCache: getPage(1)
    PageCache->>DocumentViewer: null (cache miss)
    DocumentViewer->>PageFetcher: fetchPage(1)
    PageFetcher->>DocumentsAPI: GET /documents/{id}/pages/1
    DocumentsAPI->>Database: Query page data
    Database->>DocumentsAPI: Return page content
    DocumentsAPI->>PageFetcher: PageData
    PageFetcher->>PageCache: setPage(1, pageData)
    PageCache->>DocumentViewer: Page content

    Note over PageCache: Preload adjacent pages (±2)
```

### AI Explanation Flow

```mermaid
sequenceDiagram
    participant User
    participant DocumentViewer
    participant ExplanationsAPI
    participant LangChain
    participant OpenAI

    User->>DocumentViewer: Select text
    DocumentViewer->>DocumentViewer: Extract context around selection
    DocumentViewer->>ExplanationsAPI: POST /api/explanations/
    ExplanationsAPI->>LangChain: Process with context
    LangChain->>OpenAI: Generate explanation
    OpenAI->>LangChain: AI response
    LangChain->>ExplanationsAPI: Formatted explanation
    ExplanationsAPI->>DocumentViewer: ExplanationResponse
    DocumentViewer->>User: Display explanation (inline or sidebar)
```


### Storage Systems Integration

#### Dual Storage Strategy

The system implements a dual storage approach for reliability and performance:

1. **Database Storage (Primary)**

   - SQLite database for structured queries
   - Document and DocumentPage tables with relationships
   - Optimized indexes for efficient page retrieval

2. **File System Storage (Backup)**
   - JSON metadata files for backward compatibility
   - Text content files for direct access
   - Organized directory structure

#### Database Schema

```mermaid
erDiagram
    Document {
        string id PK
        string title
        text content
        string file_type
        integer file_size
        integer word_count
        integer estimated_reading_time
        string language
        integer total_pages
        integer words_per_page
        datetime uploaded_at
    }

    DocumentPage {
        string id PK
        string document_id FK
        integer page_number
        text content
        integer start_word_index
        integer end_word_index
        integer word_count
        text context_before
        text context_after
        datetime created_at
    }

    Document ||--o{ DocumentPage : "has pages"
```

## Scalability Considerations(带扩展)


### Horizontal Scaling Strategies

#### Database Scaling

- **Read Replicas**: SQLite can be replaced with PostgreSQL for read replicas
- **Sharding**: Documents can be sharded by ID or user for large datasets
- **Caching Layer**: Redis can be added for distributed caching

#### Application Scaling

- **Load Balancing**: Multiple FastAPI instances behind a load balancer
- **Microservices**: Document processing and AI services can be separated
- **CDN Integration**: Static assets and cached content via CDN

#### External Service Scaling

- **AI Service Redundancy**: Multiple AI providers for failover
- **Rate Limiting**: Implement rate limiting for API protection
- **Async Processing**: Queue-based processing for heavy operations

### Monitoring and Observability

#### Logging Strategy

- **Structured Logging**: JSON-formatted logs for better parsing
- **Error Tracking**: Comprehensive error logging with context
- **Performance Metrics**: Response times and cache hit rates

#### Health Checks

- **Database Health**: Connection and query performance monitoring
- **External Service Health**: OpenAI API availability and response times
- **Application Health**: Memory usage and request processing metrics

## Security Architecture（面试之前可看）

### Input Validation and Sanitization

#### File Upload Security

- **MIME Type Validation**: Strict text/plain enforcement
- **File Size Limits**: 10MB maximum to prevent resource exhaustion
- **Content Validation**: UTF-8 encoding verification
- **Extension Filtering**: Only .txt files allowed

#### API Security

- **Request Validation**: Pydantic models for all API inputs
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **XSS Prevention**: Proper output encoding in React components

### CORS Configuration

The backend implements proper CORS configuration:

- **Origin Restrictions**: Only frontend URL allowed
- **Method Restrictions**: Only necessary HTTP methods enabled
- **Credential Handling**: Secure credential transmission

### Data Protection

#### Storage Security

- **File Permissions**: Proper file system permissions for document storage
- **Database Security**: SQLite file permissions and access control
- **Sensitive Data**: Environment variables for API keys and configuration

#### Privacy Considerations

- **Data Retention**: Clear policies for document storage duration
- **User Content**: Secure handling of uploaded documents
- **AI Service Privacy**: Consideration of data sent to external AI services

## Development and Deployment Architecture

### Development Environment

#### Local Development Setup

- **Frontend**: Vite development server with hot reload
- **Backend**: Uvicorn with auto-reload for development
- **Database**: Local SQLite file for development
- **Environment**: Docker Compose for consistent development environment

#### Build Process

- **Frontend Build**: TypeScript compilation and Vite bundling
- **Backend Packaging**: Python package with dependencies
- **Static Assets**: Optimized CSS and JavaScript bundles

### Deployment Considerations

#### Production Architecture

- **Reverse Proxy**: Nginx for static file serving and load balancing
- **Application Server**: Gunicorn with Uvicorn workers for production
- **Database**: PostgreSQL for production scalability
- **File Storage**: Cloud storage (S3) for document files

#### Infrastructure as Code

- **Containerization**: Docker containers for consistent deployment
- **Orchestration**: Kubernetes or Docker Compose for service management
- **CI/CD Pipeline**: Automated testing and deployment

This architecture provides a solid foundation for the AI Reader Agent application with clear separation of concerns, scalable design patterns, and comprehensive integration strategies. The modular design allows for future enhancements and scaling as the application grows.
