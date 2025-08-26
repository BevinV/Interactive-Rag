import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import QueryPage from './pages/QueryPage';
import ExportPage from './pages/ExportPage';
import Navigation from './components/Navigation';
import TestExportPage from './pages/TestExportPage';
import SettingsPage from './pages/SettingsPage';
import VectorStorePage from './pages/VectorStorePage';

import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <div className="container">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/query" element={<QueryPage />} />
            <Route path="/export" element={<ExportPage />} />
            <Route path="/test-export" element={<TestExportPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/vector-stores" element={<VectorStorePage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;