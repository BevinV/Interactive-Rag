import React, { useState } from 'react';
import { exportData } from '../api/api';

const ExportPage = () => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState('');

  const handleExport = async () => {
    setIsExporting(true);
    setExportStatus('Exporting...');
    
    try {
      const blob = await exportData();
      
      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = 'rag_export.zip';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      setExportStatus('Export completed successfully!');
    } catch (error) {
      console.error('Export error:', error);
      setExportStatus('Export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="export-container">
      <h2>Export Data</h2>
      <p>Click the button below to export the FAISS index and metadata.</p>
      
      <button onClick={handleExport} disabled={isExporting}>
        {isExporting ? 'Exporting...' : 'Export Data'}
      </button>
      
      {exportStatus && <p>{exportStatus}</p>}
    </div>
  );
};

export default ExportPage;