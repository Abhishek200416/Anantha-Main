import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ShoppingCart, ArrowLeft, Share2, Copy, Star, Sparkles, TrendingUp, Percent } from 'lucide-react';
import { useCart } from '../contexts/CartContext';
import { useLanguage } from '../contexts/LanguageContext';
import { toast } from '../hooks/use-toast';
import OptimizedImage from '../components/OptimizedImage';

const ProductDetail = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPrice, setSelectedPrice] = useState(null);
  const [selectedPriceIndex, setSelectedPriceIndex] = useState(0);
  const { addToCart } = useCart();
  const { language } = useLanguage();

  useEffect(() => {
    fetchProduct();
    // Set document title and meta tags
    if (product) {
      updateMetaTags();
    }
  }, [productId, product]);

  const fetchProduct = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/products/${productId}`);
      if (response.ok) {
        const data = await response.json();
        setProduct(data);
        setSelectedPrice(data.prices[0]);
        setSelectedPriceIndex(0);
      } else {
        toast({
          title: "Product not found",
          description: "The product you're looking for doesn't exist.",
          variant: "destructive"
        });
        navigate('/');
      }
    } catch (error) {
      console.error('Error fetching product:', error);
      toast({
        title: "Error",
        description: "Failed to load product details.",
        variant: "destructive"
      });
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const updateMetaTags = () => {
    if (!product) return;
    
    const productName = language === 'te' && product.name_telugu ? product.name_telugu : product.name;
    const productDescription = language === 'te' && product.description_telugu ? product.description_telugu : product.description;
    
    // Update page title
    document.title = `${productName} - Anantha Home Foods`;
    
    // Update or create Open Graph meta tags
    updateMetaTag('og:title', productName);
    updateMetaTag('og:description', productDescription);
    updateMetaTag('og:image', product.image);
    updateMetaTag('og:url', window.location.href);
    updateMetaTag('og:type', 'product');
    
    // Twitter Card meta tags
    updateMetaTag('twitter:card', 'summary_large_image');
    updateMetaTag('twitter:title', productName);
    updateMetaTag('twitter:description', productDescription);
    updateMetaTag('twitter:image', product.image);
  };

  const updateMetaTag = (property, content) => {
    let element = document.querySelector(`meta[property="${property}"]`);
    if (!element) {
      element = document.querySelector(`meta[name="${property}"]`);
    }
    if (!element) {
      element = document.createElement('meta');
      if (property.startsWith('og:')) {
        element.setAttribute('property', property);
      } else {
        element.setAttribute('name', property);
      }
      document.head.appendChild(element);
    }
    element.setAttribute('content', content);
  };

  const getDiscountedPrice = (priceIndex) => {
    if (product.discount_active && product.discounted_prices && product.discounted_prices[priceIndex]) {
      return product.discounted_prices[priceIndex].discounted_price;
    }
    return null;
  };

  const handleAddToCart = () => {
    if (!product.out_of_stock) {
      addToCart(product, selectedPrice);
      toast({
        title: "Added to cart!",
        description: `${productName} (${selectedPrice.weight}) added successfully.`,
      });
    }
  };

  const handleShare = async () => {
    const discountedPrice = getDiscountedPrice(selectedPriceIndex);
    const finalPrice = discountedPrice || selectedPrice.price;
    const discountText = product.discount_active && product.discount_percentage 
      ? `\n🎉 ${product.discount_percentage}% OFF!` 
      : '';
    
    // Use the share endpoint URL for better preview on social media
    const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
    const shareUrl = `${backendUrl}/api/share/product/${productId}`;
    
    const shareText = `🛍️ *${productName}*

${productDescription}

💰 Price: ₹${finalPrice}${discountedPrice ? ` (was ₹${selectedPrice.price})` : ''} for ${selectedPrice.weight}${discountText}

${product.isBestSeller ? '⭐ Best Seller\n' : ''}${product.isNew ? '✨ New Product\n' : ''}
🌐 Order now from Anantha Home Foods!

🔗 ${shareUrl}

