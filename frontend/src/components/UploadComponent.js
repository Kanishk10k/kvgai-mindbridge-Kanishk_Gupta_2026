import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import './UploadComponent.css';

const UploadComponent = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    // Check if a file is selected
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];

    // Validate file type
    if (!file.type.includes('pdf')) {
      setError('Please upload a PDF file.');
      return;
    }

    // Validate file size (50MB limit)
    if (file.size > 50 * 1024 * 1024) {
      setError('File size exceeds 50MB limit.');
      return;
    }

    // Upload file
    uploadFile(file);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1
  });

  const uploadFile = async (file) => {
    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('http://localhost:8000/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setUploadResult(response.data);
      onUploadSuccess(response.data);
    } catch (err) {
      // Handle different types of errors
      if (err.response) {
        // Server responded with error status
        setError(err.response.data?.detail || `Server error: ${err.response.status}`);
      } else if (err.request) {
        // Network error
        setError('Network error. Please check if the backend server is running.');
      } else {
        // Other error
        setError(err.message || 'Upload failed. Please try again.');
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-component">
      <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
        <input {...getInputProps()} />
        {uploading ? (
          <p>Uploading...</p>
        ) : isDragActive ? (
          <p>Drop the PDF file here ...</p>
        ) : (
          <p>Drag & drop a PDF file here, or click to select a file</p>
        )}
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {uploadResult && (
        <div className="upload-result">
          <h3>Upload Successful!</h3>
          <p><strong>Filename:</strong> {uploadResult.filename}</p>
          <p><strong>Document ID:</strong> {uploadResult.document_id}</p>
          <p><strong>Status:</strong> {uploadResult.status}</p>
          <p><strong>Chunks Processed:</strong> {uploadResult.chunks_processed}</p>
        </div>
      )}
    </div>
  );
};

export default UploadComponent;