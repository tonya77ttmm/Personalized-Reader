import React, { useState, useRef, ChangeEvent } from "react";

interface FileUploadProps {
  onUploadSuccess?: (document: any) => void;
  onUploadError?: (error: string) => void;
}

interface UploadStatus {
  isUploading: boolean;
  error: string | null;
  success: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onUploadSuccess,
  onUploadError,
}) => {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({
    isUploading: false,
    error: null,
    success: false,
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const clearError = () => {
    setUploadStatus((prev) => ({
      ...prev,
      error: null,
    }));
  };

  const validateFile = (file: File): string | null => {
    // Check file type
    if (file.type !== "text/plain") {
      return "Only text files (.txt) are allowed";
    }

    // Check file size (10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      return "File size must be less than 10MB";
    }

    if (file.size === 0) {
      return "File cannot be empty";
    }

    return null;
  };

  const uploadFile = async (file: File) => {
    // Validate file
    const validationError = validateFile(file);
    if (validationError) {
      setUploadStatus({
        isUploading: false,
        error: validationError,
        success: false,
      });
      onUploadError?.(validationError);
      return;
    }

    // Start upload
    setUploadStatus({
      isUploading: true,
      error: null,
      success: false,
    });

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/api/documents/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Upload failed");
      }

      const result = await response.json();

      setUploadStatus({
        isUploading: false,
        error: null,
        success: true,
      });

      onUploadSuccess?.(result);

      // Reset success state after 3 seconds
      setTimeout(() => {
        setUploadStatus((prev) => ({ ...prev, success: false }));
      }, 3000);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Upload failed";
      setUploadStatus({
        isUploading: false,
        error: errorMessage,
        success: false,
      });
      onUploadError?.(errorMessage);
    }
  };

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      uploadFile(files[0]);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full max-w-md mx-auto">
      {/* Upload Button */}
      <div className="text-center">
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,text/plain"
          onChange={handleFileSelect}
          className="hidden"
        />

        <button
          onClick={handleButtonClick}
          disabled={uploadStatus.isUploading}
          className={`
            inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white
            ${
              uploadStatus.isUploading
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            }
            transition-colors duration-200
          `}
        >
          {uploadStatus.isUploading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Uploading...
            </>
          ) : (
            <>
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              Select Text File
            </>
          )}
        </button>

        <p className="mt-2 text-sm text-gray-500">
          Supports .txt files up to 10MB
        </p>
      </div>

      {/* Status Messages */}
      {uploadStatus.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
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
              <p className="text-sm text-red-800">{uploadStatus.error}</p>
            </div>
            <div className="ml-auto pl-3">
              <button
                onClick={clearError}
                className="text-red-400 hover:text-red-600"
              >
                <svg
                  className="h-4 w-4"
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
        </div>
      )}

      {uploadStatus.success && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-green-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-green-800">
                File uploaded successfully!
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
