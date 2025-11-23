# UML Class Diagram - AI Reader Agent

## Current Architecture

```mermaid
classDiagram
    %% Backend Models
    class BaseModel {
        <<Pydantic>>
        +model_dump()
        +model_validate()
    }

    class DocumentMetadata {
        +str file_type
        +int file_size
        +int word_count
        +int estimated_reading_time
        +str language
    }

    class DocumentResponse {
        +str id
        +str title
        +DocumentMetadata metadata
        +datetime uploaded_at
        +str message
    }

    class ErrorResponse {
        +str error
        +str detail
        +int status_code
    }

    %% Backend Services
    class DocumentService {
        -Path storage_path
        +__init__(storage_path: str)
        +process_text_content(content: bytes, filename: str) Dict
        +store_document(content: bytes, filename: str) DocumentResponse
        +get_document(document_id: str) Optional~Dict~
        +list_documents() List~Dict~
        +delete_document(document_id: str) bool
    }

    %% API Layer
    class DocumentRouter {
        <<FastAPI Router>>
        +upload_document(file: UploadFile) DocumentResponse
        +list_documents() Dict
        +get_document(document_id: str) Dict
        +delete_document(document_id: str) Dict
        -validate_file(file: UploadFile, content: bytes) None
    }

    class ExplanationRouter {
        <<FastAPI Router>>
        +get_explanation(request: ExplanationRequest) ExplanationResponse
        +explanation_health() Dict
    }

    class ExplanationRequest {
        +str text
        +Optional~str~ context
        +Optional~str~ document_title
    }

    class ExplanationResponse {
        +str text
        +str explanation
        +bool context_used
        +int response_time_ms
    }

    %% LangChain Integration
    class ChatOpenAI {
        <<LangChain>>
        -float temperature
        -str model
        +invoke(input: Dict) str
    }

    class ChatPromptTemplate {
        <<LangChain>>
        +from_messages(messages: List) ChatPromptTemplate
    }

    class StrOutputParser {
        <<LangChain>>
        +parse(output: str) str
    }

    %% Frontend Components (TypeScript/React)
    class FileUpload {
        <<React Component>>
        -UploadStatus uploadStatus
        -HTMLInputElement fileInputRef
        +validateFile(file: File) string|null
        +uploadFile(file: File) Promise~void~
        +handleFileSelect(e: ChangeEvent) void
        +handleButtonClick() void
        +clearError() void
    }

    class UploadStatus {
        +bool isUploading
        +string|null error
        +bool success
    }

    class DocumentViewer {
        <<React Component>>
        -Document|null document
        -bool loading
        -string|null error
        -number fontSize
        -number lineHeight
        -string selectedText
        -string explanation
        -bool isLoadingExplanation
        +fetchDocument() Promise~void~
        +increaseFontSize() void
        +decreaseFontSize() void
        +handleTextSelection() void
        +requestExplanation() Promise~void~
        +getContextAroundSelection() string
    }

    class Document {
        +string id
        +string title
        +string content
        +Metadata metadata
        +string uploaded_at
    }

    class Metadata {
        +number file_size
        +number word_count
        +number estimated_reading_time
        +string language
    }

    %% File System Operations
    class FileSystemHandler {
        <<Abstract>>
        +read(path: Path) bytes
        +write(path: Path, content: bytes) void
        +delete(path: Path) bool
        +exists(path: Path) bool
    }

    %% Relationships
    BaseModel <|-- DocumentMetadata : inherits
    BaseModel <|-- DocumentResponse : inherits
    BaseModel <|-- ErrorResponse : inherits
    BaseModel <|-- ExplanationRequest : inherits
    BaseModel <|-- ExplanationResponse : inherits

    DocumentResponse *-- DocumentMetadata : contains
    DocumentService ..> DocumentResponse : creates
    DocumentService ..> DocumentMetadata : creates
    DocumentService ..> FileSystemHandler : uses

    DocumentRouter ..> DocumentService : uses
    DocumentRouter ..> DocumentResponse : returns
    DocumentRouter ..> ErrorResponse : returns

    ExplanationRouter ..> ExplanationRequest : receives
    ExplanationRouter ..> ExplanationResponse : returns
    ExplanationRouter ..> ChatOpenAI : uses
    ExplanationRouter ..> ChatPromptTemplate : uses
    ExplanationRouter ..> StrOutputParser : uses

    ChatPromptTemplate --> ChatOpenAI : chains to
    ChatOpenAI --> StrOutputParser : chains to

    FileUpload ..> UploadStatus : manages
    FileUpload ..> DocumentRouter : calls API

    DocumentViewer ..> Document : displays
    DocumentViewer ..> DocumentRouter : calls API
    DocumentViewer ..> ExplanationRouter : calls API
    Document *-- Metadata : contains
```

