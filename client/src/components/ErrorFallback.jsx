import React from 'react';

export function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-red-600 mb-4">Something went wrong</h2>
        <div className="text-gray-600 mb-4">
          {error.message}
          {error.code && (
            <span className="block text-sm text-gray-500 mt-1">
              Error code: {error.code}
            </span>
          )}
        </div>
        <button
          onClick={resetErrorBoundary}
          className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
        >
          Try again
        </button>
      </div>
    </div>
  );
}