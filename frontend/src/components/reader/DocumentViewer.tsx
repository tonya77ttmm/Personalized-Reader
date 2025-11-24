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
  onUploadDocument,
}) => {
  const [document, setDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fontSize, setFontSize] = useState(20);
  const [lineHeight, setLineHeight] = useState(2.8);
  const [selectedText, setSelectedText] = useState<string>("");
  const [explanation, setExplanation] = useState<string>("");
  const [isLoadingExplanation, setIsLoadingExplanation] = useState(false);
  const [explanationError, setExplanationError] = useState<string>("");
  const contentRef = useRef<HTMLDivElement>(null);
  const [scrolled, setScrolled] = useState(false);
  const [wordCount, setWordCount] = useState<number>(0);
  const [selectionPosition, setSelectionPosition] = useState<{
    top: number;
    left: number;
    width: number;
    height: number;
  } | null>(null);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 112) {
        // 7rem = 112px
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

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

  useEffect(() => {
    if (selectedText) {
      requestExplanation(); // Run once when selectedText changes
    }
  }, [selectedText]);

  // Utility function to count words
  const countWords = (text: string): number => {
    return text
      .trim()
      .split(/\s+/)
      .filter((word) => word.length > 0).length;
  };

  // Apply yellow highlight to selected text for inline display
  useEffect(() => {
    if (selectedText && wordCount <= 3 && wordCount > 0) {
      const selection = window.getSelection();
      if (selection) {
        const range = selection.getRangeAt(0);
        const span = window.document.createElement("span");
        span.className = "inline-highlight";
        span.style.backgroundColor = "rgb(254, 240, 138)"; // yellow-200
        span.style.padding = "2px 4px";
        span.style.borderRadius = "2px";

        try {
          range.surroundContents(span);
        } catch (e) {
          console.warn("Could not apply highlight:", e);
        }
      }
    }

    // Cleanup: remove highlights when selection changes
    return () => {
      const highlights = window.document.querySelectorAll(".inline-highlight");
      highlights.forEach((highlight: Element) => {
        const parent = highlight.parentNode;
        if (parent) {
          while (highlight.firstChild) {
            parent.insertBefore(highlight.firstChild, highlight);
          }
          parent.removeChild(highlight);
        }
      });
    };
  }, [selectedText, wordCount]);

  // Handle text selection - simple and natural
  const handleTextSelection = () => {
    const selection = window.getSelection();
    console.log(`selected text${selection}`);
    if (selection && selection.rangeCount > 0) {
      const text = selection.toString().trim();

      if (text.length > 0) {
        // User has selected text
        setSelectedText(text);
        console.log(`set selected text${text} sucessfully`);

        // Count words
        const words = countWords(text);
        setWordCount(words);

        // Get selection position for inline display
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        // get container rect (viewport coords)
        const container = contentRef.current;
        const containerRect = container?.getBoundingClientRect();

        if (containerRect) {
          // Compute selection position RELATIVE TO container (viewport - viewport = relative)
          setSelectionPosition({
            top: rect.top - containerRect.top, // relative to the top of contentRef
            left: rect.left - containerRect.left, // relative to the left of contentRef
            width: rect.width,
            height: rect.height,
          });
        } else {
          // fallback to page coords if container missing
          setSelectionPosition({
            top: rect.top + window.scrollY,
            left: rect.left + window.scrollX,
            width: rect.width,
            height: rect.height,
          });
        }

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
    setWordCount(0);
    setSelectionPosition(null);
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
    const selectedIndex = content.indexOf(selectedText); // BUG for the same word

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
      console.log(`trigger click ${selection}`);
      if (!selection || selection.toString().trim() === "") {
        setSelectedText("");
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
    <div className="min-h-screen bg-[#fcfcfc]">
      {/* Left Side - Document Content (2/3) */}
      <div className="w-3/4 px-2">
        <article className="mx-auto">
          {/* Document Header */}
          <header className="mb-8 flex items-center justify-between">
            <h1 className="text-4xl font-serif font-bold text-gray-900 mb-3">
              {document.title}
            </h1>

            <button
              onClick={onUploadDocument}
              className="px-4 py-2 bg-blue-200 text-blue-800 rounded-md hover:bg-blue-300 hover:text-blue-900 transition-colors"
              title="Upload Document"
            >
              Upload
            </button>
          </header>

          {/* Document Content */}
          <div
            ref={contentRef}
            className="text-lg leading-relaxed text-gray-800 select-text cursor-text relative"
            style={{
              fontSize: `${fontSize}px`,
              lineHeight: lineHeight,
            }}
            onMouseUp={handleTextSelection}
            onClick={handleDocumentClick}
          >
            {document.content.split("\n").map((paragraph, index) => (
              <p key={index} className="mb-6 indent-6">
                {paragraph.trim() || "\u00A0"}
              </p>
            ))}

            {/* Inline Explanation for ≤3 words */}
            {selectedText && wordCount <= 3 && selectionPosition && (
              <div
                className="absolute z-10 bg-white  "
                style={{
                  top: `${selectionPosition.top}px`,
                  left: `${selectionPosition.left}px`,
                  transform: "translateY(-110%)",
                }}
              >
                <div className="flex items-start justify-between">
                  {isLoadingExplanation && (
                    <div className="flex items-center text-xs text-gray-500">
                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600 mr-2"></div>
                      Loading...
                    </div>
                  )}

                  {explanation && !isLoadingExplanation && (
                    <p className="text-sm text-blue-600 leading-relaxed">
                      {explanation}
                    </p>
                  )}

                  {explanationError && (
                    <div className="text-xs text-red-600">
                      {explanationError}
                    </div>
                  )}
                  <button
                    onClick={clearSelection}
                    className="text-gray-400 hover:text-gray-600 ml-2"
                    title="Clear"
                  >
                    <svg
                      className="w-3 h-3"
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
              </div>
            )}
          </div>
        </article>
      </div>

      {/* Right Side - Fixed Sidebar (1/3) - Only for >3 words */}
      <div
        className="fixed right-0 w-1/4 border-l border-gray-200 bg-white px-6 overflow-y-auto"
        style={{
          top: scrolled ? "0" : "7rem",
          height: scrolled ? "100vh" : "calc(100vh - 7rem)",
        }}
      >
        {selectedText && wordCount > 3 ? (
          <div>
            <div className="flex items-start justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-700">
                Selected Text
              </h3>
              <button
                onClick={clearSelection}
                className="text-gray-400 hover:text-gray-600"
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
            <p className="text-sm text-gray-800 italic mb-4 pb-4 border-b border-gray-200">
              "{selectedText}"
            </p>

            {/* Explanation Section */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                Explanation
              </h3>
              {explanation && (
                <div>
                  <p className="text-sm text-gray-700 leading-relaxed mb-3">
                    {explanation}
                  </p>
                  <button
                    onClick={requestExplanation}
                    className="text-xs text-blue-600 hover:text-blue-800 underline"
                  >
                    Get new explanation
                  </button>
                </div>
              )}
              {explanationError && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-800 mb-2">
                    {explanationError}
                  </p>
                  <button
                    onClick={requestExplanation}
                    className="text-xs text-red-600 hover:text-red-800 underline"
                  >
                    Try again
                  </button>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="text-sm text-gray-500 text-center mt-8">
            Select text to see explanation
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentViewer;
