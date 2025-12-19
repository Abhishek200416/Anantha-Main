import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { CheckCircle, Package, Mail, Phone, ArrowRight } from 'lucide-react';

const OrderSuccess = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const orderData = location.state?.orderData;

  if (!orderData) {
    navigate('/');
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50 py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-2xl mx-auto">
          {/* Success Message */}
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center mb-6">
            <div className="flex justify-center mb-4">
              <div className="bg-green-100 rounded-full p-4">
                <CheckCircle className="h-16 w-16 text-green-600" />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              Order Placed Successfully!
            </h1>
            <p className="text-gray-600 text-lg">
              Thank you for your order. We've received it and will process it soon.
            </p>
          </div>

          {/* Order Details */}
          <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
            <div className="border-b pb-4 mb-4">
              <h2 className="text-xl font-bold text-gray-800 flex items-center">
                <Package className="h-6 w-6 mr-2 text-orange-600" />
                Order Information
              </h2>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-start">
                <span className="text-gray-600">Order ID:</span>
                <span className="font-semibold text-gray-800">{orderData.order_id}</span>
              </div>
              <div className="flex justify-between items-start">
                <span className="text-gray-600">Tracking Code:</span>
                <span className="font-semibold text-gray-800 bg-yellow-100 px-3 py-1 rounded">
                  {orderData.tracking_code}
                </span>
              </div>
              <div className="flex justify-between items-start">
                <span className="text-gray-600">Total Amount:</span>
                <span className="font-semibold text-green-600 text-lg">
                  ₹{orderData.order?.total}
                </span>
              </div>
            </div>
          </div>

          {/* Tracking Instructions */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl shadow-lg p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              📦 Track Your Order
            </h2>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="bg-blue-100 rounded-full p-2 flex-shrink-0">
                  <Mail className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">Email Confirmation</h3>
                  <p className="text-gray-600 text-sm">
                    We've sent an order confirmation email to{' '}
                    <span className="font-semibold">{orderData.order?.email}</span> with your
                    tracking code and order details.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="bg-purple-100 rounded-full p-2 flex-shrink-0">
                  <Phone className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">Track by Phone or Email</h3>
                  <p className="text-gray-600 text-sm">
                    Visit the Track Order page and enter your phone number (
                    <span className="font-semibold">{orderData.order?.phone}</span>) or email to
                    get real-time updates.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="bg-green-100 rounded-full p-2 flex-shrink-0">
                  <Package className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">Track by Code</h3>
                  <p className="text-gray-600 text-sm">
                    Use your tracking code{' '}
                    <span className="font-mono font-semibold bg-yellow-100 px-2 py-1 rounded">
                      {orderData.tracking_code}
                    </span>{' '}
                    on the Track Order page for instant status updates.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={() => navigate('/track-order')}
              className="flex-1 bg-gradient-to-r from-orange-500 to-red-500 text-white py-4 rounded-xl font-semibold hover:from-orange-600 hover:to-red-600 transition-all flex items-center justify-center space-x-2"
            >
              <span>Track Your Order</span>
              <ArrowRight className="h-5 w-5" />
            </button>
            <button
              onClick={() => navigate('/')}
              className="flex-1 bg-white border-2 border-gray-300 text-gray-800 py-4 rounded-xl font-semibold hover:bg-gray-50 transition-all"
            >
              Continue Shopping
            </button>
          </div>

          {/* Help Section */}
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Need help? Contact us at{' '}
              <a
                href="tel:9985116385"
                className="text-orange-600 font-semibold hover:underline"
              >
                9985116385
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderSuccess;
