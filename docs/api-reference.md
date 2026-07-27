# API Reference


## Base URL

```
http://localhost:8000
```

## API Overview

The AI Reader Agent API provides two main services:

- **Documents API** (`/api/documents/`): Upload, store, and retrieve text documents with intelligent page splitting
- **Explanations API** (`/api/explanations/`): Generate AI-powered explanations for selected text using OpenAI GPT models

## Content Type

All API endpoints accept and return JSON data unless otherwise specified.

？(except file uploads which use `multipart/form-data`)

---

## Documents API

The Documents API handles **document upload, processing, and retrieval** 
### Upload Document

Upload a text document for processing and storage.

**Endpoint:** `POST /api/documents/`

**Content-Type:** `multipart/form-data`

#### Request Parameters

| Parameter | Type | Required | Description                            |
| --------- | ---- | -------- | -------------------------------------- |
| `file`    | File | Yes      | Text file to upload (.txt format only) |

#### File Validation Rules

- **File Type**: Only `.txt` files with `text/plain` MIME type
- **File Size**: Maximum 10MB (10,485,760 bytes)
- **Content**: Must be valid UTF-8 encoded text
- **Content Validation**: Uses python-magic library when available for additional MIME type verification


### Get Document Metadata

Retrieve document metadata including page count and word statistics.

**Endpoint:** `GET /api/documents/{document_id}/metadata`

#### Path Parameters

| Parameter     | Type   | Required | Description                       |
| ------------- | ------ | -------- | --------------------------------- |
| `document_id` | string | Yes      | Unique document identifier (UUID) |

### Get Document Page

Retrieve a specific page from a document with context windows for AI explanations.

**Endpoint:** `GET /api/documents/{document_id}/pages/{page_number}`

#### Path Parameters

| Parameter     | Type    | Required | Description                         |
| ------------- | ------- | -------- | ----------------------------------- |
| `document_id` | string  | Yes      | Unique document identifier (UUID)   |
| `page_number` | integer | Yes      | Page number to retrieve (1-indexed) |

#### Response

**Success (200 OK):**

```json
{
  "page_number": 2,
  "content": "This is the content of page 2. It contains approximately 500 words split intelligently at sentence boundaries when possible...",
  "start_word_index": 500,
  "end_word_index": 999,
  "word_count": 499,
  "context_before": "...last 100 words from previous page for AI context...",
  "context_after": "...first 100 words from next page for AI context..."
}
```

#### Response Fields

| Field              | Type    | Description                                              |
| ------------------ | ------- | -------------------------------------------------------- |
| `page_number`      | integer | Current page number (1-indexed)                          |
| `content`          | string  | Main content of the page                                 |
| `start_word_index` | integer | Starting word position in full document                  |
| `end_word_index`   | integer | Ending word position in full document                    |
| `word_count`       | integer | Number of words on this page                             |
| `context_before`   | string  | Last 100 words from previous page (empty for first page) |
| `context_after`    | string  | First 100 words from next page (empty for last page)     |

### Get Full Document

Retrieve complete document information including full content.

**Endpoint:** `GET /api/documents/{document_id}`

#### Path Parameters

| Parameter     | Type   | Required | Description                       |
| ------------- | ------ | -------- | --------------------------------- |
| `document_id` | string | Yes      | Unique document identifier (UUID) |

#### Response

**Success (200 OK):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "example-document.txt",
  "content": "Full document content as uploaded...",
  "metadata": {
    "file_type": "text/plain",
    "file_size": 2048,
    "word_count": 350,
    "estimated_reading_time": 2,
    "language": "en"
  },
  "uploaded_at": "2024-01-15T10:30:00.000Z",
  "total_pages": 1,
  "words_per_page": 500
}
```

## Explanations API

The Explanations API provides AI-powered text explanations using OpenAI's GPT models through LangChain integration.

### Generate Explanation

Generate an AI explanation for selected text with optional context.

**Endpoint:** `POST /api/explanations/`

**Content-Type:** `application/json`


## Error Handling

### HTTP Status Codes

The API uses standard HTTP status codes to indicate success or failure:

| Status Code | Description              | Usage                                           |
| ----------- | ------------------------ | ----------------------------------------------- |
| `200`       | OK                       | Successful GET requests                         |
| `201`       | Created                  | Successful POST requests (document upload)      |
| `400`       | Bad Request              | Invalid request parameters or validation errors |
| `404`       | Not Found                | Resource not found (document, page)             |
| `413`       | Request Entity Too Large | File size exceeds 10MB limit                    |
| `500`       | Internal Server Error    | Unexpected server errors                        |

### Error Response Format

All error responses follow a consistent JSON structure:

```json
{
  "detail": "Human-readable error message with specific details"
}
```


## Data Models

### Document Response Model

```typescript
interface DocumentResponse {
  id: string; // UUID
  title: string; // Original filename
  metadata: DocumentMetadata;
  uploaded_at: string; // ISO 8601 datetime
  message: string; // Success message
}

interface DocumentMetadata {
  file_type: string; // "text/plain"
  file_size: number; // Bytes
  word_count: number; // Total words
  estimated_reading_time: number; // Minutes
  language: string; // "en"
}
```

### Page Data Model

```typescript
interface PageDataResponse {
  page_number: number; // 1-indexed
  content: string; // Page content
  start_word_index: number; // Word position in full document
  end_word_index: number; // Word position in full document
  word_count: number; // Words on this page
  context_before: string; // Previous page context
  context_after: string; // Next page context
}
```

### Explanation Models

```typescript
interface ExplanationRequest {
  text: string; // Text to explain
  context?: string; // Optional context
}

interface ExplanationResponse {
  text: string; // Original text
  explanation: string; // AI explanation
  context_used: boolean; // Whether context was provided
  response_time_ms: number; // Response time
}
```

---