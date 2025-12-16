import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';
import { ShoppingBag, MapPin, Phone, Mail, CreditCard, Wallet, User, Home, Building, MapPinned, Navigation, Sparkles, Trash2, Edit, Check } from 'lucide-react';
import imagePreloader from '../utils/imagePreloader';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function Checkout() {
  const navigate = useNavigate();
  const { cart, clearCart, updateCartItem, removeFromCart, cartTotal, addToCart } = useCart();
  const { user } = useAuth();
  const { toast } = useToast();

  // Form state
  const [customerName, setCustomerName] = useState(user?.name || '');
  const [customerEmail, setCustomerEmail] = useState(user?.email || '');
  const [customerPhone, setCustomerPhone] = useState(
    user?.phone ? (user.phone.startsWith('+91') ? user.phone : '+91' + user.phone.replace(/[^0-9]/g, '')) : '+91'
  );
  const [customerWhatsApp, setCustomerWhatsApp] = useState(
    user?.phone ? (user.phone.startsWith('+91') ? user.phone : '+91' + user.phone.replace(/[^0-9]/g, '')) : '+91'
  );
  const [useSameForWhatsApp, setUseSameForWhatsApp] = useState(true);
  
  // Structured address fields
  const [doorNo, setDoorNo] = useState('');
  const [building, setBuilding] = useState('');
  const [street, setStreet] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [pincode, setPincode] = useState('');
  
  const [paymentMethod, setPaymentMethod] = useState('razorpay');
  const [paymentSubMethod, setPaymentSubMethod] = useState('upi');
  const [loading, setLoading] = useState(false);
  const [deliveryCharge, setDeliveryCharge] = useState(0);
  const [deliveryLocations, setDeliveryLocations] = useState([]);
  const [detectingLocation, setDetectingLocation] = useState(false);
  const [previousSearchQuery, setPreviousSearchQuery] = useState('');
  const [previousSearchResults, setPreviousSearchResults] = useState([]);
  const [showPreviousResults, setShowPreviousResults] = useState(false);
  const [locationsByState, setLocationsByState] = useState({
    "Andhra Pradesh": [],
    "Telangana": []
  });
  const [editingItemIndex, setEditingItemIndex] = useState(null);
  const [selectedWeight, setSelectedWeight] = useState('');
  const [allProducts, setAllProducts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [freeDeliverySettings, setFreeDeliverySettings] = useState({ enabled: true, threshold: 1000 });
  const [showCustomCityInput, setShowCustomCityInput] = useState(false);
  const [customCity, setCustomCity] = useState('');
  const [customCityState, setCustomCityState] = useState('');
  const [customCityDeliveryCharge, setCustomCityDeliveryCharge] = useState(199);
  
  // Payment settings and WhatsApp
  const [paymentSettings, setPaymentSettings] = useState({ status: 'enabled' });
  const [whatsappNumbers, setWhatsappNumbers] = useState([]);

  // Enrich cart items with full product data
  const enrichedCart = React.useMemo(() => {
    return cart.map(item => {
      const product = allProducts.find(p => p.id === item.id);
      if (product) {
        return {
          ...item,
          prices: product.prices, // Add available price options from product
          description: product.description
        };
      }
      return item;
    });
  }, [cart, allProducts]);

  useEffect(() => {
    if (cart.length === 0) {
      navigate('/');
      return;
    }
    
    fetchAllProducts();
    fetchDeliveryLocations();
    fetchFreeDeliverySettings();
    fetchPaymentSettings();
    fetchWhatsAppNumbers();
    loadPreviousOrderData();
  }, []);

  useEffect(() => {
    calculateDeliveryCharge();
  }, [city, deliveryLocations, freeDeliverySettings, cartTotal]);

  // Debug locationsByState changes
  useEffect(() => {
    console.log('🔍 locationsByState changed:', {
      hasAndhraPradesh: locationsByState["Andhra Pradesh"]?.length || 0,
      hasTelangana: locationsByState["Telangana"]?.length || 0,
      currentState: state
    });
  }, [locationsByState, state]);

  const fetchAllProducts = async () => {
    try {
      const response = await axios.get(`${API}/products`);
      setAllProducts(response.data);
      
      // Get smart recommendations (excluding items in cart)
      const cartProductIds = cart.map(item => item.id);
      const availableProducts = response.data.filter(p => !cartProductIds.includes(p.id));
      
      // Prioritize: Festival products first, then Best Sellers, then random
      const festivalProducts = availableProducts.filter(p => p.isFestival);
      const bestSellers = availableProducts.filter(p => p.isBestSeller && !p.isFestival);
      const regularProducts = availableProducts.filter(p => !p.isBestSeller && !p.isFestival);
      
      // Shuffle each category
      const shuffledFestival = [...festivalProducts].sort(() => Math.random() - 0.5);
      const shuffledBestSellers = [...bestSellers].sort(() => Math.random() - 0.5);
      const shuffledRegular = [...regularProducts].sort(() => Math.random() - 0.5);
      
      // Combine and take 4 products
      const combinedRecommendations = [...shuffledFestival, ...shuffledBestSellers, ...shuffledRegular];
      const randomRecommendations = combinedRecommendations.slice(0, 4);
      
      setRecommendations(randomRecommendations);
      
      // Preload cart item images and recommendation images
      const cartImages = cart.map(item => item.image).filter(Boolean);
      const recommendationImages = randomRecommendations.map(p => p.image).filter(Boolean);
      const allImages = [...cartImages, ...recommendationImages];
      
      if (allImages.length > 0) {
        imagePreloader.preloadImages(allImages)
          .then(() => {
            console.log('✅ Checkout images preloaded');
          })
          .catch(err => {
            console.error('Checkout image preload error:', err);
          });
      }
    } catch (error) {
      console.error('Failed to fetch products:', error);
    }
  };

  const fetchDeliveryLocations = async () => {
    try {
      const response = await axios.get(`${API}/locations`);
      const locations = response.data;
      console.log('📦 Fetched delivery locations:', locations.length);
      setDeliveryLocations(locations);

      // Group locations by state
      const groupedByState = {
        "Andhra Pradesh": [],
        "Telangana": []
      };

      locations.forEach(loc => {
        if (groupedByState[loc.state]) {
          groupedByState[loc.state].push(loc);
        }
      });

      // Sort each state's cities alphabetically
      groupedByState["Andhra Pradesh"].sort((a, b) => a.name.localeCompare(b.name));
      groupedByState["Telangana"].sort((a, b) => a.name.localeCompare(b.name));

      console.log('🗺️ Grouped locations:', {
        'Andhra Pradesh': groupedByState["Andhra Pradesh"].length,
        'Telangana': groupedByState["Telangana"].length
      });
      console.log('📍 Sample AP cities:', groupedByState["Andhra Pradesh"].slice(0, 5).map(l => l.name));
      console.log('📍 Sample Telangana cities:', groupedByState["Telangana"].slice(0, 5).map(l => l.name));

      setLocationsByState(groupedByState);
      console.log('✅ locationsByState updated');
    } catch (error) {
      console.error('Failed to fetch locations:', error);
    }
  };

  const fetchFreeDeliverySettings = async () => {
    try {
      const response = await axios.get(`${API}/settings/free-delivery`);
      setFreeDeliverySettings(response.data);
    } catch (error) {
      console.error('Failed to fetch free delivery settings:', error);
    }
  };

  const fetchPaymentSettings = async () => {
    try {
      const response = await axios.get(`${API}/payment-settings`);
      setPaymentSettings(response.data);
      console.log('💳 Payment settings:', response.data);
    } catch (error) {
      console.error('Failed to fetch payment settings:', error);
      setPaymentSettings({ status: 'enabled' }); // Default to enabled on error
    }
  };

  const fetchWhatsAppNumbers = async () => {
    try {
      const response = await axios.get(`${API}/whatsapp-numbers`);
      setWhatsappNumbers(response.data || []);
      console.log('📱 WhatsApp numbers:', response.data?.length || 0);
    } catch (error) {
      console.error('Failed to fetch WhatsApp numbers:', error);
    }
  };

  const loadPreviousOrderData = () => {
    // Check if there's a phone number stored in localStorage from previous orders
    const storedPhone = localStorage.getItem('lastOrderPhone');
    if (storedPhone && !customerPhone) {
      setCustomerPhone(storedPhone);
    }
  };

  // Fetch customer data by phone number for auto-fill
  const fetchCustomerDataByPhone = async (phone) => {
    try {
      // Clean phone number
      const cleanedPhone = phone.replace('+91', '').replace(/[^0-9]/g, '');
      
      if (cleanedPhone.length < 10) return; // Phone number not complete
      
      const response = await axios.get(`${API}/customer-data/${cleanedPhone}`);
      
      if (response.data) {
        const data = response.data;
        console.log('✅ Customer data found, auto-filling...', data);
        
        // Auto-fill all fields
        if (data.name) setCustomerName(data.name);
        if (data.email) setCustomerEmail(data.email);
        if (data.whatsapp) setCustomerWhatsApp(data.whatsapp);
        if (data.door_no) setDoorNo(data.door_no);
        if (data.building) setBuilding(data.building);
        if (data.street) setStreet(data.street);
        if (data.city) setCity(data.city);
        if (data.state) setState(data.state);
        if (data.pincode) setPincode(data.pincode);
        
        toast({
          title: "Customer Data Found!",
          description: "Your previous details have been auto-filled. Please verify and update if needed.",
        });
      }
    } catch (error) {
      console.log('No previous customer data found');
    }
  };

  // Save customer data for future orders
  const saveCustomerData = async () => {
    try {
      await axios.post(`${API}/customer-data`, {
        phone: customerPhone,
        name: customerName,
        email: customerEmail,
        whatsapp: customerWhatsApp,
        door_no: doorNo,
        building: building,
        street: street,
        city: city,
        state: state,
        pincode: pincode
      });
      console.log('✅ Customer data saved for future orders');
    } catch (error) {
      console.error('Failed to save customer data:', error);
    }
  };

  const sendWhatsAppMessages = (orderData, orderId, trackingCode) => {
    // Create professionally formatted WhatsApp message
    // Build items list with proper formatting
    const itemsList = orderData.items.map((item, idx) => {
      // Create product link instead of showing image path
      const productLink = `${window.location.origin}/product/${item.product_id}`;
      return `${idx + 1}. *${item.name}*
   Weight: ${item.weight}
   Price: Rs.${item.price} x ${item.quantity} = Rs.${item.price * item.quantity}
   Product Link: ${productLink}`;
    }).join('\n\n');

    const message = `*NEW ORDER RECEIVED*

*ORDER DETAILS*
Order ID: ${orderId}
Tracking Code: ${trackingCode}

----------------------------------
*CUSTOMER INFORMATION*
----------------------------------
Name: ${orderData.customer_name}
Phone: ${orderData.phone}
WhatsApp: ${orderData.whatsapp_number}
Email: ${orderData.email}

----------------------------------
*DELIVERY ADDRESS*
----------------------------------
${orderData.doorNo ? `Door No: ${orderData.doorNo}\n` : ''}${orderData.building ? `Building: ${orderData.building}\n` : ''}${orderData.street ? `Street: ${orderData.street}\n` : ''}City: ${orderData.city}
State: ${orderData.state}
Pincode: ${orderData.pincode}

----------------------------------
*ORDER ITEMS*
----------------------------------
${itemsList}

----------------------------------
*PAYMENT SUMMARY*
----------------------------------
Subtotal: Rs.${orderData.subtotal}
Delivery Charge: Rs.${orderData.delivery_charge}
----------------------------------
*TOTAL: Rs.${orderData.total}*
----------------------------------

Payment Method: ${orderData.payment_method === 'razorpay' ? 'Online Payment (Razorpay)' : 'WhatsApp Booking'}
Payment Status: ${orderData.payment_status === 'completed' ? 'PAID' : 'Pending'}

_Order placed via Anantha Home Foods_
_Click product image links above to view products_`;

    const encodedMessage = encodeURIComponent(message);

    // Open WhatsApp for each configured number
    // This will open customer's WhatsApp with pre-filled message to send to each owner number
    whatsappNumbers.forEach((number, index) => {
      const whatsappUrl = `https://wa.me/${number.phone.replace(/[^0-9]/g, '')}?text=${encodedMessage}`;
      
      // Open with a slight delay between each to avoid popup blocking
      setTimeout(() => {
        window.open(whatsappUrl, '_blank');
      }, index * 500);
    });

    toast({
      title: "📱 Opening WhatsApp",
      description: `Opening WhatsApp to send beautifully formatted order details to ${whatsappNumbers.length} owner(s). Please send the pre-filled message.`,
    });
  };

  // Handle WhatsApp-only booking (when user clicks "Book via WhatsApp" button)
  const handleWhatsAppBooking = async (e) => {
    e.preventDefault();
    
    if (cart.length === 0) {
      toast({
        title: "Cart is empty",
        description: "Please add items to cart before placing order",
        variant: "destructive"
      });
      return;
    }

    // Sync WhatsApp with phone if checkbox is checked
    const finalWhatsApp = useSameForWhatsApp ? customerPhone : customerWhatsApp;
    
    // Validate all required fields
    if (!customerName || !customerEmail || !customerPhone || !finalWhatsApp || !doorNo || !street || !city || !state || !pincode) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields",
        variant: "destructive"
      });
      return;
    }

    // Validate city exists in delivery locations
    const cityExists = deliveryLocations.some(
      loc => loc.name.toLowerCase() === city.toLowerCase() && 
             loc.state.toLowerCase() === state.toLowerCase()
    );

    if (!cityExists) {
      toast({
        title: "City Not Available",
        description: `We don't currently deliver to ${city}. Please select a city from the dropdown list.`,
        variant: "destructive"
      });
      return;
    }

    setLoading(true);

    try {
      // Prepare order data for WhatsApp booking
      const orderData = {
        customer_name: customerName,
        email: customerEmail,
        phone: customerPhone,
        whatsapp_number: finalWhatsApp,
        doorNo: doorNo,
        building: building,
        street: street,
        city: city,
        state: state,
        pincode: pincode,
        location: city,
        items: cart.map(item => ({
          product_id: item.id,
          name: item.name,
          weight: item.weight || 'N/A',
          price: item.price || 0,
          quantity: item.quantity,
          image: item.image
        })),
        subtotal: cartTotal || 0,
        delivery_charge: deliveryCharge || 0,
        total: (cartTotal || 0) + (deliveryCharge || 0),
        payment_method: 'whatsapp',
        payment_sub_method: 'whatsapp',
        payment_status: 'pending',
        order_status: 'pending'
      };

      // Save customer data for future orders
      await saveCustomerData();

      // Create order directly (WhatsApp booking, no payment yet)
      const orderResponse = await axios.post(`${API}/orders`, orderData);
      const { order_id, tracking_code } = orderResponse.data;

      console.log('✅ Order created (WhatsApp booking):', order_id);

      // Send WhatsApp messages to all configured numbers
      if (whatsappNumbers.length > 0) {
        sendWhatsAppMessages(orderData, order_id, tracking_code);
      } else {
        toast({
          title: "No WhatsApp Numbers Configured",
          description: "Order created but no WhatsApp notifications will be sent. Please add WhatsApp numbers in admin panel.",
          variant: "destructive"
        });
      }

      // Clear cart and navigate to tracking
      clearCart();
      toast({
        title: "Order Booked via WhatsApp! 🎉",
        description: `Your order has been received. Tracking code: ${tracking_code}. We'll contact you on WhatsApp for payment and confirmation.`,
        duration: 5000,
      });
      navigate(`/track-order?code=${tracking_code}`);
    } catch (error) {
      console.error('❌ WhatsApp booking failed:', error);
      toast({
        title: "Booking Failed",
        description: error.response?.data?.detail || "Failed to create order. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePreviousOrderSearch = async () => {
    if (!previousSearchQuery.trim()) {
      toast({
        title: "Search Required",
        description: "Please enter phone number or email to search previous orders",
        variant: "destructive"
      });
      return;
    }

    try {
      const response = await axios.get(`${API}/orders/track/${previousSearchQuery.trim()}`);
      if (response.data.orders && response.data.orders.length > 0) {
        setPreviousSearchResults(response.data.orders);
        setShowPreviousResults(true);
        toast({
          title: "Orders Found",
          description: `Found ${response.data.total} order(s) for ${previousSearchQuery}`,
        });
      } else {
        toast({
          title: "No Orders Found",
          description: "No previous orders found with this phone or email",
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch previous orders",
        variant: "destructive"
      });
    }
  };

  const fillFromPreviousOrder = (order) => {
    setCustomerName(order.customer_name || '');
    setCustomerEmail(order.email || '');
    setCustomerPhone(order.phone || '');
    
    // Handle both old and new address formats
    if (order.doorNo) {
      // New structured format
      setDoorNo(order.doorNo || '');
      setBuilding(order.building || '');
      setStreet(order.street || '');
      setCity(order.city || '');
      setState(order.state || '');
      setPincode(order.pincode || '');
    } else if (order.address) {
      // Old single address format - try to parse it
      setStreet(order.address);
      setCity(order.location || '');
    }
    
    setShowPreviousResults(false);
    toast({
      title: "Address Filled",
      description: "Previous order details have been filled in the form",
    });
  };

  const calculateDeliveryCharge = () => {
    if (!city) {
      setDeliveryCharge(0);
      return;
    }

    // Check if city exists in delivery locations
    const location = deliveryLocations.find(
      loc => loc.name.toLowerCase() === city.toLowerCase()
    );

    if (!location) {
      // City not found in delivery locations
      setDeliveryCharge(0);
      return;
    }

    // Check for free delivery
    if (freeDeliverySettings.enabled && cartTotal >= freeDeliverySettings.threshold) {
      setDeliveryCharge(0);
      return;
    }

    // Use the delivery charge from the location
    setDeliveryCharge(location.charge || 0);
  };

  const detectCurrentLocation = async () => {
    if (!navigator.geolocation) {
      toast({
        title: "Location Not Supported",
        description: "Your browser doesn't support geolocation",
        variant: "destructive"
      });
      return;
    }

    setDetectingLocation(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        console.log('📍 Coordinates:', latitude, longitude);
        
        try {
          // Use OpenStreetMap Nominatim API for reverse geocoding with zoom=10 for better city detection
          const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10&addressdetails=1`,
            {
              headers: {
                'Accept-Language': 'en'
              }
            }
          );
          const data = await response.json();
          console.log('🗺️ Location data:', data);
          
          if (data.address) {
            const addr = data.address;
            
            // Build a detailed street address from multiple components
            const streetParts = [];
            if (addr.road) streetParts.push(addr.road);
            if (addr.neighbourhood) streetParts.push(addr.neighbourhood);
            if (addr.suburb) streetParts.push(addr.suburb);
            if (addr.hamlet) streetParts.push(addr.hamlet);
            const detectedStreet = streetParts.join(', ');
            
            // Try to use neighbourhood or suburb for building
            const detectedBuilding = addr.neighbourhood || addr.suburb || '';
            
            const detectedPincode = addr.postcode || '';
            const detectedState = addr.state || '';
            
            // Smart city detection - ENHANCED ALGORITHM with state filtering
            console.log('🌍 Detected State:', detectedState);
            
            // Try to match with our delivery locations - prioritize exact matches
            const possibleCities = [
              addr.city,
              addr.town,
              addr.municipality,
              addr.county,
              addr.district,
              addr.city_district,
              addr.village,
              addr.suburb
            ].filter(Boolean);
            
            console.log('🏙️ Possible cities from API:', possibleCities);
            console.log('📍 Our delivery cities:', deliveryLocations.map(l => `${l.name}, ${l.state}`));
            
            let detectedCity = '';
            let matchedLocation = null;
            
            // Filter cities by state first if we have state info
            let relevantLocations = deliveryLocations;
            if (detectedState) {
              relevantLocations = deliveryLocations.filter(loc => 
                loc.state.toLowerCase().includes(detectedState.toLowerCase()) ||
                detectedState.toLowerCase().includes(loc.state.toLowerCase())
              );
              console.log('🗺️ Filtered to', relevantLocations.length, 'cities in', detectedState);
            }
            
            // First try exact match (case-insensitive)
            for (const possibleCity of possibleCities) {
              const exactMatch = relevantLocations.find(
                loc => loc.name.toLowerCase() === possibleCity.toLowerCase()
              );
              
              if (exactMatch) {
                detectedCity = exactMatch.name;
                matchedLocation = exactMatch;
                console.log('✅ Exact match found:', detectedCity, ',', exactMatch.state);
                break;
              }
            }
            
            // If no exact match, try partial match within the state
            if (!detectedCity) {
              for (const possibleCity of possibleCities) {
                const partialMatch = relevantLocations.find(
                  loc => 
                    loc.name.toLowerCase().includes(possibleCity.toLowerCase()) ||
                    possibleCity.toLowerCase().includes(loc.name.toLowerCase())
                );
                
                if (partialMatch) {
                  detectedCity = partialMatch.name;
                  matchedLocation = partialMatch;
                  console.log('✅ Partial match found:', detectedCity, ',', partialMatch.state);
                  break;
                }
              }
            }
            
            // If still no match, try finding nearest major city in the detected state
            if (!detectedCity && detectedState && relevantLocations.length > 0) {
              // Use the first major city in the state as fallback
              const majorCities = relevantLocations.filter(loc => 
                ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Hyderabad', 'Warangal', 'Nizamabad'].includes(loc.name)
              );
              
              if (majorCities.length > 0) {
                detectedCity = majorCities[0].name;
                matchedLocation = majorCities[0];
                console.log('📍 Using nearby major city:', detectedCity);
                
                // Show message that we're using nearby city
                toast({
                  title: "📍 Nearby City Selected",
                  description: `We couldn't find your exact location in our delivery areas. Using nearby ${detectedCity} instead. You can change it if needed.`,
                  variant: "default",
                  duration: 7000,
                });
              }
            }
            
            // If still no match, don't fill city (let user select from dropdown)
            if (!detectedCity) {
              console.log('⚠️ No matching delivery city found');
              const nearestCity = possibleCities[0] || 'your location';
              toast({
                title: "📍 Location Detected",
                description: `Detected ${nearestCity}, but we don't deliver there yet. Please select your city from the dropdown.`,
                variant: "default",
                duration: 6000,
              });
              // Still fill other fields
              if (detectedStreet) setStreet(detectedStreet);
              if (detectedBuilding) setBuilding(detectedBuilding);
              if (detectedState) setState(detectedState);
              if (detectedPincode) setPincode(detectedPincode);
              setDetectingLocation(false);
              return;
            }
            
            console.log('🌍 Final location data:', {
              city: detectedCity,
              state: matchedLocation?.state || detectedState,
              pincode: detectedPincode,
              street: detectedStreet,
              building: detectedBuilding,
              deliveryCharge: matchedLocation?.charge
            });
            
            // Update form fields with detected values
            if (detectedStreet) setStreet(detectedStreet);
            if (detectedBuilding) setBuilding(detectedBuilding);
            if (detectedCity) {
              setCity(detectedCity);
              // Also set the correct state from matched location
              if (matchedLocation?.state) {
                setState(matchedLocation.state);
              }
            }
            if (detectedPincode) setPincode(detectedPincode);
            
            // Show success notification with delivery info
            toast({
              title: "✅ Location Detected Successfully!",
              description: (
                <div className="space-y-1 text-sm">
                  <div className="font-semibold text-green-600">📍 {detectedCity}, {matchedLocation?.state}</div>
                  {detectedStreet && <div>Street: {detectedStreet}</div>}
                  {matchedLocation && <div>Delivery Charge: ₹{matchedLocation.charge}</div>}
                  <div className="mt-2 text-amber-600">Please verify and adjust if needed</div>
                </div>
              ),
              duration: 8000,
            });
          }
        } catch (error) {
          console.error('Reverse geocoding error:', error);
          toast({
            title: "Location Error",
            description: "Failed to get address details. Please enter manually.",
            variant: "destructive"
          });
        } finally {
          setDetectingLocation(false);
        }
      },
      (error) => {
        setDetectingLocation(false);
        let errorMessage = "Failed to get location";
        
        switch(error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = "Location permission denied. Please enable location access in your browser.";
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = "Location information unavailable";
            break;
          case error.TIMEOUT:
            errorMessage = "Location request timed out";
            break;
        }
        
        toast({
          title: "Location Error",
          description: errorMessage,
          variant: "destructive"
        });
      },
      {
        timeout: 15000,
        maximumAge: 0,
        enableHighAccuracy: true
      }
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (cart.length === 0) {
      toast({
        title: "Cart is empty",
        description: "Please add items to cart before placing order",
        variant: "destructive"
      });
      return;
    }

    // Sync WhatsApp with phone if checkbox is checked
    const finalWhatsApp = useSameForWhatsApp ? customerPhone : customerWhatsApp;
    
    // Validate all required fields
    if (!customerName || !customerEmail || !customerPhone || !finalWhatsApp || !doorNo || !street || !city || !state || !pincode) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields",
        variant: "destructive"
      });
      return;
    }

    // Validate city exists in delivery locations
    const cityExists = deliveryLocations.some(
      loc => loc.name.toLowerCase() === city.toLowerCase() && 
             loc.state.toLowerCase() === state.toLowerCase()
    );

    if (!cityExists) {
      toast({
        title: "City Not Available",
        description: `We don't currently deliver to ${city}. Please select a city from the dropdown list.`,
        variant: "destructive"
      });
      return;
    }

    setLoading(true);

    try {
      // Prepare order data
      const orderData = {
        customer_name: customerName,
        email: customerEmail,
        phone: customerPhone,
        whatsapp_number: finalWhatsApp,
        doorNo: doorNo,
        building: building,
        street: street,
        city: city,
        state: state,
        pincode: pincode,
        location: city,
        items: cart.map(item => ({
          product_id: item.id,
          name: item.name,
          weight: item.weight || 'N/A',
          price: item.price || 0,
          quantity: item.quantity,
          image: item.image
        })),
        subtotal: cartTotal || 0,
        delivery_charge: deliveryCharge || 0,
        total: (cartTotal || 0) + (deliveryCharge || 0),
        payment_method: paymentMethod,
        payment_sub_method: paymentSubMethod,
        payment_status: paymentSettings.status === 'enabled' ? 'pending' : 'pending',
        order_status: 'pending'
      };

      // Store phone for next time
      localStorage.setItem('lastOrderPhone', customerPhone);

      // If payment is enabled, use Razorpay flow
      if (paymentSettings.status === 'enabled') {
        // Create Razorpay order FIRST (without creating our order)
        const razorpayOrderResponse = await axios.post(`${API}/payment/create-razorpay-order`, {
          amount: cartTotal + deliveryCharge,
          currency: 'INR',
          receipt: `temp_${Date.now()}`
        });

        const { razorpay_order_id, key_id } = razorpayOrderResponse.data;
        console.log('💳 Razorpay order created, showing payment modal...');

        // Initialize Razorpay
        const options = {
          key: key_id,
          amount: (cartTotal + deliveryCharge) * 100, // Amount in paise
          currency: 'INR',
          name: 'Anantha Lakshmi',
          description: 'Food Order Payment',
          order_id: razorpay_order_id,
          handler: async function (response) {
            try {
              console.log('✅ Payment successful! Creating order now...');
              
              // Create the order after successful payment
              orderData.payment_status = 'completed';
              orderData.order_status = 'confirmed';
              const orderResponse = await axios.post(`${API}/orders`, orderData);
              const { order_id, tracking_code } = orderResponse.data;

              console.log('✅ Order created:', order_id);

              // Verify and link payment to order
              await axios.post(`${API}/payment/verify-razorpay-payment`, {
                order_id: order_id,
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature
              });

              // Send WhatsApp messages to all configured numbers
              if (whatsappNumbers.length > 0) {
                sendWhatsAppMessages(orderData, order_id, tracking_code);
              }

              // Clear cart and navigate to tracking
              clearCart();
              toast({
                title: "Order Placed Successfully! 🎉",
                description: `Your order has been confirmed. Tracking code: ${tracking_code}`,
              });
              navigate(`/track-order?code=${tracking_code}`);
            } catch (error) {
              console.error('❌ Order creation failed after payment:', error);
              toast({
                title: "Order Creation Failed",
                description: "Payment was successful but order creation failed. Please contact support.",
                variant: "destructive"
              });
            }
          },
          modal: {
            ondismiss: function() {
              console.log('⚠️ Payment cancelled by user');
              toast({
                title: "Payment Cancelled",
                description: "No order was created. You can try again when ready.",
                variant: "default"
              });
              setLoading(false);
            }
          },
          prefill: {
            name: customerName,
            email: customerEmail,
            contact: customerPhone
          },
          theme: {
            color: '#f97316'
          }
        };

        const rzp = new window.Razorpay(options);
        rzp.open();
        setLoading(false);  // Reset loading after modal opens
      } else {
        // Payment disabled or removed - Create order directly and send to WhatsApp
        const orderResponse = await axios.post(`${API}/orders`, orderData);
        const { order_id, tracking_code } = orderResponse.data;

        console.log('✅ Order created (payment disabled):', order_id);

        // Send WhatsApp messages to all configured numbers
        if (whatsappNumbers.length > 0) {
          sendWhatsAppMessages(orderData, order_id, tracking_code);
        } else {
          toast({
            title: "No WhatsApp Numbers Configured",
            description: "Order created but no WhatsApp notifications will be sent. Please add WhatsApp numbers in admin panel.",
            variant: "destructive"
          });
        }

        // Clear cart and navigate to tracking
        clearCart();
        toast({
          title: "Order Placed Successfully! 🎉",
          description: `Your order has been received. Tracking code: ${tracking_code}. Order details sent via WhatsApp.`,
        });
        navigate(`/track-order?code=${tracking_code}`);
        setLoading(false);
      }

    } catch (error) {
      console.error('❌ Order placement failed:', error);
      toast({
        title: "Order Failed",
        description: error.response?.data?.detail || "Failed to place order. Please try again.",
        variant: "destructive"
      });
      setLoading(false);
    }
  };

  const handleEditWeight = (index) => {
    const item = enrichedCart[index];
    setEditingItemIndex(index);
    setSelectedWeight(item.weight);
  };

  const handleSaveWeight = (index) => {
    const item = enrichedCart[index];
    const newPrice = item.prices.find(p => p.weight === selectedWeight);
    if (newPrice) {
      updateCartItem(index, { 
        weight: newPrice.weight,
        price: newPrice.price
      });
      toast({
        title: "Weight Updated",
        description: `Changed to ${newPrice.weight}`,
      });
    }
    setEditingItemIndex(null);
    setSelectedWeight('');
  };

  const handleCancelEdit = () => {
    setEditingItemIndex(null);
    setSelectedWeight('');
  };

  const handleQuantityChange = (index, newQuantity) => {
    if (newQuantity < 1) return;
    updateCartItem(index, { quantity: newQuantity });
  };

  const handleRemoveItem = (index) => {
    removeFromCart(index);
    toast({
      title: "Item Removed",
      description: "Item has been removed from cart",
    });
    // Refresh recommendations to show different products
    setTimeout(() => fetchAllProducts(), 100);
  };

  const handleAddRecommendation = (product) => {
    // Add the first price option by default
    if (product.prices && product.prices.length > 0) {
      const selectedPrice = product.prices[0];
      addToCart(product, selectedPrice);
      toast({
        title: "Added to Cart",
        description: `${product.name} (${selectedPrice.weight}) added to cart`,
      });
      
      // Refresh recommendations to exclude newly added item
      fetchAllProducts();
    }
  };

  const total = (cartTotal || 0) + (deliveryCharge || 0);

  return (
    <div className="min-w-screen bg-gradient-to-br from-orange-50 via-white to-red-50 py-4 sm:py-8 px-2 sm:px-4 overflow-x-hidden">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-4 sm:mb-8">
          <h1 className="text-2xl sm:text-4xl font-bold text-gray-800 mb-1 sm:mb-2">
            Checkout
          </h1>
          <p className="text-gray-600 text-xs sm:text-base">Complete your order</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-8">
          {/* Left Column - Form */}
          <div className="lg:col-span-2 space-y-4 sm:space-y-6">
            {/* Previous Order Search */}
            <div className="bg-white rounded-2xl shadow-lg p-4 sm:p-6">
              <h3 className="text-base sm:text-lg font-bold text-gray-800 mb-3 sm:mb-4">Quick Fill from Previous Order</h3>
              <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
                <input
                  type="text"
                  value={previousSearchQuery}
                  onChange={(e) => setPreviousSearchQuery(e.target.value)}
                  placeholder="Enter phone number or email"
                  className="flex-1 px-3 sm:px-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm sm:text-base"
                />
                <button
                  type="button"
                  onClick={handlePreviousOrderSearch}
                  className="w-full sm:w-auto px-4 sm:px-6 py-2 sm:py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors font-medium text-sm sm:text-base whitespace-nowrap"
                >
                  Search
                </button>
              </div>

              {showPreviousResults && previousSearchResults.length > 0 && (
                <div className="mt-4 space-y-2">
                  <p className="text-xs sm:text-sm text-gray-600">Found {previousSearchResults.length} previous order(s). Click to use:</p>
                  {previousSearchResults.slice(0, 3).map((order) => (
                    <button
                      key={order.order_id}
                      type="button"
                      onClick={() => fillFromPreviousOrder(order)}
                      className="w-full text-left p-2 sm:p-3 border border-gray-200 rounded-lg hover:border-orange-400 hover:bg-orange-50 transition-all text-xs sm:text-sm"
                    >
                      <div className="font-medium text-gray-800">{order.customer_name}</div>
                      <div className="text-gray-600">
                        {order.doorNo && `${order.doorNo}, `}
                        {order.street && `${order.street}, `}
                        {order.city || order.location}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Customer Information */}
            <div className="bg-white rounded-2xl shadow-lg p-4 sm:p-6">
              <div className="flex items-center space-x-2 mb-3 sm:mb-4">
                <User className="h-4 w-4 sm:h-5 sm:w-5 text-orange-500" />
                <h3 className="text-base sm:text-lg font-bold text-gray-800">Customer Information</h3>
              </div>
              <div className="space-y-3 sm:space-y-4">
                <div>
                  <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm sm:text-base"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                    Email Address *
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-2 sm:left-3 top-2.5 sm:top-3 h-4 w-4 sm:h-5 sm:w-5 text-gray-400" />
                    <input
                      type="email"
                      value={customerEmail}
                      onChange={(e) => setCustomerEmail(e.target.value)}
                      className="w-full pl-8 sm:pl-10 pr-3 sm:pr-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm sm:text-base"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                    Phone Number * <span className="text-gray-500">(Primary Contact)</span>
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-2 sm:left-3 top-2.5 sm:top-3 h-4 w-4 sm:h-5 sm:w-5 text-gray-400" />
                    <span className="absolute left-8 sm:left-10 top-2.5 sm:top-3 text-gray-700 font-medium text-sm sm:text-base pointer-events-none">+91</span>
                    <input
                      type="tel"
                      value={customerPhone.startsWith('+91') ? customerPhone.slice(3) : customerPhone}
                      onChange={(e) => {
                        const value = e.target.value.replace(/[^0-9]/g, '');
                        const newPhone = '+91' + value;
                        setCustomerPhone(newPhone);
                        // Auto-sync with WhatsApp if checkbox is checked
                        if (useSameForWhatsApp) {
                          setCustomerWhatsApp(newPhone);
                        }
                      }}
                      placeholder="9876543210"
                      maxLength="10"
                      className="w-full pl-16 sm:pl-[4.5rem] pr-3 sm:pr-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm sm:text-base"
                      required
                    />
                  </div>
                  
                  {/* Checkbox to use same number for WhatsApp */}
                  <div className="mt-2 sm:mt-3 flex items-start space-x-2">
                    <input
                      type="checkbox"
                      id="sameWhatsApp"
                      checked={useSameForWhatsApp}
                      onChange={(e) => {
                        setUseSameForWhatsApp(e.target.checked);
                        if (e.target.checked) {
                          setCustomerWhatsApp(customerPhone);
                        }
                      }}
                      className="mt-0.5 h-4 w-4 text-green-500 border-gray-300 rounded focus:ring-green-500"
                    />
                    <label htmlFor="sameWhatsApp" className="text-xs sm:text-sm text-gray-700 cursor-pointer">
                      Use same number for WhatsApp (order updates will be sent here)
                    </label>
                  </div>
                </div>

                {/* Show separate WhatsApp field only if user unchecks the checkbox */}
                {!useSameForWhatsApp && (
                  <div>
                    <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                      WhatsApp Number *
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-2 sm:left-3 top-2.5 sm:top-3 h-4 w-4 sm:h-5 sm:w-5 text-green-500" />
                      <span className="absolute left-8 sm:left-10 top-2.5 sm:top-3 text-gray-700 font-medium text-sm sm:text-base pointer-events-none">+91</span>
                      <input
                        type="tel"
                        value={customerWhatsApp.startsWith('+91') ? customerWhatsApp.slice(3) : customerWhatsApp}
                        onChange={(e) => {
                          const value = e.target.value.replace(/[^0-9]/g, '');
                          setCustomerWhatsApp('+91' + value);
                        }}
                        placeholder="9876543210"
                        maxLength="10"
                        className="w-full pl-16 sm:pl-[4.5rem] pr-3 sm:pr-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm sm:text-base"
                        required
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Order details will be sent to this WhatsApp number</p>
                  </div>
                )}
              </div>
            </div>

            {/* Delivery Address */}
            <div className="bg-white rounded-2xl shadow-lg p-4 sm:p-6">
              <div className="flex items-center justify-between mb-3 sm:mb-4">
                <div className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4 sm:h-5 sm:w-5 text-orange-500" />
                  <h3 className="text-base sm:text-lg font-bold text-gray-800">Delivery Address</h3>
                </div>
                <button
                  type="button"
                  onClick={detectCurrentLocation}
                  disabled={detectingLocation}
                  className="flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-1.5 sm:py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-xs sm:text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Navigation className="h-3 w-3 sm:h-4 sm:w-4" />
                  <span>{detectingLocation ? 'Detecting...' : 'Detect Location'}</span>
                </button>
              </div>

              <div className="space-y-3 sm:space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3">
                  <div>
                    <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                      Door No / Flat No *
                    </label>
                    <input
                      type="text"
                      value={doorNo}
                      onChange={(e) => setDoorNo(e.target.value)}
                      placeholder="e.g., 123, A-4"
                      className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm sm:text-base"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                      Building / House Name
                    </label>
                    <input
                      type="text"
                      value={building}
                      onChange={(e) => setBuilding(e.target.value)}
                      placeholder="e.g., Sunshine Apartments"
                      className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm sm:text-base"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                    Street / Area / Landmark *
                  </label>
                  <input
                    type="text"
                    value={street}
                    onChange={(e) => setStreet(e.target.value)}
                    placeholder="e.g., MG Road, Near City Mall"
                    className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm sm:text-base"
                    required
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3">
                  <div>
                    <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                      State *
                    </label>
                    <select
                      value={state}
                      onChange={(e) => {
                        setState(e.target.value);
                        setCity(''); // Reset city when state changes
                      }}
                      className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm sm:text-base"
                      required
                    >
                      <option value="">Select State</option>
                      <option value="Andhra Pradesh">Andhra Pradesh</option>
                      <option value="Telangana">Telangana</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                      City * {state && `(${locationsByState[state]?.length || 0} cities)`}
                    </label>
                    <select
                      value={city}
                      onChange={(e) => {
                        console.log('🏙️ City selected:', e.target.value);
                        setCity(e.target.value);
                      }}
                      className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm sm:text-base"
                      required
                      disabled={!state}
                    >
                      <option value="">Select City</option>
                      {state && locationsByState[state]?.map((location, index) => (
                        <option key={`${location.name}-${location.state || state}-${index}`} value={location.name}>
                          {location.name} (₹{location.charge})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                    Pincode *
                  </label>
                  <input
                    type="text"
                    value={pincode}
                    onChange={(e) => {
                      const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                      setPincode(value);
                    }}
                    placeholder="e.g., 500001"
                    className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm sm:text-base"
                    maxLength="6"
                    required
                  />
                </div>
              </div>

              {/* Info note */}
              <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <p className="text-xs sm:text-sm text-amber-800">
                  <strong>Note:</strong> This checkout is only for ordering to existing delivery cities. If your city is not listed, please go to the homepage to request delivery in your area.
                </p>
              </div>
            </div>

          </div>

          {/* Right Column - Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg p-4 sm:p-6 sticky top-4">
              <div className="flex items-center space-x-2 mb-3 sm:mb-4">
                <ShoppingBag className="h-4 w-4 sm:h-5 sm:w-5 text-orange-500" />
                <h3 className="text-base sm:text-lg font-bold text-gray-800">Order Summary</h3>
              </div>

              {/* Cart Items */}
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {enrichedCart.map((item, index) => (
                  <div key={index} className="flex items-start gap-2 sm:gap-3 p-2 sm:p-3 border border-gray-200 rounded-lg">
                    <img 
                      src={item.image} 
                      alt={item.name}
                      className="w-12 h-12 sm:w-16 sm:h-16 object-cover rounded-lg flex-shrink-0"
                    />
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-800 text-xs sm:text-sm truncate">{item.name}</h4>
                      {editingItemIndex === index ? (
                        <div className="mt-1 sm:mt-2 flex items-center gap-1 sm:gap-2">
                          <select
                            value={selectedWeight}
                            onChange={(e) => setSelectedWeight(e.target.value)}
                            className="text-xs p-1 border border-gray-300 rounded"
                          >
                            {item.prices && Array.isArray(item.prices) && item.prices.map((price) => (
                              <option key={price.weight} value={price.weight}>
                                {price.weight} - ₹{price.price}
                              </option>
                            ))}
                          </select>
                          <button
                            onClick={() => handleSaveWeight(index)}
                            className="p-1 bg-green-500 text-white rounded hover:bg-green-600"
                          >
                            <Check className="h-3 w-3" />
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="p-1 bg-gray-500 text-white rounded hover:bg-gray-600"
                          >
                            ×
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 mt-1">
                          <p className="text-xs sm:text-sm text-gray-600">
                            {item.weight || 'N/A'}
                          </p>
                          <button
                            onClick={() => handleEditWeight(index)}
                            className="p-1 text-blue-500 hover:text-blue-700"
                            title="Change weight"
                          >
                            <Edit className="h-3 w-3" />
                          </button>
                        </div>
                      )}
                      <div className="flex items-center gap-2 mt-1 sm:mt-2">
                        <div className="flex items-center border border-gray-300 rounded">
                          <button
                            onClick={() => handleQuantityChange(index, item.quantity - 1)}
                            className="px-1.5 sm:px-2 py-0.5 sm:py-1 text-gray-600 hover:bg-gray-100 text-xs sm:text-sm"
                          >
                            −
                          </button>
                          <span className="px-1.5 sm:px-3 py-0.5 sm:py-1 border-x border-gray-300 text-xs sm:text-sm">
                            {item.quantity}
                          </span>
                          <button
                            onClick={() => handleQuantityChange(index, item.quantity + 1)}
                            className="px-1.5 sm:px-2 py-0.5 sm:py-1 text-gray-600 hover:bg-gray-100 text-xs sm:text-sm"
                          >
                            +
                          </button>
                        </div>
                        <button
                          onClick={() => handleRemoveItem(index)}
                          className="p-1 text-red-500 hover:text-red-700"
                          title="Remove item"
                        >
                          <Trash2 className="h-3 w-3 sm:h-4 sm:w-4" />
                        </button>
                      </div>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <p className="font-semibold text-gray-800 text-xs sm:text-sm">
                        ₹{((item.price || 0) * item.quantity).toFixed(2)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Price Breakdown */}
              <div className="mt-4 sm:mt-6 space-y-2 sm:space-y-3 pt-4 sm:pt-6 border-t border-gray-200">
                <div className="flex justify-between text-xs sm:text-sm">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="font-medium text-gray-800">₹{(cartTotal || 0).toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-xs sm:text-sm">
                  <span className="text-gray-600">Delivery Charge</span>
                  <span className="font-medium text-gray-800">
                    {deliveryCharge === 0 && freeDeliverySettings.enabled && (cartTotal || 0) >= freeDeliverySettings.threshold ? (
                      <span className="text-green-600">FREE</span>
                    ) : (
                      `₹${(deliveryCharge || 0).toFixed(2)}`
                    )}
                  </span>
                </div>
                {freeDeliverySettings.enabled && (cartTotal || 0) < freeDeliverySettings.threshold && deliveryCharge > 0 && (
                  <div className="text-xs text-amber-600 bg-amber-50 p-2 rounded">
                    Add ₹{(freeDeliverySettings.threshold - (cartTotal || 0)).toFixed(2)} more for free delivery!
                  </div>
                )}
                <div className="flex justify-between text-sm sm:text-lg font-bold pt-2 sm:pt-3 border-t border-gray-200">
                  <span className="text-gray-800">Total</span>
                  <span className="text-orange-600">₹{(total || 0).toFixed(2)}</span>
                </div>
              </div>

              {/* Payment Method - Conditional Display */}
              {paymentSettings.status !== 'removed' && (
                <div className="mt-4 sm:mt-6 pt-4 sm:pt-6 border-t border-gray-200">
                  <div className="flex items-center space-x-2 mb-3">
                    <Wallet className="h-4 w-4 sm:h-5 sm:w-5 text-orange-500" />
                    <h4 className="text-sm sm:text-base font-bold text-gray-800">Payment Method</h4>
                  </div>

                  {paymentSettings.status === 'enabled' ? (
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-indigo-200 rounded-xl p-3 sm:p-4">
                      <div className="flex items-start space-x-2 sm:space-x-3">
                        <CreditCard className="h-5 w-5 sm:h-6 sm:w-6 text-indigo-600 flex-shrink-0 mt-1" />
                        <div>
                          <h5 className="font-semibold text-indigo-900 mb-1 sm:mb-2 text-xs sm:text-sm">Secure Payment via Razorpay</h5>
                          <p className="text-xs text-indigo-700 mb-2">
                            After placing your order, you'll be redirected to Razorpay's secure payment gateway:
                          </p>
                          <ul className="space-y-1 text-xs text-indigo-700">
                            <li className="flex items-center space-x-1">
                              <span className="text-indigo-500">•</span>
                              <span><strong>UPI:</strong> PhonePe, Google Pay, Paytm, BHIM</span>
                            </li>
                            <li className="flex items-center space-x-1">
                              <span className="text-indigo-500">•</span>
                              <span><strong>Cards:</strong> Credit & Debit Cards</span>
                            </li>
                            <li className="flex items-center space-x-1">
                              <span className="text-indigo-500">•</span>
                              <span><strong>Net Banking & Wallets</strong></span>
                            </li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-gradient-to-br from-yellow-50 to-amber-50 border-2 border-yellow-300 rounded-xl p-3 sm:p-4">
                      <div className="flex items-start space-x-2 sm:space-x-3">
                        <CreditCard className="h-5 w-5 sm:h-6 sm:w-6 text-yellow-600 flex-shrink-0 mt-1" />
                        <div>
                          <h5 className="font-semibold text-yellow-900 mb-1 sm:mb-2 text-xs sm:text-sm">Payment Coming Soon</h5>
                          <p className="text-xs text-yellow-700">
                            Online payment is currently unavailable. Your order details will be sent to us via WhatsApp, and we'll contact you for payment arrangements.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Order Buttons - Show both buttons when payment enabled, only WhatsApp when disabled */}
              <div className="mt-4 sm:mt-6 space-y-3">
                {paymentSettings.status === 'enabled' ? (
                  // When payment is ENABLED - Show BOTH buttons
                  <>
                    <button
                      onClick={handleSubmit}
                      disabled={loading || cart.length === 0}
                      className="w-full py-2.5 sm:py-3 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-xl font-semibold hover:from-orange-600 hover:to-red-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
                    >
                      {loading ? 'Processing...' : 'Place Order & Pay Online'}
                    </button>
                    
                    <div className="flex items-center space-x-2 text-gray-500 text-sm justify-center">
                      <div className="flex-1 h-px bg-gray-300"></div>
                      <span>OR</span>
                      <div className="flex-1 h-px bg-gray-300"></div>
                    </div>
                    
                    <button
                      onClick={handleWhatsAppBooking}
                      disabled={loading || cart.length === 0}
                      className="w-full py-2.5 sm:py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl font-semibold hover:from-green-600 hover:to-green-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base flex items-center justify-center space-x-2"
                    >
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                      </svg>
                      <span>{loading ? 'Processing...' : 'Book via WhatsApp'}</span>
                    </button>
                  </>
                ) : (
                  // When payment is DISABLED - Show only WhatsApp button
                  <button
                    onClick={handleWhatsAppBooking}
                    disabled={loading || cart.length === 0}
                    className="w-full py-2.5 sm:py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl font-semibold hover:from-green-600 hover:to-green-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base flex items-center justify-center space-x-2"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                    </svg>
                    <span>{loading ? 'Processing...' : 'Book via WhatsApp'}</span>
                  </button>
                )}
              </div>
            </div>

            {/* Recommendations */}
            {recommendations.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg p-4 sm:p-6 mt-4">
                <div className="flex items-center space-x-2 mb-3 sm:mb-4">
                  <Sparkles className="h-4 w-4 sm:h-5 sm:w-5 text-orange-500" />
                  <h3 className="text-base sm:text-lg font-bold text-gray-800">You May Also Like</h3>
                </div>
                <div className="space-y-3">
                  {recommendations.map((product) => (
                    <div 
                      key={product.id}
                      className="flex items-center gap-2 sm:gap-3 p-2 sm:p-3 border border-gray-200 rounded-lg hover:border-orange-400 transition-all group"
                    >
                      <img 
                        src={product.image} 
                        alt={product.name}
                        className="w-12 h-12 sm:w-16 sm:h-16 object-cover rounded-lg flex-shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-gray-800 text-xs sm:text-sm truncate">{product.name}</h4>
                        <p className="text-xs sm:text-sm text-orange-600 font-semibold">
                          ₹{product.prices[0]?.price}
                          <span className="text-gray-500 text-xs ml-1">
                            {product.prices[0]?.weight}
                          </span>
                        </p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAddRecommendation(product);
                        }}
                        className="px-2 sm:px-4 py-1.5 sm:py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors font-medium text-xs sm:text-sm whitespace-nowrap flex-shrink-0"
                      >
                        <span className="hidden sm:inline">Add to Cart</span>
                        <span className="sm:hidden">Add</span>
                      </button>
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
}

export default Checkout;