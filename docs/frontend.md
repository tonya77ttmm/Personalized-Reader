# Frontend Documentation

## Overview

The AI Reader Agent frontend is a modern React TypeScript application built with Vite that provides an intuitive interface for document reading with AI-powered explanations. The application features a clean, responsive design using Tailwind CSS and implements intelligent page-based navigation with caching for optimal performance.

### Technology Stack

- **React 18.2.0**: Modern React with hooks and functional components
- **TypeScript 5.2.2**: Type-safe development with strict configuration
- **Vite 4.5.0**: Fast build tool and development server
- **React Router DOM 6.20.1**: Client-side routing and navigation
- **Tailwind CSS 3.3.5**: Utility-first CSS framework for responsive design
- **ESLint**: Code quality and consistency enforcement

### Architecture Overview

The frontend follows a component-based architecture with clear separation of concerns:

```
src/
├── components/          # Reusable UI components
│   ├── layout/         # App structure components
│   ├── reader/         # Document reading interface
│   └── upload/         # File upload functionality
├── pages/              # Route-level page components
├── services/           # Business logic and API communication
└── App.tsx            # Main application component
```

## Core Components

### Layout Components

#### Layout Component

**Purpose**: Provides the main application structure with consistent header and content area.

**Location**: `src/components/layout/Layout.tsx`

**Props Interface**:

```typescript
interface LayoutProps {
  children: ReactNode;
}
```

**Features**:

- Responsive container with consistent padding and margins
- Gray background (`bg-gray-50`) for visual hierarchy
- Integrates Header component for navigation
**Usage Example**:

```typescript
<Layout>
  <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/reader/:documentId?" element={<Reader />} />
  </Routes>
</Layout>
```

#### Header Component

**Purpose**: Application navigation bar with branding and route links.

**Location**: `src/components/layout/Header.tsx`

**Features**:

- Brand logo linking to home page
- Navigation menu with Home and Reader links

### Page Components

#### Home Component

**Purpose**: Landing page that introduces the application and provides entry point to the reader.

**Location**: `src/pages/Home.tsx`

#### Reader Component

**Purpose**: Main application page that orchestrates document upload and viewing functionality.

**Location**: `src/pages/Reader.tsx`

**State Management**:

```typescript
const [uploadedDocument, setUploadedDocument] = useState<any>(null);
```

**Key Features**:

- Conditional rendering based on document upload state
- Manages document state and passes to DocumentViewer

**Component Integration**:

- Integrates FileUpload component for document upload
- Passes document data to DocumentViewer component
- Manages state transitions between upload and reading modes

### Upload Components

#### FileUpload Component

**Purpose**: Secure file upload interface with comprehensive validation and user feedback.

**Location**: `src/components/upload/FileUpload.tsx`


**State Management**:

```typescript
interface UploadStatus {
  isUploading: boolean;
  error: string | null;
  success: boolean;
}
```

**Validation Rules**:

- **File Type**: Restricts to `text/plain` MIME type only
- **File Size**: Maximum 10MB limit with user-friendly error messages
- **Empty File**: Prevents upload of zero-byte files
- **Real-time Feedback**: Immediate validation on file selection

**Security Features**:

- MIME type validation prevents malicious file uploads
- File size limits prevent resource exhaustion
- Input sanitization and error handling

**API Integration**:

```typescript
const response = await fetch("http://localhost:8000/api/documents/", {
  method: "POST",
  body: formData,
});
```

### Reader Components

#### DocumentViewer Component

**Purpose**: Main document reading interface with AI-powered explanations and page-based navigation.

**Location**: `src/components/reader/DocumentViewer.tsx`

**Props Interface**:

```typescript
interface DocumentViewerProps {
  documentId: string;
  title?: string;
  onUploadDocument?: () => void;
}
```

**Core State Management**:

```typescript
// Document and page state
const [currentPage, setCurrentPage] = useState<number>(1);
const [totalPages, setTotalPages] = useState<number>(0);
const [currentPageData, setCurrentPageData] = useState<PageData | null>(null);
const [metadata, setMetadata] = useState<DocumentMetadata | null>(null);

// Text selection and explanation state
const [selectedText, setSelectedText] = useState<string>("");
const [explanation, setExplanation] = useState<string>("");
const [wordCount, setWordCount] = useState<number>(0);
const [selectionPosition, setSelectionPosition] =
  useState<SelectionPosition | null>(null);

// Loading and error states
const [isLoadingPage, setIsLoadingPage] = useState<boolean>(false);
const [isLoadingExplanation, setIsLoadingExplanation] = useState(false);
const [error, setError] = useState<string | null>(null);
```

**Key Features**:

1. **Page-Based Navigation**:

   - Fixed-height page container prevents scrolling
   - Previous/Next navigation with disabled states
   - Page number display with current/total format
   - Automatic page preloading for smooth navigation

2. **Text Selection and AI Explanations**:

   - Mouse-up event handling for text selection
   - Word count-based explanation display logic:
     - ≤3 words: Inline popup explanation
     - > 3 words: Fixed sidebar explanation
   - Real-time explanation requests to AI service
   - Context-aware explanations using surrounding text

3. **Intelligent Caching**:

   - Integration with PageCacheManager for performance
   - Automatic preloading of adjacent pages (±2 pages)
   - LRU-based cache eviction strategy


**Text Selection Logic**:

```typescript
const handleTextSelection = () => {
  const selection = window.getSelection();
  if (selection && selection.rangeCount > 0) {
    const text = selection.toString().trim();
    if (text.length > 0) {
      setSelectedText(text);
      const words = countWords(text);
      setWordCount(words);
      // Calculate position for inline display
      const rect = range.getBoundingClientRect();
      // Position calculation logic...
    }
  }
};
```

**Context Generation**:

```typescript
const getContextAroundSelection = (): string => {
  const content = document.content;
  const selectedIndex = selectionOffset;
  const start = Math.max(0, selectedIndex - 100);
  const end = Math.min(
    content.length,
    selectedIndex + selectedText.length + 100
  );
  return content.substring(start, end);
};
```

## Frontend Services

### PageFetcher Service

**Purpose**: Handles API communication for document pages and metadata with built-in error handling.

**Location**: `src/services/PageFetcher.ts`

**Class Structure**:

```typescript
export class PageFetcher {
  private readonly baseUrl: string;
  private readonly retryConfig: RetryConfig;

  constructor(
    baseUrl: string = "http://localhost:8000",
    retryConfig: Partial<RetryConfig> = {}
  );
}
```

**Key Methods**:

1. **fetchMetadata(documentId: string): Promise<DocumentMetadata>**

   - Retrieves document summary information
   - Returns total pages, word counts, and upload timestamp
   - Handles HTTP errors with appropriate status codes

2. **fetchPage(documentId: string, pageNumber: number): Promise<PageData>**
   - Fetches specific page content with context windows
   - Returns page content, word boundaries, and surrounding context
   - Implements error handling for missing pages

**TypeScript Interfaces**:

```typescript
export interface PageData {
  page_number: number;
  content: string;
  start_word_index: number;
  end_word_index: number;
  word_count: number;
  context_before: string;
  context_after: string;
}

export interface DocumentMetadata {
  id: string;
  title: string;
  total_pages: number;
  total_words: number;
  words_per_page: number;
  uploaded_at: string;
}
```

**Error Handling Strategy**:

- HTTP status code validation
- Descriptive error messages for different failure types
- Promise-based error propagation to calling components

### PageCacheManager Service

**Purpose**: Manages intelligent caching of document pages for optimal navigation performance.

**Location**: `src/services/PageCacheManager.ts`

**Class Structure**:

```typescript
export class PageCacheManager {
  private cache: Map<number, PageData> = new Map();
  private readonly maxSize: number = 5;
  private currentPage: number = 1;
}
```

**Core Functionality**:

