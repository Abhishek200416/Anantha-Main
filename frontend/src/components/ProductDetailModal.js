import React, { useState } from 'react';
import { X, ShoppingCart, Star, Sparkles, TrendingUp, Percent, Share2 } from 'lucide-react';
import { useCart } from '../contexts/CartContext';
import { useLanguage } from '../contexts/LanguageContext';
import { toast } from '../hooks/use-toast';

const ProductDetailModal = ({ product, onClose }) => {
  const [selectedPrice, setSelectedPrice] = useState(product.prices[0]);
  const [selectedPriceIndex, setSelectedPriceIndex] = useState(0);
  const { addToCart } = useCart();
  const { language } = useLanguage();
  
  // Get product name and description based on language
  const productName = language === 'te' && product.name_telugu ? product.name_telugu : product.name;
  const productDescription = language === 'te' && product.description_telugu ? product.description_telugu : product.description;

  // Get discounted price if available
  const getDiscountedPrice = (priceIndex) => {
    if (product.discount_active && product.discounted_prices && product.discounted_prices[priceIndex]) {
      return product.discounted_prices[priceIndex].discounted_price;
    }
    return null;
  };

  const handleAddToCart = () => {
    addToCart(product, selectedPrice);
    toast({
      title: "Added to cart!",
      description: `${productName} (${selectedPrice.weight}) added successfully.`,
    });
  };

  const handleShare = async () => {
    const discountedPrice = getDiscountedPrice(selectedPriceIndex);
    const finalPrice = discountedPrice || selectedPrice.price;
    const discountText = product.discount_active && product.discount_percentage 
      ? `\n🎉 ${product.discount_percentage}% OFF - Save ₹${Math.round(selectedPrice.price - discountedPrice)}!` 
      : '';
    
    const shareText = `🛍️ *${productName}*

${productDescription}

💰 Price: ₹${finalPrice}${discountedPrice ? ` (was ₹${selectedPrice.price})` : ''} for ${selectedPrice.weight}${discountText}

${product.isBestSeller ? '⭐ Best Seller\n' : ''}${product.isNew ? '✨ New Product\n' : ''}🏷️ Category: ${product.category.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}

🌐 Order now from Anantha Home Foods!

🔗 Product Link: ${window.location.origin}/product/${product.id}

📱 Contact us: https://wa.me/919985116385`;

    // Check if Web Share API is supported
    if (navigator.share) {
      try {
        await navigator.share({
          title: productName,
          text: shareText,
          url: window.location.href
        });
        toast({
          title: "✅ Shared successfully!",
          description: "Product shared via your selected app.",
        });
      } catch (error) {
        // User cancelled or error occurred
        if (error.name !== 'AbortError') {
          // Fallback to WhatsApp if share fails
          shareViaWhatsApp(shareText);
        }
      }
    } else {
      // Fallback to WhatsApp for desktop browsers
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

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in" onClick={onClose}>
      <div 
        className="bg-white rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl relative transform animate-in zoom-in"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 bg-white rounded-full p-2 shadow-lg hover:bg-gray-100 transition-colors"
        >
          <X className="h-6 w-6 text-gray-600" />
        </button>

        <div className="grid md:grid-cols-2 gap-6 p-6">
          {/* Left Side - Image */}
          <div className="relative">
            {/* Badges */}
            <div className="absolute top-3 left-3 z-10 flex flex-col space-y-2">
              {product.discount_active && product.discount_percentage && (
                <span className="bg-gradient-to-r from-red-600 to-pink-600 text-white px-3 py-1.5 rounded-full text-sm font-bold flex items-center space-x-1 shadow-lg animate-pulse">
                  <Percent className="h-4 w-4" />
                  <span>{product.discount_percentage}% OFF</span>
                </span>
              )}
              {product.isBestSeller && (
                <span className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-3 py-1.5 rounded-full text-sm font-bold flex items-center space-x-1 shadow-lg">
                  <TrendingUp className="h-4 w-4" />
                  <span>Best Seller</span>
                </span>
              )}
              {product.isNew && (
                <span className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-3 py-1.5 rounded-full text-sm font-bold flex items-center space-x-1 shadow-lg animate-pulse">
                  <Sparkles className="h-4 w-4" />
                  <span>New</span>
                </span>
              )}
            </div>

            {/* Pure Veg Icon */}
            <div className="absolute top-3 right-3 z-10">
              <div className="bg-white rounded-full p-1.5 shadow-md">
                <div className="w-6 h-6 border-2 border-green-600 rounded-sm flex items-center justify-center">
                  <div className="w-2.5 h-2.5 bg-green-600 rounded-full"></div>
                </div>
              </div>
            </div>

            <img
              src={product.image}
              alt={productName}
              className="w-full h-96 object-cover rounded-2xl"
            />
          </div>

          {/* Right Side - Details */}
          <div className="flex flex-col">
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-gray-800 mb-3">{productName}</h2>
              
              {/* Tag */}
              <div className="flex items-center space-x-2 mb-4">
                <span className="text-sm bg-orange-100 text-orange-700 px-3 py-1.5 rounded-full font-medium">
                  {product.tag}
                </span>
                <span className="text-sm bg-green-100 text-green-700 px-3 py-1.5 rounded-full font-medium">
                  100% Pure Vegetarian
                </span>
              </div>

              {/* Category */}
              <p className="text-gray-600 mb-2">
                <span className="font-semibold">Category:</span> {product.category.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
              </p>

              {/* Description */}
              <div className="mb-6">
                <h3 className="font-semibold text-gray-800 mb-2">Description</h3>
                <p className="text-gray-600 leading-relaxed">{productDescription}</p>
              </div>

              {/* Price Options */}
              <div className="mb-6">
                <h3 className="font-semibold text-gray-800 mb-3">Select Weight</h3>
                <div className="flex flex-wrap gap-3">
                  {product.prices.map((priceOption, index) => {
                    const discountedPrice = getDiscountedPrice(index);
                    return (
                      <button
                        key={index}
                        onClick={() => {
                          setSelectedPrice(priceOption);
                          setSelectedPriceIndex(index);
                        }}
                        className={`px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                          selectedPrice.weight === priceOption.weight
                            ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg scale-105'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        <div className="text-center">
                          <div className="font-bold">{priceOption.weight}</div>
                          {discountedPrice ? (
                            <div className="text-xs mt-0.5">
                              <span className="font-bold">₹{Math.round(discountedPrice)}</span>
                              <span className="line-through ml-1 opacity-70">₹{priceOption.price}</span>
                            </div>
                          ) : (
                            <div className="text-xs mt-0.5">₹{priceOption.price}</div>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Price Display */}
              <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-2xl p-4 mb-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm text-gray-600 mb-1">Selected Price</p>
                    {product.discount_active && getDiscountedPrice(selectedPriceIndex) ? (
                      <div>
                        <div className="flex items-center space-x-3">
                          <span className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                            ₹{Math.round(getDiscountedPrice(selectedPriceIndex))}
                          </span>
                          <span className="text-xl line-through text-gray-400">₹{selectedPrice.price}</span>
                        </div>
                        <span className="text-sm bg-red-100 text-red-700 px-2 py-1 rounded mt-2 inline-block">
                          {product.discount_percentage}% OFF - You Save ₹{Math.round(selectedPrice.price - getDiscountedPrice(selectedPriceIndex))}
                        </span>
                      </div>
                    ) : (
                      <span className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                        ₹{selectedPrice.price}
                      </span>
                    )}
                    <span className="text-gray-600 text-lg ml-2">/ {selectedPrice.weight}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  if (!product.out_of_stock) {
                    handleAddToCart();
                  }
                }}
                disabled={product.out_of_stock}
                className={`flex-1 py-4 rounded-xl font-semibold text-lg transition-all flex items-center justify-center space-x-2 shadow-lg ${
                  product.out_of_stock
                    ? 'bg-gray-400 cursor-not-allowed text-white'
                    : 'bg-gradient-to-r from-green-600 to-green-700 text-white hover:from-green-700 hover:to-green-800 transform hover:scale-105'
                }`}
              >
                <ShoppingCart className="h-6 w-6" />
                <span>{product.out_of_stock ? 'Out of Stock' : 'Add to Cart'}</span>
              </button>
              
              <button
                onClick={handleShare}
                className="py-4 px-6 rounded-xl font-semibold text-lg transition-all flex items-center justify-center space-x-2 shadow-lg bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 transform hover:scale-105"
                title="Share this product"
              >
                <Share2 className="h-6 w-6" />
                <span>Share</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailModal;
