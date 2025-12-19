import React from 'react';
import { AlertTriangle } from 'lucide-react';

const DeleteConfirmDialog = ({ isOpen, onClose, onConfirm, title, message }) => {
  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] flex items-center justify-center p-4 animate-in fade-in"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl relative transform animate-in zoom-in"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Icon */}
        <div className="flex justify-center mb-4">
          <div className="bg-red-100 rounded-full p-3">
            <AlertTriangle className="h-8 w-8 text-red-600" />
          </div>
        </div>

        {/* Title */}
        <h3 className="text-xl font-bold text-gray-800 text-center mb-2">
          {title || 'Confirm Delete'}
        </h3>

        {/* Message */}
        <p className="text-gray-600 text-center mb-6">
          {message || 'Are you sure you want to delete this item? This action cannot be undone.'}
        </p>

        {/* Buttons */}
        <div className="flex space-x-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className="flex-1 px-4 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-xl font-semibold hover:from-red-700 hover:to-red-800 transition-all shadow-lg"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmDialog;
