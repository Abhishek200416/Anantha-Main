import React, { useState } from 'react';
import { X, AlertCircle } from 'lucide-react';

const CancelOrderModal = ({ isOpen, onClose, onConfirm, orderName }) => {
  const [reason, setReason] = useState('');

  const handleSubmit = () => {
    if (reason.trim()) {
      onConfirm(reason);
      setReason('');
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 animate-fade-in">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-500 to-red-600 px-6 py-4 rounded-t-xl flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <AlertCircle className="h-6 w-6 text-white" />
            <h3 className="text-xl font-bold text-white">Cancel Order</h3>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-red-700 rounded-lg p-1 transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4">
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
            <p className="text-sm text-red-800">
              Are you sure you want to cancel this order? This action cannot be undone.
            </p>
          </div>

          {orderName && (
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-sm text-gray-600">Order:</p>
              <p className="font-semibold text-gray-800">{orderName}</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cancellation Reason <span className="text-red-500">*</span>
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows="4"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
              placeholder="Please provide a reason for cancelling this order..."
            />
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 rounded-b-xl flex space-x-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-100 transition"
          >
            Keep Order
          </button>
          <button
            onClick={handleSubmit}
            disabled={!reason.trim()}
            className="flex-1 px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg font-medium hover:from-red-600 hover:to-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Cancel Order
          </button>
        </div>
      </div>
    </div>
  );
};

export default CancelOrderModal;
