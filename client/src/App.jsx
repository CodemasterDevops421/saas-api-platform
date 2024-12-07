import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import Billing from './pages/Billing';
import Analytics from './pages/Analytics';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-100">
            <Navbar />
            <main className="container mx-auto px-4 py-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/billing" element={<Billing />} />
                <Route path="/analytics" element={<Analytics />} />
              </Routes>
            </main>
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;