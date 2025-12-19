import React, { useState } from 'react';
import { X, MapPin, Send, CheckCircle, Phone, Mail } from 'lucide-react';
import axios from 'axios';
import { toast } from '../hooks/use-toast';

const API = process.env.REACT_APP_BACKEND_URL || '';

const AddCityModal = ({ isOpen, onClose, preSelectedState = '' }) => {
  const [formData, setFormData] = useState({
    state: preSelectedState || '',
    city: '',
    name: '',
    phone: '',
    email: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const states = ['Andhra Pradesh', 'Telangana'];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.state || !formData.city || !formData.name || !formData.phone || !formData.email) {
      toast({
        title: "Required Fields",
        description: "Please fill in all required fields: State, City, Name, Phone, and Email",
        variant: "destructive"
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await axios.post(`${API}/api/suggest-city`, {
        state: formData.state,
        city: formData.city,
        customer_name: formData.name,
        phone: formData.phone,
        email: formData.email
      });

      setIsSuccess(true);
      
      // Reset form after 3 seconds and close
      setTimeout(() => {
        setFormData({
          state: '',
          city: '',
          name: '',
          phone: '',
          email: ''
        });
        setIsSuccess(false);
        onClose();
      }, 3000);

    } catch (error) {
      console.error('Error submitting city suggestion:', error);
      toast({
        title: "Submission Failed",
        description: "Please try again or contact us directly",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto my-8">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-orange-500 to-orange-600 text-white p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <MapPin className="h-6 w-6" />
              <h2 className="text-xl font-bold">Add My City</h2>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/20 rounded-full p-1 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {isSuccess ? (
            <div className="text-center py-8 space-y-4">
              <CheckCircle className="h-16 w-16 text-green-500 mx-auto" />
              <h3 className="text-2xl font-bold text-gray-800">Thank You!</h3>
              <p className="text-gray-600 leading-relaxed">
                Your city suggestion has been received with your contact details. We'll review and add it to our delivery locations.
              </p>
              <p className="text-sm text-blue-600 font-medium">
                We'll contact you at <span className="font-semibold">{formData.phone}</span> or <span className="font-semibold">{formData.email}</span> if we need to confirm your exact location!
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Info Message */}
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
                <p className="text-sm text-blue-800 leading-relaxed">
                  <span className="font-semibold">Can't find your city?</span> Let us know with your contact details and we'll add it to our delivery locations. We may contact you to confirm the exact location!
                </p>
              </div>

              {/* State Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  State <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  required
                >
                  <option value="">Select State</option>
                  {states.map(state => (
                    <option key={state} value={state}>{state}</option>
                  ))}
                </select>
              </div>

              {/* City Name */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  City Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  placeholder="e.g., Nellore, Kurnool, Kadapa..."
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  required
                />
              </div>

              {/* Contact Info - REQUIRED */}
              <div className="border-t pt-4">
                <p className="text-sm font-semibold text-gray-700 mb-3">📞 Contact Details (Required)</p>
                <p className="text-xs text-gray-500 mb-3">We'll contact you if we need to confirm the exact location or delivery details</p>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Your Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="Enter your full name"
                      className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                      <Phone className="w-4 h-4 text-orange-500" />
                      Phone Number <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      placeholder="e.g., 9876543210"
                      className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">We'll call if we can't find your location</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                      <Mail className="w-4 h-4 text-orange-500" />
                      Email Address <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      placeholder="your.email@example.com"
                      className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">For order updates and delivery confirmation</p>
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-gradient-to-r from-orange-500 to-orange-600 text-white py-4 rounded-lg font-semibold hover:from-orange-600 hover:to-orange-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Submitting...</span>
                  </>
                ) : (
                  <>
                    <Send className="h-5 w-5" />
                    <span>Submit City Request</span>
                  </>
                )}
              </button>

              {/* Footer Message */}
              <p className="text-xs text-center text-gray-500 leading-relaxed">
                We'll review and add your city. If we need clarification about your location, we'll contact you at the provided phone or email!
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default AddCityModal;
