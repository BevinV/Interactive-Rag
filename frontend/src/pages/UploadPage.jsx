import React, { useState, useEffect } from 'react';
import { uploadDocument } from '../api/api';

const UploadPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [availableModels, setAvailableModels] = useState([]);
  const [availableChunkingMethods, setAvailableChunkingMethods] = useState([]);
  const [selectedModel, setSelectedModel] = useState('all-MiniLM-L6-v2');
  const [selectedChunkingMethod, setSelectedChunkingMethod] = useState('fixed_size');
  const [chunkSize, setChunkSize] = useState(500);
  const [chunkOverlap, setChunkOverlap] = useState(50);

  useEffect(() => {
    // Fetch available models and chunking methods
    const fetchOptions = async () => {
      try {
        const modelsResponse = await fetch('http://localhost:8000/available_models');
        const models = await modelsResponse.json();
        setAvailableModels(models);

        const chunkingResponse = await fetch('http://localhost:8000/available_chunking_methods');
        const chunkingMethods = await chunkingResponse.json();
        setAvailableChunkingMethods(chunkingMethods);
      } catch (error) {
        console.error('Error fetching options:', error);
      }
    };

    fetchOptions();
  }, []);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('Please select a file first.');
      return;
    }

    setIsUploading(true);
    setUploadStatus('Uploading...');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      // Add processing options
      formData.append('model_name', selectedModel);
      formData.append('chunking_method', selectedChunkingMethod);
      formData.append('chunk_size', chunkSize.toString());
      formData.append('chunk_overlap', chunkOverlap.toString());

      const response = await uploadDocument(formData);
      setUploadStatus(`Upload successful! ${response.chunk_ids.length} chunks created.`);
      setSelectedFile(null);
      // Reset file input
      document.getElementById('file-input').value = '';
    } catch (error) {
      setUploadStatus('Upload failed. Please try again.');
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload PDF Document</h2>
      
      <div>
        <h3>Select File</h3>
        <input
          id="file-input"
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
        />
      </div>

      <div>
        <h3>Embedding Model</h3>
        <select 
          value={selectedModel} 
          onChange={(e) => setSelectedModel(e.target.value)}
          style={{ padding: '8px', margin: '10px 0', width: '300px' }}
        >
          {Object.entries(availableModels).map(([key, model]) => (
            <option key={key} value={key}>
              {model.name} - {model.description}
            </option>
          ))}
        </select>
      </div>

      <div>
        <h3>Chunking Method</h3>
        <select 
          value={selectedChunkingMethod} 
          onChange={(e) => setSelectedChunkingMethod(e.target.value)}
          style={{ padding: '8px', margin: '10px 0', width: '300px' }}
        >
          {Object.entries(availableChunkingMethods).map(([key, method]) => (
            <option key={key} value={key}>
              {method.name} - {method.description}
            </option>
          ))}
        </select>
      </div>

      <div>
        <h3>Chunking Parameters</h3>
        <div style={{ margin: '10px 0' }}>
          <label>
            Chunk Size: 
            <input
              type="number"
              value={chunkSize}
              onChange={(e) => setChunkSize(parseInt(e.target.value))}
              style={{ marginLeft: '10px', padding: '5px', width: '80px' }}
            />
          </label>
        </div>
        <div style={{ margin: '10px 0' }}>
          <label>
            Chunk Overlap: 
            <input
              type="number"
              value={chunkOverlap}
              onChange={(e) => setChunkOverlap(parseInt(e.target.value))}
              style={{ marginLeft: '10px', padding: '5px', width: '80px' }}
            />
          </label>
        </div>
      </div>

      <button onClick={handleUpload} disabled={isUploading || !selectedFile}>
        {isUploading ? 'Uploading...' : 'Upload & Process'}
      </button>
      
      {uploadStatus && <p>{uploadStatus}</p>}
    </div>
  );
};

export default UploadPage;