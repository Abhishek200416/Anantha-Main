import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from '../hooks/use-toast';

const ReportBug = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    mobile: '',
    issue_description: ''
  });
  const [photo, setPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
      if (!validTypes.includes(file.type)) {
        toast({
          title: "Invalid File Type",
          description: "Please upload an image file (JPG, PNG, or GIF)",
          variant: "destructive"
        });
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast({
          title: "File Too Large",
          description: "Please upload an image smaller than 5MB",
          variant: "destructive"
        });
        return;
      }

      setPhoto(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const removePhoto = () => {
    setPhoto(null);
    setPhotoPreview(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.email || !formData.mobile || !formData.issue_description) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields",
        variant: "destructive"
      });
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      toast({
        title: "Invalid Email",
        description: "Please enter a valid email address",
        variant: "destructive"
      });
      return;
    }

    // Mobile validation (10 digits)
    const mobileRegex = /^[0-9]{10}$/;
    if (!mobileRegex.test(formData.mobile)) {
      toast({
        title: "Invalid Mobile Number",
        description: "Please enter a valid 10-digit mobile number",
        variant: "destructive"
      });
      return;
    }

    setIsSubmitting(true);

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const formDataToSend = new FormData();
      formDataToSend.append('email', formData.email);
      formDataToSend.append('mobile', formData.mobile);
      formDataToSend.append('issue_description', formData.issue_description);
      
      if (photo) {
        formDataToSend.append('photo', photo);
      }

      const response = await fetch(`${backendUrl}/reports`, {
        method: 'POST',
        body: formDataToSend
      });

      const data = await response.json();

      if (response.ok) {
        toast({
          title: "✅ Report Submitted!",
          description: data.message || "Thank you for reporting this issue. We'll look into it soon.",
          duration: 5000
        });

        // Reset form
        setFormData({ email: '', mobile: '', issue_description: '' });
        setPhoto(null);
        setPhotoPreview(null);

        // Navigate back to home after a delay
        setTimeout(() => {
          navigate('/');
        }, 2000);
      } else {
        throw new Error(data.detail || 'Failed to submit report');
      }
    } catch (error) {
      console.error('Error submitting bug report:', error);
      toast({
        title: "Submission Failed",
        description: error.message || "Failed to submit bug report. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-orange-500 to-red-500 px-6 py-8 text-white">
            <h1 className="text-3xl font-bold mb-2">Report a Bug</h1>
            <p className="text-orange-100">
              Found an issue? Let us know and we'll fix it as soon as possible!
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-6">
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-2">
                Email Address <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition"
                placeholder="your.email@example.com"
                required
              />
            </div>

            {/* Mobile */}
            <div>
              <label htmlFor="mobile" className="block text-sm font-semibold text-gray-700 mb-2">
                Mobile Number <span className="text-red-500">*</span>
              </label>
              <input
                type="tel"
                id="mobile"
                name="mobile"
                value={formData.mobile}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition"
                placeholder="9876543210"
                pattern="[0-9]{10}"
                maxLength="10"
                required
              />
              <p className="text-xs text-gray-500 mt-1">Enter 10-digit mobile number</p>
            </div>

            {/* Issue Description */}
            <div>
              <label htmlFor="issue_description" className="block text-sm font-semibold text-gray-700 mb-2">
                What's the issue? <span className="text-red-500">*</span>
              </label>
              <textarea
                id="issue_description"
                name="issue_description"
                value={formData.issue_description}
                onChange={handleChange}
                rows="6"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition resize-none"
                placeholder="Please describe the issue in detail. Include steps to reproduce if possible..."
                required
              />
            </div>

            {/* Photo Upload */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Upload Screenshot/Photo (Optional)
              </label>
              
              {!photoPreview ? (
                <div className="relative">
                  <input
                    type="file"
                    id="photo"
                    accept="image/*"
                    onChange={handlePhotoChange}
                    className="hidden"
                  />
                  <label
                    htmlFor="photo"
                    className="flex flex-col items-center justify-center w-full h-32 px-4 transition bg-white border-2 border-gray-300 border-dashed rounded-lg cursor-pointer hover:bg-gray-50 hover:border-orange-400"
                  >
                    <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p className="mt-2 text-sm text-gray-600">
                      <span className="font-semibold">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-gray-500">PNG, JPG, GIF up to 5MB</p>
                  </label>
                </div>
              ) : (
                <div className="relative">
                  <img
                    src={photoPreview}
                    alt="Preview"
                    className="w-full h-64 object-contain rounded-lg border-2 border-gray-200"
                  />
                  <button
                    type="button"
                    onClick={removePhoto}
                    className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition shadow-lg"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              )}
            </div>

            {/* Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 pt-4">
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 px-6 rounded-lg font-semibold hover:from-orange-600 hover:to-red-600 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg"
              >
                {isSubmitting ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Submitting...
                  </span>
                ) : (
                  'Submit Report'
                )}
              </button>
              <button
                type="button"
                onClick={() => navigate('/')}
                className="flex-1 sm:flex-initial bg-gray-200 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-300 transition"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>

        {/* Info Cards */}
        <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-orange-500 text-2xl mb-2">🐛</div>
            <p className="text-sm text-gray-600">Report bugs to help us improve</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-orange-500 text-2xl mb-2">⚡</div>
            <p className="text-sm text-gray-600">We respond within 24 hours</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-orange-500 text-2xl mb-2">✅</div>
            <p className="text-sm text-gray-600">Your feedback matters to us</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportBug;
