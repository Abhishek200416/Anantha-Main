import React, { useState } from 'react';
import { X, AlertCircle, Send, CheckCircle, Upload, Phone, Mail, Image as ImageIcon } from 'lucide-react';
import axios from 'axios';
import { toast } from '../hooks/use-toast';

const API = process.env.REACT_APP_BACKEND_URL || '';

const ReportBugModal = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    issueTitle: '',
    description: '',
    page: ''
  });
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        toast({
          title: "Image Too Large",
          description: "Please select an image smaller than 5MB",
          variant: "destructive"
        });
        return;
      }
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.issueTitle || !formData.description) {
      toast({
        title: "Required Fields",
        description: "Please provide issue title and description",
        variant: "destructive"
      });
      return;
    }

    setIsSubmitting(true);
    try {
      const formDataToSend = new FormData();
      formDataToSend.append('email', formData.email || 'no-email@provided.com');
      formDataToSend.append('mobile', formData.phone || '0000000000');
      formDataToSend.append('issue_description', `${formData.issueTitle ? formData.issueTitle + ': ' : ''}${formData.description}`);
      
      if (selectedImage) {
        formDataToSend.append('photo', selectedImage);
      }

      await axios.post(`${API}/api/reports`, formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setIsSuccess(true);
      
      // Reset form after 3 seconds and close
      setTimeout(() => {
        setFormData({
          name: '',
          email: '',
          phone: '',
          issueTitle: '',
          description: '',
          page: ''
        });
        setSelectedImage(null);
        setImagePreview(null);
        setIsSuccess(false);
        onClose();
      }, 4000);

    } catch (error) {
      console.error('Error submitting bug report:', error);
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-red-500 to-red-600 text-white p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-6 w-6" />
              <h2 className="text-xl font-bold">Report an Issue</h2>
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
                Your issue report has been submitted successfully. Our team will review it and get back to you soon.
              </p>
              <div className="bg-blue-50 p-4 rounded-lg space-y-2">
                <p className="text-sm text-gray-700">
                  <strong>Need immediate help?</strong>
                </p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
                  <a href="tel:9985116385" className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium">
                    <Phone className="h-4 w-4" />
                    Call: 9985116385
                  </a>
                  <a href="mailto:support@ananthalakshmi.com" className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium">
                    <Mail className="h-4 w-4" />
                    Email Us
                  </a>
                </div>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Info Message */}
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg">
                <p className="text-sm text-yellow-800 leading-relaxed">
                  <span className="font-semibold">Found a bug or issue?</span> Please describe the problem and attach a screenshot if possible. We'll investigate and fix it as soon as possible!
                </p>
              </div>

              {/* Contact Info */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Your Name
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Enter your name"
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="your@email.com"
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="10-digit mobile number"
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Page/Section
                  </label>
                  <input
                    type="text"
                    value={formData.page}
                    onChange={(e) => setFormData({ ...formData, page: e.target.value })}
                    placeholder="e.g., Home, Checkout, Admin"
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  />
                </div>
              </div>

              {/* Issue Title */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Issue Title <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.issueTitle}
                  onChange={(e) => setFormData({ ...formData, issueTitle: e.target.value })}
                  placeholder="Brief description of the issue"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  required
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Detailed Description <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Please describe the issue in detail. Include steps to reproduce, what you expected to happen, and what actually happened."
                  rows="5"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 resize-none"
                  required
                />
              </div>

              {/* Image Upload */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Attach Screenshot (Optional)
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-red-400 transition-colors">
                  {imagePreview ? (
                    <div className="space-y-3">
                      <img 
                        src={imagePreview} 
                        alt="Preview" 
                        className="max-h-48 mx-auto rounded-lg shadow-md"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedImage(null);
                          setImagePreview(null);
                        }}
                        className="text-red-600 hover:text-red-700 text-sm font-medium"
                      >
                        Remove Image
                      </button>
                    </div>
                  ) : (
                    <label className="cursor-pointer">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageChange}
                        className="hidden"
                      />
                      <ImageIcon className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-sm text-gray-600 mb-1">
                        Click to upload or drag and drop
                      </p>
                      <p className="text-xs text-gray-400">
                        PNG, JPG, JPEG up to 5MB
                      </p>
                    </label>
                  )}
                </div>
              </div>

              {/* Contact Options */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm font-semibold text-gray-700 mb-2">Other Ways to Reach Us:</p>
                <div className="flex flex-col sm:flex-row gap-3">
                  <a 
                    href="tel:9985116385" 
                    className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    <Phone className="h-4 w-4" />
                    Call: 9985116385
                  </a>
                  <a 
                    href="mailto:support@ananthalakshmi.com" 
                    className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    <Mail className="h-4 w-4" />
                    support@ananthalakshmi.com
                  </a>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-gradient-to-r from-red-500 to-red-600 text-white py-4 rounded-lg font-semibold hover:from-red-600 hover:to-red-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Submitting...</span>
                  </>
                ) : (
                  <>
                    <Send className="h-5 w-5" />
                    <span>Submit Issue Report</span>
                  </>
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportBugModal;
