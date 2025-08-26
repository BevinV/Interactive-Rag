import React, { useState, useEffect } from 'react';
import {
  uploadVectorStore,
  queryVectorStore,
  listVectorStores,
  updateVectorStoreChunk,
  deleteVectorStore,
  deleteFromVectorStore,
  addToVectorStore,
  exportVectorStore
} from '../api/api'; // Import the actual API functions

const VectorStorePage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedModel, setSelectedModel] = useState('all-MiniLM-L6-v2');
  const [vectorStores, setVectorStores] = useState({});
  const [selectedStore, setSelectedStore] = useState('');
  const [query, setQuery] = useState('');
  const [kValue, setKValue] = useState(5);
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [editingChunk, setEditingChunk] = useState(null);
  const [editText, setEditText] = useState('');
  const [newChunkText, setNewChunkText] = useState('');
  const [newChunkDocument, setNewChunkDocument] = useState('custom');
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    fetchVectorStores();
  }, []);

  const fetchVectorStores = async () => {
    try {
      const response = await listVectorStores();
      setVectorStores(response.data);
    } catch (error) {
      console.error('Error fetching vector stores:', error);
      setStatus('Error fetching vector stores');
    }
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setStatus('Please select a file first.');
      return;
    }

    setIsLoading(true);
    setStatus('Uploading...');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('model_name', selectedModel);

      const response = await uploadVectorStore(formData);
      setStatus(response.data.message);
      setSelectedFile(null);
      fetchVectorStores();
    } catch (error) {
      setStatus('Upload failed. Please try again.');
      console.error('Upload error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!selectedStore || !query.trim()) {
      setStatus('Please select a vector store and enter a query.');
      return;
    }

    setIsLoading(true);
    setResults([]);

    try {
      const response = await queryVectorStore(selectedStore, query, kValue);
      setResults(response.data.results || []);
      setStatus(`Found ${response.data.results?.length || 0} results`);
    } catch (error) {
      setStatus('Query failed. Please try again.');
      console.error('Query error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (chunk) => {
    setEditingChunk(chunk.chunk_id);
    setEditText(chunk.text);
  };

  const handleSaveEdit = async () => {
    if (!editingChunk) return;
    
    try {
      await updateVectorStoreChunk(selectedStore, editingChunk, editText);
      setEditingChunk(null);
      setEditText('');
      setStatus('Chunk updated successfully');
      handleQuery();
    } catch (error) {
      console.error('Error updating chunk:', error);
      setStatus('Failed to update chunk');
    }
  };

  const handleCancelEdit = () => {
    setEditingChunk(null);
    setEditText('');
  };

  const handleDeleteChunk = async (chunkId) => {
    if (!window.confirm('Are you sure you want to delete this chunk?')) {
      return;
    }

    try {
      await deleteFromVectorStore(selectedStore, chunkId);
      setStatus('Chunk deleted successfully');
      handleQuery();
    } catch (error) {
      console.error('Error deleting chunk:', error);
      setStatus('Failed to delete chunk');
    }
  };

  const handleAddChunk = async () => {
    if (!newChunkText.trim()) {
      setStatus('Please enter text for the new chunk.');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('text', newChunkText);
      formData.append('document', newChunkDocument);
      formData.append('page', '1');
      formData.append('start_index', '0');

      const response = await addToVectorStore(selectedStore, formData);
      setStatus(response.data.message);
      setNewChunkText('');
      setShowAddForm(false);
      handleQuery();
    } catch (error) {
      console.error('Error adding chunk:', error);
      setStatus('Failed to add chunk');
    }
  };

  const handleExport = async () => {
    if (!selectedStore) {
      setStatus('Please select a vector store to export.');
      return;
    }

    try {
      const blob = await exportVectorStore(selectedStore);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `vector_store_${selectedStore}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setStatus('Export completed successfully');
    } catch (error) {
      console.error('Error exporting vector store:', error);
      setStatus('Failed to export vector store');
    }
  };

  const handleDelete = async (storeId) => {
    if (!window.confirm('Are you sure you want to delete this vector store?')) {
      return;
    }

    try {
      await deleteVectorStore(storeId);
      setStatus('Vector store deleted successfully');
      fetchVectorStores();
      if (selectedStore === storeId) {
        setSelectedStore('');
        setResults([]);
      }
    } catch (error) {
      console.error('Delete error:', error);
      setStatus('Delete failed. Please try again.');
    }
  };

  return (
    <div className="container vector-store-container">
      <h2>Manage Vector Stores</h2>

      <div className="upload-section upload-container">
        <h3>Upload New Vector Store</h3>
        <div>
          <input
            type="file"
            accept=".zip"
            onChange={handleFileChange}
          />
        </div>
        <div>
          <label>
            Embedding Model:
            <select 
              value={selectedModel} 
              onChange={(e) => setSelectedModel(e.target.value)}
            >
              <option value="all-MiniLM-L6-v2">all-MiniLM-L6-v2</option>
              <option value="all-mpnet-base-v2">all-mpnet-base-v2</option>
              <option value="multi-qa-MiniLM-L6-cos-v1">multi-qa-MiniLM-L6-cos-v1</option>
            </select>
          </label>
        </div>
        <button onClick={handleUpload} disabled={isLoading || !selectedFile}>
          {isLoading ? 'Uploading...' : 'Upload Vector Store'}
        </button>
      </div>

      <div className="stores-section upload-container">
        <h3>Available Vector Stores</h3>
        {Object.keys(vectorStores).length === 0 ? (
          <p>No vector stores available.</p>
        ) : (
          <div>
            <select 
              value={selectedStore} 
              onChange={(e) => setSelectedStore(e.target.value)}
            >
              <option value="">Select a vector store</option>
              {Object.entries(vectorStores).map(([id, store]) => (
                <option key={id} value={id}>
                  {id} - {store.model_name} - {new Date(store.created_at).toLocaleDateString()}
                </option>
              ))}
            </select>
            
            {selectedStore && (
              <div className="store-actions">
                <button onClick={() => handleDelete(selectedStore)}>
                  Delete This Vector Store
                </button>
                <button onClick={handleExport}>
                  Export Vector Store
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {selectedStore && (
        <div className="query-section query-container">
          <h3>Query Vector Store</h3>
          <div className="query-inputs">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your query"
              onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
            />
            <select 
              value={kValue} 
              onChange={(e) => setKValue(parseInt(e.target.value))}
            >
              <option value={3}>Top 3</option>
              <option value={5}>Top 5</option>
              <option value={10}>Top 10</option>
              <option value={15}>Top 15</option>
              <option value={20}>Top 20</option>
            </select>
            <button onClick={handleQuery} disabled={isLoading}>
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </div>

          {results.length > 0 ? (
            <div className="results-container">
              <h4>Search Results ({results.length}):</h4>
              {results.map((result) => (
                <div key={result.chunk_id} className="result-item">
                  {editingChunk === result.chunk_id ? (
                    <div className="edit-mode">
                      <textarea
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        rows="4"
                      />
                      <div className="edit-actions">
                        <button onClick={handleSaveEdit}>Save</button>
                        <button onClick={handleCancelEdit}>Cancel</button>
                      </div>
                    </div>
                  ) : (
                    <div className="view-mode">
                      <p><strong>Document:</strong> {result.document || 'N/A'}</p>
                      <p><strong>Page:</strong> {result.page || 'N/A'}</p>
                      <p><strong>Text:</strong> {result.text || 'No text available'}</p>
                      <p><strong>Score:</strong> {result.score ? result.score.toFixed(4) : 'N/A'}</p>
                      <div className="chunk-actions">
                        <button onClick={() => handleEdit(result)}>Edit</button>
                        <button onClick={() => handleDeleteChunk(result.chunk_id)}>Delete</button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            isLoading ? <p>Searching...</p> : <p>No results found or waiting for query</p>
          )}
        </div>
      )}

      {status && <div className="status">{status}</div>}
    </div>
  );
};

export default VectorStorePage;