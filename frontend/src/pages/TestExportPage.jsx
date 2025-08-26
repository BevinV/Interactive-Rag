import React, { useState } from 'react';
import { testExport } from '../api/api';

const TestExportPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isTesting, setIsTesting] = useState(false);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleTest = async () => {
    if (!selectedFile || !query.trim()) {
      alert('Please select an export file and enter a query');
      return;
    }

    setIsTesting(true);
    setResults([]);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('query', query);
      formData.append('k', 5);

      console.log("Sending test export request...");
      const response = await testExport(formData);
      console.log("Test export response:", response);
      setResults(response.results);
      
      if (response.results.length === 0) {
        alert('Test completed but no results found. Check console for details.');
      }
    } catch (error) {
      console.error('Test error:', error);
      let errorMsg = 'Test failed. Please try again.';
      
      if (error.response) {
        console.error('Response data:', error.response.data);
        console.error('Response status:', error.response.status);
        errorMsg = error.response.data.detail || errorMsg;
      }
      
      alert(errorMsg);
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="test-export-container">
      <h2>Test Exported Data</h2>
      
      <div>
        <h3>Upload Export ZIP File</h3>
        <input
          type="file"
          accept=".zip"
          onChange={handleFileChange}
        />
      </div>
      
      <div>
        <h3>Test Query</h3>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your test query"
          style={{ width: '300px', marginRight: '10px' }}
        />
        <button onClick={handleTest} disabled={isTesting}>
          {isTesting ? 'Testing...' : 'Test Export'}
        </button>
      </div>
      
      {results.length > 0 && (
        <div className="results-container">
          <h3>Test Results:</h3>
          {results.map((result, index) => (
            <div key={index} className="result-item">
              <p><strong>Document:</strong> {result.document}</p>
              <p><strong>Page:</strong> {result.page}</p>
              <p><strong>Text:</strong> {result.text}</p>
              <p><strong>Score:</strong> {result.score.toFixed(4)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TestExportPage;