## Enhanced Architecture with Full OOP Concepts

This diagram shows how the system could be enhanced to demonstrate all OOP principles:

```mermaid
classDiagram
    %% Abstract Base Classes (Abstraction)
    class DocumentProcessor {
        <<abstract>>
        +process(content: bytes, filename: str)* Dict
        +validate(content: bytes)* bool
        +extract_metadata(content: bytes)* DocumentMetadata
        #calculate_reading_time(word_count: int) int
    }

    class StorageHandler {
        <<abstract>>
        -Path base_path
        +save(id: str, content: Any)* bool
        +load(id: str)* Optional~Any~
        +delete(id: str)* bool
        +list_all()* List
        #ensure_directory_exists(path: Path) void
    }

    %% Concrete Implementations (Inheritance & Polymorphism)
    class TextDocumentProcessor {
        -str encoding
        +process(content: bytes, filename: str) Dict
        +validate(content: bytes) bool
        +extract_metadata(content: bytes) DocumentMetadata
        +count_words(text: str) int
        +detect_language(text: str) str
    }

    class PDFDocumentProcessor {
        -bool extract_images
        +process(content: bytes, filename: str) Dict
        +validate(content: bytes) bool
        +extract_metadata(content: bytes) DocumentMetadata
        +extract_text_from_pdf(content: bytes) str
        +get_page_count(content: bytes) int
    }

    class MarkdownDocumentProcessor {
        -bool preserve_formatting
        +process(content: bytes, filename: str) Dict
        +validate(content: bytes) bool
        +extract_metadata(content: bytes) DocumentMetadata
        +parse_markdown(text: str) str
        +extract_headers(text: str) List~str~
    }

    %% Storage Implementations (Polymorphism)
    class FileSystemStorage {
        -Path storage_path
        +save(id: str, content: Any) bool
        +load(id: str) Optional~Any~
        +delete(id: str) bool
        +list_all() List
        -get_file_path(id: str) Path
    }

    class DatabaseStorage {
        -str connection_string
        -Connection db_connection
        +save(id: str, content: Any) bool
        +load(id: str) Optional~Any~
        +delete(id: str) bool
        +list_all() List
        -execute_query(query: str) Any
    }

    class CloudStorage {
        -str bucket_name
        -str api_key
        +save(id: str, content: Any) bool
        +load(id: str) Optional~Any~
        +delete(id: str) bool
        +list_all() List
        -upload_to_cloud(id: str, content: Any) bool
    }

    %% Service Layer with Dependency Injection
    class EnhancedDocumentService {
        -DocumentProcessor processor
        -StorageHandler content_storage
        -StorageHandler metadata_storage
        +__init__(processor: DocumentProcessor, content_storage: StorageHandler, metadata_storage: StorageHandler)
        +process_and_store(content: bytes, filename: str) DocumentResponse
        +retrieve_document(document_id: str) Optional~Dict~
        +list_all_documents() List~Dict~
        +remove_document(document_id: str) bool
        +set_processor(processor: DocumentProcessor) void
    }

    %% Factory Pattern (Polymorphism)
    class DocumentProcessorFactory {
        <<factory>>
        +create_processor(file_type: str) DocumentProcessor
        +register_processor(file_type: str, processor_class: Type) void
        -processors: Dict~str, Type~
    }

    %% Models with Inheritance
    class BaseDocument {
        <<abstract>>
        +str id
        +str title
        +datetime created_at
        +datetime updated_at
        +get_summary()* str
        +to_dict() Dict
    }

    class TextDocument {
        +str content
        +int word_count
        +str language
        +get_summary() str
        +get_preview(length: int) str
    }

    class StructuredDocument {
        +List~Section~ sections
        +Dict~str, Any~ metadata
        +get_summary() str
        +get_table_of_contents() List~str~
    }

    class Section {
        +str title
        +str content
        +int level
        +List~Section~ subsections
    }

    %% Method Overloading Simulation (Python doesn't have true overloading)
    class DocumentValidator {
        +validate(content: bytes) bool
        +validate(content: bytes, file_type: str) bool
        +validate(content: bytes, file_type: str, max_size: int) bool
        +validate_with_schema(content: bytes, schema: Dict) bool
    }

    %% Relationships - Inheritance
    DocumentProcessor <|-- TextDocumentProcessor : inherits
    DocumentProcessor <|-- PDFDocumentProcessor : inherits
    DocumentProcessor <|-- MarkdownDocumentProcessor : inherits

    StorageHandler <|-- FileSystemStorage : inherits
    StorageHandler <|-- DatabaseStorage : inherits
    StorageHandler <|-- CloudStorage : inherits

    BaseDocument <|-- TextDocument : inherits
    BaseDocument <|-- StructuredDocument : inherits

    %% Relationships - Composition & Aggregation
    EnhancedDocumentService o-- DocumentProcessor : uses (polymorphism)
    EnhancedDocumentService o-- StorageHandler : uses (polymorphism)
    StructuredDocument *-- Section : contains
    Section *-- Section : recursive composition

    %% Relationships - Dependencies
    DocumentProcessorFactory ..> DocumentProcessor : creates
    EnhancedDocumentService ..> DocumentResponse : returns
    EnhancedDocumentService ..> BaseDocument : manages

    %% Override Examples
    note for TextDocumentProcessor "Overrides:\n- process()\n- validate()\n- extract_metadata()"
    note for FileSystemStorage "Overrides:\n- save()\n- load()\n- delete()\n- list_all()"
    note for TextDocument "Overrides:\n- get_summary()"
```