📱 WhatsApp: https://wa.me/919985116385`;

    // Check if Web Share API is supported
    if (navigator.share) {
      try {
        await navigator.share({
          title: productName,
          text: shareText,
          url: shareUrl
        });
        toast({
          title: "✅ Shared successfully!",
          description: "Product shared via your selected app.",
        });
      } catch (error) {
        if (error.name !== 'AbortError') {
          shareViaWhatsApp(shareText);
        }
      }
    } else {
      shareViaWhatsApp(shareText);
    }
  };

  const shareViaWhatsApp = (text) => {
    const encodedText = encodeURIComponent(text);
    const whatsappUrl = `https://wa.me/?text=${encodedText}`;
    window.open(whatsappUrl, '_blank');
    toast({
      title: "📱 Opening WhatsApp",
      description: "Share this product with your friends!",
    });
  };

  const handleCopyLink = async () => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
    const shareUrl = `${backendUrl}/api/share/product/${productId}`;
    
    try {
      await navigator.clipboard.writeText(shareUrl);
      toast({
        title: "✅ Link Copied!",
        description: "Product link copied to clipboard. Paste it anywhere to share!",
      });
    } catch (error) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = shareUrl;
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        toast({
          title: "✅ Link Copied!",
          description: "Product link copied to clipboard.",
        });
      } catch (err) {
        toast({
          title: "❌ Copy Failed",
          description: "Please copy the link manually: " + shareUrl,
          variant: "destructive"
        });
      }
      document.body.removeChild(textArea);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-orange-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading product...</p>
        </div>
      </div>
    );
  }

  if (!product) {
    return null;
  }

  const productName = language === 'te' && product.name_telugu ? product.name_telugu : product.name;
  const productDescription = language === 'te' && product.description_telugu ? product.description_telugu : product.description;

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-pink-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Back Button */}
        <button
          onClick={() => navigate('/')}
          className="flex items-center space-x-2 text-orange-600 hover:text-orange-700 mb-6 transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
          <span className="font-medium">Back to Products</span>
        </button>

        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
          <div className="grid md:grid-cols-2 gap-8 p-8">
            {/* Left Column - Image */}
            <div className="relative">
              {/* Badges */}
              <div className="absolute top-4 left-4 z-10 flex flex-col space-y-2">
                {product.out_of_stock && (
                  <span className="bg-gradient-to-r from-gray-700 to-gray-900 text-white px-4 py-2 rounded-full text-sm font-bold shadow-lg">
                    OUT OF STOCK
                  </span>
                )}
                {!product.out_of_stock && product.discount_active && product.discount_percentage && (
                  <span className="bg-gradient-to-r from-red-600 to-pink-600 text-white px-4 py-2 rounded-full text-sm font-bold flex items-center space-x-1 shadow-lg animate-pulse">
                    <Percent className="h-4 w-4" />
                    <span>{product.discount_percentage}% OFF</span>
                  </span>
                )}
                {!product.out_of_stock && product.isBestSeller && (
                  <span className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-4 py-2 rounded-full text-sm font-bold flex items-center space-x-1 shadow-lg">
                    <TrendingUp className="h-4 w-4" />
                    <span>Best Seller</span>
                  </span>
                )}
                {!product.out_of_stock && product.isNew && (
                  <span className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-4 py-2 rounded-full text-sm font-bold flex items-center space-x-1 shadow-lg animate-pulse">
                    <Sparkles className="h-4 w-4" />
                    <span>New</span>
                  </span>
                )}
              </div>

              {/* Pure Veg Icon */}
              <div className="absolute top-4 right-4 z-10">
                <div className="bg-white rounded-full p-2 shadow-md">
                  <div className="w-6 h-6 border-2 border-green-600 rounded-sm flex items-center justify-center">
                    <div className="w-3 h-3 bg-green-600 rounded-full"></div>
                  </div>
                </div>
              </div>

              {/* Product Image */}
              <div className="bg-gradient-to-br from-orange-100 to-red-100 rounded-xl overflow-hidden">
                <OptimizedImage
                  src={product.image}
                  alt={productName}
                  loading="eager"
                  priority={true}
                  className="w-full h-96 object-cover"
                />
              </div>
            </div>

            {/* Right Column - Details */}
            <div className="flex flex-col">
              <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">{productName}</h1>
              
              {/* Tag */}
              <div className="mb-4">
                <span className="text-sm bg-orange-100 text-orange-700 px-3 py-1 rounded-full font-medium">
                  {product.tag}
                </span>
              </div>

              <p className="text-gray-600 text-lg mb-6 leading-relaxed">{productDescription}</p>

              {/* Price Options */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Select Weight:</h3>
                <div className="flex flex-wrap gap-3">
                  {product.prices.map((priceOption, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setSelectedPrice(priceOption);
                        setSelectedPriceIndex(index);
                      }}
                      className={`px-6 py-3 rounded-lg text-base font-medium transition-all ${
                        selectedPrice.weight === priceOption.weight
                          ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg scale-105'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {priceOption.weight}
                    </button>
                  ))}
                </div>
              </div>

              {/* Price Display */}
              <div className="mb-6 p-6 bg-gradient-to-br from-orange-50 to-red-50 rounded-xl">
                {product.discount_active && getDiscountedPrice(selectedPriceIndex) ? (
                  <div>
                    <div className="flex items-center space-x-3">
                      <span className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                        ₹{Math.round(getDiscountedPrice(selectedPriceIndex))}
                      </span>
                      <span className="text-xl line-through text-gray-400">₹{selectedPrice.price}</span>
                    </div>
                    <span className="text-sm bg-red-100 text-red-700 px-3 py-1 rounded mt-2 inline-block">
                      Save {product.discount_percentage}% - You save ₹{selectedPrice.price - Math.round(getDiscountedPrice(selectedPriceIndex))}
                    </span>
                  </div>
                ) : (
                  <span className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                    ₹{selectedPrice.price}
                  </span>
                )}
                <span className="text-gray-600 text-lg ml-2">for {selectedPrice.weight}</span>
              </div>

              {/* Inventory/Stock Warning */}
              {!product.out_of_stock && product.inventory_count !== null && product.inventory_count !== undefined && (
                <div className="mb-6">
                  {product.inventory_count < 10 ? (
                    <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3">
                      <p className="text-sm font-semibold text-red-700 flex items-center space-x-2">
                        <span>⚡</span>
                        <span>Hurry! Only {product.inventory_count} left in stock</span>
                      </p>
                    </div>
                  ) : (
                    <p className="text-sm text-green-600 font-medium">
                      ✓ In Stock ({product.inventory_count} available)
                    </p>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col gap-4 mt-auto">
                <button
                  onClick={handleAddToCart}
                  disabled={product.out_of_stock}
                  className={`w-full py-4 rounded-xl font-semibold text-lg transition-all flex items-center justify-center space-x-2 shadow-lg ${
                    product.out_of_stock
                      ? 'bg-gray-400 cursor-not-allowed text-white'
                      : 'bg-gradient-to-r from-green-600 to-green-700 text-white hover:from-green-700 hover:to-green-800 transform hover:scale-105'
                  }`}
                >
                  <ShoppingCart className="h-6 w-6" />
                  <span>{product.out_of_stock ? 'Out of Stock' : 'Add to Cart'}</span>
                </button>
                
                <div className="flex gap-3">
                  <button
                    onClick={handleShare}
                    className="flex-1 py-3 rounded-xl font-semibold transition-all flex items-center justify-center space-x-2 shadow-lg bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 transform hover:scale-105"
                    title="Share this product"
                  >
                    <Share2 className="h-5 w-5" />
                    <span className="hidden sm:inline">Share</span>
                  </button>
                  
                  <button
                    onClick={handleCopyLink}
                    className="flex-1 py-3 rounded-xl font-semibold transition-all flex items-center justify-center space-x-2 shadow-lg bg-gradient-to-r from-purple-500 to-purple-600 text-white hover:from-purple-600 hover:to-purple-700 transform hover:scale-105"
                    title="Copy product link"
                  >
                    <Copy className="h-5 w-5" />
                    <span className="hidden sm:inline">Copy Link</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;
