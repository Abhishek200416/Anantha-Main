import React, { useState } from 'react';
import { Search, Package, Truck, CheckCircle, Clock, MapPin, Mail, Phone, CreditCard, Calendar, User, XCircle, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from '../hooks/use-toast';
import { useCart } from '../contexts/CartContext';
import CancelOrderModal from '../components/CancelOrderModal';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TrackOrder = () => {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const [searchTerm, setSearchTerm] = useState('');
  const [orders, setOrders] = useState([]);
  const [totalOrders, setTotalOrders] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [expandedOrderIndex, setExpandedOrderIndex] = useState(0); // Auto-expand first order
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('online');
  const [paymentSubMethod, setPaymentSubMethod] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchTerm.trim()) {
      toast({ title: 'Error', description: 'Please enter Order ID, Tracking Code, Phone Number, or Email', variant: 'destructive' });
      return;
    }

    setLoading(true);
    setSearched(true);

    try {
      const response = await axios.get(`${API}/orders/track/${searchTerm.trim()}`);
      setOrders(response.data.orders || []);
      setTotalOrders(response.data.total || 0);
      setExpandedOrderIndex(0); // Auto-expand first order
    } catch (error) {
      setOrders([]);
      setTotalOrders(0);
      if (error.response && error.response.status === 404) {
        toast({ 
          title: 'Order Not Found', 
          description: 'No order found with this information. Please check and try again, or contact support if you recently placed an order.', 
          variant: 'destructive' 
        });
      } else {
        toast({ 
          title: 'Error', 
          description: 'Failed to search for order. Please try again.', 
          variant: 'destructive' 
        });
      }
    }

    setLoading(false);
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'confirmed':
      case 'pending':
        return <Clock className="h-8 w-8 text-yellow-500" />;
      case 'processing':
        return <Package className="h-8 w-8 text-blue-500" />;
      case 'shipped':
      case 'out for delivery':
        return <Truck className="h-8 w-8 text-purple-500" />;
      case 'delivered':
        return <CheckCircle className="h-8 w-8 text-green-500" />;
      case 'cancelled':
        return <XCircle className="h-8 w-8 text-red-500" />;
      default:
        return <Package className="h-8 w-8 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'confirmed':
      case 'pending':
        return 'bg-yellow-100 text-yellow-700';
      case 'processing':
        return 'bg-blue-100 text-blue-700';
      case 'shipped':
      case 'out for delivery':
        return 'bg-purple-100 text-purple-700';
      case 'delivered':
        return 'bg-green-100 text-green-700';
      case 'cancelled':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const formatAddress = (order) => {
    if (order.doorNo || order.building) {
      // New format with separate fields
      return (
        <>
          <p>{order.doorNo}, {order.building}</p>
          <p>{order.street}</p>
          <p>{order.city}, {order.state} - {order.pincode}</p>
        </>
      );
    }
    // Old format with single address field
    return <p>{order.address}</p>;
  };

  const handleCancelOrder = async (cancelReason) => {
    try {
      // Use customer cancellation endpoint
      await axios.post(
        `${API}/orders/${selectedOrder.order_id}/cancel-customer`,
        { cancel_reason: cancelReason }
      );

      toast({
        title: "Order Cancelled",
        description: "Your order has been cancelled successfully. You will receive a confirmation email shortly.",
        duration: 5000
      });

      setShowCancelModal(false);
      
      // Refresh order details
      const response = await axios.get(`${API}/orders/track/${searchTerm.trim()}`);
      setOrders(response.data.orders || []);
      setTotalOrders(response.data.total || 0);
    } catch (error) {
      console.error('Cancel order error:', error);
      toast({
        title: "Cancellation Failed",
        description: error.response?.data?.detail || "Failed to cancel order. Please try again or contact support.",
        variant: "destructive",
        duration: 6000
      });
    }
  };

  const handlePaymentComplete = async () => {
    if (!paymentMethod) {
      toast({
        title: "Error",
        description: "Please select a payment method",
        variant: "destructive"
      });
      return;
    }

    if (paymentMethod === 'online' && !paymentSubMethod) {
      toast({
        title: "Error",
        description: "Please select an online payment option",
        variant: "destructive"
      });
      return;
    }

    if (paymentMethod === 'card' && !paymentSubMethod) {
      toast({
        title: "Error",
        description: "Please select a card type",
        variant: "destructive"
      });
      return;
    }
    
    try {
      const response = await axios.post(
        `${API}/orders/${selectedOrder.order_id}/complete-payment`,
        { 
          payment_method: paymentMethod,
          payment_sub_method: paymentSubMethod
        }
      );
      
      toast({
        title: "Payment Completed",
        description: "Your payment has been recorded. Order status has been updated to Confirmed.",
        duration: 5000
      });
      
      setShowPaymentModal(false);
      setPaymentMethod('online');
      setPaymentSubMethod('');
      
      // Refresh order details
      const refreshResponse = await axios.get(`${API}/orders/track/${searchTerm.trim()}`);
      setOrders(refreshResponse.data.orders || []);
      setTotalOrders(refreshResponse.data.total || 0);
    } catch (error) {
      console.error('Payment completion error:', error);
      toast({
        title: "Payment Failed",
        description: error.response?.data?.detail || "Failed to record payment. Please try again.",
        variant: "destructive",
        duration: 6000
      });
    }
  };

  const toggleOrderExpansion = (index) => {
    setExpandedOrderIndex(expandedOrderIndex === index ? null : index);
  };

  const handleReorder = (order) => {
    // Add all items from the order back to cart
    if (order.items && order.items.length > 0) {
      order.items.forEach(item => {
        // Prepare product and price objects for addToCart
        const product = {
          id: item.product_id || item.id,
          name: item.name,
          image: item.image,
          description: item.description || ''
        };
        
        const selectedPrice = {
          weight: item.weight || item.size || 'N/A',
          price: item.price || 0
        };
        
        // Add item to cart using proper addToCart signature
        addToCart(product, selectedPrice);
      });

      toast({
        title: "Items Added to Cart!",
        description: `${order.items.length} item(s) from Order #${order.order_id} have been added to your cart.`,
        duration: 5000
      });

      // Navigate to checkout or home
      setTimeout(() => {
        navigate('/checkout');
      }, 1000);
    }
  };

  const OrderCard = ({ order, index, total }) => {
    const isExpanded = expandedOrderIndex === index;
    
    return (
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden mb-6">
        {/* Order Header - Always Visible */}
        <div 
          className="bg-gradient-to-r from-orange-500 to-red-500 p-6 text-white cursor-pointer hover:from-orange-600 hover:to-red-600 transition-all"
          onClick={() => toggleOrderExpansion(index)}
        >
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-bold">Order #{order.order_id}</h2>
                {total > 1 && (
                  <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium">
                    {index + 1} of {total}
                  </span>
                )}
              </div>
              <p className="text-orange-100">Tracking Code: {order.tracking_code}</p>
              <div className="mt-2">
                <span className={`inline-block px-3 py-1 rounded-full font-semibold text-sm ${getStatusColor(order.order_status)}`}>
                  {order.order_status?.toUpperCase()}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4">
                {getStatusIcon(order.order_status)}
              </div>
              {isExpanded ? (
                <ChevronUp className="h-6 w-6" />
              ) : (
                <ChevronDown className="h-6 w-6" />
              )}
            </div>
          </div>
        </div>

        {/* Order Details - Expandable */}
        {isExpanded && (
          <div>
            {/* Status Badge */}
            <div className="p-6 border-b">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex-1">
                  <p className="text-gray-600 text-sm mb-1">Order Date</p>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-gray-500" />
                    <span className="font-semibold">{new Date(order.order_date).toLocaleString()}</span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {order.order_status?.toLowerCase() === 'pending' && order.payment_required && (
                    <button
                      onClick={() => {
                        setSelectedOrder(order);
                        setShowPaymentModal(true);
                      }}
                      className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg font-semibold transition-colors flex items-center gap-2"
                    >
                      Complete Payment
                    </button>
                  )}
                  {order.order_status?.toLowerCase() !== 'cancelled' && 
                   order.order_status?.toLowerCase() !== 'delivered' && (
                    <button
                      onClick={() => {
                        setSelectedOrder(order);
                        setShowCancelModal(true);
                      }}
                      className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
                    >
                      Cancel Order
                    </button>
                  )}
                  <button
                    onClick={() => handleReorder(order)}
                    className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg font-semibold transition-colors flex items-center gap-2"
                  >
                    <RefreshCw className="h-4 w-4" />
                    Reorder
                  </button>
                </div>
              </div>
            </div>

            {/* Customer Details */}
            <div className="p-6 border-b">
              <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                <User className="h-5 w-5 text-orange-600" />
                Customer Details
              </h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-600 text-sm mb-1">Name</p>
                  <p className="font-semibold">{order.customer_name}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Phone className="h-4 w-4 text-gray-600" />
                    <p className="text-gray-600 text-sm">Phone</p>
                  </div>
                  <p className="font-semibold mt-1">{order.phone}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-gray-600" />
                    <p className="text-gray-600 text-sm">Email</p>
                  </div>
                  <p className="font-semibold mt-1">{order.email}</p>
                </div>
              </div>
            </div>

            {/* Delivery Address */}
            <div className="p-6 border-b">
              <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                <MapPin className="h-5 w-5 text-orange-600" />
                Delivery Address
              </h3>
              <div className="bg-gradient-to-br from-orange-50 to-red-50 p-6 rounded-lg">
                {formatAddress(order)}
                <p className="mt-2 font-semibold text-orange-600">{order.location}</p>
              </div>
            </div>

            {/* Payment Information */}
            <div className="p-6 border-b">
              <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                <CreditCard className="h-5 w-5 text-orange-600" />
                Payment Information
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-600 text-sm mb-1">Payment Method</p>
                  <p className="font-semibold capitalize">{order.payment_method}</p>
                  {order.payment_sub_method && (
                    <p className="text-sm text-gray-600 mt-1">({order.payment_sub_method})</p>
                  )}
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-600 text-sm mb-1">Payment Status</p>
                  <p className={`font-semibold capitalize ${
                    order.payment_status === 'completed' ? 'text-green-600' : 
                    order.payment_status === 'pending' ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {order.payment_status}
                  </p>
                </div>
              </div>
            </div>

            {/* Order Items */}
            <div className="p-6 border-b">
              <h3 className="font-bold text-lg mb-4">Order Items</h3>
              <div className="space-y-4">
                {order.items?.map((item, idx) => (
                  <div key={idx} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                    <img
                      src={item.image}
                      alt={item.name}
                      className="w-20 h-20 object-cover rounded-lg"
                    />
                    <div className="flex-1">
                      <h4 className="font-semibold">{item.name}</h4>
                      <p className="text-sm text-gray-600">{item.description}</p>
                      <div className="flex items-center gap-4 mt-2">
                        <span className="text-sm text-gray-600">Quantity: {item.quantity}</span>
                        <span className="text-sm text-gray-600">Size: {item.size}</span>
                        <span className="font-semibold text-orange-600">₹{item.price}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Order Summary */}
            <div className="p-6 bg-gradient-to-br from-orange-50 to-red-50">
              <h3 className="font-bold text-lg mb-4">Order Summary</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="font-semibold">₹{order.subtotal}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Delivery Charge</span>
                  <span className="font-semibold">₹{order.delivery_charge}</span>
                </div>
                <div className="border-t pt-2 mt-2">
                  <div className="flex justify-between text-lg">
                    <span className="font-bold">Total</span>
                    <span className="font-bold text-orange-600">₹{order.total}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-pink-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">Track Your Order</h1>
          <p className="text-gray-600 text-lg">Enter your Order ID, Tracking Code, Phone Number, or Email</p>
        </div>

        {/* Search Box */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Enter Order ID, Tracking Code, Phone Number, or Email..."
                className="w-full px-6 py-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent text-lg"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-4 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white rounded-xl font-semibold transition-all shadow-lg hover:shadow-xl disabled:opacity-50 flex items-center gap-2 text-lg"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Search className="h-5 w-5" />
                  <span>Track</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Orders Display */}
        {orders.length > 0 && (
          <>
            {totalOrders > 1 && (
              <div className="bg-blue-100 border-l-4 border-blue-500 p-4 mb-6 rounded-lg">
                <p className="text-blue-800 font-semibold">
                  📦 Found {totalOrders} orders for this account (including cancelled orders)
                </p>
                <p className="text-blue-700 text-sm mt-1">
                  Click on any order to view details
                </p>
              </div>
            )}
            {orders.map((order, index) => (
              <OrderCard 
                key={order.order_id} 
                order={order} 
                index={index} 
                total={totalOrders}
              />
            ))}
          </>
        )}

        {/* No Results */}
        {searched && orders.length === 0 && !loading && (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <Package className="h-24 w-24 text-gray-300 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-gray-800 mb-2">Order Not Found</h3>
            <p className="text-gray-600">
              We couldn't find an order with the provided information.
              <br />Please check your Order ID, Tracking Code, Phone Number, or Email and try again.
              <br />If you just placed an order, it may take a few moments to appear in our system.
            </p>
          </div>
        )}

        {/* Cancel Order Modal */}
        {showCancelModal && selectedOrder && (
          <CancelOrderModal
            isOpen={showCancelModal}
            onClose={() => setShowCancelModal(false)}
            onConfirm={handleCancelOrder}
            orderData={selectedOrder}
          />
        )}

        {/* Payment Modal */}
        {showPaymentModal && selectedOrder && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
              <h3 className="text-2xl font-bold mb-6 text-gray-800">Complete Payment</h3>
              
              <div className="mb-6">
                <p className="text-gray-600 mb-2">Order ID: <span className="font-semibold">{selectedOrder.order_id}</span></p>
                <p className="text-gray-600 mb-2">Total Amount: <span className="font-semibold text-orange-600">₹{selectedOrder.total}</span></p>
              </div>

              <div className="mb-6">
                <label className="block text-gray-700 font-medium mb-3">Select Payment Method</label>
                
                {/* Online Payment */}
                <div className="mb-4">
                  <label className="flex items-center p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                    <input
                      type="radio"
                      name="payment"
                      value="online"
                      checked={paymentMethod === 'online'}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                      className="mr-3 h-5 w-5"
                    />
                    <span className="font-medium">Online Payment (UPI)</span>
                  </label>
                  
                  {paymentMethod === 'online' && (
                    <div className="ml-8 mt-3 space-y-2">
                      {['Paytm', 'PhonePe', 'Google Pay', 'BHIM UPI'].map((method) => (
                        <label key={method} className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                          <input
                            type="radio"
                            name="onlineMethod"
                            value={method}
                            checked={paymentSubMethod === method}
                            onChange={(e) => setPaymentSubMethod(e.target.value)}
                            className="mr-3"
                          />
                          <span>{method}</span>
                        </label>
                      ))}
                    </div>
                  )}
                </div>

                {/* Card Payment */}
                <div>
                  <label className="flex items-center p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                    <input
                      type="radio"
                      name="payment"
                      value="card"
                      checked={paymentMethod === 'card'}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                      className="mr-3 h-5 w-5"
                    />
                    <span className="font-medium">Card Payment</span>
                  </label>
                  
                  {paymentMethod === 'card' && (
                    <div className="ml-8 mt-3 space-y-2">
                      {['Debit Card', 'Credit Card'].map((method) => (
                        <label key={method} className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                          <input
                            type="radio"
                            name="cardMethod"
                            value={method}
                            checked={paymentSubMethod === method}
                            onChange={(e) => setPaymentSubMethod(e.target.value)}
                            className="mr-3"
                          />
                          <span>{method}</span>
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex gap-4">
                <button
                  onClick={() => {
                    setShowPaymentModal(false);
                    setPaymentMethod('online');
                    setPaymentSubMethod('');
                  }}
                  className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handlePaymentComplete}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white rounded-lg font-semibold transition-colors"
                >
                  Confirm Payment
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrackOrder;