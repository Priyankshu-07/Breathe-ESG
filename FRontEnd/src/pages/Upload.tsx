import React, { useState, useCallback } from 'react';
import {
  Upload as UploadIcon,
  FileSpreadsheet,
  Check,
  AlertCircle,
  X,
} from 'lucide-react';

import Layout from '../components/Layout';
import { API_BASE } from '../api/client';

type SourceType = 'SAP' | 'Utility' | 'Travel';

const sourceTypes: SourceType[] = ['SAP', 'Utility', 'Travel'];

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [sourceType, setSourceType] = useState<SourceType>('SAP');
  const [isDragging, setIsDragging] = useState(false);

  const [uploadStatus, setUploadStatus] = useState<
    'idle' | 'uploading' | 'success' | 'error'
  >('idle');

  const [errorMessage, setErrorMessage] = useState('');
  const [jobInfo, setJobInfo] = useState<any>(null);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    setIsDragging(false);

    const files = e.dataTransfer.files;

    if (files && files[0]) {
      setFile(files[0]);
      setUploadStatus('idle');
    }
  }, []);

  const handleFileSelect = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadStatus('idle');
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setUploadStatus('idle');
    setErrorMessage('');
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploadStatus('uploading');
    setErrorMessage('');

    try {
      const formData = new FormData();

      formData.append('file', file);
      formData.append('source_type', sourceType.toLowerCase());

      const response = await fetch(
        `${API_BASE}/api/ingestion/upload/`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!response.ok) {
        const data = await response.json();

        throw new Error(data.detail || 'Upload failed');
      }

      const data = await response.json();

      setJobInfo(data);
      setUploadStatus('success');
    } catch (err: any) {
      setUploadStatus('error');

      setErrorMessage(
        err.message || 'Upload failed. Please try again.'
      );
    }
  };

  const resetUpload = () => {
    setFile(null);
    setUploadStatus('idle');
    setErrorMessage('');
    setJobInfo(null);
  };

  return (
    <Layout>
      <div className="p-8 max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white mb-2">
            Upload Emissions Data
          </h1>

          <p className="text-gray-400">
            Upload your emissions data files for processing and review
          </p>
        </div>

        {/* Upload Card */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-8">
          {/* Success State */}
          {uploadStatus === 'success' && (
            <div className="text-center py-12">
              <div className="w-20 h-20 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-6">
                <Check className="w-10 h-10 text-emerald-500" />
              </div>

              <h3 className="text-xl font-semibold text-white mb-2">
                Upload Successful!
              </h3>

              <p className="text-gray-400 mb-2">
                Your file has been uploaded successfully.
              </p>

              {jobInfo && (
                <div className="mb-6 text-sm text-gray-300 space-y-2">
                  <p>
                    <span className="font-medium text-white">
                      Job ID:
                    </span>{' '}
                    {jobInfo.job_id}
                  </p>

                  <p>
                    <span className="font-medium text-white">
                      Status:
                    </span>{' '}
                    {jobInfo.status}
                  </p>
                </div>
              )}

              <button
                onClick={resetUpload}
                className="px-6 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                Upload Another File
              </button>
            </div>
          )}

          {/* Upload Form */}
          {uploadStatus !== 'success' && (
            <>
              {/* Drag and Drop Area */}
              <div
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all ${
                  isDragging
                    ? 'border-emerald-500 bg-emerald-500/10'
                    : 'border-gray-700 hover:border-gray-600'
                }`}
              >
                <input
                  type="file"
                  onChange={handleFileSelect}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  accept=".csv,.xlsx,.xls"
                  disabled={uploadStatus === 'uploading'}
                />

                {file ? (
                  <div className="flex items-center justify-center gap-4">
                    <FileSpreadsheet className="w-12 h-12 text-emerald-500" />

                    <div className="text-left">
                      <p className="text-white font-medium">
                        {file.name}
                      </p>

                      <p className="text-gray-400 text-sm">
                        {(file.size / 1024).toFixed(2)} KB
                      </p>
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemoveFile();
                      }}
                      className="ml-4 text-gray-400 hover:text-red-400 transition-colors"
                      disabled={uploadStatus === 'uploading'}
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                ) : (
                  <>
                    <UploadIcon className="w-12 h-12 text-gray-500 mx-auto mb-4" />

                    <p className="text-white font-medium mb-2">
                      Drag and drop your file here
                    </p>

                    <p className="text-gray-400 text-sm">
                      or click to browse (CSV, XLSX, XLS)
                    </p>
                  </>
                )}
              </div>

              {/* Error Message */}
              {uploadStatus === 'error' && (
                <div className="mt-4 p-4 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />

                  <p className="text-red-400 text-sm">
                    {errorMessage}
                  </p>
                </div>
              )}

              {/* Source Type Dropdown */}
              <div className="mt-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Source Type
                </label>

                <select
                  value={sourceType}
                  onChange={(e) =>
                    setSourceType(e.target.value as SourceType)
                  }
                  className="w-full md:w-64 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                  disabled={uploadStatus === 'uploading'}
                >
                  {sourceTypes.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>

              {/* Upload Button */}
              <button
                onClick={handleUpload}
                disabled={!file || uploadStatus === 'uploading'}
                className="mt-6 w-full md:w-auto px-8 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {uploadStatus === 'uploading' ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />

                    Uploading...
                  </>
                ) : (
                  <>
                    <UploadIcon className="w-5 h-5" />

                    Upload File
                  </>
                )}
              </button>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}