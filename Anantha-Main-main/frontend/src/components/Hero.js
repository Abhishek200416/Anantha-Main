import React from 'react';
import { Award, Sparkles, TrendingUp } from 'lucide-react';

const Hero = () => {
  return (
    <section className="relative bg-gradient-to-br from-orange-50 via-red-50 to-yellow-50 overflow-hidden">
      {/* Decorative Background */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-10 left-10 w-72 h-72 bg-orange-300 rounded-full filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-red-300 rounded-full filter blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      <div className="container mx-auto px-4 py-12 md:py-24 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          {/* Pure Veg Badge */}
          <div className="inline-flex items-center space-x-2 bg-green-100 text-green-800 px-3 py-1.5 md:px-4 md:py-2 rounded-full mb-4 md:mb-6 animate-bounce">
            <Award className="h-4 w-4 md:h-5 md:w-5" />
            <span className="font-semibold text-sm md:text-base">100% Pure Vegetarian</span>
          </div>

          {/* Main Title */}
          <h1 className="text-4xl md:text-7xl font-bold mb-3 md:mb-4">
            <span className="bg-gradient-to-r from-orange-600 via-red-600 to-orange-700 bg-clip-text text-transparent">
              Anantha Home Foods
            </span>
          </h1>

          {/* Telugu Text */}
          <p className="text-xl md:text-3xl text-gray-700 font-semibold mb-2 md:mb-4">
            అమ్మ చేతి రుచులు...
          </p>

          {/* Subtitle */}
          <p className="text-base md:text-2xl text-gray-600 mb-6 md:mb-8">
            Traditional Homemade Foods Since 2000
          </p>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-10">
            <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 md:p-6 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1">
              <Sparkles className="h-6 w-6 md:h-8 md:w-8 text-yellow-500 mx-auto mb-2 md:mb-3" />
              <h3 className="font-bold text-base md:text-lg mb-1 md:mb-2">Fresh Daily</h3>
              <p className="text-gray-600 text-xs md:text-sm">Made fresh with authentic recipes</p>
            </div>
            <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 md:p-6 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1">
              <Award className="h-6 w-6 md:h-8 md:w-8 text-orange-500 mx-auto mb-2 md:mb-3" />
              <h3 className="font-bold text-base md:text-lg mb-1 md:mb-2">Premium Quality</h3>
              <p className="text-gray-600 text-xs md:text-sm">Best ingredients, no preservatives</p>
            </div>
            <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 md:p-6 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1">
              <TrendingUp className="h-6 w-6 md:h-8 md:w-8 text-green-500 mx-auto mb-2 md:mb-3" />
              <h3 className="font-bold text-base md:text-lg mb-1 md:mb-2">Trusted Brand</h3>
              <p className="text-gray-600 text-xs md:text-sm">20+ years of excellence</p>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-3 sm:space-y-0 sm:space-x-4">
            <a 
              href="#products"
              className="w-full sm:w-auto bg-gradient-to-r from-orange-500 to-red-500 text-white px-6 md:px-8 py-3 md:py-4 rounded-full font-semibold text-base md:text-lg hover:from-orange-600 hover:to-red-600 transition-all transform hover:scale-105 shadow-lg text-center"
            >
              🛒 Shop Now
            </a>
            <a 
              href="https://chat.whatsapp.com/BA0roEDGMHPHCpuOm6EmyU"
              target="_blank"
              rel="noopener noreferrer"
              className="w-full sm:w-auto bg-white text-gray-800 px-6 md:px-8 py-3 md:py-4 rounded-full font-semibold text-base md:text-lg hover:bg-gray-100 transition-all transform hover:scale-105 shadow-lg border-2 border-gray-200 text-center"
            >
              💬 Contact Us
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;