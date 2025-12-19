import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAdmin } from '../contexts/AdminContext';
import { CheckCircle, Package, Truck, Phone, Home } from 'lucide-react';

const OrderConfirmation = () => {
  const { orderId } = useParams();
  const { orders } = useAdmin();
  
  const order = orders.find(o => o.id === parseInt(orderId));

  if (!order) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Order not found</h2>
        <Link
          to="/"
          className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-6 py-3 rounded-full font-medium hover:from-orange-600 hover:to-red-600 transition-all"
        >
          Go to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50 py-8">
      <div className="container mx-auto px-4 max-w-3xl">
        {/* Success Message */}
        <div className="bg-white rounded-3xl shadow-lg p-8 text-center mb-6">
          <div className="bg-green-100 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="h-12 w-12 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Order Placed Successfully!</h1>
          <p className="text-gray-600 mb-4">Thank you for your order. We'll call you soon for confirmation.</p>
          <div className="bg-orange-50 rounded-xl p-4 inline-block">
            <p className="text-sm text-gray-600">Order ID</p>
            <p className="text-2xl font-bold text-orange-600">#{order.id}</p>
          </div>
        </div>

        {/* Order Details */}
        <div className="bg-white rounded-3xl shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center space-x-2">
            <Package className="h-6 w-6 text-orange-600" />
            <span>Order Details</span>
          </h2>

          {/* Items */}
          <div className="space-y-3 mb-6">
            {order.items.map((item, index) => (
              <div key={index} className="flex items-center space-x-3 pb-3 border-b">
                <img src={item.image} alt={item.name} className="w-16 h-16 object-cover rounded-lg" />
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-800">{item.name}</h3>
                  <p className="text-sm text-gray-600">{item.weight} x {item.quantity}</p>
                </div>
                <span className="font-bold text-orange-600">₹{item.price * item.quantity}</span>
              </div>
            ))}
          </div>

          {/* Price Summary */}
          <div className="space-y-2 border-t pt-4">
            <div className="flex justify-between text-gray-700">
              <span>Subtotal:</span>
              <span>₹{order.subtotal}</span>
            </div>
            <div className="flex justify-between text-gray-700">
              <span>Delivery Charge:</span>
              <span>₹{order.deliveryCharge}</span>
            </div>
            <div className="flex justify-between text-xl font-bold border-t pt-2">
              <span>Total Paid:</span>
              <span className="text-orange-600">₹{order.total}</span>
            </div>
          </div>
        </div>

        {/* Delivery Info */}
        <div className="bg-white rounded-3xl shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
            <Truck className="h-6 w-6 text-orange-600" />
            <span>Delivery Information</span>
          </h2>
          <div className="space-y-3 text-gray-700">
            <div>
              <p className="text-sm text-gray-500">Customer Name</p>
              <p className="font-semibold">{order.customer.name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Phone Number</p>
              <p className="font-semibold">{order.customer.phone}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Delivery Address</p>
              <p className="font-semibold">{order.customer.address}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Location</p>
              <p className="font-semibold">{order.customer.location}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Payment Method</p>
              <p className="font-semibold">{order.paymentMethod === 'cod' ? 'Cash on Delivery' : 'Online Payment'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Estimated Delivery</p>
              <p className="font-semibold">{new Date(order.estimatedDelivery).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="grid md:grid-cols-2 gap-4">
          <Link
            to="/"
            className="bg-gradient-to-r from-orange-500 to-red-500 text-white py-4 rounded-xl font-semibold hover:from-orange-600 hover:to-red-600 transition-all flex items-center justify-center space-x-2 shadow-lg"
          >
            <Home className="h-5 w-5" />
            <span>Continue Shopping</span>
          </Link>
          <a
            href="tel:9985116385"
            className="bg-white border-2 border-orange-500 text-orange-600 py-4 rounded-xl font-semibold hover:bg-orange-50 transition-all flex items-center justify-center space-x-2"
          >
            <Phone className="h-5 w-5" />
            <span>Contact Us</span>
          </a>
        </div>
      </div>
    </div>
  );
};

export default OrderConfirmation;