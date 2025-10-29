import { useState } from "react";
import FileUpload from "../components/upload/FileUpload.tsx";

const Reader = () => {
  const [uploadedDocument, setUploadedDocument] = useState<any>(null);

  const handleUploadSuccess = (document: any) => {
    console.log("Document uploaded:", document);
    setUploadedDocument(document);
  };

  const handleUploadError = (error: string) => {
    console.error("Upload error:", error);
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">AI Reader</h1>

      {!uploadedDocument ? (
        <div className="bg-white rounded-lg shadow-sm border p-8">
          <div className="text-center mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Upload a Document
            </h2>
            <p className="text-gray-600">
              Upload a text file to start reading with AI assistance
            </p>
          </div>

          <FileUpload
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="mb-4 pb-4 border-b">
            <h2 className="text-xl font-semibold text-gray-900">
              {uploadedDocument.title}
            </h2>
            <div className="flex items-center space-x-4 text-sm text-gray-500 mt-2">
              <span>
                📄 {Math.round(uploadedDocument.metadata.file_size / 1024)} KB
              </span>
              <span>📖 {uploadedDocument.metadata.word_count} words</span>
              <span>
                ⏱️ {uploadedDocument.metadata.estimated_reading_time} min read
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <p className="text-gray-600">
              Document uploaded successfully! Reading interface coming soon...
            </p>
            <button
              onClick={() => setUploadedDocument(null)}
              className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              Upload Another
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reader;
