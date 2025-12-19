import React from 'react';
import { X, Plus, Minus, Trash2, ShoppingBag } from 'lucide-react';
import { useCart } from '../contexts/CartContext';
import { useNavigate } from 'react-router-dom';

const CartSidebar = () => {
  const { cart, isOpen, setIsOpen, updateQuantity, removeFromCart, getCartTotal, getCartCount } = useCart();
  const navigate = useNavigate();

  const handleCheckout = () => {
    setIsOpen(false);
    navigate('/checkout');
  };

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-50 transition-opacity"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed right-0 top-0 h-full w-full md:w-96 bg-white shadow-2xl z-50 transform transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-orange-500 to-red-500 text-white">
            <div className="flex items-center space-x-2">
              <ShoppingBag className="h-6 w-6" />
              <h2 className="text-xl font-bold">Your Cart</h2>
              {getCartCount() > 0 && (
                <span className="bg-white text-orange-600 rounded-full px-2 py-1 text-sm font-bold">
                  {getCartCount()}
                </span>
              )}
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="hover:bg-white/20 p-1 rounded-full transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Cart Items */}
          <div className="flex-1 overflow-y-auto p-4">
            {cart.length === 0 ? (
              <div className="text-center py-12">
                <ShoppingBag className="h-24 w-24 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">Your cart is empty</p>
                <button
                  onClick={() => setIsOpen(false)}
                  className="mt-4 bg-gradient-to-r from-orange-500 to-red-500 text-white px-6 py-2 rounded-full font-medium hover:from-orange-600 hover:to-red-600 transition-all"
                >
                  Start Shopping
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {cart.map((item, index) => (
                  <div key={`${item.id}-${item.weight}-${index}`} className="bg-gray-50 rounded-lg p-3 flex space-x-3">
                    <img
                      src={item.image}
                      alt={item.name}
                      className="w-20 h-20 object-cover rounded-lg"
                    />
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-800 mb-1 line-clamp-1">{item.name}</h3>
                      <p className="text-sm text-gray-600 mb-2">{item.weight}</p>
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-orange-600">₹{item.price}</span>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => updateQuantity(item.id, item.weight, item.quantity - 1)}
                            className="bg-white border border-gray-300 p-1 rounded hover:bg-gray-100 transition-colors"
                          >
                            <Minus className="h-4 w-4" />
                          </button>
                          <span className="font-semibold w-8 text-center">{item.quantity}</span>
                          <button
                            onClick={() => updateQuantity(item.id, item.weight, item.quantity + 1)}
                            className="bg-white border border-gray-300 p-1 rounded hover:bg-gray-100 transition-colors"
                          >
                            <Plus className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFromCart(item.id, item.weight)}
                      className="text-red-500 hover:text-red-700 transition-colors"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {cart.length > 0 && (
            <div className="border-t p-4 bg-gray-50">
              <div className="flex items-center justify-between mb-4">
                <span className="text-lg font-semibold text-gray-700">Subtotal:</span>
                <span className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                  ₹{getCartTotal()}
                </span>
              </div>
              <button
                onClick={handleCheckout}
                className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-4 rounded-xl font-semibold hover:from-green-700 hover:to-green-800 transition-all transform hover:scale-105 shadow-lg"
              >
                Proceed to Checkout
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default CartSidebar;