import React, { useState, useEffect, useMemo, useCallback } from 'react';
import CategoryFilter from '../components/CategoryFilter';
import ProductCard from '../components/ProductCard';
import ProductDetailModal from '../components/ProductDetailModal';
import AddCityModal from '../components/AddCityModal';
import { useAdmin } from '../contexts/AdminContext';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations/translations';
import { Sparkles, X, ArrowRight, MapPin, Plus, Globe } from 'lucide-react';
import axios from 'axios';
import imagePreloader from '../utils/imagePreloader';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedState, setSelectedState] = useState('all');
  const [selectedCity, setSelectedCity] = useState('');
  const [autoDetectedCity, setAutoDetectedCity] = useState('');
  const [showFestivalPopup, setShowFestivalPopup] = useState(false);
  const [showBestSellerPopup, setShowBestSellerPopup] = useState(false);
  const [selectedPopupProduct, setSelectedPopupProduct] = useState(null);
  const [allProducts, setAllProducts] = useState([]);
  const { products: contextProducts, festivalProduct, deliveryLocations } = useAdmin();
  const { language, changeLanguage } = useLanguage();

  const [detectingLocation, setDetectingLocation] = useState(false);
  const [showAddCityModal, setShowAddCityModal] = useState(false);
  const [locationNotification, setLocationNotification] = useState(null);
  const [loadingProducts, setLoadingProducts] = useState(true);
  const [imagesLoaded, setImagesLoaded] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const t = (key) => getTranslation(language, key);

  // Show custom location notification (memoized)
  const showLocationNotification = useCallback((message, type = 'success', city = null) => {
    setLocationNotification({ message, type, city });
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      setLocationNotification(null);
    }, 5000);
  }, []);

  // Improved location detection function with custom notifications (memoized)
  const detectLocation = useCallback(async () => {
    if (!('geolocation' in navigator)) {
      showLocationNotification('Geolocation is not supported by your browser', 'error');
      return;
    }

    setDetectingLocation(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          console.log('📍 Coordinates:', latitude, longitude);
          
          // Use OpenStreetMap Nominatim for reverse geocoding
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
          
          const addr = data.address;
          
          // Get state to help narrow down cities
          const detectedState = addr.state;
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
          
          console.log('🏙️ Possible cities from location:', possibleCities);
          console.log('📍 Our delivery cities:', deliveryLocations.map(l => `${l.name}, ${l.state}`));
          
          let matchedCity = '';
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
              matchedCity = exactMatch.name;
              matchedLocation = exactMatch;
              console.log('✅ Exact match found:', matchedCity, ',', exactMatch.state);
              break;
            }
          }
          
          // If no exact match, try partial match
          if (!matchedCity) {
            for (const possibleCity of possibleCities) {
              const partialMatch = relevantLocations.find(
                loc => 
                  loc.name.toLowerCase().includes(possibleCity.toLowerCase()) ||
                  possibleCity.toLowerCase().includes(loc.name.toLowerCase())
              );
              
              if (partialMatch) {
                matchedCity = partialMatch.name;
                matchedLocation = partialMatch;
                console.log('✅ Partial match found:', matchedCity, ',', partialMatch.state);
                break;
              }
            }
          }
          
          // If still no match, try finding nearest city by checking all locations in the detected state
          if (!matchedCity && detectedState && relevantLocations.length > 0) {
            // Use the first major city in the state as fallback
            const majorCities = relevantLocations.filter(loc => 
              ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Hyderabad', 'Warangal', 'Nizamabad'].includes(loc.name)
            );
            
            if (majorCities.length > 0) {
              matchedCity = majorCities[0].name;
              matchedLocation = majorCities[0];
              console.log('📍 Using major city as fallback:', matchedCity);
            } else if (relevantLocations.length > 0) {
              // Just use first city in the state
              matchedCity = relevantLocations[0].name;
              matchedLocation = relevantLocations[0];
              console.log('📍 Using first available city in state:', matchedCity);
            }
          }
          
          if (matchedCity && matchedLocation) {
            setAutoDetectedCity(matchedCity);
            setSelectedCity(matchedCity);
            setSelectedState(matchedLocation.state);
            
            // Show custom notification instead of alert
            showLocationNotification(
              `Location detected! Now showing products available in ${matchedCity}, ${matchedLocation.state}`, 
              'success', 
              `${matchedCity}, ${matchedLocation.state}`
            );
          } else {
            const nearestCity = possibleCities[0] || 'your area';
            const detectedArea = detectedState ? `${nearestCity} (${detectedState})` : nearestCity;
            // Show custom notification for areas not in delivery
            showLocationNotification(
              `Detected ${detectedArea}, but we don't deliver there yet. Please select your city manually.`, 
              'warning', 
              detectedArea
            );
          }
        } catch (error) {
          console.error('Location detection error:', error);
          showLocationNotification('Failed to detect location. Please select your city manually.', 'error');
        } finally {
          setDetectingLocation(false);
        }
      },
      (error) => {
        console.error('Geolocation error:', error);
        setDetectingLocation(false);
        
        let errorMessage = 'Unable to detect your location. ';
        if (error.code === error.PERMISSION_DENIED) {
          errorMessage = 'Please allow location access in your browser settings.';
        } else if (error.code === error.POSITION_UNAVAILABLE) {
          errorMessage = 'Location information is unavailable.';
        } else if (error.code === error.TIMEOUT) {
          errorMessage = 'Location request timed out.';
        }
        showLocationNotification(errorMessage, 'error');
      },
      { 
        timeout: 15000, 
        maximumAge: 0,
        enableHighAccuracy: true 
      }
    );
  }, [deliveryLocations, showLocationNotification]);

  // Auto-detect location on page load (only once)
  useEffect(() => {
    if (!sessionStorage.getItem('locationDetected') && deliveryLocations.length > 0) {
      // Don't auto-detect on page load, let user trigger it
      // detectLocation();
      sessionStorage.setItem('locationDetected', 'true');
    }
  }, [deliveryLocations]);

  // Fetch products based on selected city and state
  useEffect(() => {
    const fetchProducts = async () => {
      setLoadingProducts(true);
      setImagesLoaded(false);
      
      try {
        let url = `${API}/products`;
        const params = new URLSearchParams();
        
        if (selectedCity) {
          params.append('city', selectedCity);
        } else if (selectedState && selectedState !== 'all') {
          params.append('state', selectedState);
        }
        
        if (params.toString()) {
          url += `?${params.toString()}`;
        }
        
        const response = await axios.get(url);
        const productsData = response.data || [];
        
        // Preload ALL product images BEFORE showing products
        if (productsData.length > 0) {
          const imageUrls = productsData
            .filter(p => p.image)
            .map(p => p.image);
          
          console.log('🖼️ Starting to preload', imageUrls.length, 'product images...');
          
          // Preload all images and wait for completion
          await imagePreloader.preloadImages(imageUrls);
          console.log('✅ All', imagePreloader.getCacheSize(), 'product images preloaded!');
          
          // Now set products AFTER images are loaded
          setAllProducts(productsData);
          setImagesLoaded(true);
        } else {
          setAllProducts(productsData);
          setImagesLoaded(true);
        }
      } catch (error) {
        console.error('Error fetching products:', error);
        setAllProducts(contextProducts);
        setImagesLoaded(true);
      } finally {
        setLoadingProducts(false);
      }
    };
    fetchProducts();
  }, [selectedCity, selectedState, contextProducts]);

  // Use allProducts instead of contextProducts
  const products = allProducts.length > 0 ? allProducts : contextProducts;

  // Show festival popup on load if set
  useEffect(() => {
    if (festivalProduct && !sessionStorage.getItem('festivalPopupShown')) {
      // Add a small delay to ensure products are loaded
      setTimeout(() => {
        setShowFestivalPopup(true);
        sessionStorage.setItem('festivalPopupShown', 'true');
      }, 500);
    }
  }, [festivalProduct]);

  // Show best seller popup
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!sessionStorage.getItem('bestSellerPopupShown')) {
        setShowBestSellerPopup(true);
        sessionStorage.setItem('bestSellerPopupShown', 'true');
      }
    }, 5000);
    return () => clearTimeout(timer);
  }, []);

  // Memoize filtered products with smart ordering
  const filteredProducts = useMemo(() => {
    let categoryFiltered = selectedCategory === 'all'
      ? products
      : products.filter(p => p.category === selectedCategory);
    
    // Sort products: Best Sellers first, then Festival, then others (random)
    const bestSellers = categoryFiltered.filter(p => p.isBestSeller && !p.isFestival);
    const festivalProducts = categoryFiltered.filter(p => p.isFestival);
    const regularProducts = categoryFiltered.filter(p => !p.isBestSeller && !p.isFestival);
    
    // Shuffle regular products randomly
    const shuffledRegular = [...regularProducts].sort(() => Math.random() - 0.5);
    
    // Combine: Best Sellers → Festival → Random Regular
    return [...bestSellers, ...festivalProducts, ...shuffledRegular];
  }, [products, selectedCategory]);

  // Memoize best sellers to prevent unnecessary filtering
  const bestSellers = useMemo(() => {
    return products.filter(p => p.isBestSeller).slice(0, 3);
  }, [products]);

  const handleViewProduct = (product) => {
    setShowFestivalPopup(false);
    setShowBestSellerPopup(false);
    // Open product detail modal instead of scrolling
    setSelectedPopupProduct(product);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50">
      {/* Custom Location Notification */}
      {locationNotification && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 animate-slide-down">
          <div className={`
            flex items-start space-x-3 p-4 rounded-xl shadow-2xl backdrop-blur-sm border-2
            ${locationNotification.type === 'success' 
              ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-300' 
              : locationNotification.type === 'warning'
              ? 'bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-300'
              : 'bg-gradient-to-r from-red-50 to-pink-50 border-red-300'
            }
            max-w-md mx-4 min-w-[300px] sm:min-w-[400px]
          `}>
            {/* Icon */}
            <div className={`
              flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center
              ${locationNotification.type === 'success'
                ? 'bg-green-500'
                : locationNotification.type === 'warning'
                ? 'bg-yellow-500'
                : 'bg-red-500'
              }
            `}>
              {locationNotification.type === 'success' ? (
                <MapPin className="w-5 h-5 text-white" />
              ) : (
                <span className="text-white text-xl">⚠️</span>
              )}
            </div>
            
            {/* Content */}
            <div className="flex-1">
              <div className={`
                font-semibold text-sm
                ${locationNotification.type === 'success'
                  ? 'text-green-900'
                  : locationNotification.type === 'warning'
                  ? 'text-yellow-900'
                  : 'text-red-900'
                }
              `}>
                {locationNotification.city && locationNotification.type === 'success' && (
                  <span className="text-lg">📍 {locationNotification.city}</span>
                )}
              </div>
              <p className={`
                text-sm mt-1
                ${locationNotification.type === 'success'
                  ? 'text-green-700'
                  : locationNotification.type === 'warning'
                  ? 'text-yellow-700'
                  : 'text-red-700'
                }
              `}>
                {locationNotification.message}
              </p>
            </div>
            
            {/* Close button */}
            <button
              onClick={() => setLocationNotification(null)}
              className={`
                flex-shrink-0 p-1 rounded-lg hover:bg-white/50 transition-colors
                ${locationNotification.type === 'success'
                  ? 'text-green-600'
                  : locationNotification.type === 'warning'
                  ? 'text-yellow-600'
                  : 'text-red-600'
                }
              `}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Hero Section */}
      <section className="relative py-8 md:py-20 px-4 overflow-hidden">
        <div className="container mx-auto text-center">
          {/* Language Selector - Mobile Only (Above Hero Title) */}
          <div className="md:hidden flex justify-end mb-6">
            <div className="inline-flex items-center space-x-2 bg-white rounded-full p-1 shadow-lg border-2 border-orange-200">
              <button
                onClick={() => changeLanguage('en')}
                className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                  language === 'en' 
                    ? 'bg-orange-500 text-white shadow-md' 
                    : 'text-gray-600'
                }`}
              >
                EN
              </button>
              <button
                onClick={() => changeLanguage('te')}
                className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                  language === 'te' 
                    ? 'bg-orange-500 text-white shadow-md' 
                    : 'text-gray-600'
                }`}
              >
                TE
              </button>
              <button
                onClick={() => changeLanguage('hi')}
                className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                  language === 'hi' 
                    ? 'bg-orange-500 text-white shadow-md' 
                    : 'text-gray-600'
                }`}
              >
                HI
              </button>
            </div>
          </div>

          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent mb-6" style={{ fontFamily: "'Poppins', sans-serif" }}>
            {t('heroTitle')}
          </h1>
          <p className="text-lg md:text-xl text-gray-600 mb-8">{t('heroSubtitle')}</p>
        </div>
      </section>

      {/* Products Section */}
      <section id="products" className="container mx-auto px-4 pb-20 pt-8">
        <div className="mb-6">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mb-2">{t('ourProducts')}</h2>
          <p className="text-gray-600 text-sm md:text-base">{t('browseProducts')}</p>
        </div>
        
        {/* City Filter with Auto-detect button */}
        <div className="mb-6 bg-gradient-to-r from-orange-50 to-red-50 rounded-xl shadow-md border border-orange-200 p-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 flex-wrap">
            {/* Filter Label */}
            <div className="flex items-center gap-2 text-gray-700 font-semibold">
              <MapPin className="h-5 w-5 text-orange-600" />
              <span>{t('filterByLocation')}</span>
            </div>

            {/* State Filter */}
            <select
              value={selectedState}
              onChange={(e) => {
                setSelectedState(e.target.value);
                setSelectedCity(''); // Reset city when state changes
              }}
              className="px-4 py-2 border-2 border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white font-medium shadow-sm"
            >
              <option value="all">{t('allStates')}</option>
              {[...new Set(deliveryLocations.map(l => l.state))].sort().map((state) => (
                <option key={state} value={state}>{state}</option>
              ))}
            </select>

            {/* City Filter */}
            <select
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              className="px-4 py-2 border-2 border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white font-medium shadow-sm"
            >
              <option value="">{t('allCities')}</option>
              {[...new Set(
                deliveryLocations
                  .filter(location => selectedState === 'all' || location.state === selectedState)
                  .map(location => location.name)
              )].sort().map((cityName) => (
                <option key={cityName} value={cityName}>
                  {cityName}
                </option>
              ))}
            </select>

            {/* Detect Location Button */}
            <button
              onClick={detectLocation}
              disabled={detectingLocation}
              className="px-5 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:from-orange-600 hover:to-red-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-md flex items-center gap-2 whitespace-nowrap"
            >
              <MapPin className="h-4 w-4" />
              <span>{detectingLocation ? t('detecting') : t('detectMyLocation')}</span>
            </button>

            {/* Add My City Button */}
            <button
              onClick={() => setShowAddCityModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 transition-all font-medium shadow-md"
            >
              <Plus className="h-4 w-4" />
              <span className="hidden sm:inline">{t('cityNotFound')}</span>
              <span className="sm:hidden">{t('addCity')}</span>
            </button>

            {/* Status - Inline */}
            {selectedCity && (
              <span className="text-sm text-orange-700 bg-white px-3 py-2 rounded-lg border border-orange-300 font-medium shadow-sm">
                📍 Showing: {selectedCity}
              </span>
            )}
          </div>
        </div>

        {/* Add City Modal */}
        <AddCityModal 
          isOpen={showAddCityModal}
          onClose={() => setShowAddCityModal(false)}
          preSelectedState={selectedState !== 'all' ? selectedState : ''}
        />
        
        <CategoryFilter selectedCategory={selectedCategory} onSelectCategory={setSelectedCategory} />
        
        {/* Loading State - Show while products/images are loading */}
        {loadingProducts && (
          <div className="flex flex-col items-center justify-center py-16 md:py-24">
            <div className="relative">
              <div className="w-16 h-16 md:w-20 md:h-20 border-4 border-orange-200 border-t-orange-600 rounded-full animate-spin"></div>
              <div className="absolute inset-0 w-16 h-16 md:w-20 md:h-20 border-4 border-transparent border-b-red-600 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1s' }}></div>
            </div>
            <p className="mt-6 text-gray-600 text-base md:text-lg font-medium animate-pulse">Loading delicious products...</p>
            <p className="mt-2 text-gray-400 text-sm">Please wait while we prepare everything for you</p>
          </div>
        )}

        {/* Products Grid - Show only after loading */}
        {!loadingProducts && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-6 mt-6 md:mt-8">
              {filteredProducts.map((product) => (
                <div key={product.id} id={`product-${product.id}`}>
                  <ProductCard product={product} />
                </div>
              ))}
            </div>

            {filteredProducts.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500 text-base md:text-lg">No products found in this category.</p>
              </div>
            )}
          </>
        )}
      </section>

      {/* Festival Product Popup */}
      {showFestivalPopup && festivalProduct && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in">
          <div className="bg-white rounded-2xl md:rounded-3xl max-w-md w-full p-4 md:p-6 shadow-2xl relative transform animate-in zoom-in max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setShowFestivalPopup(false)}
              className="absolute top-3 right-3 md:top-4 md:right-4 text-gray-500 hover:text-gray-700 z-10 bg-white rounded-full p-1"
            >
              <X className="h-5 w-5 md:h-6 md:w-6" />
            </button>
            
            <div className="text-center">
              <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-3 py-1.5 md:px-4 md:py-2 rounded-full inline-flex items-center space-x-2 mb-3 md:mb-4 animate-bounce text-sm md:text-base">
                <Sparkles className="h-4 w-4 md:h-5 md:w-5" />
                <span className="font-bold">Festival Special!</span>
              </div>
              
              <img 
                src={festivalProduct.image} 
                alt={festivalProduct.name}
                className="w-full h-48 md:h-64 object-cover rounded-xl md:rounded-2xl mb-3 md:mb-4 shadow-lg"
              />
              
              <h2 className="text-xl md:text-2xl font-bold text-gray-800 mb-2">{festivalProduct.name}</h2>
              <p className="text-gray-600 mb-3 md:mb-4 text-sm md:text-base">{festivalProduct.description}</p>
              <p className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent mb-4 md:mb-6">
                ₹{festivalProduct.prices[0]?.price}
              </p>
              
              <button
                onClick={() => handleViewProduct(festivalProduct)}
                className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white py-2.5 md:py-3 rounded-xl font-semibold hover:from-orange-600 hover:to-red-600 transition-all flex items-center justify-center space-x-2 text-sm md:text-base"
              >
                <span>View Product</span>
                <ArrowRight className="h-4 w-4 md:h-5 md:w-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Best Seller Popup */}
      {showBestSellerPopup && bestSellers.length > 0 && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in">
          <div className="bg-white rounded-2xl md:rounded-3xl max-w-2xl w-full p-4 md:p-6 shadow-2xl relative transform animate-in zoom-in max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setShowBestSellerPopup(false)}
              className="absolute top-3 right-3 md:top-4 md:right-4 text-gray-500 hover:text-gray-700 z-10 bg-white rounded-full p-1"
            >
              <X className="h-5 w-5 md:h-6 md:w-6" />
            </button>
            
            <div className="text-center mb-4 md:mb-6">
              <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-3 py-1.5 md:px-4 md:py-2 rounded-full inline-flex items-center space-x-2 mb-3 md:mb-4">
                <Sparkles className="h-4 w-4 md:h-5 md:w-5" />
                <span className="font-bold text-sm md:text-base">Our Best Sellers!</span>
              </div>
              <p className="text-gray-600 text-sm md:text-base">Check out our most popular products</p>
            </div>
            
            <div className="grid grid-cols-3 gap-2 md:gap-4 mb-4 md:mb-6">
              {bestSellers.map(product => (
                <div key={product.id} className="group cursor-pointer" onClick={() => handleViewProduct(product)}>
                  <div className="relative overflow-hidden rounded-lg md:rounded-xl shadow-md group-hover:shadow-xl transition-shadow">
                    <img 
                      src={product.image} 
                      alt={product.name}
                      className="w-full h-24 md:h-32 object-cover group-hover:scale-110 transition-transform duration-300"
                    />
                  </div>
                  <h3 className="text-xs md:text-sm font-semibold text-gray-800 mt-2 text-center line-clamp-2">{product.name}</h3>
                  <p className="text-orange-600 font-bold text-sm md:text-base text-center">₹{product.prices[0]?.price}</p>
                </div>
              ))}
            </div>
            
            <button
              onClick={() => setShowBestSellerPopup(false)}
              className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white py-2.5 md:py-3 rounded-xl font-semibold hover:from-orange-600 hover:to-red-600 transition-all flex items-center justify-center space-x-2 text-sm md:text-base"
            >
              <span>Start Shopping</span>
              <ArrowRight className="h-4 w-4 md:h-5 md:w-5" />
            </button>
          </div>
        </div>
      )}

      {/* Product Detail Modal */}
      {selectedPopupProduct && (
        <ProductDetailModal 
          product={selectedPopupProduct} 
          isOpen={!!selectedPopupProduct}
          onClose={() => setSelectedPopupProduct(null)}
        />
      )}
    </div>
  );
};

export default Home;