1. **Cache Operations**:

   ```typescript
   getPage(pageNumber: number): PageData | null
   setPage(pageNumber: number, page: PageData): void
   hasPage(pageNumber: number): boolean
   clearCache(): void
   ```

2. **Intelligent Preloading**:
   ```typescript
   async preloadPages(
     documentId: string,
     currentPage: number,
     totalPages: number,
     fetchPage: PageFetchFunction,
     radius: number = 2
   ): Promise<void>
   ```

**Caching Strategy**:

- **LRU Eviction**: Removes oldest pages when cache exceeds 5 pages
- **Preloading Radius**: Automatically loads ±2 pages around current page
- **Parallel Fetching**: Uses Promise.all for concurrent page requests
- **Error Resilience**: Continues preloading even if individual pages fail

**Performance Optimizations**:

- Map-based storage for O(1) lookup performance
- Configurable cache size limits
- Distance-based eviction prioritizes recently accessed pages
- Async preloading doesn't block user interactions         



## Data Flow and State Management

### Component Communication Patterns

The application uses a combination of props, callbacks, and local state for data flow:

1. **Parent-to-Child**: Props for configuration and data
2. **Child-to-Parent**: Callback functions for events and state updates
3. **Service Integration**: Direct service instantiation in components

**Example Data Flow**:

```
Reader (Page)
├── FileUpload (onUploadSuccess callback)
└── DocumentViewer (documentId prop)
    ├── PageFetcher (API calls)
    └── PageCacheManager (caching)
```

### State Management Strategy

**Local Component State**: Each component manages its own UI state using React hooks:

- `useState` for simple state values
- `useEffect` for side effects and lifecycle management
- `useRef` for DOM element references

**Service State**: Business logic state is managed within service classes:

- PageCacheManager maintains cache state
- PageFetcher handles request state internally

## Styling and Design System

### Tailwind CSS Implementation

The application uses Tailwind CSS for consistent, responsive design with a utility-first approach.

**Configuration**: `tailwind.config.js`

```javascript
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

**Color Palette**:

- **Primary**: Blue (`blue-600`, `blue-700`) for interactive elements
- **Background**: Gray (`gray-50`, `gray-100`) for subtle backgrounds
- **Text**: Gray scale (`gray-600`, `gray-700`, `gray-900`) for hierarchy
- **Success**: Green (`green-50`, `green-400`) for positive feedback
- **Error**: Red (`red-50`, `red-400`) for error states

**Typography Scale**:

- **Headings**: `text-4xl`, `text-3xl`, `text-2xl` with `font-bold`
- **Body Text**: `text-lg`, `text-base`, `text-sm` with appropriate line heights
- **Interactive Elements**: `font-medium`, `font-semibold` for emphasis

**Responsive Design Patterns**:

- **Container**: `max-w-4xl mx-auto` for content width constraints
- **Spacing**: Consistent padding (`px-4`, `py-8`) and margins
- **Flexbox**: `flex items-center justify-between` for layout alignment
- **Grid**: Implicit grid behavior through flexbox and width utilities

### Component Styling Conventions

**Button Styles**:

```css
/* Primary Button */
bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 transition-colors

/* Secondary Button */
bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200

/* Disabled State */
bg-gray-400 text-gray-500 cursor-not-allowed
```

**Status Message Styles**:

```css
/* Success Message */
bg-green-50 border border-green-200 text-green-800

/* Error Message */
bg-red-50 border border-red-200 text-red-800

