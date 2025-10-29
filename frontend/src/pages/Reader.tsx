import { useState } from "react";
import FileUpload from "../components/upload/FileUpload.tsx";
import DocumentViewer from "../components/reader/DocumentViewer.tsx";

const Reader = () => {
  const [uploadedDocument, setUploadedDocument] = useState<any>(null);

  const handleUploadSuccess = (document: any) => {
    console.log("Document uploaded:", document);
    setUploadedDocument(document);
  };

  const handleUploadError = (error: string) => {
    console.error("Upload error:", error);
  };

  const handleUploadAnother = () => {
    setUploadedDocument(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {!uploadedDocument ? (
        <div className="max-w-4xl mx-auto pt-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">AI Reader</h1>
            <h2 className="text-xl font-semibold text-gray-700 mb-2">
              Upload a Document
            </h2>
            <p className="text-gray-600">
              Upload a text file to start reading with AI assistance
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-8">
            <FileUpload
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />
          </div>
        </div>
      ) : (
        <div className="min-h-screen">
          {/* Header with Upload Another Button */}
          <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
            <div className="max-w-6xl mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-gray-900">AI Reader</h1>
                <button
                  onClick={handleUploadAnother}
                  className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Upload Another Document
                </button>
              </div>
            </div>
          </div>

          {/* Document Viewer */}
          <div className="py-8 px-4">
            <DocumentViewer
              documentId={uploadedDocument.id}
              title={uploadedDocument.title}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Reader;
