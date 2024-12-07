import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link to="/" className="flex items-center">
              <span className="text-xl font-bold">SaaS Platform</span>
            </Link>
          </div>
          <div className="flex items-center">
            {user ? (
              <>
                <Link to="/dashboard" className="text-gray-700 hover:text-gray-900 px-3 py-2">
                  Dashboard
                </Link>
                <Link to="/analytics" className="text-gray-700 hover:text-gray-900 px-3 py-2">
                  Analytics
                </Link>
                <Link to="/billing" className="text-gray-700 hover:text-gray-900 px-3 py-2">
                  Billing
                </Link>
                <button
                  onClick={logout}
                  className="ml-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-gray-700 hover:text-gray-900 px-3 py-2">
                  Login
                </Link>
                <Link
                  to="/register"
                  className="ml-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}