import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Truck, MapPin, CreditCard, Mail, Phone, Home, Building2, Navigation, Plus, Minus, Edit2, X, Sparkles } from 'lucide-react';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import { toast } from '../hooks/use-toast';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const Checkout = () => {
  const { cart, getCartTotal, clearCart, updateQuantity, removeFromCart } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchIdentifier, setSearchIdentifier] = useState('');
  const [searching, setSearching] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    doorNo: '',
    building: '',
    street: '',
    city: '',
    state: '',
    pincode: '',
    location: '',
    paymentMethod: 'online',
    paymentSubMethod: ''
  });
  const [errors, setErrors] = useState({});
  const [deliveryCharge, setDeliveryCharge] = useState(0);
  const [deliveryLocations, setDeliveryLocations] = useState([]);
  const [detectingLocation, setDetectingLocation] = useState(false);
  const [stateCities, setStateCities] = useState({
    "Andhra Pradesh": [],
    "Telangana": []
  });
  const [editingItemIndex, setEditingItemIndex] = useState(null);
  const [selectedWeight, setSelectedWeight] = useState('');
  const [allProducts, setAllProducts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [freeDeliverySettings, setFreeDeliverySettings] = useState({ enabled: false, threshold: 1000 });

  useEffect(() => {
    fetchDeliveryLocations();
    fetchAllProducts();
    fetchFreeDeliverySettings();
  }, []);

  const fetchFreeDeliverySettings = async () => {
    try {
      const response = await axios.get(`${API}/settings/free-delivery`);
      setFreeDeliverySettings(response.data);
    } catch (error) {
      console.error('Failed to fetch free delivery settings:', error);
    }
  };

  const fetchAllProducts = async () => {
    try {
      const response = await axios.get(`${API}/products`);
      setAllProducts(response.data);
      // Get best sellers for recommendations
      const bestSellers = response.data.filter(p => p.isBestSeller).slice(0, 4);
      setRecommendations(bestSellers);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    }
  };

  const fetchDeliveryLocations = async () => {
    try {
      const response = await axios.get(`${API}/locations`);
      const locations = response.data;
      setDeliveryLocations(locations);
      
      const apCities = [];
      const telCities = [];
      
      locations.forEach(loc => {
        const cityName = loc.name;
        const state = loc.state || "Andhra Pradesh";
        
        if (state === "Andhra Pradesh") {
          apCities.push(cityName);
        } else if (state === "Telangana") {
          telCities.push(cityName);
        }
      });
      
      setStateCities({
        "Andhra Pradesh": apCities.sort(),
        "Telangana": telCities.sort()
      });
    } catch (error) {
      console.error('Failed to fetch delivery locations:', error);
    }
  };

  const handleQuantityChange = (index, delta) => {
    const item = cart[index];
    const newQuantity = (item.quantity || 1) + delta;
    
    if (newQuantity < 1) {
      if (window.confirm(`Remove ${item.name} from cart?`)) {
        removeFromCart(item.id, item.weight || item.selectedWeight);
      }
      return;
    }
    
    updateQuantity(item.id, item.weight || item.selectedWeight, newQuantity);
  };

  const handleWeightEdit = (index) => {
    const item = cart[index];
    setEditingItemIndex(index);
    setSelectedWeight(item.weight || item.selectedWeight);
  };

  const handleWeightChange = (index) => {
    const item = cart[index];
    const weight = selectedWeight;
    
    // Find the new price for selected weight
    const product = allProducts.find(p => p.id === item.id);
    if (product) {
      const priceInfo = product.prices.find(p => p.weight === weight);
      if (priceInfo) {
        // Remove old item and add with new weight
        removeFromCart(item.id, item.weight || item.selectedWeight);
        
        // Update cart with new weight (this will be handled by CartContext)
        const updatedItem = {
          ...item,
          weight: weight,
          selectedWeight: weight,
          price: priceInfo.price,
          selectedPrice: priceInfo.price
        };
        
        // Add back with new weight
        toast({
          title: "Weight Updated",
          description: `Updated to ${weight} - ₹${priceInfo.price}`
        });
      }
    }
    
    setEditingItemIndex(null);
    setSelectedWeight('');
  };

  const calculateDeliveryCharge = () => {
    const subtotal = getCartTotal();
    
    // Check if free delivery is enabled and threshold is met
    if (freeDeliverySettings.enabled && subtotal >= freeDeliverySettings.threshold) {
      return 0;
    }
    
    return deliveryCharge;
  };

  const isFreeDeliveryApplicable = () => {
    const subtotal = getCartTotal();
    return freeDeliverySettings.enabled && subtotal >= freeDeliverySettings.threshold;
  };

  const getRemainingForFreeDelivery = () => {
    const subtotal = getCartTotal();
    return freeDeliverySettings.threshold - subtotal;
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) newErrors.email = 'Enter valid email address';
    if (!formData.phone.trim()) newErrors.phone = 'Phone number is required';
    else if (!/^\d{10}$/.test(formData.phone)) newErrors.phone = 'Enter valid 10-digit phone number';
    
    if (!formData.doorNo.trim()) newErrors.doorNo = 'Door number is required';
    if (!formData.building.trim()) newErrors.building = 'Building/House name is required';
    if (!formData.street.trim()) newErrors.street = 'Street/Area is required';
    if (!formData.state.trim()) newErrors.state = 'State is required';
    if (!formData.city.trim()) newErrors.city = 'City is required';
    if (!formData.pincode.trim()) newErrors.pincode = 'Pincode is required';
    else if (!/^\d{6}$/.test(formData.pincode)) newErrors.pincode = 'Enter valid 6-digit pincode';
    
    if (!formData.paymentMethod) newErrors.paymentMethod = 'Please select payment method';
    if (formData.paymentMethod && !formData.paymentSubMethod) {
      newErrors.paymentSubMethod = 'Please select payment option';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSearchUserDetails = async () => {
    if (!searchIdentifier.trim()) {
      toast({
        title: "Error",
        description: "Please enter phone number or email",
        variant: "destructive"
      });
      return;
    }

    setSearching(true);
    try {
      const response = await axios.get(`${API}/user-details/${searchIdentifier.trim()}`);
      
      if (response.data) {
        const details = response.data;
        const cityValue = details.city || formData.city;
        setFormData(prev => ({
          ...prev,
          name: details.customer_name || prev.name,
          email: details.email || prev.email,
          phone: details.phone || prev.phone,
          doorNo: details.doorNo || prev.doorNo,
          building: details.building || prev.building,
          street: details.street || prev.street,
          city: cityValue,
          state: details.state || prev.state,
          pincode: details.pincode || prev.pincode,
          location: details.location || cityValue || prev.location
        }));
        
        if (cityValue) {
          const selectedLocation = deliveryLocations.find(loc => loc.name === cityValue);
          if (selectedLocation) {
            setDeliveryCharge(selectedLocation.charge);
          } else {
            setDeliveryCharge(99);
          }
        }
        
        toast({
          title: "Details Found!",
          description: "Your saved details have been filled. Please verify and update if needed."
        });
      }
    } catch (error) {
      toast({
        title: "No Details Found",
        description: "No saved details found for this phone/email. Please enter manually.",
        variant: "destructive"
      });
    } finally {
      setSearching(false);
    }
  };

  const detectCurrentLocation = () => {
    if (!navigator.geolocation) {
      toast({
        title: "Error",
        description: "Geolocation is not supported by your browser",
        variant: "destructive"
      });
      return;
    }

    setDetectingLocation(true);
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        
        try {
          const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&addressdetails=1`
          );
          const data = await response.json();
          
          if (data && data.address) {
            const addr = data.address;
            
            // Enhanced address extraction with multiple fallbacks
            const detectedAddress = {
              doorNo: addr.house_number || addr.housenumber || addr.building_number || '',
              building: addr.building || addr.house || addr.apartment || addr.neighbourhood || addr.suburb || addr.residential || '',
              street: addr.road || addr.street || addr.pedestrian || addr.footway || addr.path || addr.cycleway || '',
              city: addr.city || addr.town || addr.village || addr.municipality || addr.county || addr.hamlet || '',
              state: addr.state || addr.state_district || addr.region || '',
              pincode: addr.postcode || addr.postal_code || ''
            };
            
            setFormData(prev => ({
              ...prev,
              doorNo: detectedAddress.doorNo || prev.doorNo,
              building: detectedAddress.building || prev.building,
              street: detectedAddress.street || prev.street,
              city: detectedAddress.city || prev.city,
              state: detectedAddress.state || prev.state,
              pincode: detectedAddress.pincode || prev.pincode
            }));
            
            const filledFields = Object.values(detectedAddress).filter(v => v).length;
            
            toast({
              title: "Location Detected!",
              description: `${filledFields} address field(s) detected. Please verify and fill any missing fields.`
            });
          }
        } catch (error) {
          toast({
            title: "Error",
            description: "Unable to fetch address details. Please enter manually.",
            variant: "destructive"
          });
        } finally {
          setDetectingLocation(false);
        }
      },
      (error) => {
        setDetectingLocation(false);
        toast({
          title: "Error",
          description: "Unable to detect location. Please allow location access and try again.",
          variant: "destructive"
        });
      }
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast({
        title: "Error",
        description: "Please fill all required fields correctly.",
        variant: "destructive"
      });
      return;
    }

    if (!cart || cart.length === 0) {
      toast({
        title: "Error",
        description: "Your cart is empty.",
        variant: "destructive"
      });
      return;
    }

    const fullAddress = `${formData.doorNo}, ${formData.building}, ${formData.street}, ${formData.city}, ${formData.state} - ${formData.pincode}`;
    const finalDeliveryCharge = calculateDeliveryCharge();

    const orderData = {
      user_id: user?.id || 'guest',
      customer_name: formData.name,
      email: formData.email,
      phone: formData.phone,
      address: fullAddress,
      doorNo: formData.doorNo,
      building: formData.building,
      street: formData.street,
      city: formData.city,
      state: formData.state,
      pincode: formData.pincode,
      location: formData.location || formData.city,
      items: cart.map(item => ({
        product_id: String(item.id || ''),
        name: item.name || '',
        image: item.image || '',
        weight: item.weight || item.selectedWeight || (item.prices && item.prices.length > 0 ? item.prices[0].weight : ''),
        price: parseFloat(item.price || item.selectedPrice || (item.prices && item.prices.length > 0 ? item.prices[0].price : 0)),
        quantity: parseInt(item.quantity) || 1,
        description: item.description || ''
      })),
      subtotal: getCartTotal(),
      delivery_charge: finalDeliveryCharge,
      total: getCartTotal() + finalDeliveryCharge,
      payment_method: formData.paymentMethod,
      payment_sub_method: formData.paymentSubMethod
    };

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/orders`, orderData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const result = response.data;
      clearCart();

      toast({
        title: "Order Placed Successfully!",
        description: `Order ID: ${result.order_id}. Check your email for tracking code.`,
      });

      navigate('/order-success', { state: { orderData: result } });
    } catch (error) {
      console.error('Order error:', error);
      const errorMsg = error.response?.data?.detail || 
                       (error.response?.data?.message) ||
                       "Failed to place order. Please try again.";
      toast({
        title: "Error",
        description: Array.isArray(errorMsg) ? errorMsg[0]?.msg || errorMsg[0] : errorMsg,
        variant: "destructive"
      });
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    if (name === 'state') {
      setFormData(prev => ({ ...prev, [name]: value, city: '' }));
      setDeliveryCharge(0);
      if (errors.city) {
        setErrors(prev => ({ ...prev, city: '' }));
      }
    } else if (name === 'city') {
      setFormData(prev => ({ ...prev, [name]: value, location: value }));
      const selectedLocation = deliveryLocations.find(loc => loc.name === value);
      if (selectedLocation) {
        setDeliveryCharge(selectedLocation.charge);
      } else {
        setDeliveryCharge(99);
      }
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const scrollToProduct = (productId) => {
    navigate('/');
    setTimeout(() => {
      const element = document.getElementById(`product-${productId}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        element.classList.add('ring-4', 'ring-orange-400', 'ring-offset-2');
        setTimeout(() => {
          element.classList.remove('ring-4', 'ring-orange-400', 'ring-offset-2');
        }, 2000);
      }
    }, 300);
  };

  const finalDeliveryCharge = calculateDeliveryCharge();
  const totalAmount = getCartTotal() + finalDeliveryCharge;

  if (!cart || cart.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Your cart is empty</h2>
          <button
            onClick={() => navigate('/')}
            className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-6 py-3 rounded-lg hover:from-orange-600 hover:to-red-600"
          >
            Continue Shopping
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl md:text-4xl font-bold text-center mb-8 bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
          Checkout
        </h1>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Checkout Form - Keeping the same as before */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Delivery Details</h2>
            
            {/* Previous Details Search */}
            <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Have you ordered before?</h3>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={searchIdentifier}
                  onChange={(e) => setSearchIdentifier(e.target.value)}
                  placeholder="Enter phone number or email"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleSearchUserDetails}
                  disabled={searching}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                >
                  {searching ? 'Searching...' : 'Search'}
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">Full Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                    errors.name ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Enter your full name"
                />
                {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
              </div>

              {/* Email */}
              <div>
                <label className="block text-gray-700 font-medium mb-2 flex items-center space-x-2">
                  <Mail className="h-4 w-4" />
                  <span>Email Address *</span>
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                    errors.email ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="your.email@example.com"
                />
                {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
              </div>

              {/* Phone */}
              <div>
                <label className="block text-gray-700 font-medium mb-2 flex items-center space-x-2">
                  <Phone className="h-4 w-4" />
                  <span>Phone Number *</span>
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  maxLength="10"
                  className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                    errors.phone ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="10-digit mobile number"
                />
                {errors.phone && <p className="text-red-500 text-sm mt-1">{errors.phone}</p>}
              </div>

              {/* Address Section */}
              <div className="pt-4 border-t">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-bold text-gray-800 flex items-center space-x-2">
                    <Home className="h-5 w-5" />
                    <span>Delivery Address</span>
                  </h3>
                  <button
                    type="button"
                    onClick={detectCurrentLocation}
                    disabled={detectingLocation}
                    className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all disabled:opacity-50 text-sm"
                  >
                    <Navigation className="h-4 w-4" />
                    <span>{detectingLocation ? 'Detecting...' : 'Detect Location'}</span>
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {/* Door No */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Door No *</label>
                    <input
                      type="text"
                      name="doorNo"
                      value={formData.doorNo}
                      onChange={handleChange}
                      className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                        errors.doorNo ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="12-34"
                    />
                    {errors.doorNo && <p className="text-red-500 text-sm mt-1">{errors.doorNo}</p>}
                  </div>

                  {/* Building */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Building/House *</label>
                    <input
                      type="text"
                      name="building"
                      value={formData.building}
                      onChange={handleChange}
                      className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                        errors.building ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="Apartment/House name"
                    />
                    {errors.building && <p className="text-red-500 text-sm mt-1">{errors.building}</p>}
                  </div>
                </div>

                {/* Street */}
                <div className="mt-4">
                  <label className="block text-gray-700 font-medium mb-2">Street/Area *</label>
                  <input
                    type="text"
                    name="street"
                    value={formData.street}
                    onChange={handleChange}
                    className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                      errors.street ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Street name or area"
                  />
                  {errors.street && <p className="text-red-500 text-sm mt-1">{errors.street}</p>}
                </div>

                <div className="grid grid-cols-2 gap-4 mt-4">
                  {/* State */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">State *</label>
                    <select
                      name="state"
                      value={formData.state}
                      onChange={handleChange}
                      className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                        errors.state ? 'border-red-500' : 'border-gray-300'
                      }`}
                    >
                      <option value="">Select State</option>
                      <option value="Andhra Pradesh">Andhra Pradesh</option>
                      <option value="Telangana">Telangana</option>
                    </select>
                    {errors.state && <p className="text-red-500 text-sm mt-1">{errors.state}</p>}
                  </div>

                  {/* City */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">City *</label>
                    <select
                      name="city"
                      value={formData.city}
                      onChange={handleChange}
                      disabled={!formData.state}
                      className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                        errors.city ? 'border-red-500' : 'border-gray-300'
                      } ${!formData.state ? 'bg-gray-100 cursor-not-allowed' : ''}`}
                    >
                      <option value="">
                        {formData.state ? 'Select City' : 'Select State First'}
                      </option>
                      {formData.state && stateCities[formData.state] && 
                        stateCities[formData.state].map((city, index) => {
                          const locationData = deliveryLocations.find(loc => loc.name === city && loc.state === formData.state);
                          const charge = locationData ? locationData.charge : 99;
                          return (
                            <option key={`${formData.state}-${city}-${index}`} value={city}>
                              {city} - ₹{charge}
                            </option>
                          );
                        })
                      }
                    </select>
                    {errors.city && <p className="text-red-500 text-sm mt-1">{errors.city}</p>}
                    {formData.city && (
                      <p className="text-sm text-green-600 mt-1">
                        ✓ Delivery Charge: ₹{deliveryCharge}
                      </p>
                    )}
                  </div>
                </div>

                {/* Pincode */}
                <div className="mt-4">
                  <label className="block text-gray-700 font-medium mb-2">Pincode *</label>
                  <input
                    type="text"
                    name="pincode"
                    value={formData.pincode}
                    onChange={handleChange}
                    maxLength="6"
                    className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                      errors.pincode ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="6-digit pincode"
                  />
                  {errors.pincode && <p className="text-red-500 text-sm mt-1">{errors.pincode}</p>}
                </div>
              </div>

              {/* Payment Method */}
              <div className="pt-4 border-t">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Payment Method</h3>
                
                {/* Online Payment */}
                <div className="mb-4">
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="online"
                      checked={formData.paymentMethod === 'online'}
                      onChange={handleChange}
                      className="w-4 h-4 text-orange-600"
                    />
                    <div className="flex items-center space-x-2">
                      <CreditCard className="h-5 w-5 text-blue-600" />
                      <span className="font-semibold">Online Payment (UPI)</span>
                    </div>
                  </label>
                  {formData.paymentMethod === 'online' && (
                    <div className="mt-3 ml-8 p-4 bg-white border border-gray-200 rounded-lg">
                      <p className="text-sm text-gray-600 mb-3 font-medium">Select UPI Payment Option:</p>
                      <div className="grid grid-cols-2 gap-3">
                        {['Paytm', 'PhonePe', 'Google Pay', 'BHIM UPI'].map((app) => (
                          <label 
                            key={app}
                            className={`flex items-center space-x-2 p-3 border rounded-lg cursor-pointer transition-all ${
                              formData.paymentSubMethod === app 
                                ? 'border-orange-500 bg-orange-50' 
                                : 'border-gray-200 hover:border-orange-300'
                            }`}
                          >
                            <input
                              type="radio"
                              name="paymentSubMethod"
                              value={app}
                              checked={formData.paymentSubMethod === app}
                              onChange={handleChange}
                              className="w-4 h-4 text-orange-600"
                            />
                            <span className="text-sm font-medium">{app}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Card Payment */}
                <div>
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="card"
                      checked={formData.paymentMethod === 'card'}
                      onChange={handleChange}
                      className="w-4 h-4 text-orange-600"
                    />
                    <div className="flex items-center space-x-2">
                      <CreditCard className="h-5 w-5 text-purple-600" />
                      <span className="font-semibold">Card Payment</span>
                    </div>
                  </label>
                  {formData.paymentMethod === 'card' && (
                    <div className="mt-3 ml-8 p-4 bg-white border border-gray-200 rounded-lg">
                      <p className="text-sm text-gray-600 mb-3 font-medium">Select Card Type:</p>
                      <div className="flex space-x-4">
                        {['Debit Card', 'Credit Card'].map((cardType) => (
                          <label 
                            key={cardType}
                            className={`flex items-center space-x-2 p-3 border rounded-lg cursor-pointer transition-all ${
                              formData.paymentSubMethod === cardType 
                                ? 'border-orange-500 bg-orange-50' 
                                : 'border-gray-200 hover:border-orange-300'
                            }`}
                          >
                            <input
                              type="radio"
                              name="paymentSubMethod"
                              value={cardType}
                              checked={formData.paymentSubMethod === cardType}
                              onChange={handleChange}
                              className="w-4 h-4 text-orange-600"
                            />
                            <span className="text-sm font-medium">{cardType}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <button
                type="submit"
                className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-4 rounded-xl font-semibold hover:from-green-700 hover:to-green-800 transition-all transform hover:scale-105 shadow-lg flex items-center justify-center space-x-2"
              >
                <Truck className="h-5 w-5" />
                <span>Place Order</span>
              </button>
            </form>
          </div>

          {/* Order Summary with Edit Features */}
          <div>
            <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Order Summary</h2>
              
              {/* Cart Items with Edit Options */}
              <div className="space-y-4 mb-6">
                {cart.map((item, index) => (
                  <div key={index} className="border-b pb-4">
                    <div className="flex items-start space-x-4">
                      <img src={item.image} alt={item.name} className="w-20 h-20 object-cover rounded-lg" />
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-800">{item.name}</h3>
                        <div className="flex items-center space-x-2 mt-1">
                          <p className="text-sm text-gray-600">{item.weight || item.selectedWeight}</p>
                          {allProducts.find(p => p.id === item.id)?.prices?.length > 1 && (
                            <button
                              onClick={() => handleWeightEdit(index)}
                              className="text-blue-600 hover:text-blue-700"
                            >
                              <Edit2 className="h-3 w-3" />
                            </button>
                          )}
                        </div>
                        
                        {/* Weight Edit Modal */}
                        {editingItemIndex === index && (
                          <div className="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
                            <p className="text-xs font-semibold text-gray-700 mb-2">Select Weight:</p>
                            <select
                              value={selectedWeight}
                              onChange={(e) => setSelectedWeight(e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            >
                              {allProducts.find(p => p.id === item.id)?.prices?.map((priceInfo, idx) => (
                                <option key={idx} value={priceInfo.weight}>
                                  {priceInfo.weight} - ₹{priceInfo.price}
                                </option>
                              ))}
                            </select>
                            <div className="flex space-x-2 mt-2">
                              <button
                                onClick={() => handleWeightChange(index)}
                                className="flex-1 px-3 py-1 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700"
                              >
                                Update
                              </button>
                              <button
                                onClick={() => setEditingItemIndex(null)}
                                className="flex-1 px-3 py-1 bg-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-400"
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        )}
                        
                        {/* Quantity Controls */}
                        <div className="flex items-center space-x-3 mt-2">
                          <button
                            onClick={() => handleQuantityChange(index, -1)}
                            className="w-8 h-8 flex items-center justify-center bg-gray-200 rounded-full hover:bg-gray-300 transition-colors"
                          >
                            <Minus className="h-4 w-4" />
                          </button>
                          <span className="font-semibold text-gray-700">{item.quantity}</span>
                          <button
                            onClick={() => handleQuantityChange(index, 1)}
                            className="w-8 h-8 flex items-center justify-center bg-orange-500 text-white rounded-full hover:bg-orange-600 transition-colors"
                          >
                            <Plus className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      <p className="font-bold text-orange-600">₹{(item.price || item.selectedPrice || 0) * (item.quantity || 1)}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Free Delivery Progress */}
              {freeDeliverySettings.enabled && !isFreeDeliveryApplicable() && getRemainingForFreeDelivery() > 0 && (
                <div className="mb-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
                  <div className="flex items-center space-x-2 mb-2">
                    <Truck className="h-5 w-5 text-green-600" />
                    <p className="text-sm font-semibold text-green-800">
                      Add ₹{getRemainingForFreeDelivery().toFixed(2)} more for FREE delivery!
                    </p>
                  </div>
                  <div className="w-full bg-green-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full transition-all"
                      style={{ width: `${(getCartTotal() / freeDeliverySettings.threshold) * 100}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {/* Price Breakdown */}
              <div className="space-y-3 border-t pt-4">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal:</span>
                  <span className="font-semibold">₹{getCartTotal()}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Delivery Charge:</span>
                  <span className={`font-semibold ${isFreeDeliveryApplicable() ? 'text-green-600' : ''}`}>
                    {isFreeDeliveryApplicable() ? (
                      <span className="flex items-center space-x-1">
                        <span className="line-through text-gray-400">₹{deliveryCharge}</span>
                        <span className="text-green-600 font-bold">FREE</span>
                      </span>
                    ) : (
                      `₹${finalDeliveryCharge}`
                    )}
                  </span>
                </div>
                <div className="flex justify-between text-xl font-bold text-gray-800 border-t pt-3">
                  <span>Total:</span>
                  <span className="text-orange-600">₹{totalAmount}</span>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            {recommendations.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Sparkles className="h-5 w-5 text-orange-500" />
                  <h3 className="text-lg font-bold text-gray-800">You May Also Like</h3>
                </div>
                <div className="space-y-3">
                  {recommendations.map((product) => (
                    <div 
                      key={product.id}
                      onClick={() => scrollToProduct(product.id)}
                      className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:border-orange-400 hover:bg-orange-50 transition-all cursor-pointer group"
                    >
                      <img src={product.image} alt={product.name} className="w-16 h-16 object-cover rounded-lg" />
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-800 text-sm group-hover:text-orange-600">{product.name}</h4>
                        <p className="text-xs text-gray-600">{product.category}</p>
                        <p className="text-sm font-bold text-orange-600 mt-1">
                          From ₹{product.prices[0]?.price}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
