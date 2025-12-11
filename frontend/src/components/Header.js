import React, { useState, useEffect } from 'react';
import { Phone, ShoppingCart, Menu, X, Download, AlertCircle, Globe } from 'lucide-react';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations/translations';
import { Link } from 'react-router-dom';
import ReportBugModal from './ReportBugModal';
import NotificationBell from './NotificationBell';

const Header = () => {
  const { getCartCount, setIsOpen } = useCart();
  const { isAuthenticated } = useAuth();
  const { language, changeLanguage } = useLanguage();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showInstallButton, setShowInstallButton] = useState(false);
  const [showReportBugModal, setShowReportBugModal] = useState(false);

  const t = (key) => getTranslation(language, key);

  useEffect(() => {
    const handler = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstallButton(true);
    };

    window.addEventListener('beforeinstallprompt', handler);

    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      setShowInstallButton(false);
    }
    
    setDeferredPrompt(null);
  };

  return (
    <>
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-orange-400 to-orange-500 text-white py-2 px-4 text-center text-sm md:text-base font-medium">
        {t('bannerText')}
      </div>

      {/* Main Header */}
      <header className="bg-white shadow-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <img 
                src="https://customer-assets.emergentagent.com/job_indian-cuisine-5/artifacts/hf2n1yv5_WhatsApp%20Image%202025-11-06%20at%2011.41.26_268c6b9c.jpg"
                alt="Anantha Lakshmi"
                className="h-12 w-12 rounded-full object-cover"
              />
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent" style={{ fontFamily: "'Poppins', sans-serif" }}>
                  {t('brandName')}
                </h1>
                <p className="text-xs text-gray-600">{t('brandTagline')}</p>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-6">
              <Link to="/" className="text-gray-700 hover:text-orange-600 font-medium transition-colors">{t('home')}</Link>
              <Link to="/track-order" className="text-gray-700 hover:text-orange-600 font-medium transition-colors">{t('trackOrder')}</Link>
              
              {/* Language Selector - Desktop (Toggle Buttons) */}
              <div className="flex items-center space-x-2 bg-gray-100 rounded-full p-1">
                <button
                  onClick={() => changeLanguage('en')}
                  className={`px-3 py-1 rounded-full text-sm font-semibold transition-all ${
                    language === 'en' 
                      ? 'bg-orange-500 text-white shadow-md' 
                      : 'text-gray-600 hover:text-orange-600'
                  }`}
                  title="English"
                >
                  EN
                </button>
                <button
                  onClick={() => changeLanguage('te')}
                  className={`px-3 py-1 rounded-full text-sm font-semibold transition-all ${
                    language === 'te' 
                      ? 'bg-orange-500 text-white shadow-md' 
                      : 'text-gray-600 hover:text-orange-600'
                  }`}
                  title="Telugu"
                >
                  TE
                </button>
                <button
                  onClick={() => changeLanguage('hi')}
                  className={`px-3 py-1 rounded-full text-sm font-semibold transition-all ${
                    language === 'hi' 
                      ? 'bg-orange-500 text-white shadow-md' 
                      : 'text-gray-600 hover:text-orange-600'
                  }`}
                  title="Hindi"
                >
                  HI
                </button>
              </div>
            </nav>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2 md:space-x-4">
              {/* Admin Notification Bell */}
              <NotificationBell />
              
              {/* Report Bug Button - Hidden on mobile, shown on desktop */}
              <button
                onClick={() => setShowReportBugModal(true)}
                className="hidden md:flex items-center space-x-2 bg-red-500 text-white px-3 py-2 rounded-full hover:bg-red-600 transition-colors text-sm font-medium shadow-md"
                title={t('reportIssue')}
              >
                <AlertCircle className="h-4 w-4" />
                <span>{t('reportIssue')}</span>
              </button>

              {/* Install App Button */}
              {showInstallButton && (
                <button
                  onClick={handleInstallClick}
                  className="hidden md:flex items-center space-x-2 bg-purple-500 text-white px-3 py-2 rounded-full hover:bg-purple-600 transition-colors"
                  title={t('install')}
                >
                  <Download className="h-4 w-4" />
                  <span className="text-sm font-medium">{t('install')}</span>
                </button>
              )}

              {/* Phone */}
              <a 
                href="tel:9985116385" 
                className="hidden md:flex items-center space-x-2 text-gray-700 hover:text-orange-600 transition-colors"
              >
                <Phone className="h-5 w-5" />
                <span className="font-medium">9985116385</span>
              </a>

              {/* WhatsApp Button */}
              <a
                href="https://chat.whatsapp.com/BA0roEDGMHPHCpuOm6EmyU"
                target="_blank"
                rel="noopener noreferrer"
                className="hidden md:flex items-center space-x-2 bg-green-500 text-white px-4 py-2 rounded-full hover:bg-green-600 transition-colors"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                </svg>
                <span className="font-medium">Join Group</span>
              </a>

              {/* Cart */}
              <button
                onClick={() => setIsOpen(true)}
                className="relative bg-orange-500 text-white p-2 rounded-full hover:bg-orange-600 transition-colors"
              >
                <ShoppingCart className="h-6 w-6" />
                {getCartCount() > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center font-bold">
                    {getCartCount()}
                  </span>
                )}
              </button>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden text-gray-700"
              >
                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>

          {/* Mobile Menu - User Friendly Order */}
          {mobileMenuOpen && (
            <nav className="md:hidden mt-4 pb-4 space-y-1 border-t pt-4">
              {/* Language Selector - Mobile */}
              <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-lg p-3 mb-3 border border-orange-200">
                <p className="text-xs text-orange-700 font-semibold mb-2 px-1 flex items-center gap-1">
                  <Globe className="h-4 w-4" />
                  {t('language')}
                </p>
                <div className="flex items-center space-x-2 bg-white rounded-full p-1 shadow-sm">
                  <button
                    onClick={() => changeLanguage('en')}
                    className={`flex-1 px-3 py-2 rounded-full text-sm font-bold transition-all ${
                      language === 'en' 
                        ? 'bg-orange-500 text-white shadow-md' 
                        : 'text-gray-600 hover:text-orange-600'
                    }`}
                  >
                    EN
                  </button>
                  <button
                    onClick={() => changeLanguage('te')}
                    className={`flex-1 px-3 py-2 rounded-full text-sm font-bold transition-all ${
                      language === 'te' 
                        ? 'bg-orange-500 text-white shadow-md' 
                        : 'text-gray-600 hover:text-orange-600'
                    }`}
                  >
                    TE
                  </button>
                  <button
                    onClick={() => changeLanguage('hi')}
                    className={`flex-1 px-3 py-2 rounded-full text-sm font-bold transition-all ${
                      language === 'hi' 
                        ? 'bg-orange-500 text-white shadow-md' 
                        : 'text-gray-600 hover:text-orange-600'
                    }`}
                  >
                    HI
                  </button>
                </div>
              </div>

              {/* Primary Navigation - Most Important Links First */}
              <div className="bg-orange-50 rounded-lg p-2 mb-3">
                <p className="text-xs text-orange-700 font-semibold mb-2 px-2">{t('quickLinks')}</p>
                <Link 
                  to="/" 
                  className="block py-3 px-4 text-gray-800 hover:bg-orange-100 font-semibold rounded-lg transition-colors text-lg"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  🏠 {t('home')}
                </Link>
                <Link 
                  to="/track-order" 
                  className="block py-3 px-4 text-gray-800 hover:bg-orange-100 font-semibold rounded-lg transition-colors text-lg"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  📦 {t('trackOrder')}
                </Link>
                {isAuthenticated && (
                  <Link 
                    to="/my-orders" 
                    className="block py-3 px-4 text-gray-800 hover:bg-orange-100 font-semibold rounded-lg transition-colors text-lg"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    📋 {t('myOrders')}
                  </Link>
                )}
              </div>

              {/* Contact Section */}
              <div className="space-y-1">
                <p className="text-xs text-gray-600 font-semibold mb-2 px-2">{t('contactUs')}</p>
                <a 
                  href="tel:9985116385" 
                  className="flex items-center space-x-3 py-2.5 px-4 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <Phone className="h-5 w-5 text-orange-600" />
                  <span className="font-medium">Call: 9985116385</span>
                </a>
                <a
                  href="https://chat.whatsapp.com/BA0roEDGMHPHCpuOm6EmyU"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-3 py-2.5 px-4 text-green-700 hover:bg-green-50 rounded-lg transition-colors"
                >
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                  </svg>
                  <span className="font-medium">{t('whatsappGroup')}</span>
                </a>
              </div>

              {/* Report Bug Section */}
              <div className="space-y-1 pt-2">
                <p className="text-xs text-gray-600 font-semibold mb-2 px-2">{t('helpSupport')}</p>
                <button
                  onClick={() => {
                    setShowReportBugModal(true);
                    setMobileMenuOpen(false);
                  }}
                  className="flex items-center space-x-3 py-2.5 px-4 text-red-600 hover:bg-red-50 rounded-lg transition-colors w-full"
                >
                  <AlertCircle className="h-5 w-5" />
                  <span className="font-medium">{t('reportBug')}</span>
                </button>
              </div>

              {/* Install App Button */}
              {showInstallButton && (
                <div className="pt-2">
                  <button
                    onClick={handleInstallClick}
                    className="flex items-center justify-center space-x-2 py-3 px-4 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors w-full font-medium"
                  >
                    <Download className="h-5 w-5" />
                    <span>{t('installApp')}</span>
                  </button>
                </div>
              )}

              {/* Made by PROMPT FORGE IN */}
              <div className="pt-2 border-t mt-2">
                <a
                  href="https://docs.google.com/forms/d/e/1FAIpQLScmA2rRfJjHOEASpd6QPPAnRfbwQTZzCe_WhVzsvDIbjedeug/viewform?usp=publish-editor"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center space-x-1 py-2 text-blue-600 hover:text-blue-700 font-medium text-sm"
                >
                  <span>Made by</span>
                  <span className="font-bold">PROMPT FORGE IN</span>
                </a>
              </div>
            </nav>
          )}
        </div>
      </header>

      {/* Report Bug Modal */}
      <ReportBugModal 
        isOpen={showReportBugModal}
        onClose={() => setShowReportBugModal(false)}
      />
    </>
  );
};

export default Header;