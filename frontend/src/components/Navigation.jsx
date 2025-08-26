import React from 'react';
import { Link } from 'react-router-dom';

const Navigation = () => {
  return (
    <nav className="nav">
      <Link to="/">Upload</Link>
      <Link to="/query">Query</Link>
      <Link to="/export">Export</Link>
      <Link to="/test-export">Test Export</Link>
      <Link to="/settings">Settings</Link>
      <Link to="/vector-stores">Vector Stores</Link>
    </nav>
  );
};

export default Navigation;