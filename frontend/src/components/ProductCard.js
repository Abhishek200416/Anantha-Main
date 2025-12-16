import React, { useState } from 'react';
import { ShoppingCart, Star, Sparkles, TrendingUp, Percent, Share2 } from 'lucide-react';
import { useCart } from '../contexts/CartContext';
import { useLanguage } from '../contexts/LanguageContext';
import { toast } from '../hooks/use-toast';
import ProductDetailModal from './ProductDetailModal';
import OptimizedImage from './OptimizedImage';

const ProductCard = ({ product }) => {
  const [selectedPrice, setSelectedPrice] = useState(product.prices[0]);
  const [selectedPriceIndex, setSelectedPriceIndex] = useState(0);
  const [showDetailModal, setShowDetailModal] = useState(false);
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

  const handleShare = async (e) => {
    e.stopPropagation();
    
    const discountedPrice = getDiscountedPrice(selectedPriceIndex);
    const finalPrice = discountedPrice || selectedPrice.price;
    const discountText = product.discount_active && product.discount_percentage 
      ? `\n🎉 ${product.discount_percentage}% OFF!` 
      : '';
    
    // Generate product-specific URL
    const productUrl = `${window.location.origin}/product/${product.id}`;
    
    const shareText = `🛍️ *${productName}*

${productDescription}

💰 Price: ₹${finalPrice}${discountedPrice ? ` (was ₹${selectedPrice.price})` : ''} for ${selectedPrice.weight}${discountText}

${product.isBestSeller ? '⭐ Best Seller\n' : ''}${product.isNew ? '✨ New Product\n' : ''}
🌐 Order now from Anantha Home Foods!

🔗 View Product: ${productUrl}

📱 WhatsApp: https://wa.me/919985116385`;

    // Check if Web Share API is supported
    if (navigator.share) {
      try {
        await navigator.share({
          title: productName,
          text: shareText,
          url: productUrl
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
    <>
      <div 
        className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 relative group cursor-pointer"
        onClick={() => setShowDetailModal(true)}
      >
      {/* Badges */}
      <div className="absolute top-3 left-3 z-10 flex flex-col space-y-2">
        {product.out_of_stock && (
          <span className="bg-gradient-to-r from-gray-700 to-gray-900 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center space-x-1 shadow-lg">
            <span>OUT OF STOCK</span>
          </span>
        )}
        {!product.out_of_stock && product.discount_active && product.discount_percentage && (
          <span className="bg-gradient-to-r from-red-600 to-pink-600 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center space-x-1 shadow-lg animate-pulse">
            <Percent className="h-3 w-3" />
            <span>{product.discount_percentage}% OFF</span>
          </span>
        )}
        {!product.out_of_stock && product.isBestSeller && (
          <span className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center space-x-1 shadow-lg">
            <TrendingUp className="h-3 w-3" />
            <span>Best Seller</span>
          </span>
        )}
        {!product.out_of_stock && product.isNew && (
          <span className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center space-x-1 shadow-lg animate-pulse">
            <Sparkles className="h-3 w-3" />
            <span>New</span>
          </span>
        )}
      </div>

      {/* Pure Veg Icon */}
      <div className="absolute top-3 right-3 z-10">
        <div className="bg-white rounded-full p-1 shadow-md">
          <div className="w-5 h-5 border-2 border-green-600 rounded-sm flex items-center justify-center">
            <div className="w-2 h-2 bg-green-600 rounded-full"></div>
          </div>
        </div>
      </div>

      {/* Product Image - Eager Loading for Better UX */}
      <div className="relative overflow-hidden bg-gradient-to-br from-orange-50 to-red-50">
        <OptimizedImage
          src={product.image}
          alt={productName}
          loading="eager"
          priority={true}
          className="w-full h-56 object-cover group-hover:scale-110 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
      </div>

      {/* Product Info */}
      <div className="p-5">
        <h3 className="text-xl font-bold text-gray-800 mb-2 line-clamp-1">{productName}</h3>
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">{productDescription}</p>

        {/* Tag */}
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded-full font-medium">
            {product.tag}
          </span>
        </div>

        {/* Price Options */}
        <div className="mb-4">
          <div className="flex flex-wrap gap-2">
            {product.prices.map((priceOption, index) => (
              <button
                key={index}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedPrice(priceOption);
                  setSelectedPriceIndex(index);
                }}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  selectedPrice.weight === priceOption.weight
                    ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {priceOption.weight}
              </button>
            ))}
          </div>
        </div>

        {/* Price Display */}
        <div className="flex items-center justify-between mb-4">
          <div>
            {product.discount_active && getDiscountedPrice(selectedPriceIndex) ? (
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                    ₹{Math.round(getDiscountedPrice(selectedPriceIndex))}
                  </span>
                  <span className="text-sm line-through text-gray-400">₹{selectedPrice.price}</span>
                </div>
                <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded mt-1 inline-block">
                  {product.discount_percentage}% OFF
                </span>
              </div>
            ) : (
              <span className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                ₹{selectedPrice.price}
              </span>
            )}
            <span className="text-gray-500 text-sm ml-2">/{selectedPrice.weight}</span>
          </div>
        </div>

        {/* Inventory/Stock Warning */}
        {!product.out_of_stock && product.inventory_count !== null && product.inventory_count !== undefined && (
          <div className="mb-3">
            {product.inventory_count < 10 ? (
              <div className="bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                <p className="text-xs font-semibold text-red-700 flex items-center space-x-1">
                  <span>⚡</span>
                  <span>Order fast! Only {product.inventory_count} left in stock</span>
                </p>
              </div>
            ) : (
              <p className="text-xs text-green-600 font-medium">
                ✓ In Stock ({product.inventory_count} available)
              </p>
            )}
          </div>
        )}

        {/* Action Buttons - Add to Cart and Share */}
        <div className="flex gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (!product.out_of_stock) {
                handleAddToCart();
              }
            }}
            disabled={product.out_of_stock}
            className={`flex-1 py-3 rounded-xl font-semibold transition-all flex items-center justify-center space-x-2 shadow-lg ${
              product.out_of_stock
                ? 'bg-gray-400 cursor-not-allowed text-white'
                : 'bg-gradient-to-r from-green-600 to-green-700 text-white hover:from-green-700 hover:to-green-800 transform hover:scale-105'
            }`}
          >
            <ShoppingCart className="h-5 w-5" />
            <span className="hidden sm:inline">{product.out_of_stock ? 'Out of Stock' : 'Add to Cart'}</span>
            <span className="sm:hidden">{product.out_of_stock ? 'Out' : 'Add'}</span>
          </button>
          
          <button
            onClick={handleShare}
            className="py-3 px-4 rounded-xl font-semibold transition-all flex items-center justify-center space-x-2 shadow-lg bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 transform hover:scale-105"
            title="Share this product"
          >
            <Share2 className="h-5 w-5" />
            <span className="hidden sm:inline">Share</span>
          </button>
        </div>
      </div>
    </div>

    {/* Product Detail Modal */}
    {showDetailModal && (
      <ProductDetailModal 
        product={product} 
        onClose={() => setShowDetailModal(false)} 
      />
    )}
    </>
  );
};

// Wrap with React.memo to prevent unnecessary re-renders
export default React.memo(ProductCard);