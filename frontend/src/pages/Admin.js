import React, { useState, useEffect } from 'react';
import { useAdmin } from '../contexts/AdminContext';
import { useLocation } from 'react-router-dom';
import { LogIn, LogOut, Package, MapPin, Star, PlusCircle, Edit, Trash2, Save, X, Sparkles, Upload, TrendingUp, Percent, Zap, Code, Palette, Wrench, Archive, Truck, Search, CreditCard } from 'lucide-react';
import { toast } from '../hooks/use-toast';
import { categories } from '../mock';
import DeleteConfirmDialog from '../components/DeleteConfirmDialog';
import AdminOrders from '../components/AdminOrders';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

// Helper function to format error messages properly
const formatErrorMessage = (error) => {
  if (!error.response?.data?.detail) {
    return "An error occurred";
  }
  
  const detail = error.response.data.detail;
  
  // If detail is an array of validation errors
  if (Array.isArray(detail)) {
    return detail.map(err => {
      if (typeof err === 'object' && err.msg) {
        return err.msg;
      }
      return String(err);
    }).join(', ');
  }
  
  // If detail is a string
  if (typeof detail === 'string') {
    return detail;
  }
  
  // If detail is an object
  if (typeof detail === 'object') {
    return JSON.stringify(detail);
  }
  
  return "An error occurred";
};

