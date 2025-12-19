import React from 'react';
import { Link } from 'react-router-dom';
import { Phone, Mail, MapPin, Heart } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gradient-to-br from-gray-900 to-gray-800 text-white pt-12 pb-6">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* About - First Column */}
          <div className="order-1">
            <h3 className="text-xl font-bold mb-4 text-orange-400" style={{ fontFamily: "'Poppins', sans-serif" }}>Anantha Home Foods</h3>
            <p className="text-gray-300 text-sm mb-4">
              Traditional homemade foods crafted with love and authentic recipes since 2000.
            </p>
            <div className="flex items-center space-x-2 text-sm text-gray-300">
              <div className="w-6 h-6 border-2 border-green-500 rounded-sm flex items-center justify-center">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              </div>
              <span>100% Pure Vegetarian</span>
            </div>
          </div>

          {/* Quick Links - Second Column */}
          <div className="order-2">
            <h3 className="text-lg font-bold mb-4 text-orange-400">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li><Link to="/" className="text-gray-300 hover:text-orange-400 transition-colors">Home</Link></li>
              <li><Link to="/track-order" className="text-gray-300 hover:text-orange-400 transition-colors">Track Order</Link></li>
              <li><Link to="/report-bug" className="text-gray-300 hover:text-orange-400 transition-colors">Report Bug</Link></li>
            </ul>
          </div>

          {/* Contact Info - Third Column */}
          <div className="order-3">
            <h3 className="text-lg font-bold mb-4 text-orange-400">Contact Us</h3>
            <ul className="space-y-3 text-sm">
              <li className="flex items-center space-x-2 text-gray-300">
                <Phone className="h-4 w-4" />
                <a href="tel:9985116385" className="hover:text-orange-400 transition-colors">9985116385</a>
              </li>
              <li className="flex items-center space-x-2 text-gray-300">
                <Mail className="h-4 w-4" />
                <a href="mailto:contact.ananthahomefoods@gmail.com" className="hover:text-orange-400 transition-colors">contact.ananthahomefoods@gmail.com</a>
              </li>
              <li className="flex items-start space-x-2 text-gray-300">
                <MapPin className="h-4 w-4 mt-1" />
                <span>Guntur, Andhra Pradesh</span>
              </li>
            </ul>
          </div>

          {/* Social - Fourth Column */}
          <div className="order-4">
            <h3 className="text-lg font-bold mb-4 text-orange-400">Follow Us</h3>
            <a
              href="https://chat.whatsapp.com/BA0roEDGMHPHCpuOm6EmyU"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-2 bg-green-500 text-white px-4 py-2 rounded-full hover:bg-green-600 transition-colors text-sm mb-4"
            >
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
              </svg>
              <span>WhatsApp Group</span>
            </a>
            <div className="mt-4">
              <Link to="/admin" className="text-xs text-gray-500 hover:text-gray-400 transition-colors">Admin Panel</Link>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="my-8 rounded-2xl bg-gradient-to-r from-orange-500 via-orange-600 to-red-500 p-8 text-center">
          <h3 className="text-2xl md:text-3xl font-bold text-white mb-3">Need a Website Like This?</h3>
          <p className="text-white text-sm md:text-base mb-6">Get your own professional e-commerce website for your business</p>
          <a
            href="https://docs.google.com/forms/d/e/1FAIpQLScmA2rRfJjHOEASpd6QPPAnRfbwQTZzCe_WhVzsvDIbjedeug/viewform?usp=publish-editor"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-white text-orange-600 px-8 py-3 rounded-full font-semibold hover:bg-gray-100 transition-all transform hover:scale-105 shadow-lg"
          >
            Contact Us for Your Website
          </a>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-700 pt-6 text-center">
          <p className="text-sm text-gray-400">
            © {new Date().getFullYear()} Anantha Home Foods. Made by <Heart className="inline h-4 w-4 text-red-500" /> in India.
          </p>
          <p className="text-xs text-gray-500 mt-2">
            Made by{' '}
            <a 
              href="https://docs.google.com/forms/d/e/1FAIpQLScmA2rRfJjHOEASpd6QPPAnRfbwQTZzCe_WhVzsvDIbjedeug/viewform?usp=publish-editor"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-orange-500 text-white px-3 py-1 rounded-md font-semibold hover:bg-orange-600 transition-colors"
            >
              PROMPT FORGE IN
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;