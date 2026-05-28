import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Upload from './pages/Upload';
import Jobs from './pages/Jobs';
import Dashboard from './pages/Dashboard';
import Audit from './pages/Audit';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/upload" element={<Upload />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/audit" element={<Audit />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;