// City Suggestions Component (from homepage "Suggest a City" form)
const CitySuggestionsSection = ({ fetchDeliveryLocations }) => {
  const [citySuggestions, setCitySuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(null);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState(null);
  const [statusFilter, setStatusFilter] = useState('all'); // all, pending, approved, rejected
  const [approvalData, setApprovalData] = useState({
    deliveryCharge: '',
    freeDeliveryThreshold: ''
  });
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [rejectingSuggestionId, setRejectingSuggestionId] = useState(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [deletingSuggestionId, setDeleteSuggestionId] = useState(null);
  const [deletingSuggestionName, setDeleteSuggestionName] = useState('');

  React.useEffect(() => {
    fetchCitySuggestions();
  }, [statusFilter]);

  const fetchCitySuggestions = async (filterStatus = null) => {
    setLoading(true);
    try {
      const adminToken = localStorage.getItem('token');
      // Use passed parameter if provided, otherwise use state
      const filter = filterStatus !== null ? filterStatus : statusFilter;
      const url = filter === 'all' 
        ? `${BACKEND_URL}/api/admin/city-suggestions`
        : `${BACKEND_URL}/api/admin/city-suggestions?status=${filter}`;
      
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${adminToken}` }
      });
      setCitySuggestions(response.data);
    } catch (error) {
      console.error('Failed to fetch city suggestions:', error);
      toast({
        title: "Error",
        description: formatErrorMessage(error) || "Failed to load city suggestions",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleOpenApprovalModal = (suggestion) => {
    setSelectedSuggestion(suggestion);
    setApprovalData({
      deliveryCharge: '99',
      freeDeliveryThreshold: '1000'
    });
    setShowApprovalModal(true);
  };

  const handleApproveSuggestion = async () => {
    if (!selectedSuggestion) return;
    
    // Validation
    if (!approvalData.deliveryCharge || isNaN(parseFloat(approvalData.deliveryCharge))) {
      toast({
        title: "Validation Error",
        description: "Please enter a valid delivery charge",
        variant: "destructive"
      });
      return;
    }

    setProcessing(selectedSuggestion.id);
    try {
      const adminToken = localStorage.getItem('token');
      
      // Add city to locations using PUT endpoint with query parameters
      const params = new URLSearchParams({
        charge: approvalData.deliveryCharge,
        state: selectedSuggestion.state
      });
      
      if (approvalData.freeDeliveryThreshold && approvalData.freeDeliveryThreshold.trim() !== '') {
        params.append('free_delivery_threshold', approvalData.freeDeliveryThreshold);
      }
      
      await axios.put(
        `${BACKEND_URL}/api/admin/locations/${encodeURIComponent(selectedSuggestion.city)}?${params.toString()}`,
        {},
        {
          headers: { Authorization: `Bearer ${adminToken}` }
        }
      );

      // Update suggestion status to approved (with delivery charge for email)
      const statusUpdateData = { 
        status: 'approved',
        delivery_charge: parseInt(approvalData.deliveryCharge)
      };
      
      if (approvalData.freeDeliveryThreshold && approvalData.freeDeliveryThreshold.trim() !== '') {
        statusUpdateData.free_delivery_threshold = parseInt(approvalData.freeDeliveryThreshold);
      }
      
      await axios.put(
        `${BACKEND_URL}/api/admin/city-suggestions/${selectedSuggestion.id}/status`,
        statusUpdateData,
        {
          headers: { Authorization: `Bearer ${adminToken}` }
        }
      );

      toast({
        title: "City Approved!",
        description: `${selectedSuggestion.city} has been added to delivery locations with ₹${approvalData.deliveryCharge} charge`
      });

      setShowApprovalModal(false);
      setSelectedSuggestion(null);
      setApprovalData({ deliveryCharge: '', freeDeliveryThreshold: '' });
      
      // Switch to "all" filter and refresh to show all cities including the newly approved one
      setStatusFilter('all');
      // Explicitly fetch with 'all' filter to avoid stale closure issue
      await fetchCitySuggestions('all');
      // Also refresh the delivery locations list to show the newly approved city
      if (fetchDeliveryLocations) {
        await fetchDeliveryLocations();
      }
    } catch (error) {
      console.error('Failed to approve city suggestion:', error);
      toast({
        title: "Error",
        description: formatErrorMessage(error) || "Failed to approve city suggestion",
        variant: "destructive"
      });
    } finally {
      setProcessing(null);
    }
  };

  const openRejectDialog = (suggestionId) => {
    setRejectingSuggestionId(suggestionId);
    setShowRejectDialog(true);
  };

  const handleRejectSuggestion = async () => {
    const suggestionId = rejectingSuggestionId;
    setShowRejectDialog(false);
    
    setProcessing(suggestionId);
    try {
      const adminToken = localStorage.getItem('token');
      
      await axios.put(
        `${BACKEND_URL}/api/admin/city-suggestions/${suggestionId}/status`,
        { status: 'rejected' },
        {
          headers: { Authorization: `Bearer ${adminToken}` }
        }
      );

      toast({
        title: "Success",
        description: "City suggestion rejected"
      });

      // Switch to "all" filter and refresh to show all cities including the newly rejected one
      setStatusFilter('all');
      // Explicitly fetch with 'all' filter to avoid stale closure issue
      await fetchCitySuggestions('all');
    } catch (error) {
      console.error('Failed to reject city suggestion:', error);
      toast({
        title: "Error",
        description: formatErrorMessage(error) || "Failed to reject city suggestion",
        variant: "destructive"
      });
    } finally {
      setProcessing(null);
    }
  };

  const openDeleteDialog = (suggestionId, suggestionName, suggestionStatus) => {
    // Only allow deleting approved or rejected suggestions (not pending)
    if (suggestionStatus === 'pending') {
      toast({
        title: "Cannot Delete",
        description: "Please approve or reject the suggestion first before deleting",
        variant: "destructive"
      });
      return;
    }

    setDeleteSuggestionId(suggestionId);
    setDeleteSuggestionName(suggestionName);
    setShowDeleteDialog(true);
  };

  const handleDeleteSuggestion = async () => {
    const suggestionId = deletingSuggestionId;
    setShowDeleteDialog(false);

    setProcessing(suggestionId);
    try {
      const adminToken = localStorage.getItem('token');
      
      await axios.delete(
        `${BACKEND_URL}/api/admin/city-suggestions/${suggestionId}`,
        {
          headers: { Authorization: `Bearer ${adminToken}` }
        }
      );

      toast({
        title: "Deleted",
        description: "City suggestion deleted successfully"
      });

      // Switch to "all" filter and refresh to show remaining cities after deletion
      setStatusFilter('all');
      // Explicitly fetch with 'all' filter to avoid stale closure issue
      await fetchCitySuggestions('all');
    } catch (error) {
      console.error('Failed to delete city suggestion:', error);
      toast({
        title: "Error",
        description: formatErrorMessage(error) || "Failed to delete city suggestion",
        variant: "destructive"
      });
    } finally {
      setProcessing(null);
    }
  };

  // Status badge color helper
  const getStatusBadgeClass = (status) => {
    switch(status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'approved':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'rejected':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
        <p className="text-gray-600 mt-2">Loading city suggestions...</p>
      </div>
    );
  }

  return (
    <>
      {/* Filter Buttons */}
      <div className="mb-6 flex flex-wrap gap-3">
        <button
          onClick={() => setStatusFilter('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-all ${
            statusFilter === 'all' 
              ? 'bg-orange-600 text-white shadow-md' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All ({citySuggestions.length})
        </button>
        <button
          onClick={() => setStatusFilter('pending')}
          className={`px-4 py-2 rounded-lg font-medium transition-all ${
            statusFilter === 'pending' 
              ? 'bg-yellow-500 text-white shadow-md' 
              : 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100'
          }`}
        >
          Pending
        </button>
        <button
          onClick={() => setStatusFilter('approved')}
          className={`px-4 py-2 rounded-lg font-medium transition-all ${
            statusFilter === 'approved' 
              ? 'bg-green-600 text-white shadow-md' 
              : 'bg-green-50 text-green-700 hover:bg-green-100'
          }`}
        >
          Approved
        </button>
        <button
          onClick={() => setStatusFilter('rejected')}
          className={`px-4 py-2 rounded-lg font-medium transition-all ${
            statusFilter === 'rejected' 
              ? 'bg-red-600 text-white shadow-md' 
              : 'bg-red-50 text-red-700 hover:bg-red-100'
          }`}
        >
          Rejected
        </button>
      </div>

      {citySuggestions.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <MapPin className="h-12 w-12 mx-auto mb-3 opacity-50" />
          <p className="font-semibold">No City Suggestions Found</p>
          <p className="text-sm mt-2">
            {statusFilter === 'all' 
              ? "When customers suggest new cities, they'll appear here for review"
              : `No ${statusFilter} city suggestions at the moment`
            }
          </p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {citySuggestions.map((suggestion) => (
            <div key={suggestion.id} className="bg-white border-2 border-orange-200 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden">
              {/* Header with gradient */}
              <div className="bg-gradient-to-r from-orange-500 to-red-500 p-4 text-white">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <MapPin className="h-6 w-6" />
                    <div>
                      <h3 className="font-bold text-lg">{suggestion.city}</h3>
                      <p className="text-xs text-orange-100">{suggestion.state}</p>
                    </div>
                  </div>
                  <span className={`text-xs font-bold px-3 py-1 rounded-full border ${getStatusBadgeClass(suggestion.status)}`}>
                    {suggestion.status ? suggestion.status.toUpperCase() : 'PENDING'}
                </span>
              </div>
            </div>

            {/* Customer Details */}
            <div className="p-4 space-y-3">
              {suggestion.customer_name && (
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-bold">👤</span>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Customer</p>
                    <p className="font-semibold text-gray-800">{suggestion.customer_name}</p>
                  </div>
                </div>
              )}
              
              {suggestion.phone && (
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <span className="text-green-600 font-bold">📞</span>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Phone</p>
                    <p className="font-semibold text-gray-800">{suggestion.phone}</p>
                  </div>
                </div>
              )}
              
              {suggestion.email && (
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <span className="text-purple-600 font-bold">✉️</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-gray-500">Email</p>
                    <p className="font-semibold text-gray-800 text-xs truncate">{suggestion.email}</p>
                  </div>
                </div>
              )}
              
              {suggestion.created_at && (
                <div className="pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-500">
                    📅 Suggested on {new Date(suggestion.created_at).toLocaleDateString()} at {new Date(suggestion.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="p-4 pt-0">
              {suggestion.status === 'pending' ? (
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleOpenApprovalModal(suggestion)}
                    disabled={processing === suggestion.id}
                    className="flex-1 px-4 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 transition-all duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed font-bold text-sm shadow-md hover:shadow-lg transform hover:scale-105"
                  >
                    {processing === suggestion.id ? (
                      <span className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Processing...
                      </span>
                    ) : (
                      '✓ Approve'
                    )}
                  </button>
                  <button
                    onClick={() => openRejectDialog(suggestion.id)}
                    disabled={processing === suggestion.id}
                    className="flex-1 px-4 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg hover:from-red-600 hover:to-red-700 transition-all duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed font-bold text-sm shadow-md hover:shadow-lg transform hover:scale-105"
                  >
                    ✗ Reject
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => openDeleteDialog(suggestion.id, `${suggestion.city}, ${suggestion.state}`, suggestion.status)}
                  disabled={processing === suggestion.id}
                  className="w-full px-4 py-3 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-lg hover:from-gray-700 hover:to-gray-800 transition-all duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed font-bold text-sm shadow-md hover:shadow-lg transform hover:scale-105"
                >
                  {processing === suggestion.id ? (
                    <span className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Deleting...
                    </span>
                  ) : (
                    '🗑️ Delete'
                  )}
                </button>
              )}
            </div>
          </div>
        ))}
        </div>
      )}

      {/* Approval Modal */}
      {showApprovalModal && selectedSuggestion && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden">
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-orange-500 to-red-500 p-6 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <MapPin className="h-8 w-8" />
                  <div>
                    <h2 className="text-xl font-bold">Approve City</h2>
                    <p className="text-sm text-orange-100">{selectedSuggestion.city}, {selectedSuggestion.state}</p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setShowApprovalModal(false);
                    setSelectedSuggestion(null);
                  }}
                  className="text-white hover:text-gray-200 transition-colors"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Delivery Charge (₹) *
                </label>
                <input
                  type="number"
                  value={approvalData.deliveryCharge}
                  onChange={(e) => setApprovalData({ ...approvalData, deliveryCharge: e.target.value })}
                  placeholder="e.g., 99"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-orange-500 focus:outline-none text-gray-800 font-semibold"
                />
                <p className="text-xs text-gray-500 mt-1">Enter the delivery charge for this city</p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Free Delivery Threshold (₹)
                </label>
                <input
                  type="number"
                  value={approvalData.freeDeliveryThreshold}
                  onChange={(e) => setApprovalData({ ...approvalData, freeDeliveryThreshold: e.target.value })}
                  placeholder="e.g., 1000 (optional)"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-orange-500 focus:outline-none text-gray-800 font-semibold"
                />
                <p className="text-xs text-gray-500 mt-1">Orders above this amount get free delivery (optional)</p>
              </div>

              {/* Customer Info Preview */}
              {selectedSuggestion.customer_name && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-xs text-blue-600 font-semibold mb-2">Suggested by:</p>
                  <p className="text-sm text-gray-800"><strong>{selectedSuggestion.customer_name}</strong></p>
                  {selectedSuggestion.phone && <p className="text-sm text-gray-600">{selectedSuggestion.phone}</p>}
                  {selectedSuggestion.email && <p className="text-xs text-gray-600">{selectedSuggestion.email}</p>}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-6 pt-0 flex space-x-3">
              <button
                onClick={() => {
                  setShowApprovalModal(false);
                  setSelectedSuggestion(null);
                }}
                className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleApproveSuggestion}
                disabled={processing}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 transition-all disabled:bg-gray-400 disabled:cursor-not-allowed font-bold shadow-md"
              >
                {processing ? (
                  <span className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Approving...
                  </span>
                ) : (
                  '✓ Approve & Add City'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Dialog */}
      {showRejectDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">❌ Reject City Suggestion?</h3>
            <p className="text-gray-600 mb-6">
              This will reject the city suggestion. The customer will receive an email notification about the rejection.
            </p>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowRejectDialog(false)}
                className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleRejectSuggestion}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg hover:from-red-600 hover:to-red-700 transition-all font-bold shadow-md"
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Dialog */}
      {showDeleteDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">🗑️ Delete City Suggestion?</h3>
            <p className="text-gray-600 mb-2">
              Are you sure you want to delete the suggestion for:
            </p>
            <p className="text-lg font-bold text-orange-600 mb-6">
              {deletingSuggestionName}
            </p>
            <p className="text-sm text-gray-500 mb-6">
              This action cannot be undone.
            </p>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowDeleteDialog(false)}
                className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteSuggestion}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-lg hover:from-gray-700 hover:to-gray-800 transition-all font-bold shadow-md"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};


const Admin = () => {
  const {
    isAuthenticated,
    login,
    logout,
    products,
    fetchProducts,
    addProduct,
    updateProduct,
    deleteProduct,
    deliveryLocations,
    fetchDeliveryLocations,
    updateDeliveryLocation,
    deleteDeliveryLocation,
    states,
    fetchStates,
    addState,
    updateState,
    deleteState,
    festivalProduct,
    setFestivalProduct,
    orders
  } = useAdmin();

  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [activeTab, setActiveTab] = useState('products');
  const [editingProduct, setEditingProduct] = useState(null);
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState({ isOpen: false, productId: null, productName: '' });
  const [imageFile, setImageFile] = useState(null);
  const [imageUploading, setImageUploading] = useState(false);
  const [editingLocation, setEditingLocation] = useState(null);
  const [showAddLocation, setShowAddLocation] = useState(false);
  const [newLocation, setNewLocation] = useState({ name: '', charge: 49, state: 'Andhra Pradesh', free_delivery_threshold: null });
  const [discountData, setDiscountData] = useState({});
  const [editingDiscount, setEditingDiscount] = useState(null);
  const [selectedBestSellers, setSelectedBestSellers] = useState([]);
  const [selectedFestivalProducts, setSelectedFestivalProducts] = useState([]);
  const [showAddState, setShowAddState] = useState(false);
  const [newState, setNewState] = useState({ name: '', enabled: true });
  const [deleteLocationDialog, setDeleteLocationDialog] = useState({ isOpen: false, cityName: '' });
  const [deleteStateDialog, setDeleteStateDialog] = useState({ isOpen: false, stateName: '' });
  const [citySearchEdit, setCitySearchEdit] = useState('');
  const [citySearchAdd, setCitySearchAdd] = useState('');
  const [stateFilter, setStateFilter] = useState('');
  
  // Product filters
  const [productCategoryFilter, setProductCategoryFilter] = useState('all');
  const [productStateFilter, setProductStateFilter] = useState('all');
  const [productCityFilter, setProductCityFilter] = useState('all');
  const [productSearch, setProductSearch] = useState('');
  
  // Reports tab state
  const [bugReports, setBugReports] = useState([]);
  const [reportsLoading, setReportsLoading] = useState(false);
  const [deleteReportDialog, setDeleteReportDialog] = useState({ isOpen: false, reportId: null, reportEmail: '', reportIndex: 0 });
  
  // Profile tab state
  const [adminProfile, setAdminProfile] = useState({ mobile: '', email: '' });
  const [profileLoading, setProfileLoading] = useState(false);
  const [otpEmail, setOtpEmail] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [otpCode, setOtpCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  // REMOVED: Settings tab state variables - functionality moved to Cities & States tab
  // const [freeDeliveryEnabled, setFreeDeliveryEnabled] = useState(false);
  // const [freeDeliveryThreshold, setFreeDeliveryThreshold] = useState(1000);
  // const [citySpecificFreeDeliveryEnabled, setCitySpecificFreeDeliveryEnabled] = useState(true);
  
  // Payment Settings state
  const [paymentStatus, setPaymentStatus] = useState('enabled');
  const [paymentStatusSaved, setPaymentStatusSaved] = useState(false);
  
  // WhatsApp Numbers state
  const [whatsappNumbers, setWhatsappNumbers] = useState([]);
  const [showAddWhatsApp, setShowAddWhatsApp] = useState(false);
  const [editingWhatsApp, setEditingWhatsApp] = useState(null);
  const [whatsappForm, setWhatsappForm] = useState({ phone: '', name: '' });
  
  const [newProduct, setNewProduct] = useState({
    name: '',
    category: 'laddus-chikkis',
    description: '',
    image: '',
    prices: [{ weight: '¼ kg', price: 199 }],
    isBestSeller: false,
    isNew: false,
    tag: 'Traditional',
    discount: 0,
    available_cities: []
  });

  const addPriceOption = (productData, setProductData) => {
    setProductData({
      ...productData,
      prices: [...productData.prices, { weight: '', price: 0 }]
    });
  };

  const updatePriceOption = (productData, setProductData, index, field, value) => {
    const newPrices = [...productData.prices];
    newPrices[index][field] = field === 'price' ? parseInt(value) || 0 : value;
    setProductData({ ...productData, prices: newPrices });
  };

  const removePriceOption = (productData, setProductData, index) => {
    if (productData.prices.length > 1) {
      const newPrices = productData.prices.filter((_, i) => i !== index);
      setProductData({ ...productData, prices: newPrices });
    }
  };

  const handleImageUpload = async (file, productData, setProductData) => {
    if (!file) return;
    
    setImageUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${BACKEND_URL}/api/upload-image`, formData, {
        headers: { 
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        }
      });
      
      setProductData({ ...productData, image: response.data.url });
      toast({
        title: "Success",
        description: "Image uploaded successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to upload image",
        variant: "destructive"
      });
    } finally {
      setImageUploading(false);
    }
  };

  const calculateDiscountedPrice = (originalPrice, discount) => {
    if (!discount || discount === 0) return originalPrice;
    return Math.round(originalPrice - (originalPrice * discount / 100));
  };

  // Helper function to check if a product is a real backend product (not mock)
  const isRealProduct = (product) => {
    // Real products have IDs like "product_1731050000000" or "prod_kandi_podi", mock products have numeric IDs like 1, 2, 3
    return typeof product.id === 'string' && (product.id.startsWith('product_') || product.id.startsWith('prod_'));
  };

  // Filter to get only real products (not mock data)
  const realProducts = products.filter(isRealProduct);

  const handleLogin = async (e) => {
    e.preventDefault();
    
    // Use the context login function which now calls the backend API
    const success = await login(email, password);
    
    if (success) {
      toast({
        title: "Login Successful",
        description: "Welcome to admin panel",
      });
      setEmail('');
      setPassword('');
    } else {
      toast({
        title: "Login Failed",
        description: "Incorrect email or password",
        variant: "destructive"
      });
    }
  };

  const handleAddProduct = () => {
    if (!newProduct.name || !newProduct.image) {
      toast({
        title: "Error",
        description: "Please fill all required fields and upload an image",
        variant: "destructive"
      });
      return;
    }
    addProduct(newProduct);
    toast({
      title: "Success",
      description: "Product added successfully",
    });
    setShowAddProduct(false);
    setNewProduct({
      name: '',
      category: 'laddus-chikkis',
      description: '',
      image: '',
      prices: [{ weight: '¼ kg', price: 199 }],
      isBestSeller: false,
      isNew: false,
      tag: 'Traditional',
      discount: 0
    });
    setImageFile(null);
  };

  const handleUpdateProduct = async (id) => {
    try {
      // Update basic product info
      updateProduct(id, editingProduct);
      
      const token = localStorage.getItem('token');
      
      // Update discount if set
      if (editingProduct.discount_percentage > 0 && editingProduct.discount_expiry_date) {
        try {
          await axios.post(
            `${BACKEND_URL}/api/admin/products/${id}/discount`,
            {
              discount_percentage: editingProduct.discount_percentage,
              discount_expiry_date: new Date(editingProduct.discount_expiry_date).toISOString()
            },
            { headers: { Authorization: `Bearer ${token}` } }
          );
        } catch (discountError) {
          console.error('Discount update error:', discountError);
        }
      } else if (editingProduct.discount_percentage === 0 || !editingProduct.discount_expiry_date) {
        // Remove discount if percentage is 0 or no expiry date
        try {
          await axios.delete(
            `${BACKEND_URL}/api/admin/products/${id}/discount`,
            { headers: { Authorization: `Bearer ${token}` } }
          );
        } catch (err) {
          // Ignore error if discount doesn't exist
        }
      }
      
      // Update inventory settings
      try {
        await axios.put(
          `${BACKEND_URL}/api/admin/products/${id}/inventory`,
          { inventory_count: editingProduct.inventory_count ?? 0 },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } catch (inventoryError) {
        console.error('Inventory update error:', inventoryError);
      }
      
      // Update stock status
      try {
        await axios.put(
          `${BACKEND_URL}/api/admin/products/${id}/stock-status`,
          { out_of_stock: editingProduct.out_of_stock || false },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } catch (stockError) {
        console.error('Stock status update error:', stockError);
      }
      
      // Update available cities
      try {
        await axios.put(
          `${BACKEND_URL}/api/admin/products/${id}/available-cities`,
          { available_cities: editingProduct.available_cities || [] },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } catch (citiesError) {
        console.error('Available cities update error:', citiesError);
      }
      
      toast({
        title: "Success",
        description: "Product updated successfully with discount and inventory settings",
      });
      
      setEditingProduct(null);
      setImageFile(null);
      
      // Reload to see changes
      window.location.reload();
    } catch (error) {
      console.error('Update error:', error);
      toast({
        title: "Error",
        description: "Failed to update product completely",
        variant: "destructive"
      });
    }
  };

  const handleDeleteProduct = (id, name) => {
    setDeleteDialog({ isOpen: true, productId: id, productName: name });
  };

  const confirmDelete = () => {
    deleteProduct(deleteDialog.productId);
    toast({
      title: "Success",
      description: "Product deleted successfully",
    });
  };

  const toggleProductFestival = async (product) => {
    try {
      const token = localStorage.getItem('token');
      const newFestivalStatus = !product.isFestival;
      
      await axios.put(
        `${BACKEND_URL}/api/admin/products/${product.id}/festival`,
        { isFestival: newFestivalStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast({
        title: "Success",
        description: newFestivalStatus ? "Product marked as festival!" : "Removed from festival products",
      });
      
      // Reload products
      window.location.reload();
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to update festival status",
        variant: "destructive"
      });
    }
  };

  const handleAddLocation = async () => {
    if (!newLocation.name || !newLocation.charge || !newLocation.state) {
      toast({
        title: "Error",
        description: "Please fill all fields including state",
        variant: "destructive"
      });
      return;
    }
    const success = await updateDeliveryLocation(newLocation.name, newLocation.charge, newLocation.free_delivery_threshold, newLocation.state);
    if (success) {
      toast({
        title: "Success",
        description: "Location added and saved successfully",
      });
      setShowAddLocation(false);
      setNewLocation({ name: '', charge: 49, state: 'Andhra Pradesh', free_delivery_threshold: null });
    } else {
      toast({
        title: "Warning",
        description: "Location added locally but may not have saved to server",
        variant: "default"
      });
      setShowAddLocation(false);
      setNewLocation({ name: '', charge: 49, state: 'Andhra Pradesh', free_delivery_threshold: null });
    }
  };

  const handleUpdateLocation = async () => {
    // Ensure values are properly converted to numbers
    const charge = typeof editingLocation.charge === 'string' ? parseInt(editingLocation.charge) : editingLocation.charge;
    const threshold = editingLocation.free_delivery_threshold === '' ? null : 
                     (typeof editingLocation.free_delivery_threshold === 'string' ? parseInt(editingLocation.free_delivery_threshold) : editingLocation.free_delivery_threshold);
    
    const success = await updateDeliveryLocation(editingLocation.name, charge, threshold, editingLocation.state);
    if (success) {
      toast({
        title: "Success",
        description: "Location updated and saved successfully",
      });
      setEditingLocation(null);
    } else {
      toast({
        title: "Warning",
        description: "Location updated locally but may not have saved to server",
        variant: "default"
      });
      setEditingLocation(null);
    }
  };

  const handleDeleteLocation = (cityName) => {
    setDeleteLocationDialog({ isOpen: true, cityName });
  };

  const confirmDeleteLocation = async () => {
    try {
      await deleteDeliveryLocation(deleteLocationDialog.cityName);
      toast({
        title: "Success",
        description: "City deleted successfully",
      });
      setDeleteLocationDialog({ isOpen: false, cityName: '' });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete city",
        variant: "destructive"
      });
    }
  };

  // Discount Management Functions
  const handleAddDiscount = async (productId) => {
    const discount = discountData[productId];
    if (!discount || !discount.percentage || !discount.expiryDate) {
      toast({
        title: "Error",
        description: "Please fill in discount percentage and expiry date",
        variant: "destructive"
      });
      return;
    }

    if (discount.percentage < 0 || discount.percentage > 70) {
      toast({
        title: "Error",
        description: "Discount must be between 0% and 70%",
        variant: "destructive"
      });
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${BACKEND_URL}/api/admin/products/${productId}/discount`,
        {
          discount_percentage: discount.percentage,
          discount_expiry_date: new Date(discount.expiryDate).toISOString()
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      toast({
        title: "Success",
        description: "Discount added successfully",
      });

      // Reload products
      window.location.reload();
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to add discount",
        variant: "destructive"
      });
    }
  };

  const handleRemoveDiscount = async (productId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(
        `${BACKEND_URL}/api/admin/products/${productId}/discount`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      toast({
        title: "Success",
        description: "Discount removed successfully",
      });

      // Reload products
      window.location.reload();
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to remove discount",
        variant: "destructive"
      });
    }
  };

  const handleDiscountChange = (productId, field, value) => {
    setDiscountData(prev => ({
      ...prev,
      [productId]: {
        ...prev[productId],
        [field]: value
      }
    }));
  };

  // Best Seller Management Functions
  const handleToggleBestSeller = (productId) => {
    setSelectedBestSellers(prev => {
      if (prev.includes(productId)) {
        return prev.filter(id => id !== productId);
      } else {
        return [...prev, productId];
      }
    });
  };

  const handleSaveBestSellers = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${BACKEND_URL}/api/admin/best-sellers`,
        { product_ids: selectedBestSellers },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      toast({
        title: "Success",
        description: "Best sellers updated successfully",
      });

      // Reload products
      window.location.reload();
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to update best sellers",
        variant: "destructive"
      });
    }
  };

  // Festival Products Management Functions
  const handleToggleFestivalProduct = (productId) => {
    setSelectedFestivalProducts(prev => {
      if (prev.includes(productId)) {
        return prev.filter(id => id !== productId);
      } else {
        return [...prev, productId];
      }
    });
  };

  const handleSaveFestivalProducts = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${BACKEND_URL}/api/admin/festival-products`,
        { product_ids: selectedFestivalProducts },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      toast({
        title: "Success",
        description: "Festival products updated successfully",
      });

      // Reload products
      window.location.reload();
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to update festival products",
        variant: "destructive"
      });
    }
  };

  // States Management Functions
  const handleAddState = async () => {
    if (!newState.name.trim()) {
      toast({
        title: "Error",
        description: "Please enter state name",
        variant: "destructive"
      });
      return;
    }
    try {
      await addState(newState.name);
      toast({
        title: "Success",
        description: "State added successfully",
      });
      setShowAddState(false);
      setNewState({ name: '', enabled: true });
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to add state",
        variant: "destructive"
      });
    }
  };

  const handleToggleState = async (stateName, enabled) => {
    try {
      await updateState(stateName, enabled);
      toast({
        title: "Success",
        description: `State ${enabled ? 'enabled' : 'disabled'} successfully`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update state",
        variant: "destructive"
      });
    }
  };

  const handleDeleteState = (stateName) => {
    setDeleteStateDialog({ isOpen: true, stateName });
  };

  const confirmDeleteState = async () => {
    try {
      await deleteState(deleteStateDialog.stateName);
      toast({
        title: "Success",
        description: "State deleted successfully",
      });
      setDeleteStateDialog({ isOpen: false, stateName: '' });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete state",
        variant: "destructive"
      });
    }
  };

  // Read tab from URL query parameter on mount and when location changes
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const tabParam = searchParams.get('tab');
    const sectionParam = searchParams.get('section');
    
    if (tabParam) {
      // Validate tab parameter against allowed tabs
      const allowedTabs = ['products', 'orders', 'analytics', 'bestsellers', 'festival', 'discounts', 'settings', 'reports', 'profile', 'delivery', 'payment-settings', 'whatsapp'];
      if (allowedTabs.includes(tabParam)) {
        setActiveTab(tabParam);
        
        // Auto-scroll to section after tab is set
        if (sectionParam) {
          setTimeout(() => {
            const sectionElement = document.getElementById(sectionParam);
            if (sectionElement) {
              sectionElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
              // Add highlight effect
              sectionElement.classList.add('ring-4', 'ring-orange-400', 'ring-opacity-50');
              setTimeout(() => {
                sectionElement.classList.remove('ring-4', 'ring-orange-400', 'ring-opacity-50');
              }, 3000);
            }
          }, 300);
        }
      }
    }
  }, [location.search]);

  // Load selected best sellers on mount
  React.useEffect(() => {
    const bestSellerIds = products.filter(p => p.isBestSeller).map(p => p.id);
    setSelectedBestSellers(bestSellerIds);
  }, [products]);

  // Load selected festival products on mount
  React.useEffect(() => {
    const festivalIds = products.filter(p => p.isFestival).map(p => p.id);
    setSelectedFestivalProducts(festivalIds);
  }, [products]);

  // Fetch bug reports
  const fetchBugReports = async () => {
    setReportsLoading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/reports`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setBugReports(data);
      } else {
        throw new Error('Failed to fetch reports');
      }
    } catch (error) {
      console.error('Error fetching reports:', error);
      toast({
        title: "Error",
        description: "Failed to fetch bug reports",
        variant: "destructive"
      });
    } finally {
      setReportsLoading(false);
    }
  };

  // Update report status
  const updateReportStatus = async (reportId, status) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/reports/${reportId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ status })
      });
      
      if (response.ok) {
        toast({
          title: "Success",
          description: "Report status updated successfully"
        });
        fetchBugReports();
      } else {
        throw new Error('Failed to update status');
      }
    } catch (error) {
      console.error('Error updating status:', error);
      toast({
        title: "Error",
        description: "Failed to update report status",
        variant: "destructive"
      });
    }
  };

  // Handle delete report
  const handleDeleteReport = (reportId, email, index) => {
    setDeleteReportDialog({ isOpen: true, reportId, reportEmail: email, reportIndex: index + 1 });
  };

  // Confirm delete report
  const confirmDeleteReport = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/reports/${deleteReportDialog.reportId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        toast({
          title: "Success",
          description: "Report deleted successfully"
        });
        fetchBugReports();
        setDeleteReportDialog({ isOpen: false, reportId: null, reportEmail: '', reportIndex: 0 });
      } else {
        throw new Error('Failed to delete report');
      }
    } catch (error) {
      console.error('Error deleting report:', error);
      toast({
        title: "Error",
        description: "Failed to delete report",
        variant: "destructive"
      });
    }
  };

  // Fetch admin profile
  const fetchAdminProfile = async () => {
    setProfileLoading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/profile`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      // Get logged-in user email from localStorage
      let loggedInEmail = 'admin@ananthalakshmi.com'; // default
      try {
        const user = localStorage.getItem('user');
        if (user) {
          const userData = JSON.parse(user);
          if (userData.email) {
            loggedInEmail = userData.email;
          }
        }
      } catch (e) {
        console.error('Error parsing user data:', e);
      }
      
      if (response.ok) {
        const data = await response.json();
        // Use logged-in email if no email in profile
        const profileEmail = data.email || loggedInEmail;
        setAdminProfile({
          mobile: data.mobile || '',
          email: profileEmail
        });
        // Pre-fill OTP email with profile email
        setOtpEmail(profileEmail);
      } else {
        // If profile doesn't exist, use logged-in email
        setAdminProfile({
          mobile: '',
          email: loggedInEmail
        });
        setOtpEmail(loggedInEmail);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      // Fallback to logged-in email on error
      let loggedInEmail = 'admin@ananthalakshmi.com';
      try {
        const user = localStorage.getItem('user');
        if (user) {
          const userData = JSON.parse(user);
          if (userData.email) {
            loggedInEmail = userData.email;
          }
        }
      } catch (e) {}
      setAdminProfile({ mobile: '', email: loggedInEmail });
      setOtpEmail(loggedInEmail);
    } finally {
      setProfileLoading(false);
    }
  };

  // Update admin profile
  const updateAdminProfile = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(adminProfile)
      });
      
      if (response.ok) {
        toast({
          title: "Success",
          description: "Profile updated successfully"
        });
      } else {
        throw new Error('Failed to update profile');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      toast({
        title: "Error",
        description: "Failed to update profile",
        variant: "destructive"
      });
    }
  };

  // Send OTP for password change
  const sendOTP = async () => {
    if (!otpEmail) {
      toast({
        title: "Error",
        description: "Please enter your email address",
        variant: "destructive"
      });
      return;
    }
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/profile/send-otp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ email: otpEmail })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setOtpSent(true);
        toast({
          title: "OTP Sent",
          description: data.message || `OTP sent to ${otpEmail}`,
          duration: 5000
        });
      } else {
        throw new Error(data.detail || 'Failed to send OTP');
      }
    } catch (error) {
      console.error('Error sending OTP:', error);
      toast({
        title: "Error",
        description: error.message || "Failed to send OTP",
        variant: "destructive"
      });
    }
  };

  // Verify OTP and change password
  const verifyOTPAndChangePassword = async () => {
    if (!otpCode || !newPassword || !confirmPassword) {
      toast({
        title: "Error",
        description: "Please fill all fields",
        variant: "destructive"
      });
      return;
    }
    
    if (newPassword !== confirmPassword) {
      toast({
        title: "Error",
        description: "Passwords do not match",
        variant: "destructive"
      });
      return;
    }
    
    if (newPassword.length < 6) {
      toast({
        title: "Error",
        description: "Password must be at least 6 characters",
        variant: "destructive"
      });
      return;
    }
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/profile/verify-otp-change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          email: otpEmail,
          otp: otpCode,
          new_password: newPassword
        })
      });
      
      // Parse response once
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to change password');
      }
      
      toast({
        title: "Success",
        description: data.message || "Password changed successfully! Please login again.",
        duration: 7000
      });
      
      // Reset form
      setOtpEmail('');
      setOtpCode('');
      setNewPassword('');
      setConfirmPassword('');
      setOtpSent(false);
      
      // Logout after 3 seconds
      setTimeout(() => {
        handleLogout();
      }, 3000);
    } catch (error) {
      console.error('Error changing password:', error);
      toast({
        title: "Error",
        description: error.message || "Failed to change password",
        variant: "destructive"
      });
    }
  };

  // Fetch payment settings
  const fetchPaymentSettings = async () => {
    try {
      const adminToken = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/admin/payment-settings`, {
        headers: { Authorization: `Bearer ${adminToken}` }
      });
      setPaymentStatus(response.data.status || 'enabled');
    } catch (error) {
      console.error('Failed to fetch payment settings:', error);
    }
  };

  // Update payment settings
  const handlePaymentStatusChange = async (status) => {
    try {
      const adminToken = localStorage.getItem('token');
      await axios.put(`${BACKEND_URL}/api/admin/payment-settings?status=${status}`, {}, {
        headers: { Authorization: `Bearer ${adminToken}` }
      });
      setPaymentStatus(status);
      setPaymentStatusSaved(true);
      setTimeout(() => setPaymentStatusSaved(false), 3000);
      toast({
        title: "Success",
        description: "Payment settings updated successfully"
      });
    } catch (error) {
      console.error('Failed to update payment settings:', error);
      toast({
        title: "Error",
        description: formatErrorMessage(error) || "Failed to update payment settings",
        variant: "destructive"
      });
    }
  };

  // Fetch WhatsApp numbers
  const fetchWhatsAppNumbers = async () => {
    try {
      const adminToken = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/admin/whatsapp-numbers`, {
        headers: { Authorization: `Bearer ${adminToken}` }
      });
      setWhatsappNumbers(response.data || []);
    } catch (error) {
      console.error('Failed to fetch WhatsApp numbers:', error);
    }
  };

  // Add or update WhatsApp number
  const handleSaveWhatsApp = async () => {
    try {
      const adminToken = localStorage.getItem('token');
      
      if (editingWhatsApp) {
        // Update existing number
        await axios.put(`${BACKEND_URL}/api/admin/whatsapp-numbers/${editingWhatsApp.id}`, whatsappForm, {
          headers: { Authorization: `Bearer ${adminToken}` }
        });
        toast({
          title: "Success",
          description: "WhatsApp number updated successfully"
        });
      } else {
        // Add new number
        await axios.post(`${BACKEND_URL}/api/admin/whatsapp-numbers`, whatsappForm, {
          headers: { Authorization: `Bearer ${adminToken}` }
        });
        toast({
          title: "Success",
          description: "WhatsApp number added successfully"
        });
      }
      
      setShowAddWhatsApp(false);
      setEditingWhatsApp(null);
      setWhatsappForm({ phone: '', name: '' });
      fetchWhatsAppNumbers();
    } catch (error) {
      console.error('Failed to save WhatsApp number:', error);
      toast({
        title: "Error",
        description: formatErrorMessage(error) || "Failed to save WhatsApp number",
        variant: "destructive"
      });
    }
  };

  // Edit WhatsApp number
  const handleEditWhatsApp = (number) => {
    setEditingWhatsApp(number);
    setWhatsappForm({ phone: number.phone, name: number.name });
    setShowAddWhatsApp(true);
  };

  // Delete WhatsApp number
  const handleDeleteWhatsApp = async (numberId) => {
    if (!window.confirm('Are you sure you want to delete this WhatsApp number?')) return;
    
    try {
      const adminToken = localStorage.getItem('token');
      await axios.delete(`${BACKEND_URL}/api/admin/whatsapp-numbers/${numberId}`, {
        headers: { Authorization: `Bearer ${adminToken}` }
      });
      toast({
        title: "Success",
        description: "WhatsApp number deleted successfully"
      });
      fetchWhatsAppNumbers();
    } catch (error) {
      console.error('Failed to delete WhatsApp number:', error);
      toast({
        title: "Error",
        description: formatErrorMessage(error) || "Failed to delete WhatsApp number",
        variant: "destructive"
      });
    }
  };

  // Fetch reports when reports tab is accessed
  React.useEffect(() => {
    if (activeTab === 'reports' && isAuthenticated) {
      fetchBugReports();
    }
  }, [activeTab, isAuthenticated]);

  // Fetch profile when profile tab is accessed
  React.useEffect(() => {
    if (activeTab === 'profile' && isAuthenticated) {
      fetchAdminProfile();
    }
  }, [activeTab, isAuthenticated]);

  // Fetch states when delivery tab is accessed
  React.useEffect(() => {
    if (activeTab === 'delivery' && isAuthenticated) {
      fetchStates();
    }
  }, [activeTab, isAuthenticated]);

  // Fetch payment settings when payment-settings tab is accessed
  React.useEffect(() => {
    if (activeTab === 'payment-settings' && isAuthenticated) {
      fetchPaymentSettings();
    }
  }, [activeTab, isAuthenticated]);

  // Fetch WhatsApp numbers when whatsapp tab is accessed
  React.useEffect(() => {
    if (activeTab === 'whatsapp' && isAuthenticated) {
      fetchWhatsAppNumbers();
    }
  }, [activeTab, isAuthenticated]);

  // REMOVED: Free delivery settings functions - functionality moved to Cities & States tab
  // const fetchFreeDeliverySettings = async () => { ... }
  // const handleSaveFreeDeliverySettings = async () => { ... }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full">
          <div className="text-center mb-6">
            <LogIn className="h-12 w-12 text-orange-600 mx-auto mb-4" />
            <h1 className="text-3xl font-bold text-gray-800">Admin Login</h1>
            <p className="text-gray-600 mt-2">Enter your credentials to access admin panel</p>
          </div>
          <form onSubmit={handleLogin}>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter admin email"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 mb-4"
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter admin password"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 mb-4"
            />
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 rounded-lg font-semibold hover:from-orange-600 hover:to-red-600 transition-all"
            >
              Login
            </button>
          </form>
          <p className="text-sm text-gray-500 mt-4 text-center">Default: admin@ananthalakshmi.com / admin123</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                Admin Panel
              </h1>
              <p className="text-gray-600">Manage your products and orders</p>
            </div>
            <button
              onClick={logout}
              className="flex items-center space-x-2 bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors"
            >
              <LogOut className="h-5 w-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-2xl shadow-lg mb-6">
          <div className="flex border-b overflow-x-auto">
            <button
              onClick={() => setActiveTab('products')}
              className={`flex-1 py-4 px-2 font-semibold transition-colors whitespace-nowrap ${
                activeTab === 'products'
                  ? 'border-b-2 border-orange-500 text-orange-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Products
            </button>
            <button
              onClick={() => setActiveTab('festival')}
              className={`flex-1 py-4 px-2 font-semibold transition-colors flex items-center justify-center space-x-1 whitespace-nowrap ${
                activeTab === 'festival'
                  ? 'border-b-2 border-orange-500 text-orange-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <Sparkles className="h-4 w-4" />
              <span>Festival Special</span>
            </button>
            <button
              onClick={() => setActiveTab('bestseller')}
              className={`flex-1 py-4 px-2 font-semibold transition-colors flex items-center justify-center space-x-1 whitespace-nowrap ${
                activeTab === 'bestseller'
                  ? 'border-b-2 border-orange-500 text-orange-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <TrendingUp className="h-4 w-4" />
              <span>Best Selling</span>
            </button>
            <button
              onClick={() => setActiveTab('orders')}
              className={`flex-1 py-4 px-2 font-semibold transition-colors whitespace-nowrap ${
                activeTab === 'orders'
                  ? 'border-b-2 border-orange-500 text-orange-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Orders
            </button>
            <button
              onClick={() => setActiveTab('delivery')}
              className={`flex-1 py-4 px-2 font-semibold transition-colors whitespace-nowrap ${
                activeTab === 'delivery'
                  ? 'border-b-2 border-orange-500 text-orange-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Cities & States
            </button>
            <button
              onClick={() => setActiveTab('reports')}
              className={`flex-1 py-4 px-2 font-semibold transition-colors whitespace-nowrap ${
                activeTab === 'reports'
                  ? 'border-b-2 border-orange-500 text-orange-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Reports
            </button>
            <button
              onClick={() => setActiveTab('profile')}
              className={`flex-1 py-4 px-2 font-semibold transition-colors whitespace-nowrap ${
                activeTab === 'profile'
                  ? 'border-b-2 border-orange-500 text-orange-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Profile
            </button>
            <button
              onClick={() => setActiveTab('payment-settings')}
              className={`flex-1 py-4 px-2 font-semibold transition-colors whitespace-nowrap ${
                activeTab === 'payment-settings'
                  ? 'border-b-2 border-orange-500 text-orange-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Payment
            </button>
            <button
              onClick={() => setActiveTab('whatsapp')}
              className={`flex-1 py-4 px-2 font-semibold transition-colors whitespace-nowrap ${
                activeTab === 'whatsapp'
                  ? 'border-b-2 border-orange-500 text-orange-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              WhatsApp
            </button>
          </div>

          {/* Products Tab */}
          {activeTab === 'products' && (
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Manage Products</h2>
                <button
                  type="button"
                  onClick={() => setShowAddProduct(true)}
                  className="flex items-center space-x-2 bg-gradient-to-r from-green-600 to-green-700 text-white px-4 py-2 rounded-lg hover:from-green-700 hover:to-green-800 transition-all"
                >
                  <PlusCircle className="h-5 w-5" />
                  <span>Add Product</span>
                </button>
              </div>

              {/* Search Bar */}
              <div className="mb-4">
                <div className="relative">
                  <input
                    type="text"
                    value={productSearch}
                    onChange={(e) => setProductSearch(e.target.value)}
                    placeholder="Search products by name..."
                    className="w-full px-4 py-3 pl-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-sm"
                  />
                  <Search className="absolute left-3 top-3.5 h-4 w-4 text-gray-400" />
                </div>
              </div>

              {/* Product Filters */}
              <div className="mb-6 bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Category Filter */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                    <select
                      value={productCategoryFilter}
                      onChange={(e) => setProductCategoryFilter(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    >
                      <option value="all">All Categories</option>
                      {categories.map(cat => (
                        <option key={cat.id} value={cat.id}>{cat.name}</option>
                      ))}
                    </select>
                  </div>

                  {/* State Filter */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">State</label>
                    <select
                      value={productStateFilter}
                      onChange={(e) => {
                        setProductStateFilter(e.target.value);
                        setProductCityFilter('all');
                      }}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    >
                      <option value="all">All States</option>
                      {[...new Set(deliveryLocations.map(l => l.state))].sort().map(state => (
                        <option key={state} value={state}>{state}</option>
                      ))}
                    </select>
                  </div>

                  {/* City Filter */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">City</label>
                    <select
                      value={productCityFilter}
                      onChange={(e) => setProductCityFilter(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    >
                      <option value="all">All Cities</option>
                      {[...new Set(
                        deliveryLocations
                          .filter(loc => productStateFilter === 'all' || loc.state === productStateFilter)
                          .map(loc => loc.name)
                      )].sort().map(cityName => (
                        <option key={cityName} value={cityName}>{cityName}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {realProducts
                  .filter(product => {
                    // Search filter
                    if (productSearch && !product.name.toLowerCase().includes(productSearch.toLowerCase())) {
                      return false;
                    }
                    
                    // Category filter
                    if (productCategoryFilter !== 'all' && product.category !== productCategoryFilter) {
                      return false;
                    }
                    
                    // State/City filter for product availability
                    if (productCityFilter !== 'all') {
                      // If product has available_cities, check if selected city is in the list
                      if (product.available_cities && product.available_cities.length > 0) {
                        return product.available_cities.includes(productCityFilter);
                      }
                      // If no available_cities restriction, show it
                      return true;
                    }
                    
                    if (productStateFilter !== 'all' && productCityFilter === 'all') {
                      // Get all cities in the selected state
                      const stateCities = deliveryLocations
                        .filter(loc => loc.state === productStateFilter)
                        .map(loc => loc.name);
                      
                      // If product has available_cities, check if any city from selected state is in the list
                      if (product.available_cities && product.available_cities.length > 0) {
                        return product.available_cities.some(city => stateCities.includes(city));
                      }
                      // If no available_cities restriction, show it
                      return true;
                    }
                    
                    return true;
                  })
                  .map(product => (
                  <div key={product.id} className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow p-4 flex flex-col">
                    {/* Product Image */}
                    <div className="relative mb-3">
                      <img src={product.image} alt={product.name} className="w-full h-48 object-cover rounded-lg" />
                      {/* Discount Badge Overlay */}
                      {product.discount_active && product.discount_percentage > 0 && (
                        <div className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded-lg text-xs font-bold">
                          {product.discount_percentage}% OFF
                        </div>
                      )}
                      {/* Out of Stock Overlay */}
                      {product.out_of_stock && (
                        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
                          <span className="bg-gray-800 text-white px-3 py-1 rounded-lg text-sm font-bold">
                            OUT OF STOCK
                          </span>
                        </div>
                      )}
                    </div>
                    
                    {/* Product Name */}
                    <h3 className="font-bold text-gray-800 text-base mb-1 line-clamp-2">{product.name}</h3>
                    
                    {/* Category */}
                    <p className="text-xs text-gray-500 mb-2 capitalize">{product.category.replace('-', ' ')}</p>
                    
                    {/* Prices */}
                    {product.prices && product.prices.length > 0 && (
                      <div className="text-xs text-gray-600 mb-3 space-y-1">
                        {product.prices.map((p, idx) => (
                          <div key={idx} className="flex justify-between">
                            <span>{p.weight}</span>
                            <span className="font-semibold text-orange-600">₹{p.price}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {/* Badges */}
                    <div className="flex flex-wrap gap-1 mb-3">
                      {product.isBestSeller && (
                        <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded flex items-center gap-1">
                          <span className="text-yellow-500">⭐</span> Best Seller
                        </span>
                      )}
                      {product.isFestival && (
                        <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded flex items-center gap-1">
                          <span className="text-yellow-500">⭐</span> Festival
                        </span>
                      )}
                      {product.isNew && (
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">New</span>
                      )}
                      {product.inventory_count !== null && product.inventory_count !== undefined && (
                        <span className={`text-xs px-2 py-0.5 rounded font-semibold ${
                          product.inventory_count < 10 
                            ? 'bg-orange-100 text-orange-700' 
                            : 'bg-green-100 text-green-700'
                        }`}>
                          Stock: {product.inventory_count}
                        </span>
                      )}
                    </div>
                    
                    {/* Inventory Input */}
                    <div className="mb-3">
                      <label className="text-xs text-gray-600 block mb-1">Inventory</label>
                      <input
                        type="number"
                        min="0"
                        value={product.inventory_count ?? ''}
                        onChange={async (e) => {
                          const newCount = e.target.value === '' ? 0 : parseInt(e.target.value);
                          try {
                            const token = localStorage.getItem('token');
                            await axios.put(
                              `${BACKEND_URL}/api/admin/products/${product.id}/inventory`,
                              { inventory_count: newCount },
                              { headers: { Authorization: `Bearer ${token}` } }
                            );
                            toast({
                              title: "Success",
                              description: "Inventory updated"
                            });
                            window.location.reload();
                          } catch (error) {
                            toast({
                              title: "Error",
                              description: "Failed to update inventory",
                              variant: "destructive"
                            });
                          }
                        }}
                        placeholder="Stock"
                        className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
                      />
                    </div>
                    
                    {/* Action Buttons - Below Product */}
                    <div className="grid grid-cols-3 gap-2 mt-auto">
                      <button
                        type="button"
                        onClick={() => toggleProductFestival(product)}
                        className={`flex flex-col items-center justify-center p-2 rounded-lg transition-colors border ${
                          product.isFestival
                            ? 'bg-gradient-to-br from-yellow-100 to-orange-100 text-yellow-700 border-yellow-400 hover:from-yellow-200 hover:to-orange-200'
                            : 'bg-gray-50 text-gray-500 border-gray-200 hover:bg-gray-100'
                        }`}
                        title={product.isFestival ? "Remove from festival" : "Mark as festival"}
                      >
                        <Star className={`h-4 w-4 mb-1 ${product.isFestival ? 'fill-yellow-500 text-yellow-600' : ''}`} />
                        <span className="text-xs">Festival</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setEditingProduct({...product})}
                        className="flex flex-col items-center justify-center p-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors border border-blue-200"
                        title="Edit product"
                      >
                        <Edit className="h-4 w-4 mb-1" />
                        <span className="text-xs">Edit</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteProduct(product.id, product.name)}
                        className="flex flex-col items-center justify-center p-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors border border-red-200"
                        title="Delete product"
                      >
                        <Trash2 className="h-4 w-4 mb-1" />
                        <span className="text-xs">Delete</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Festival Special Tab */}
          {activeTab === 'festival' && (
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">Festival Special Products</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Total Festival Products: <span className="font-bold text-yellow-600">{products.filter(p => p.isFestival).length}</span>
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleSaveFestivalProducts}
                  className="flex items-center space-x-2 bg-gradient-to-r from-yellow-600 to-orange-600 text-white px-4 py-2 rounded-lg hover:from-yellow-700 hover:to-orange-700 transition-all"
                >
                  <Save className="h-5 w-5" />
                  <span>Save Changes</span>
                </button>
              </div>
              
              <p className="text-gray-600 mb-4">Manage festival special products - only showing products marked as festival</p>
              
              {products.filter(p => p.isFestival).length === 0 ? (
                <div className="text-center py-16 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                  <Sparkles className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">No Festival Products Yet</h3>
                  <p className="text-gray-500 mb-4">Mark products as festival using the star icon in the Products tab</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {products.filter(p => p.isFestival).map(product => (
                  <div 
                    key={product.id} 
                    className={`rounded-lg p-4 flex items-center space-x-4 border-2 transition-all cursor-pointer ${
                      selectedFestivalProducts.includes(product.id)
                        ? 'bg-gradient-to-br from-orange-50 to-yellow-50 border-orange-400'
                        : 'bg-white border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleToggleFestivalProduct(product.id)}
                  >
                    <input
                      type="checkbox"
                      checked={selectedFestivalProducts.includes(product.id)}
                      onChange={() => handleToggleFestivalProduct(product.id)}
                      className="h-5 w-5 text-orange-600 rounded focus:ring-orange-500 cursor-pointer"
                      onClick={(e) => e.stopPropagation()}
                    />
                    <img src={product.image} alt={product.name} className="w-20 h-20 object-cover rounded-lg" />
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        {selectedFestivalProducts.includes(product.id) && (
                          <span className="text-yellow-500 text-xl">⭐</span>
                        )}
                        <Sparkles className={`h-4 w-4 ${selectedFestivalProducts.includes(product.id) ? 'text-orange-600' : 'text-gray-400'}`} />
                        <h3 className="font-bold text-gray-800">{product.name}</h3>
                      </div>
                      <p className="text-sm text-gray-600 line-clamp-1">{product.description}</p>
                      <p className="text-sm font-bold text-orange-600 mt-1">
                        {product.prices && product.prices.length > 0 ? `₹${product.prices[0].price}` : 'Price not set'}
                      </p>
                    </div>
                    {selectedFestivalProducts.includes(product.id) && (
                      <div className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-3 py-1 rounded-full text-xs font-bold">
                        FESTIVAL
                      </div>
                    )}
                  </div>
                ))}
                </div>
              )}
            </div>
          )}

          {/* Best Selling Tab */}
          {activeTab === 'bestseller' && (
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Best Selling Products</h2>
                <button
                  type="button"
                  onClick={handleSaveBestSellers}
                  className="flex items-center space-x-2 bg-gradient-to-r from-orange-600 to-red-600 text-white px-4 py-2 rounded-lg hover:from-orange-700 hover:to-red-700 transition-all"
                >
                  <Save className="h-5 w-5" />
                  <span>Save Changes</span>
                </button>
              </div>
              
              <p className="text-gray-600 mb-4">Select products to mark as best sellers</p>
              
              <div className="grid gap-4">
                {products.map(product => (
                  <div 
                    key={product.id} 
                    className={`rounded-lg p-4 flex items-center space-x-4 border-2 transition-all cursor-pointer ${
                      selectedBestSellers.includes(product.id)
                        ? 'bg-gradient-to-br from-orange-50 to-red-50 border-orange-400'
                        : 'bg-white border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleToggleBestSeller(product.id)}
                  >
                    <input
                      type="checkbox"
                      checked={selectedBestSellers.includes(product.id)}
                      onChange={() => handleToggleBestSeller(product.id)}
                      className="w-5 h-5 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                    />
                    <img src={product.image} alt={product.name} className="w-20 h-20 object-cover rounded-lg" />
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        {selectedBestSellers.includes(product.id) && <TrendingUp className="h-4 w-4 text-orange-600" />}
                        <h3 className="font-bold text-gray-800">{product.name}</h3>
                      </div>
                      <p className="text-sm text-gray-600">{product.description}</p>
                      <p className="text-sm font-bold text-orange-600 mt-1">₹{product.prices[0].price}</p>
                    </div>
                  </div>
                ))}
                {products.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <TrendingUp className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                    <p>No products available</p>
                    <p className="text-sm mt-1">Add products first to mark them as best sellers</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Discounts Tab - REMOVED: Discount management now in product edit modal */}
          {activeTab === 'discounts' && null}

          {/* Inventory Tab - REMOVED: Inventory management now in product edit modal */}
          {activeTab === 'inventory' && null}

          {/* KEEP OLD TABS BELOW FOR BACKWARD COMPATIBILITY BUT DONT RENDER */}
          {false && activeTab === 'discounts' && (
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Discount Management</h2>
                <p className="text-sm text-gray-600">Max discount: 70%</p>
              </div>
              
              <p className="text-gray-600 mb-4">Add discounts to products with expiry dates</p>
              
              {realProducts.length === 0 && (
                <div className="text-center py-12 bg-yellow-50 border-2 border-yellow-200 rounded-lg">
                  <Percent className="h-12 w-12 mx-auto mb-3 text-yellow-600" />
                  <p className="text-gray-800 font-semibold mb-2">No products available for discount management</p>
                  <p className="text-sm text-gray-600">Please add products from the Products tab first.</p>
                  <p className="text-xs text-gray-500 mt-2">Note: Demo/mock products cannot have discounts applied.</p>
                </div>
              )}
              
              <div className="grid gap-4">
                {realProducts.map(product => {
                  const hasDiscount = product.discount_percentage && product.discount_expiry_date;
                  const isExpired = hasDiscount && new Date(product.discount_expiry_date) < new Date();
                  
                  return (
                    <div 
                      key={product.id} 
                      className={`rounded-lg p-4 border-2 ${
                        hasDiscount && !isExpired
                          ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-300'
                          : 'bg-white border-gray-200'
                      }`}
                    >
                      <div className="flex items-start space-x-4">
                        <img src={product.image} alt={product.name} className="w-20 h-20 object-cover rounded-lg" />
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="font-bold text-gray-800">{product.name}</h3>
                            {hasDiscount && !isExpired && (
                              <span className="bg-green-500 text-white px-2 py-1 rounded text-sm font-bold">
                                {product.discount_percentage}% OFF
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{product.description}</p>
                          <p className="text-sm font-bold text-orange-600">₹{product.prices[0].price}</p>
                          
                          {hasDiscount && !isExpired && (
                            <div className="mt-2 text-sm text-gray-600">
                              <p>Expires: {new Date(product.discount_expiry_date).toLocaleDateString()}</p>
                            </div>
                          )}
                          
                          {editingDiscount === product.id ? (
                            <div className="mt-4 space-y-3">
                              <div className="grid grid-cols-2 gap-3">
                                <div>
                                  <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Discount % (Max 70%)
                                  </label>
                                  <input
                                    type="number"
                                    min="0"
                                    max="70"
                                    value={discountData[product.id]?.percentage || ''}
                                    onChange={(e) => handleDiscountChange(product.id, 'percentage', parseFloat(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                                    placeholder="0-70"
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Expiry Date
                                  </label>
                                  <input
                                    type="date"
                                    min={new Date().toISOString().split('T')[0]}
                                    value={discountData[product.id]?.expiryDate || ''}
                                    onChange={(e) => handleDiscountChange(product.id, 'expiryDate', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                                  />
                                </div>
                              </div>
                              <div className="flex space-x-2">
                                <button
                                  type="button"
                                  onClick={() => handleAddDiscount(product.id)}
                                  className="flex items-center space-x-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-all"
                                >
                                  <Save className="h-4 w-4" />
                                  <span>Save</span>
                                </button>
                                <button
                                  type="button"
                                  onClick={() => setEditingDiscount(null)}
                                  className="flex items-center space-x-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition-all"
                                >
                                  <X className="h-4 w-4" />
                                  <span>Cancel</span>
                                </button>
                              </div>
                            </div>
                          ) : (
                            <div className="mt-3 flex space-x-2">
                              <button
                                type="button"
                                onClick={() => {
                                  setEditingDiscount(product.id);
                                  setDiscountData(prev => ({
                                    ...prev,
                                    [product.id]: {
                                      percentage: product.discount_percentage || 0,
                                      expiryDate: product.discount_expiry_date ? product.discount_expiry_date.split('T')[0] : ''
                                    }
                                  }));
                                }}
                                className="flex items-center space-x-1 bg-blue-100 text-blue-700 px-3 py-1 rounded-lg hover:bg-blue-200 transition-colors text-sm"
                              >
                                <Edit className="h-4 w-4" />
                                <span>{hasDiscount ? 'Edit' : 'Add'} Discount</span>
                              </button>
                              {hasDiscount && (
                                <button
                                  type="button"
                                  onClick={() => handleRemoveDiscount(product.id)}
                                  className="flex items-center space-x-1 bg-red-100 text-red-700 px-3 py-1 rounded-lg hover:bg-red-200 transition-colors text-sm"
                                >
                                  <Trash2 className="h-4 w-4" />
                                  <span>Remove</span>
                                </button>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
                {products.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <Percent className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                    <p>No products available</p>
                    <p className="text-sm mt-1">Add products first to manage discounts</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {false && activeTab === 'inventory' && (
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Inventory Management</h2>
                <p className="text-sm text-gray-600">Manage stock levels and availability</p>
              </div>
              
              {realProducts.length === 0 && (
                <div className="text-center py-12 bg-yellow-50 border-2 border-yellow-200 rounded-lg">
                  <Archive className="h-12 w-12 mx-auto mb-3 text-yellow-600" />
                  <p className="text-gray-800 font-semibold mb-2">No products available for inventory management</p>
                  <p className="text-sm text-gray-600">Please add products from the Products tab first.</p>
                  <p className="text-xs text-gray-500 mt-2">Note: Demo/mock products cannot have inventory settings applied.</p>
                </div>
              )}
              
              <div className="space-y-3">
                {realProducts.map(product => {
                  const inventoryCount = product.inventory_count ?? null;
                  const outOfStock = product.out_of_stock || false;
                  
                  return (
                    <div key={product.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 flex-1">
                          <img 
                            src={product.image} 
                            alt={product.name} 
                            className="w-16 h-16 object-cover rounded-lg"
                          />
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-800">{product.name}</h3>
                            <p className="text-sm text-gray-600">{product.category}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                          {/* Inventory Count Input */}
                          <div className="flex flex-col">
                            <label className="text-xs text-gray-600 mb-1">Inventory Limit</label>
                            <input
                              type="number"
                              min="0"
                              value={inventoryCount ?? ''}
                              onChange={async (e) => {
                                const newCount = e.target.value === '' ? null : parseInt(e.target.value);
                                try {
                                  const token = localStorage.getItem('token');
                                  await axios.put(
                                    `${BACKEND_URL}/api/admin/products/${product.id}/inventory`,
                                    { inventory_count: newCount ?? 0 },
                                    { headers: { Authorization: `Bearer ${token}` } }
                                  );
                                  toast({
                                    title: "Success",
                                    description: "Inventory updated"
                                  });
                                  window.location.reload();
                                } catch (error) {
                                  console.error('Inventory update error:', error);
                                  toast({
                                    title: "Error",
                                    description: error.response?.data?.detail || "Failed to update inventory",
                                    variant: "destructive"
                                  });
                                }
                              }}
                              placeholder="No limit"
                              className="w-24 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                            />
                            <span className="text-xs text-gray-500 mt-1">
                              {inventoryCount !== null ? `${inventoryCount} units` : 'Unlimited'}
                            </span>
                          </div>

                          {/* Out of Stock Toggle */}
                          <div className="flex flex-col items-center">
                            <label className="text-xs text-gray-600 mb-2">Out of Stock</label>
                            <button
                              onClick={async () => {
                                try {
                                  const token = localStorage.getItem('token');
                                  await axios.put(
                                    `${BACKEND_URL}/api/admin/products/${product.id}/stock-status`,
                                    { out_of_stock: !outOfStock },
                                    { headers: { Authorization: `Bearer ${token}` } }
                                  );
                                  toast({
                                    title: "Success",
                                    description: outOfStock ? "Product marked as available" : "Product marked as out of stock"
                                  });
                                  window.location.reload();
                                } catch (error) {
                                  console.error('Stock status error:', error);
                                  toast({
                                    title: "Error",
                                    description: error.response?.data?.detail || "Failed to update stock status",
                                    variant: "destructive"
                                  });
                                }
                              }}
                              className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 ${
                                outOfStock ? 'bg-red-600' : 'bg-green-600'
                              }`}
                            >
                              <span
                                className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                                  outOfStock ? 'translate-x-7' : 'translate-x-1'
                                }`}
                              />
                            </button>
                            <span className={`text-xs font-medium mt-1 ${outOfStock ? 'text-red-600' : 'text-green-600'}`}>
                              {outOfStock ? 'Out of Stock' : 'In Stock'}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Orders Tab */}
          {activeTab === 'orders' && (
            <div id="orders" className="p-6 transition-all duration-300 rounded-lg">
              <AdminOrders />
            </div>
          )}

          {/* Delivery Tab (Cities & States Combined) */}
          {activeTab === 'delivery' && (
            <div className="p-6">
              {/* Cities Section */}
              <div className="mb-8">
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800">Delivery Cities & Charges</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      {stateFilter ? (
                        <>
                          Showing <span className="font-bold text-orange-600">{deliveryLocations.filter(location => location.state === stateFilter && (!citySearchEdit || location.name.toLowerCase().includes(citySearchEdit.toLowerCase()))).length}</span> cities in {stateFilter}
                        </>
                      ) : (
                        <>
                          Total Cities: <span className="font-bold text-orange-600">{deliveryLocations.filter(location => !citySearchEdit || location.name.toLowerCase().includes(citySearchEdit.toLowerCase())).length}</span>
                          {citySearchEdit && <span> (filtered from {deliveryLocations.length})</span>}
                        </>
                      )}
                    </p>
                  </div>
                  <button
                    onClick={() => setShowAddLocation(true)}
                    className="flex items-center space-x-2 bg-gradient-to-r from-green-600 to-green-700 text-white px-4 py-2 rounded-lg hover:from-green-700 hover:to-green-800 transition-all"
                  >
                    <PlusCircle className="h-5 w-5" />
                    <span>Add City</span>
                  </button>
                </div>
                
                {/* Filters */}
                <div className="mb-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* State Filter */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Filter by State</label>
                    <select
                      value={stateFilter}
                      onChange={(e) => setStateFilter(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">All States</option>
                      {states && states.length > 0 && states.map(state => (
                        <option key={state.name} value={state.name}>{state.name}</option>
                      ))}
                    </select>
                  </div>

                  {/* Search Field */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Search Cities</label>
                    <div className="relative">
                      <input
                        type="text"
                        value={citySearchEdit}
                        onChange={(e) => setCitySearchEdit(e.target.value)}
                        placeholder="Search by city name..."
                        className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    </div>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {Array.isArray(deliveryLocations) && deliveryLocations
                    .filter(location => !stateFilter || location.state === stateFilter)
                    .filter(location => !citySearchEdit || location.name.toLowerCase().includes(citySearchEdit.toLowerCase()))
                    .map((location, index) => (
                    <div key={`${location.state || 'unknown'}-${location.name}-${index}`} className="bg-gray-50 rounded-lg p-4 flex items-center justify-between">
                      <div className="flex items-center space-x-3 flex-1">
                        <MapPin className="h-5 w-5 text-orange-600" />
                        <div className="flex-1">
                          <span className="font-semibold text-gray-800 block">
                            {location.name}{location.state ? `, ${location.state}` : ''}
                          </span>
                          <span className="text-sm font-bold text-orange-600">₹{location.charge}</span>
                          {location.free_delivery_threshold && (
                            <span className="text-xs text-green-600 block mt-1">
                              🎁 Free above ₹{location.free_delivery_threshold}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {
                            console.log('📝 Editing location:', location);
                            setEditingLocation({
                              name: location.name,
                              charge: location.charge || 0,
                              state: location.state || 'Andhra Pradesh',
                              free_delivery_threshold: location.free_delivery_threshold || null
                            });
                          }}
                          className="p-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                          title="Edit delivery charge"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteLocation(location.name)}
                          className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                          title="Delete city"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* States Section */}
              <div className="border-t pt-8">
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800">Available States</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      Total States: <span className="font-bold text-blue-600">{states && states.length > 0 ? states.length : 0}</span>
                    </p>
                  </div>
                  <button
                    onClick={() => setShowAddState(true)}
                    className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-2 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all"
                  >
                    <PlusCircle className="h-5 w-5" />
                    <span>Add State</span>
                  </button>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Array.isArray(states) && states.length > 0 ? states.map(state => (
                    <div key={state.name} className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3 flex-1">
                          <MapPin className="h-5 w-5 text-blue-600" />
                          <span className="font-bold text-gray-800">{state.name}</span>
                        </div>
                        <button
                          onClick={() => handleDeleteState(state.name)}
                          className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                          title="Delete state"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Delivery Available:</span>
                        <button
                          onClick={() => handleToggleState(state.name, !state.enabled)}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                            state.enabled ? 'bg-green-600' : 'bg-gray-300'
                          }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              state.enabled ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </div>
                      <p className="text-xs text-gray-500 mt-2">
                        {state.enabled ? 'Currently accepting orders from this state' : 'Delivery not available in this state'}
                      </p>
                    </div>
                  )) : (
                    <div className="col-span-full text-center py-8 text-gray-500">
                      <MapPin className="h-12 w-12 mx-auto mb-3 opacity-50" />
                      <p className="font-semibold">No states available yet</p>
                      <p className="text-sm mt-2">Click "Add State" to add a new state for delivery</p>
                    </div>
                  )}
                </div>
              </div>

              {/* City Suggestions Section (from homepage form) */}
              <div id="city-suggestions" className="border-t pt-8 transition-all duration-300 rounded-lg">
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800">📍 City Suggestions from Customers</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      New cities suggested by customers through the "Suggest a City" form on homepage
                    </p>
                  </div>
                </div>
                <CitySuggestionsSection fetchDeliveryLocations={fetchDeliveryLocations} />
              </div>
            </div>
          )}

          {/* Settings Tab - REMOVED: Functionality moved to Cities & States tab */}
          {false && activeTab === 'settings' && (
            <div className="p-6">
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Delivery Settings</h2>
                <p className="text-gray-600 text-sm">Configure free delivery threshold and manage city delivery charges</p>
              </div>

              {/* Free Delivery Settings */}
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200 mb-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <Truck className="h-8 w-8 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Free Delivery Threshold</h3>
                    
                    <div className="space-y-4">
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={freeDeliveryEnabled}
                          onChange={(e) => setFreeDeliveryEnabled(e.target.checked)}
                          className="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500"
                        />
                        <label className="text-gray-700 font-medium">Enable Free Delivery</label>
                      </div>

                      {freeDeliveryEnabled && (
                        <div>
                          <label className="block text-gray-700 font-medium mb-2">
                            Minimum Order Amount for Free Delivery (₹)
                          </label>
                          <input
                            type="number"
                            value={freeDeliveryThreshold}
                            onChange={(e) => setFreeDeliveryThreshold(e.target.value)}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                            placeholder="e.g., 1000"
                            min="0"
                          />
                          <p className="text-sm text-gray-600 mt-2">
                            Customers will get free delivery when their order total is ₹{freeDeliveryThreshold} or above
                          </p>
                        </div>
                      )}

                      <button
                        onClick={handleSaveFreeDeliverySettings}
                        className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all font-semibold shadow-md"
                      >
                        Save Free Delivery Settings
                      </button>
                    </div>

                    {!freeDeliveryEnabled && (
                      <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <p className="text-sm text-yellow-800">
                          <strong>Note:</strong> Free delivery is currently disabled. Enable it to offer free delivery on orders above a certain amount.
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* City-Specific Free Delivery Toggle */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200 mb-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">City-Specific Free Delivery</h3>
                    <p className="text-sm text-gray-600">
                      When enabled, cities can have their own free delivery thresholds. When disabled, global threshold applies to all cities.
                    </p>
                  </div>
                  <div className="flex-shrink-0 ml-6">
                    <button
                      onClick={() => setCitySpecificFreeDeliveryEnabled(!citySpecificFreeDeliveryEnabled)}
                      className={`relative inline-flex h-8 w-16 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                        citySpecificFreeDeliveryEnabled ? 'bg-green-600' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                          citySpecificFreeDeliveryEnabled ? 'translate-x-9' : 'translate-x-1'
                        }`}
                      />
                    </button>
                    <p className="text-sm font-semibold mt-2 text-center">
                      {citySpecificFreeDeliveryEnabled ? (
                        <span className="text-green-600">ON</span>
                      ) : (
                        <span className="text-gray-500">OFF</span>
                      )}
                    </p>
                  </div>
                </div>
                {!citySpecificFreeDeliveryEnabled && (
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      <strong>Note:</strong> City-specific thresholds are disabled. All cities will use the global free delivery threshold set above.
                    </p>
                  </div>
                )}
              </div>

              {/* City Delivery Charges */}
              <div className={`bg-white rounded-xl p-6 border border-gray-200 ${!citySpecificFreeDeliveryEnabled ? 'opacity-60' : ''}`}>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800">City Delivery Charges & Free Delivery Thresholds</h3>
                    <p className="text-sm text-gray-600">
                      {citySpecificFreeDeliveryEnabled 
                        ? 'Manage delivery charges and city-specific free delivery thresholds' 
                        : 'Manage delivery charges (thresholds disabled - using global setting)'}
                    </p>
                  </div>
                  <div className="text-sm text-gray-600">
                    Total Cities: <span className="font-bold text-orange-600">{deliveryLocations.length}</span>
                  </div>
                </div>

                {/* Info Banner */}
                <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="h-5 w-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h4 className="text-sm font-semibold text-blue-800 mb-1">How City-Specific Free Delivery Works:</h4>
                      <ul className="text-sm text-blue-700 space-y-1">
                        <li>• Set different free delivery thresholds for different cities based on their delivery costs</li>
                        <li>• Example: Guntur (₹49 delivery) → Free above ₹1000 | Hyderabad (₹149 delivery) → Free above ₹2000</li>
                        <li>• If not set, the global threshold (above) will be used for that city</li>
                        <li>• Customers will see city-specific free delivery message during checkout</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Group cities by state */}
                <div className="space-y-6">
                  {['Andhra Pradesh', 'Telangana'].map((stateName) => {
                    const stateCities = deliveryLocations.filter(loc => loc.state === stateName);
                    
                    if (stateCities.length === 0) return null;
                    
                    return (
                      <div key={stateName} className="border border-gray-200 rounded-lg overflow-hidden">
                        <div className="bg-gradient-to-r from-orange-100 to-red-100 px-4 py-3 border-b border-gray-200">
                          <h4 className="font-semibold text-gray-800 flex items-center justify-between">
                            <span>{stateName}</span>
                            <span className="text-sm text-gray-600">{stateCities.length} cities</span>
                          </h4>
                        </div>
                        
                        <div className="max-h-96 overflow-y-auto">
                          <table className="w-full">
                            <thead className="bg-gray-50 sticky top-0">
                              <tr>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">City Name</th>
                                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Delivery Charge (₹)</th>
                                {citySpecificFreeDeliveryEnabled && (
                                  <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Free Delivery Above (₹)</th>
                                )}
                                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Actions</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                              {stateCities.map((location, index) => (
                                <tr key={`${location.state || selectedStateTab}-${location.name}-${index}`} className="hover:bg-gray-50">
                                  <td className="px-4 py-3 text-gray-800 font-medium">{location.name}</td>
                                  <td className="px-4 py-3 text-right">
                                    {editingLocation === location.name ? (
                                      <input
                                        type="number"
                                        value={location.charge}
                                        onChange={(e) => {
                                          const updatedLocations = deliveryLocations.map(loc =>
                                            loc.name === location.name ? { ...loc, charge: parseInt(e.target.value) || 0 } : loc
                                          );
                                          setDeliveryLocations(updatedLocations);
                                        }}
                                        className="w-24 px-2 py-1 border border-gray-300 rounded text-right"
                                        min="0"
                                      />
                                    ) : (
                                      <span className="font-semibold text-orange-600">₹{location.charge}</span>
                                    )}
                                  </td>
                                  {citySpecificFreeDeliveryEnabled && (
                                    <td className="px-4 py-3 text-right">
                                      {editingLocation === location.name ? (
                                        <input
                                          type="number"
                                          value={location.free_delivery_threshold || ''}
                                          onChange={(e) => {
                                            const value = e.target.value;
                                            const updatedLocations = deliveryLocations.map(loc =>
                                              loc.name === location.name ? { ...loc, free_delivery_threshold: value === '' ? null : parseInt(value) || null } : loc
                                            );
                                            setDeliveryLocations(updatedLocations);
                                          }}
                                          className="w-24 px-2 py-1 border border-gray-300 rounded text-right"
                                          placeholder="Optional"
                                          min="0"
                                        />
                                      ) : (
                                        <span className="text-gray-700">
                                          {location.free_delivery_threshold ? (
                                            <span className="font-semibold text-green-600">₹{location.free_delivery_threshold}</span>
                                          ) : (
                                            <span className="text-gray-400 text-xs">Not set</span>
                                          )}
                                        </span>
                                      )}
                                    </td>
                                  )}
                                  <td className="px-4 py-3 text-center">
                                    {editingLocation === location.name ? (
                                      <div className="flex items-center justify-center space-x-2">
                                        <button
                                          onClick={() => {
                                            updateDeliveryLocation(location.name, location.charge, location.free_delivery_threshold);
                                            setEditingLocation(null);
                                          }}
                                          className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                                        >
                                          Save
                                        </button>
                                        <button
                                          onClick={() => {
                                            setEditingLocation(null);
                                            fetchProducts(); // Refresh to reset values
                                          }}
                                          className="px-3 py-1 bg-gray-300 text-gray-700 rounded text-sm hover:bg-gray-400"
                                        >
                                          Cancel
                                        </button>
                                      </div>
                                    ) : (
                                      <button
                                        onClick={() => setEditingLocation(location.name)}
                                        className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                                      >
                                        Edit
                                      </button>
                                    )}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {deliveryLocations.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <MapPin className="h-12 w-12 mx-auto mb-3 opacity-50" />
                    <p>No cities configured yet. Add cities from the "Cities & States" tab.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Reports Tab */}
          {activeTab === 'reports' && (
            <div id="reports" className="p-6 transition-all duration-300 rounded-lg">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Bug Reports</h2>
                <button
                  onClick={fetchBugReports}
                  className="flex items-center space-x-2 bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Refresh</span>
                </button>
              </div>

              {reportsLoading ? (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
                  <p className="mt-4 text-gray-600">Loading reports...</p>
                </div>
              ) : bugReports.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 rounded-lg">
                  <div className="text-6xl mb-4">📋</div>
                  <p className="text-gray-600 text-lg">No bug reports yet</p>
                  <p className="text-gray-500 text-sm mt-2">Reports submitted by users will appear here</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full bg-white rounded-lg overflow-hidden shadow">
                    <thead className="bg-gradient-to-r from-orange-500 to-red-500 text-white">
                      <tr>
                        <th className="px-4 py-3 text-left">Sr No</th>
                        <th className="px-4 py-3 text-left">Date</th>
                        <th className="px-4 py-3 text-left">Email</th>
                        <th className="px-4 py-3 text-left">Mobile</th>
                        <th className="px-4 py-3 text-left">Issue</th>
                        <th className="px-4 py-3 text-left">Photo</th>
                        <th className="px-4 py-3 text-left">Status</th>
                        <th className="px-4 py-3 text-left">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {bugReports.map((report, index) => (
                        <tr key={report.id} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                          <td className="px-4 py-3 text-sm font-semibold text-gray-700">
                            #{index + 1}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {new Date(report.created_at).toLocaleDateString('en-IN', { 
                              day: '2-digit', 
                              month: 'short', 
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <a href={`mailto:${report.email}`} className="text-blue-600 hover:underline">
                              {report.email}
                            </a>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <a href={`tel:${report.mobile}`} className="text-blue-600 hover:underline">
                              {report.mobile}
                            </a>
                          </td>
                          <td className="px-4 py-3 text-sm max-w-md">
                            <div className="line-clamp-3" title={report.issue_description}>
                              {report.issue_description}
                            </div>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {report.photo_url ? (
                              <a 
                                href={report.photo_url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:underline"
                              >
                                View Photo
                              </a>
                            ) : (
                              <span className="text-gray-400">No photo</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <select
                              value={report.status}
                              onChange={(e) => updateReportStatus(report.id, e.target.value)}
                              className={`px-3 py-1 rounded-full text-xs font-semibold ${
                                report.status === 'New' 
                                  ? 'bg-blue-100 text-blue-800' 
                                  : report.status === 'In Progress'
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-green-100 text-green-800'
                              }`}
                            >
                              <option value="New">New</option>
                              <option value="In Progress">In Progress</option>
                              <option value="Resolved">Resolved</option>
                            </select>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <button
                              onClick={() => handleDeleteReport(report.id, report.email, index)}
                              className="text-red-600 hover:text-red-800 font-semibold"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="p-6 max-w-4xl mx-auto">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Admin Profile</h2>

              {profileLoading ? (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
                  <p className="mt-4 text-gray-600">Loading profile...</p>
                </div>
              ) : (
                <div className="space-y-8">
                  {/* Profile Information */}
                  <div className="bg-white rounded-xl shadow-lg p-6">
                    <h3 className="text-xl font-semibold text-gray-800 mb-4">Profile Information</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Mobile Number
                        </label>
                        <input
                          type="tel"
                          value={adminProfile.mobile}
                          onChange={(e) => setAdminProfile({...adminProfile, mobile: e.target.value})}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                          placeholder="Enter mobile number"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Email Address
                        </label>
                        <input
                          type="email"
                          value={adminProfile.email}
                          onChange={(e) => setAdminProfile({...adminProfile, email: e.target.value})}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                          placeholder="Enter email address"
                        />
                      </div>
                      <button
                        onClick={updateAdminProfile}
                        className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 rounded-lg font-semibold hover:from-orange-600 hover:to-red-600 transition"
                      >
                        Update Profile
                      </button>
                    </div>
                  </div>

                  {/* Change Password */}
                  <div className="bg-white rounded-xl shadow-lg p-6">
                    <h3 className="text-xl font-semibold text-gray-800 mb-4">Change Password</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Email for OTP
                        </label>
                        <div className="flex flex-col sm:flex-row gap-2">
                          <input
                            type="email"
                            value={otpEmail}
                            onChange={(e) => setOtpEmail(e.target.value)}
                            disabled={otpSent}
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:bg-gray-100"
                            placeholder="Enter your email"
                          />
                          <button
                            onClick={sendOTP}
                            disabled={otpSent}
                            className="w-full sm:w-auto px-6 py-2 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition whitespace-nowrap"
                          >
                            {otpSent ? 'OTP Sent' : 'Send OTP'}
                          </button>
                        </div>
                        {otpSent && (
                          <p className="text-sm text-green-600 mt-1 break-words">
                            ✓ OTP sent to {otpEmail}. Please check your email.
                          </p>
                        )}
                      </div>

                      {otpSent && (
                        <>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Enter OTP
                            </label>
                            <input
                              type="text"
                              value={otpCode}
                              onChange={(e) => setOtpCode(e.target.value)}
                              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                              placeholder="Enter 6-digit OTP"
                              maxLength="6"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              New Password
                            </label>
                            <input
                              type="password"
                              value={newPassword}
                              onChange={(e) => setNewPassword(e.target.value)}
                              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                              placeholder="Enter new password"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Confirm Password
                            </label>
                            <input
                              type="password"
                              value={confirmPassword}
                              onChange={(e) => setConfirmPassword(e.target.value)}
                              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                              placeholder="Confirm new password"
                            />
                          </div>
                          <button
                            onClick={verifyOTPAndChangePassword}
                            className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white py-3 rounded-lg font-semibold hover:from-green-600 hover:to-green-700 transition"
                          >
                            Verify OTP & Change Password
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Payment Settings Tab */}
          {activeTab === 'payment-settings' && (
            <div className="p-6 max-w-4xl mx-auto">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Payment Settings</h2>
              
              {/* Razorpay API Keys section removed */}
              
              {/* Payment Gateway Control */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">Payment Gateway Control</h3>
                <p className="text-sm text-gray-600 mb-6">
                  Control how customers can pay for their orders. All orders will still be sent to WhatsApp regardless of payment status.
                </p>
                
                <div className="space-y-4">
                  <label className="flex items-start space-x-3 p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors border-green-500 bg-green-50">
                    <input
                      type="radio"
                      name="payment-status"
                      value="enabled"
                      checked={paymentStatus === 'enabled'}
                      onChange={(e) => handlePaymentStatusChange(e.target.value)}
                      className="mt-1 h-5 w-5 text-green-600"
                    />
                    <div className="flex-1">
                      <span className="font-semibold text-gray-800 block">Enable Payment</span>
                      <span className="text-sm text-gray-600">Customers can pay online using Razorpay (UPI, Cards, Net Banking, Wallets). Orders also sent to WhatsApp.</span>
                    </div>
                  </label>
                  
                  <label className="flex items-start space-x-3 p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors border-yellow-500 bg-yellow-50">
                    <input
                      type="radio"
                      name="payment-status"
                      value="disabled"
                      checked={paymentStatus === 'disabled'}
                      onChange={(e) => handlePaymentStatusChange(e.target.value)}
                      className="mt-1 h-5 w-5 text-yellow-600"
                    />
                    <div className="flex-1">
                      <span className="font-semibold text-gray-800 block">Disable Payment (Coming Soon Message)</span>
                      <span className="text-sm text-gray-600">Show "Payment Coming Soon" message. Orders still created and sent to WhatsApp.</span>
                    </div>
                  </label>
                  
                  <label className="flex items-start space-x-3 p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors border-red-500 bg-red-50">
                    <input
                      type="radio"
                      name="payment-status"
                      value="removed"
                      checked={paymentStatus === 'removed'}
                      onChange={(e) => handlePaymentStatusChange(e.target.value)}
                      className="mt-1 h-5 w-5 text-red-600"
                    />
                    <div className="flex-1">
                      <span className="font-semibold text-gray-800 block">Remove Payment Section</span>
                      <span className="text-sm text-gray-600">Completely hide payment section from checkout. Orders sent directly to WhatsApp.</span>
                    </div>
                  </label>
                </div>
                
                {paymentStatusSaved && (
                  <div className="mt-4 p-4 bg-green-100 text-green-800 rounded-lg">
                    ✓ Payment settings saved successfully!
                  </div>
                )}
              </div>
            </div>
          )}

          {/* WhatsApp Numbers Tab */}
          {activeTab === 'whatsapp' && (
            <div className="p-6 max-w-6xl mx-auto">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">WhatsApp Numbers</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Add up to 5 WhatsApp numbers to receive order notifications
                  </p>
                </div>
                <button
                  onClick={() => setShowAddWhatsApp(true)}
                  disabled={whatsappNumbers.length >= 5}
                  className="flex items-center space-x-2 bg-gradient-to-r from-green-600 to-green-700 text-white px-4 py-2 rounded-lg hover:from-green-700 hover:to-green-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <PlusCircle className="h-5 w-5" />
                  <span>Add Number</span>
                </button>
              </div>

              {whatsappNumbers.length === 0 ? (
                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-8 text-center">
                  <div className="text-yellow-600 mb-4">
                    <svg className="h-16 w-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">No WhatsApp Numbers Added</h3>
                  <p className="text-gray-600 mb-4">
                    Add WhatsApp numbers to receive order notifications from customers
                  </p>
                  <button
                    onClick={() => setShowAddWhatsApp(true)}
                    className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Add Your First Number
                  </button>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {whatsappNumbers.map((number) => (
                    <div key={number.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-800 text-lg">{number.name}</h3>
                          <p className="text-green-600 font-mono text-sm mt-1">{number.phone}</p>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleEditWhatsApp(number)}
                            className="p-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                            title="Edit"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteWhatsApp(number.id)}
                            className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500">
                        Added: {new Date(number.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {whatsappNumbers.length > 0 && whatsappNumbers.length < 5 && (
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg text-center text-sm text-blue-700">
                  You can add {5 - whatsappNumbers.length} more number{5 - whatsappNumbers.length !== 1 ? 's' : ''}
                </div>
              )}
            </div>
          )}

          {/* States Tab - REMOVED: Combined with Cities */}
          {false && activeTab === 'states' && (
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">States Management</h2>
                <button
                  onClick={() => setShowAddState(true)}
                  className="flex items-center space-x-2 bg-gradient-to-r from-green-600 to-green-700 text-white px-4 py-2 rounded-lg hover:from-green-700 hover:to-green-800 transition-all"
                >
                  <PlusCircle className="h-5 w-5" />
                  <span>Add State</span>
                </button>
              </div>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Array.isArray(states) && states.map(state => (
                  <div key={state.name} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3 flex-1">
                        <MapPin className="h-5 w-5 text-orange-600" />
                        <span className="font-semibold text-gray-800">{state.name}</span>
                      </div>
                      <button
                        onClick={() => handleDeleteState(state.name)}
                        className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                        title="Delete state"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Delivery Available:</span>
                      <button
                        onClick={() => handleToggleState(state.name, !state.enabled)}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 ${
                          state.enabled ? 'bg-green-600' : 'bg-gray-300'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            state.enabled ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      {state.enabled ? 'Currently accepting orders' : 'Delivery not available'}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmDialog
        isOpen={deleteDialog.isOpen}
        onClose={() => setDeleteDialog({ isOpen: false, productId: null, productName: '' })}
        onConfirm={confirmDelete}
        title="Delete Product"
        message={`Are you sure you want to delete "${deleteDialog.productName}"? This action cannot be undone.`}
      />

      {/* Edit Location Modal */}
      {editingLocation && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-2xl font-bold text-gray-800">Edit City Details</h3>
              <button onClick={() => setEditingLocation(null)}>
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">City Name</label>
                <input
                  type="text"
                  value={editingLocation.name || ''}
                  disabled
                  className="w-full px-4 py-2 border rounded-lg bg-gray-100 text-gray-800 font-semibold"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">State</label>
                <select
                  value={editingLocation.state || 'Andhra Pradesh'}
                  onChange={(e) => setEditingLocation({...editingLocation, state: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg"
                >
                  <option value="Andhra Pradesh">Andhra Pradesh</option>
                  <option value="Telangana">Telangana</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Delivery Charge: <span className="text-orange-600 font-bold">₹{editingLocation.charge || 0}</span>
                </label>
                <label className="block text-sm font-medium text-gray-700 mb-2 mt-3">New Delivery Charge (₹)</label>
                <input
                  type="number"
                  value={editingLocation.charge === 0 ? '0' : (editingLocation.charge || '')}
                  onChange={(e) => {
                    const value = e.target.value;
                    // Keep as string during editing, convert only when saving
                    setEditingLocation({...editingLocation, charge: value === '' ? '' : (Number(value) || 0)});
                  }}
                  className="w-full px-4 py-2 border rounded-lg"
                  placeholder="Enter new charge"
                  min="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Free Delivery Threshold: {editingLocation.free_delivery_threshold ? (
                    <span className="text-green-600 font-bold">₹{editingLocation.free_delivery_threshold}</span>
                  ) : (
                    <span className="text-gray-400">Not set</span>
                  )}
                </label>
                <label className="block text-sm font-medium text-gray-700 mb-2 mt-3">New Free Delivery Above (₹)</label>
                <input
                  type="number"
                  value={editingLocation.free_delivery_threshold === 0 ? '0' : (editingLocation.free_delivery_threshold || '')}
                  onChange={(e) => {
                    const value = e.target.value;
                    // Keep as string/number during editing
                    setEditingLocation({
                      ...editingLocation, 
                      free_delivery_threshold: value === '' ? null : (Number(value) || null)
                    });
                  }}
                  className="w-full px-4 py-2 border rounded-lg"
                  placeholder="e.g., 1000 (optional)"
                  min="0"
                />
                <p className="text-xs text-gray-500 mt-1">Leave empty to use global threshold or no free delivery for this city</p>
              </div>
              <button
                onClick={handleUpdateLocation}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800"
              >
                Update City
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Location Modal */}
      {showAddLocation && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-2xl font-bold text-gray-800">Add New City</h3>
              <button onClick={() => setShowAddLocation(false)}>
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">City Name</label>
                <input
                  type="text"
                  value={newLocation.name}
                  onChange={(e) => setNewLocation({...newLocation, name: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg"
                  placeholder="Enter city name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">State</label>
                <select
                  value={newLocation.state}
                  onChange={(e) => setNewLocation({...newLocation, state: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg"
                >
                  {states && states.length > 0 ? (
                    states.map(state => (
                      <option key={state.name} value={state.name}>{state.name}</option>
                    ))
                  ) : (
                    <>
                      <option value="Andhra Pradesh">Andhra Pradesh</option>
                      <option value="Telangana">Telangana</option>
                    </>
                  )}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Delivery Charge (₹)</label>
                <input
                  type="number"
                  value={newLocation.charge}
                  onChange={(e) => setNewLocation({...newLocation, charge: parseInt(e.target.value) || 0})}
                  className="w-full px-4 py-2 border rounded-lg"
                  placeholder="Enter charge"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Free Delivery Above (₹)</label>
                <input
                  type="number"
                  value={newLocation.free_delivery_threshold || ''}
                  onChange={(e) => {
                    const value = e.target.value;
                    setNewLocation({
                      ...newLocation, 
                      free_delivery_threshold: value === '' ? null : parseInt(value) || null
                    });
                  }}
                  className="w-full px-4 py-2 border rounded-lg"
                  placeholder="e.g., 1000 (optional)"
                />
                <p className="text-xs text-gray-500 mt-1">Leave empty to use global threshold or no free delivery for this city</p>
              </div>
              <button
                onClick={handleAddLocation}
                className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800"
              >
                Add City
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Product Modal */}
      {editingProduct && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-2xl font-bold text-gray-800">Edit Product</h3>
              <button type="button" onClick={() => { setEditingProduct(null); setImageFile(null); }}>
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="space-y-4">
              {/* Language Options Section */}
              <div className="bg-gradient-to-r from-orange-50 to-amber-50 border-2 border-orange-200 rounded-xl p-4">
                <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                  <span className="text-orange-600 mr-2">🌐</span>
                  Multilingual Product Details (English & Telugu)
                </h4>
                
                {/* English Fields */}
                <div className="space-y-3 mb-4 p-3 bg-white rounded-lg border border-gray-200">
                  <label className="block text-sm font-medium text-gray-700">
                    <span className="inline-flex items-center">
                      <span className="mr-2">🇬🇧</span>
                      English Details
                    </span>
                  </label>
                  <input
                    type="text"
                    placeholder="Product Name (English)"
                    value={editingProduct.name}
                    onChange={(e) => setEditingProduct({...editingProduct, name: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                  <textarea
                    placeholder="Description (English)"
                    value={editingProduct.description}
                    onChange={(e) => setEditingProduct({...editingProduct, description: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    rows="3"
                  />
                </div>

                {/* Telugu Fields */}
                <div className="space-y-3 p-3 bg-white rounded-lg border border-gray-200">
                  <label className="block text-sm font-medium text-gray-700">
                    <span className="inline-flex items-center">
                      <span className="mr-2">🇮🇳</span>
                      Telugu Details (తెలుగు వివరాలు)
                    </span>
                  </label>
                  <input
                    type="text"
                    placeholder="Product Name (Telugu) - ఉత్పత్తి పేరు"
                    value={editingProduct.name_telugu || ''}
                    onChange={(e) => setEditingProduct({...editingProduct, name_telugu: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500"
                  />
                  <textarea
                    placeholder="Description (Telugu) - వివరణ"
                    value={editingProduct.description_telugu || ''}
                    onChange={(e) => setEditingProduct({...editingProduct, description_telugu: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500"
                    rows="3"
                  />
                </div>
              </div>

              <select
                value={editingProduct.category}
                onChange={(e) => setEditingProduct({...editingProduct, category: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg"
              >
                {categories.filter(c => c.id !== 'all').map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
              
              {/* Image Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Product Image</label>
                {editingProduct.image && (
                  <img src={editingProduct.image} alt="Preview" className="w-32 h-32 object-cover rounded-lg mb-2" />
                )}
                <div className="flex items-center space-x-2">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files[0];
                      if (file) {
                        setImageFile(file);
                        handleImageUpload(file, editingProduct, setEditingProduct);
                      }
                    }}
                    className="hidden"
                    id="edit-image-upload"
                  />
                  <label
                    htmlFor="edit-image-upload"
                    className="cursor-pointer flex items-center space-x-2 bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg transition-colors"
                  >
                    <Upload className="h-5 w-5" />
                    <span>{imageUploading ? 'Uploading...' : 'Upload New Image'}</span>
                  </label>
                </div>
              </div>
              
              {/* Discount Management Section */}
              <div className="border-t border-b py-4 space-y-3">
                <h4 className="font-semibold text-gray-800 flex items-center space-x-2">
                  <Percent className="h-5 w-5 text-orange-600" />
                  <span>Discount Settings</span>
                </h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Discount % (Max 70%)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="70"
                      value={editingProduct.discount_percentage || 0}
                      onChange={(e) => setEditingProduct({...editingProduct, discount_percentage: parseFloat(e.target.value) || 0})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                      placeholder="0-70"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Expiry Date
                    </label>
                    <input
                      type="date"
                      min={new Date().toISOString().split('T')[0]}
                      value={editingProduct.discount_expiry_date ? editingProduct.discount_expiry_date.split('T')[0] : ''}
                      onChange={(e) => setEditingProduct({...editingProduct, discount_expiry_date: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    />
                  </div>
                </div>
                {editingProduct.discount_percentage > 0 && editingProduct.prices && editingProduct.prices[0] && (
                  <p className="text-sm text-green-600">
                    Discounted Price: ₹{Math.round(editingProduct.prices[0].price * (1 - editingProduct.discount_percentage / 100))}
                  </p>
                )}
              </div>

              {/* Inventory Management Section */}
              <div className="border-b pb-4 space-y-3">
                <h4 className="font-semibold text-gray-800 flex items-center space-x-2">
                  <Archive className="h-5 w-5 text-orange-600" />
                  <span>Inventory Settings</span>
                </h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Inventory Count
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={editingProduct.inventory_count ?? ''}
                      onChange={(e) => setEditingProduct({...editingProduct, inventory_count: e.target.value === '' ? null : parseInt(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                      placeholder="Leave empty for unlimited"
                    />
                    <span className="text-xs text-gray-500 mt-1 block">
                      {editingProduct.inventory_count !== null && editingProduct.inventory_count !== undefined && editingProduct.inventory_count !== '' ? `${editingProduct.inventory_count} units available` : 'Unlimited stock'}
                    </span>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Stock Status
                    </label>
                    <label className="flex items-center space-x-2 cursor-pointer mt-2">
                      <input
                        type="checkbox"
                        checked={editingProduct.out_of_stock || false}
                        onChange={(e) => setEditingProduct({...editingProduct, out_of_stock: e.target.checked})}
                        className="rounded w-5 h-5 text-red-500"
                      />
                      <span className="text-sm font-medium">Mark as Out of Stock</span>
                    </label>
                  </div>
                </div>
              </div>
              
              {/* Price Options */}
              <div className="border-t pt-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-semibold text-gray-800">Price Options</h4>
                  <button
                    type="button"
                    onClick={() => addPriceOption(editingProduct, setEditingProduct)}
                    className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-lg hover:bg-blue-200"
                  >
                    + Add More
                  </button>
                </div>
                {editingProduct.prices.map((price, index) => (
                  <div key={index} className="flex flex-col md:flex-row md:space-x-2 space-y-2 md:space-y-0 mb-3">
                    <input
                      type="text"
                      placeholder="Weight (e.g., ¼ kg, 500g)"
                      value={price.weight}
                      onChange={(e) => updatePriceOption(editingProduct, setEditingProduct, index, 'weight', e.target.value)}
                      className="flex-1 px-3 py-2 border rounded-lg w-full"
                    />
                    <input
                      type="number"
                      placeholder="Price"
                      value={price.price}
                      onChange={(e) => updatePriceOption(editingProduct, setEditingProduct, index, 'price', e.target.value)}
                      className="flex-1 px-3 py-2 border rounded-lg w-full"
                    />
                    {editingProduct.prices.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removePriceOption(editingProduct, setEditingProduct, index)}
                        className="text-red-500 hover:text-red-700 px-2 py-2 md:py-0 self-center"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {/* City Availability Section */}
              <div className="border-t border-b py-4 space-y-3">
                <h4 className="font-semibold text-gray-800 flex items-center space-x-2">
                  <MapPin className="h-5 w-5 text-blue-600" />
                  <span>City Availability ({deliveryLocations.length} cities available)</span>
                </h4>
                <p className="text-sm text-gray-600">
                  Select cities where this product can be delivered. Leave empty to make available everywhere.
                </p>
                
                {/* Search Input */}
                <div className="relative">
                  <input
                    type="text"
                    placeholder="🔍 Search cities... (e.g., Guntur, Hyderabad)"
                    value={citySearchEdit}
                    onChange={(e) => setCitySearchEdit(e.target.value)}
                    className="w-full px-4 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  {citySearchEdit && (
                    <button
                      onClick={() => setCitySearchEdit('')}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </div>
                
                {/* Quick Actions */}
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      const allCities = deliveryLocations.map(loc => loc.name);
                      setEditingProduct({...editingProduct, available_cities: allCities});
                    }}
                    className="flex-1 px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 font-medium"
                  >
                    ✓ Select All
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditingProduct({...editingProduct, available_cities: []})}
                    className="flex-1 px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium"
                  >
                    ✗ Clear All
                  </button>
                </div>
                
                <div className="max-h-64 overflow-y-auto border rounded-lg p-3 bg-gray-50">
                  <label className="flex items-center space-x-2 cursor-pointer mb-2 p-2 hover:bg-white rounded sticky top-0 bg-green-50 border-b">
                    <input
                      type="checkbox"
                      checked={!editingProduct.available_cities || editingProduct.available_cities.length === 0}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setEditingProduct({...editingProduct, available_cities: []});
                        }
                      }}
                      className="rounded w-4 h-4 text-green-500"
                    />
                    <span className="text-sm font-semibold text-green-600">All Cities (No Restriction)</span>
                  </label>
                  {Array.isArray(deliveryLocations) && deliveryLocations
                    .filter(location => 
                      !citySearchEdit || 
                      location.name.toLowerCase().includes(citySearchEdit.toLowerCase()) ||
                      location.state.toLowerCase().includes(citySearchEdit.toLowerCase())
                    )
                    .map((location, index) => (
                    <label key={`${location.state}-${location.name}-${index}`} className="flex items-center space-x-2 cursor-pointer mb-1 p-2 hover:bg-white rounded">
                      <input
                        type="checkbox"
                        checked={editingProduct.available_cities && editingProduct.available_cities.includes(location.name)}
                        onChange={(e) => {
                          const currentCities = editingProduct.available_cities || [];
                          if (e.target.checked) {
                            setEditingProduct({
                              ...editingProduct,
                              available_cities: [...currentCities, location.name]
                            });
                          } else {
                            setEditingProduct({
                              ...editingProduct,
                              available_cities: currentCities.filter(c => c !== location.name)
                            });
                          }
                        }}
                        className="rounded w-4 h-4 text-blue-500"
                      />
                      <span className="text-sm">{location.name}, {location.state}</span>
                    </label>
                  ))}
                  {citySearchEdit && deliveryLocations.filter(location => 
                    location.name.toLowerCase().includes(citySearchEdit.toLowerCase()) ||
                    location.state.toLowerCase().includes(citySearchEdit.toLowerCase())
                  ).length === 0 && (
                    <p className="text-center text-gray-500 py-4">No cities found matching "{citySearchEdit}"</p>
                  )}
                </div>
                {editingProduct.available_cities && editingProduct.available_cities.length > 0 && (
                  <p className="text-sm text-blue-600 font-semibold">
                    ✓ Available in {editingProduct.available_cities.length} selected cities
                  </p>
                )}
              </div>

              {/* Best Seller & New Product Toggles */}
              <div className="flex space-x-4">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editingProduct.isBestSeller}
                    onChange={(e) => setEditingProduct({...editingProduct, isBestSeller: e.target.checked})}
                    className="rounded w-5 h-5 text-orange-500"
                  />
                  <span className="text-sm font-medium">Best Seller</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editingProduct.isNew}
                    onChange={(e) => setEditingProduct({...editingProduct, isNew: e.target.checked})}
                    className="rounded w-5 h-5 text-green-500"
                  />
                  <span className="text-sm font-medium">New Product</span>
                </label>
              </div>

              <input
                type="text"
                placeholder="Tag (e.g., Traditional, Healthy, Festival Special)"
                value={editingProduct.tag}
                onChange={(e) => setEditingProduct({...editingProduct, tag: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg"
              />

              <button
                type="button"
                onClick={() => handleUpdateProduct(editingProduct.id)}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800"
              >
                Update Product
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Product Modal */}
      {showAddProduct && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-2xl font-bold text-gray-800">Add New Product</h3>
              <button type="button" onClick={() => { setShowAddProduct(false); setImageFile(null); }}>
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="space-y-4">
              {/* Language Options Section */}
              <div className="bg-gradient-to-r from-orange-50 to-amber-50 border-2 border-orange-200 rounded-xl p-4">
                <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                  <span className="text-orange-600 mr-2">🌐</span>
                  Multilingual Product Details (English & Telugu)
                </h4>
                
                {/* English Fields */}
                <div className="space-y-3 mb-4 p-3 bg-white rounded-lg border border-gray-200">
                  <label className="block text-sm font-medium text-gray-700">
                    <span className="inline-flex items-center">
                      <span className="mr-2">🇬🇧</span>
                      English Details
                    </span>
                  </label>
                  <input
                    type="text"
                    placeholder="Product Name (English)"
                    value={newProduct.name}
                    onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                  <textarea
                    placeholder="Description (English)"
                    value={newProduct.description}
                    onChange={(e) => setNewProduct({...newProduct, description: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    rows="3"
                  />
                </div>

                {/* Telugu Fields */}
                <div className="space-y-3 p-3 bg-white rounded-lg border border-gray-200">
                  <label className="block text-sm font-medium text-gray-700">
                    <span className="inline-flex items-center">
                      <span className="mr-2">🇮🇳</span>
                      Telugu Details (తెలుగు వివరాలు)
                    </span>
                  </label>
                  <input
                    type="text"
                    placeholder="Product Name (Telugu) - ఉత్పత్తి పేరు"
                    value={newProduct.name_telugu || ''}
                    onChange={(e) => setNewProduct({...newProduct, name_telugu: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500"
                  />
                  <textarea
                    placeholder="Description (Telugu) - వివరణ"
                    value={newProduct.description_telugu || ''}
                    onChange={(e) => setNewProduct({...newProduct, description_telugu: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500"
                    rows="3"
                  />
                </div>
              </div>

              <select
                value={newProduct.category}
                onChange={(e) => setNewProduct({...newProduct, category: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg"
              >
                {categories.filter(c => c.id !== 'all').map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
              
              {/* Image Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Product Image *</label>
                {newProduct.image && (
                  <img src={newProduct.image} alt="Preview" className="w-32 h-32 object-cover rounded-lg mb-2" />
                )}
                <div className="flex items-center space-x-2">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files[0];
                      if (file) {
                        setImageFile(file);
                        handleImageUpload(file, newProduct, setNewProduct);
                      }
                    }}
                    className="hidden"
                    id="new-image-upload"
                  />
                  <label
                    htmlFor="new-image-upload"
                    className="cursor-pointer flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    <Upload className="h-5 w-5" />
                    <span>{imageUploading ? 'Uploading...' : 'Upload Image'}</span>
                  </label>
                </div>
              </div>

              {/* Discount Management Section */}
              <div className="border-t border-b py-4 space-y-3">
                <h4 className="font-semibold text-gray-800 flex items-center space-x-2">
                  <Percent className="h-5 w-5 text-orange-600" />
                  <span>Discount Settings</span>
                </h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Discount % (Max 70%)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="70"
                      value={newProduct.discount_percentage || 0}
                      onChange={(e) => setNewProduct({...newProduct, discount_percentage: parseFloat(e.target.value) || 0})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                      placeholder="0-70"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Expiry Date
                    </label>
                    <input
                      type="date"
                      min={new Date().toISOString().split('T')[0]}
                      value={newProduct.discount_expiry_date ? newProduct.discount_expiry_date.split('T')[0] : ''}
                      onChange={(e) => setNewProduct({...newProduct, discount_expiry_date: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    />
                  </div>
                </div>
                {newProduct.discount_percentage > 0 && newProduct.prices && newProduct.prices[0] && (
                  <p className="text-sm text-green-600">
                    Discounted Price: ₹{Math.round(newProduct.prices[0].price * (1 - newProduct.discount_percentage / 100))}
                  </p>
                )}
              </div>

              {/* Inventory Management Section */}
              <div className="border-b pb-4 space-y-3">
                <h4 className="font-semibold text-gray-800 flex items-center space-x-2">
                  <Archive className="h-5 w-5 text-orange-600" />
                  <span>Inventory Settings</span>
                </h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Inventory Count
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={newProduct.inventory_count ?? ''}
                      onChange={(e) => setNewProduct({...newProduct, inventory_count: e.target.value === '' ? null : parseInt(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                      placeholder="Leave empty for unlimited"
                    />
                    <span className="text-xs text-gray-500 mt-1 block">
                      {newProduct.inventory_count !== null && newProduct.inventory_count !== undefined && newProduct.inventory_count !== '' ? `${newProduct.inventory_count} units available` : 'Unlimited stock'}
                    </span>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Stock Status
                    </label>
                    <label className="flex items-center space-x-2 cursor-pointer mt-2">
                      <input
                        type="checkbox"
                        checked={newProduct.out_of_stock || false}
                        onChange={(e) => setNewProduct({...newProduct, out_of_stock: e.target.checked})}
                        className="rounded w-5 h-5 text-red-500"
                      />
                      <span className="text-sm font-medium">Mark as Out of Stock</span>
                    </label>
                  </div>
                </div>
              </div>
              
              {/* Price Options */}
              <div className="border-t pt-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-semibold text-gray-800">Price Options (like ¼ kg - ₹199)</h4>
                  <button
                    type="button"
                    onClick={() => addPriceOption(newProduct, setNewProduct)}
                    className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-lg hover:bg-blue-200"
                  >
                    + Add More
                  </button>
                </div>
                {newProduct.prices.map((price, index) => (
                  <div key={index} className="flex flex-col md:flex-row md:space-x-2 space-y-2 md:space-y-0 mb-3">
                    <input
                      type="text"
                      placeholder="Weight (e.g., ¼ kg, 500g)"
                      value={price.weight}
                      onChange={(e) => updatePriceOption(newProduct, setNewProduct, index, 'weight', e.target.value)}
                      className="flex-1 px-3 py-2 border rounded-lg w-full"
                    />
                    <input
                      type="number"
                      placeholder="Price (e.g., 199)"
                      value={price.price}
                      onChange={(e) => updatePriceOption(newProduct, setNewProduct, index, 'price', e.target.value)}
                      className="flex-1 px-3 py-2 border rounded-lg w-full"
                    />
                    {newProduct.prices.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removePriceOption(newProduct, setNewProduct, index)}
                        className="text-red-500 hover:text-red-700 px-2 py-2 md:py-0 self-center"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {/* City Availability Section */}
              <div className="border-t border-b py-4 space-y-3">
                <h4 className="font-semibold text-gray-800 flex items-center space-x-2">
                  <MapPin className="h-5 w-5 text-blue-600" />
                  <span>City Availability ({deliveryLocations.length} cities available)</span>
                </h4>
                <p className="text-sm text-gray-600">
                  Select cities where this product can be delivered. Leave empty to make available everywhere.
                </p>
                
                {/* Search Input */}
                <div className="relative">
                  <input
                    type="text"
                    placeholder="🔍 Search cities... (e.g., Guntur, Hyderabad)"
                    value={citySearchAdd}
                    onChange={(e) => setCitySearchAdd(e.target.value)}
                    className="w-full px-4 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  {citySearchAdd && (
                    <button
                      onClick={() => setCitySearchAdd('')}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </div>
                
                {/* Quick Actions */}
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      const allCities = deliveryLocations.map(loc => loc.name);
                      setNewProduct({...newProduct, available_cities: allCities});
                    }}
                    className="flex-1 px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 font-medium"
                  >
                    ✓ Select All
                  </button>
                  <button
                    type="button"
                    onClick={() => setNewProduct({...newProduct, available_cities: []})}
                    className="flex-1 px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium"
                  >
                    ✗ Clear All
                  </button>
                </div>
                
                <div className="max-h-64 overflow-y-auto border rounded-lg p-3 bg-gray-50">
                  <label className="flex items-center space-x-2 cursor-pointer mb-2 p-2 hover:bg-white rounded sticky top-0 bg-green-50 border-b">
                    <input
                      type="checkbox"
                      checked={!newProduct.available_cities || newProduct.available_cities.length === 0}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setNewProduct({...newProduct, available_cities: []});
                        }
                      }}
                      className="rounded w-4 h-4 text-green-500"
                    />
                    <span className="text-sm font-semibold text-green-600">All Cities (No Restriction)</span>
                  </label>
                  {Array.isArray(deliveryLocations) && deliveryLocations
                    .filter(location => 
                      !citySearchAdd || 
                      location.name.toLowerCase().includes(citySearchAdd.toLowerCase()) ||
                      location.state.toLowerCase().includes(citySearchAdd.toLowerCase())
                    )
                    .map((location, index) => (
                    <label key={`${location.state}-${location.name}-${index}`} className="flex items-center space-x-2 cursor-pointer mb-1 p-2 hover:bg-white rounded">
                      <input
                        type="checkbox"
                        checked={newProduct.available_cities && newProduct.available_cities.includes(location.name)}
                        onChange={(e) => {
                          const currentCities = newProduct.available_cities || [];
                          if (e.target.checked) {
                            setNewProduct({
                              ...newProduct,
                              available_cities: [...currentCities, location.name]
                            });
                          } else {
                            setNewProduct({
                              ...newProduct,
                              available_cities: currentCities.filter(c => c !== location.name)
                            });
                          }
                        }}
                        className="rounded w-4 h-4 text-blue-500"
                      />
                      <span className="text-sm">{location.name}, {location.state}</span>
                    </label>
                  ))}
                  {citySearchAdd && deliveryLocations.filter(location => 
                    location.name.toLowerCase().includes(citySearchAdd.toLowerCase()) ||
                    location.state.toLowerCase().includes(citySearchAdd.toLowerCase())
                  ).length === 0 && (
                    <p className="text-center text-gray-500 py-4">No cities found matching "{citySearchAdd}"</p>
                  )}
                </div>
                {newProduct.available_cities && newProduct.available_cities.length > 0 && (
                  <p className="text-sm text-blue-600 font-semibold">
                    ✓ Available in {newProduct.available_cities.length} selected cities
                  </p>
                )}
              </div>

              {/* Additional Options */}
              <div className="flex space-x-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={newProduct.isBestSeller}
                    onChange={(e) => setNewProduct({...newProduct, isBestSeller: e.target.checked})}
                    className="rounded"
                  />
                  <span className="text-sm">Best Seller</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={newProduct.isNew}
                    onChange={(e) => setNewProduct({...newProduct, isNew: e.target.checked})}
                    className="rounded"
                  />
                  <span className="text-sm">New Product</span>
                </label>
              </div>

              <input
                type="text"
                placeholder="Tag (e.g., Traditional, Healthy, Festival Special)"
                value={newProduct.tag}
                onChange={(e) => setNewProduct({...newProduct, tag: e.target.value})}
                className="w-full px-4 py-2 border rounded-lg"
              />

              <button
                type="button"
                onClick={handleAddProduct}
                disabled={imageUploading}
                className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {imageUploading ? 'Uploading Image...' : 'Add Product'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Location Dialog */}
      <DeleteConfirmDialog
        isOpen={deleteLocationDialog.isOpen}
        onClose={() => setDeleteLocationDialog({ isOpen: false, cityName: '' })}
        onConfirm={confirmDeleteLocation}
        title="Delete City"
        message={`Are you sure you want to delete "${deleteLocationDialog.cityName}"? This action cannot be undone.`}
      />

      {/* Delete State Dialog */}
      <DeleteConfirmDialog
        isOpen={deleteStateDialog.isOpen}
        onClose={() => setDeleteStateDialog({ isOpen: false, stateName: '' })}
        onConfirm={confirmDeleteState}
        title="Delete State"
        message={`Are you sure you want to delete "${deleteStateDialog.stateName}"? This action cannot be undone.`}
      />

      {/* Delete Report Dialog */}
      <DeleteConfirmDialog
        isOpen={deleteReportDialog.isOpen}
        onClose={() => setDeleteReportDialog({ isOpen: false, reportId: null, reportEmail: '', reportIndex: 0 })}
        onConfirm={confirmDeleteReport}
        title={`Delete Report #${deleteReportDialog.reportIndex}`}
        message={`Are you sure you want to delete report from "${deleteReportDialog.reportEmail}"? This action cannot be undone.`}
      />

      {/* Add State Modal */}
      {showAddState && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-2xl font-bold text-gray-800">Add New State</h3>
              <button onClick={() => setShowAddState(false)}>
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">State Name</label>
                <input
                  type="text"
                  value={newState.name}
                  onChange={(e) => setNewState({...newState, name: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg"
                  placeholder="Enter state name"
                />
                <p className="text-xs text-gray-500 mt-1">Enter the state name (e.g., Andhra Pradesh, Telangana, etc.)</p>
              </div>
              <button
                onClick={handleAddState}
                className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800"
              >
                Add State
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add/Edit WhatsApp Number Modal */}
      {showAddWhatsApp && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-2xl font-bold text-gray-800">
                {editingWhatsApp ? 'Edit WhatsApp Number' : 'Add WhatsApp Number'}
              </h3>
              <button onClick={() => {
                setShowAddWhatsApp(false);
                setEditingWhatsApp(null);
                setWhatsappForm({ phone: '', name: '' });
              }}>
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Name/Label</label>
                <input
                  type="text"
                  value={whatsappForm.name}
                  onChange={(e) => setWhatsappForm({...whatsappForm, name: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                  placeholder="Owner name or label (e.g., Main Owner, Store Manager)"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">WhatsApp Number</label>
                <div className="relative">
                  <span className="absolute left-4 top-2.5 text-gray-700 font-medium pointer-events-none">+91</span>
                  <input
                    type="tel"
                    value={whatsappForm.phone.startsWith('+91') ? whatsappForm.phone.slice(3) : whatsappForm.phone}
                    onChange={(e) => {
                      const value = e.target.value.replace(/[^0-9]/g, '');
                      setWhatsappForm({...whatsappForm, phone: '+91' + value});
                    }}
                    placeholder="9876543210"
                    maxLength="10"
                    className="w-full pl-14 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  This number will receive order notifications via WhatsApp.
                </p>
              </div>
              <button
                onClick={handleSaveWhatsApp}
                disabled={!whatsappForm.phone || !whatsappForm.name}
                className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {editingWhatsApp ? 'Update Number' : 'Add Number'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Admin;
