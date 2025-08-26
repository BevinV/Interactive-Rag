import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { queryDocuments, updateChunk, deleteChunk } from '../api/api';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Set up PDF worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const QueryPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [selectedPdf, setSelectedPdf] = useState(null);
  const [numPages, setNumPages] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [editingChunk, setEditingChunk] = useState(null);
  const [editText, setEditText] = useState('');
  const [kValue, setKValue] = useState(5); 

  const handleSearch = async () => {
  if (!query.trim()) return;
  
  setIsSearching(true);
  setResults([]); // Clear previous results
  console.log("Starting search with query:", query, "k:", kValue);
  
  try {
    const response = await queryDocuments(query, kValue);
    console.log("Search completed, results:", response.results);
    setResults(response.results);
    
    // If we have results, load the first PDF
    if (response.results.length > 0) {
      const firstResult = response.results[0];
      setSelectedPdf(`http://localhost:8000/storage/docs/${firstResult.document}`);
      console.log("Setting PDF to:", firstResult.document);
    }
  } catch (error) {
    console.error('Search error:', error);
    
    // Show specific error message for model mismatch
    if (error.message.includes('Please reset the index')) {
      alert(`Search failed: ${error.message}`);
    } else {
      alert('Search failed. Please check the console for details.');
    }
  } finally {
    setIsSearching(false);
  }
};

  const handleEdit = (chunk) => {
    setEditingChunk(chunk.chunk_id);
    setEditText(chunk.text);
  };

  const handleSaveEdit = async (chunkId) => {
    try {
      await updateChunk(chunkId, editText);
      setEditingChunk(null);
      // Refresh the search results
      handleSearch();
    } catch (error) {
      console.error('Update error:', error);
    }
  };

  const handleFixMappings = async () => {
    try {
      const response = await api.post('/fix_mappings');
      alert(`Mappings fixed: ${response.data.message}`);
      console.log('Fix mappings response:', response.data);
    } catch (error) {
      console.error('Error fixing mappings:', error);
      alert('Failed to fix mappings. Check console for details.');
    }
  };

  const handleRebuildMappings = async () => {
    try {
      const response = await api.post('/fix_mappings');
      alert(`Mappings rebuilt: ${response.data.message}`);
      console.log('Rebuild mappings response:', response.data);
    } catch (error) {
      console.error('Error rebuilding mappings:', error);
      alert('Failed to rebuild mappings. Check console for details.');
    }
  };

  const handleDelete = async (chunkId) => {
    try {
      await deleteChunk(chunkId);
      // Refresh the search results
      handleSearch();
    } catch (error) {
      console.error('Delete error:', error);
    }
  };

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
  };

  return (
    <div className="query-container">
      <h2>Query Documents</h2>
      
      <div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query"
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          style={{ marginRight: '10px', padding: '8px', width: '300px' }}
        />
        
        <select 
          value={kValue} 
          onChange={(e) => setKValue(parseInt(e.target.value))}
          style={{ marginRight: '10px', padding: '8px' }}
        >
          <option value={3}>Top 3</option>
          <option value={5}>Top 5</option>
          <option value={10}>Top 10</option>
          <option value={15}>Top 15</option>
          <option value={20}>Top 20</option>
        </select>
        
        <button onClick={handleSearch} disabled={isSearching}>
          {isSearching ? 'Searching...' : 'Search'}
        </button>
      </div>


      {results.length > 0 && (
        <div className="results-container">
          <h3>Search Results:</h3>
          {results.map((result, index) => (
            <div key={index} className="result-item">
              {editingChunk === result.chunk_id ? (
                <div>
                  <textarea
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    rows="4"
                    style={{ width: '100%' }}
                  />
                  <button onClick={() => handleSaveEdit(result.chunk_id)}>Save</button>
                  <button onClick={() => setEditingChunk(null)}>Cancel</button>
                </div>
              ) : (
                <div>
                  <p><strong>Document:</strong> {result.document}</p>
                  <p><strong>Page:</strong> {result.page}</p>
                  <p><strong>Text:</strong> {result.text}</p>
                  <p><strong>Score:</strong> {result.score.toFixed(4)}</p>
                  {/* Add model and chunking method information */}
                  {result.model && <p><strong>Embedding Model:</strong> {result.model}</p>}
                  {result.chunking_method && <p><strong>Chunking Method:</strong> {result.chunking_method}</p>}
                  <button onClick={() => handleEdit(result)}>Edit</button>
                  <button onClick={() => handleDelete(result.chunk_id)}>Delete</button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {selectedPdf && (
        <div className="pdf-viewer">
          <h3>PDF Viewer</h3>
          <p>Viewing: {selectedPdf.split('/').pop()}</p>
          <Document
            file={selectedPdf}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={(error) => console.error('PDF load error:', error)}
          >
            {Array.from(new Array(numPages), (el, index) => (
              <Page key={`page_${index + 1}`} pageNumber={index + 1} />
            ))}
          </Document>
        </div>
      )}
    </div>
  );
};

export default QueryPage;