## OOP Concepts Demonstrated

### 1. **Inheritance**

- `DocumentMetadata`, `DocumentResponse`, `ErrorResponse` inherit from Pydantic's `BaseModel`
- `TextDocumentProcessor`, `PDFDocumentProcessor`, `MarkdownDocumentProcessor` inherit from `DocumentProcessor`
- `FileSystemStorage`, `DatabaseStorage`, `CloudStorage` inherit from `StorageHandler`
- `TextDocument`, `StructuredDocument` inherit from `BaseDocument`

### 2. **Abstraction**

- `DocumentProcessor` - abstract base class defining interface for document processing
- `StorageHandler` - abstract base class for storage operations
- `BaseDocument` - abstract base class for document models
- These classes define contracts that concrete implementations must follow

### 3. **Polymorphism**

- `EnhancedDocumentService` can work with any `DocumentProcessor` implementation
- Storage operations work with any `StorageHandler` implementation
- Different document types can be processed through the same interface
- Factory pattern allows runtime selection of appropriate processor

### 4. **Overriding**

- Each concrete processor overrides `process()`, `validate()`, and `extract_metadata()`
- Each storage implementation overrides `save()`, `load()`, `delete()`, `list_all()`
- Document types override `get_summary()` with type-specific implementations

### 5. **Overloading** (Simulated in Python)

- `DocumentValidator` demonstrates method overloading through default parameters
- Python uses `@overload` decorator for type hints (not shown in diagram)
- Multiple signatures for `validate()` method

### 6. **File Processing**

- `FileSystemStorage` - saves/loads documents to/from hard drive
- `DocumentService.store_document()` - writes content and metadata files
- `DocumentService.get_document()` - reads files from storage
- Uses Python's `Path` and file I/O operations (`open()`, `read()`, `write()`)

## Current Implementation Notes

The current codebase demonstrates:

- ✅ **File Processing**: Full implementation in `DocumentService`
- ✅ **Basic Inheritance**: Through Pydantic models
- ⚠️ **Limited Abstraction**: No abstract base classes yet
- ⚠️ **Limited Polymorphism**: Single document processor type
- ❌ **No Overloading**: Python doesn't support traditional overloading
- ❌ **No Overriding**: No inheritance hierarchy to override

## Recommendations for Enhancement

To fully demonstrate all OOP concepts, consider:

1. **Add Abstract Base Classes** for document processors and storage handlers
2. **Implement Multiple Document Types** (PDF, Markdown, DOCX processors)
3. **Create Storage Abstraction** to support different storage backends
4. **Add Factory Pattern** for creating appropriate processors
5. **Implement Method Overloading** using `@overload` decorator and `functools.singledispatch`
6. **Create Document Type Hierarchy** with overridden methods