/* Loading State */
animate-spin rounded-full border-b-2 border-blue-600
```

## Error Handling Strategies 不重要

### Component-Level Error Handling

**FileUpload Component**:

- Validation errors displayed immediately with clear messages
- Network errors caught and displayed with retry options
- Loading states prevent multiple simultaneous uploads

**DocumentViewer Component**:

- Page loading errors with fallback content
- AI explanation errors with retry functionality
- Graceful degradation when services are unavailable

**Error Display Patterns**:

```typescript
// Inline error with icon and dismiss button
{
  error && (
    <div className="bg-red-50 border border-red-200 rounded-md p-3">
      <div className="flex">
        <ErrorIcon />
        <p className="text-sm text-red-800">{error}</p>
        <button onClick={clearError}>×</button>
      </div>
    </div>
  );
}
```

### Service-Level Error Handling

**PageFetcher Service**:

- HTTP status code validation
- Descriptive error messages based on response codes
- Promise rejection for proper error propagation

**PageCacheManager Service**:

- Graceful handling of failed preload requests
- Continues operation even when individual pages fail
- Console logging for debugging without breaking user experience

## Performance Optimizations

### Caching Strategy

**Page Caching**:

- 5-page LRU cache reduces API calls
- Preloading adjacent pages for smooth navigation
- Parallel fetching minimizes wait times

**Component Optimization**:

- Conditional rendering prevents unnecessary DOM updates
- Event handler optimization with proper cleanup
- Ref usage for direct DOM manipulation when needed

### Memory Management

**Cache Eviction**:

- Automatic cleanup when cache exceeds size limits
- Distance-based eviction prioritizes relevant pages
- Manual cache clearing when switching documents

**Component Cleanup**:

- Effect cleanup functions prevent memory leaks
- Event listener removal in useEffect cleanup
- Proper state reset when components unmount

## Integration Examples

### Adding a New Component

To add a new component to the application:

1. **Create Component File**:

```typescript
// src/components/example/NewComponent.tsx
import React from "react";

interface NewComponentProps {
  title: string;
  onAction?: () => void;
}

const NewComponent: React.FC<NewComponentProps> = ({ title, onAction }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      {onAction && (
        <button
          onClick={onAction}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Action
        </button>
      )}
    </div>
  );
};

export default NewComponent;
```

2. **Integrate with Parent Component**:

```typescript
import NewComponent from "../components/example/NewComponent";

const ParentComponent = () => {
  const handleAction = () => {
    console.log("Action triggered");
  };

  return (
    <div>
      <NewComponent title="Example Component" onAction={handleAction} />
    </div>
  );
};
```

### Customizing Existing Components

**DocumentViewer Customization**:

```typescript
// Custom font size and line height
const [fontSize, setFontSize] = useState(20);
const [lineHeight, setLineHeight] = useState(2.8);

// Apply to content div
<div
  style={{
    fontSize: `${fontSize}px`,
    lineHeight: lineHeight,
  }}
>
  {content}
</div>;
```

**FileUpload Validation Extension**:

```typescript
const validateFile = (file: File): string | null => {
  // Existing validations...

  // Add custom validation
  if (file.name.includes("temp")) {
    return "Temporary files are not allowed";
  }

  return null;
};
```

## Common Usage Patterns

### API Integration Pattern

```typescript
const [data, setData] = useState<DataType | null>(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiService.fetchData();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  fetchData();
}, [dependency]);
```

### Form Handling Pattern

```typescript
const [formData, setFormData] = useState<FormType>(initialState);
const [errors, setErrors] = useState<Record<string, string>>({});

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  const validationErrors = validateForm(formData);
  if (Object.keys(validationErrors).length > 0) {
    setErrors(validationErrors);
    return;
  }

  try {
    await submitForm(formData);
    // Handle success
  } catch (error) {
    // Handle error
  }
};
```

### Conditional Rendering Pattern

```typescript
// Loading state
if (loading) {
  return <LoadingSpinner />;
}

// Error state
if (error) {
  return <ErrorMessage error={error} onRetry={retry} />;
}

// Success state with conditional content
return (
  <div>
    {data ? (
      <DataDisplay data={data} />
    ) : (
      <EmptyState message="No data available" />
    )}
  </div>
);
```

This comprehensive frontend documentation provides developers with everything needed to understand, maintain, and extend the AI Reader Agent frontend application. The modular architecture, clear component interfaces, and consistent patterns make it easy to add new features while maintaining code quality and user experience standards.
