import React, { useState, useEffect, useRef } from "react";

interface DocumentViewerProps {
  documentId: string;
  title?: string;
  onUploadDocument?: () => void;
}

interface Document {
  id: string;
  title: string;
  content: string;
  metadata: {
    file_size: number;
    word_count: number;
    estimated_reading_time: number;
    language: string;
  };
  uploaded_at: string;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({
  documentId,
  title,
  onUploadDocument,
}) => {
  const [document, setDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fontSize, setFontSize] = useState(16);
  const [lineHeight, setLineHeight] = useState(1.6);
  const [selectedText, setSelectedText] = useState<string>("");
  const [explanation, setExplanation] = useState<string>("");
  const [isLoadingExplanation, setIsLoadingExplanation] = useState(false);
  const [explanationError, setExplanationError] = useState<string>("");
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(
          `http://localhost:8000/api/documents/${documentId}`
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch document: ${response.statusText}`);
        }

        const documentData = await response.json();
        setDocument(documentData);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to load document";
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    if (documentId) {
      fetchDocument();
    }
  }, [documentId]);

  const increaseFontSize = () => {
    setFontSize((prev) => Math.min(prev + 2, 24));
  };

  const decreaseFontSize = () => {
    setFontSize((prev) => Math.max(prev - 2, 12));
  };

  const resetFontSize = () => {
    setFontSize(16);
  };

  const increaseLineHeight = () => {
    setLineHeight((prev) => Math.min(prev + 0.1, 2.0));
  };

  const decreaseLineHeight = () => {
    setLineHeight((prev) => Math.max(prev - 0.1, 1.2));
  };
  useEffect(() => {
    if (selectedText) {
      requestExplanation(); // Run once when selectedText changes
    }
  }, [selectedText]);

  // Handle text selection - simple and natural
  const handleTextSelection = () => {
    const selection = window.getSelection();

    if (selection && selection.rangeCount > 0) {
      const text = selection.toString().trim();

      if (text.length > 0) {
        // User has selected text
        setSelectedText(text);
        // Clear previous explanation when new text is selected
        setExplanation("");
        setExplanationError("");
      } else {
        // No text selected (empty selection)
        clearSelection();
      }
    } else {
      // No selection at all
      clearSelection();
    }
  };

  const clearSelection = () => {
    setSelectedText("");
    setExplanation("");
    setExplanationError("");
    setIsLoadingExplanation(false);
  };

  const requestExplanation = async () => {
    if (!selectedText.trim()) return;

    setIsLoadingExplanation(true);
    setExplanationError("");

    try {
      const response = await fetch("http://localhost:8000/api/explanations/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: selectedText,
          document_title: document?.title,
          context: getContextAroundSelection(),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to get explanation");
      }

      const result = await response.json();
      setExplanation(result.explanation);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to get explanation";
      setExplanationError(errorMessage);
    } finally {
      setIsLoadingExplanation(false);
    }
  };

  const getContextAroundSelection = (): string => {
    // Get some context around the selected text for better explanations
    if (!document?.content) return "";

    const content = document.content;
    const selectedIndex = content.indexOf(selectedText);

    if (selectedIndex === -1) return "";

    // Get 100 characters before and after the selection
    const start = Math.max(0, selectedIndex - 100);
    const end = Math.min(
      content.length,
      selectedIndex + selectedText.length + 100
    );

    return content.substring(start, end);
  };

  // Clear selection when clicking elsewhere
  const handleDocumentClick = () => {
    // Small delay to let selection events complete first
    setTimeout(() => {
      const selection = window.getSelection();
      if (!selection || selection.toString().trim() === "") {
        clearSelection();
      }
    }, 10);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading document...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">
              Error loading document
            </h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="text-center py-12 text-gray-500">No document found</div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Document Header */}
      <div className="mb-6 pb-4 border-b border-gray-200 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {document.title}
        </h1>
        <button
          onClick={onUploadDocument}
          className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Upload
        </button>
      </div>

      {/* Selected Text Display */}
      {selectedText && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <p className="text-sm text-blue-800 italic">"{selectedText}"</p>
            </div>
            <button
              onClick={clearSelection}
              className="ml-4 text-blue-400 hover:text-blue-600"
              title="Clear selection"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Explanation Display */}
          {explanation && (
            <div className="mt-3 p-3 bg-white border border-blue-200 rounded-md">
              <p className="text-sm text-gray-700 leading-relaxed">
                {explanation}
              </p>
              <button
                onClick={requestExplanation}
                className="mt-2 text-xs text-blue-600 hover:text-blue-800 underline"
              >
                Get new explanation
              </button>
            </div>
          )}
          {/* Error Display */}
          {explanationError && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
              <div className="flex items-start">
                <svg
                  className="w-4 h-4 text-red-400 mt-0.5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <div className="flex-1">
                  <p className="text-sm text-red-800">{explanationError}</p>
                  <button
                    onClick={requestExplanation}
                    className="mt-1 text-xs text-red-600 hover:text-red-800 underline"
                  >
                    Try again
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Document Content */}
      <div className="bg-white rounded-lg shadow-sm border p-8">
        <div
          ref={contentRef}
          className="prose max-w-none text-gray-900 leading-relaxed select-text cursor-text"
          style={{
            fontSize: `${fontSize}px`,
            lineHeight: lineHeight,
          }}
          onMouseUp={handleTextSelection}
          onClick={handleDocumentClick}
        >
          {document.content.split("\n").map((paragraph, index) => (
            <p key={index} className="mb-4 last:mb-0">
              {paragraph.trim() || "\u00A0"}{" "}
              {/* Non-breaking space for empty lines */}
            </p>
          ))}
        </div>
      </div>

      {/* Document Footer */}
      <div className="mt-6 text-center text-sm text-gray-500">
        <p>
          Uploaded on {new Date(document.uploaded_at).toLocaleDateString()} at{" "}
          {new Date(document.uploaded_at).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
};

export default DocumentViewer;
