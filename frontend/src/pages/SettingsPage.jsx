import React, { useState, useEffect } from 'react';
import { resetIndex } from '../api/api';

const SettingsPage = () => {
  const [currentSettings, setCurrentSettings] = useState({});
  const [availableModels, setAvailableModels] = useState([]);
  const [availableChunkingMethods, setAvailableChunkingMethods] = useState([]);
  const [resetStatus, setResetStatus] = useState('');
  const [isResetting, setIsResetting] = useState(false);

  useEffect(() => {
    // Fetch current settings and available options
    const fetchData = async () => {
      try {
        const modelsResponse = await fetch('http://localhost:8000/available_models');
        const models = await modelsResponse.json();
        setAvailableModels(models);

        const chunkingResponse = await fetch('http://localhost:8000/available_chunking_methods');
        const chunkingMethods = await chunkingResponse.json();
        setAvailableChunkingMethods(chunkingMethods);

        setCurrentSettings({
          defaultModel: 'all-MiniLM-L6-v2',
          defaultChunkingMethod: 'fixed_size',
          defaultChunkSize: 500,
          defaultChunkOverlap: 50
        });
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  const handleResetIndex = async () => {
    if (!window.confirm('Are you sure you want to reset the index? This will delete all uploaded documents and cannot be undone.')) {
      return;
    }

    setIsResetting(true);
    setResetStatus('Resetting index...');
    
    try {
      const response = await resetIndex();
      setResetStatus(response.message);
    } catch (error) {
      console.error('Error resetting index:', error);
      setResetStatus('Failed to reset index. Please try again.');
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="settings-container">
      <h2>System Settings</h2>
      
      <div className="settings-section">
        <h3>Index Management</h3>
        <p>Reset the index to use a different embedding model. This will delete all uploaded documents.</p>
        <button 
          onClick={handleResetIndex} 
          disabled={isResetting}
          style={{backgroundColor: '#ff4444', color: 'white', padding: '10px 15px', border: 'none', borderRadius: '4px', cursor: 'pointer'}}
        >
          {isResetting ? 'Resetting...' : 'Reset Index'}
        </button>
        {resetStatus && <p style={{marginTop: '10px'}}>{resetStatus}</p>}
      </div>

      <div className="settings-section">
        <h3>Available Embedding Models</h3>
        <div className="models-list">
          {Object.entries(availableModels).map(([key, model]) => (
            <div key={key} className="model-item" style={{border: '1px solid #ddd', padding: '10px', margin: '10px 0', borderRadius: '4px'}}>
              <h4>{model.name}</h4>
              <p>{model.description}</p>
              <p>Dimensions: {model.dimensions}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="settings-section">
        <h3>Available Chunking Methods</h3>
        <div className="chunking-methods-list">
          {Object.entries(availableChunkingMethods).map(([key, method]) => (
            <div key={key} className="method-item" style={{border: '1px solid #ddd', padding: '10px', margin: '10px 0', borderRadius: '4px'}}>
              <h4>{method.name}</h4>
              <p>{method.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="settings-section">
        <h3>Default Settings</h3>
        <div className="default-settings" style={{border: '1px solid #ddd', padding: '10px', borderRadius: '4px'}}>
          <p><strong>Default Model:</strong> {currentSettings.defaultModel}</p>
          <p><strong>Default Chunking Method:</strong> {currentSettings.defaultChunkingMethod}</p>
          <p><strong>Default Chunk Size:</strong> {currentSettings.defaultChunkSize}</p>
          <p><strong>Default Chunk Overlap:</strong> {currentSettings.defaultChunkOverlap}</p>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;