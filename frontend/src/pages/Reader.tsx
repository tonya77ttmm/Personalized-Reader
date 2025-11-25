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
    <div>
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
        <div>
          {/* Document Viewer */}
          <div>
            <DocumentViewer
              documentId={uploadedDocument.id}
              title={uploadedDocument.title}
              onUploadDocument={handleUploadAnother}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Reader;
