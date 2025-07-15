import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { FaTwitter, FaLinkedin, FaGithub, FaEnvelope, FaMapMarkerAlt, FaPhone } from 'react-icons/fa';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-slate-900/80 backdrop-blur border-t border-white/10 mt-auto w-full">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="flex flex-col gap-4">
            <span className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">LeadTap</span>
            <span className="text-gray-400 text-sm leading-relaxed">
              Advanced Google Maps data extraction platform for businesses, researchers, and marketers.
            </span>
            <div className="flex gap-4">
              <a href="#" className="text-gray-400 hover:text-indigo-400" aria-label="Twitter"><FaTwitter size={20} /></a>
              <a href="#" className="text-gray-400 hover:text-indigo-400" aria-label="LinkedIn"><FaLinkedin size={20} /></a>
              <a href="#" className="text-gray-400 hover:text-indigo-400" aria-label="GitHub"><FaGithub size={20} /></a>
              <a href="mailto:contact@leadtap.com" className="text-gray-400 hover:text-indigo-400" aria-label="Email"><FaEnvelope size={20} /></a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="flex flex-col gap-4">
            <span className="font-bold text-white text-lg">Quick Links</span>
            <div className="flex flex-col gap-2">
              <RouterLink to="/" className="text-gray-400 hover:text-indigo-400">Home</RouterLink>
              <RouterLink to="/about" className="text-gray-400 hover:text-indigo-400">About</RouterLink>
              <RouterLink to="/pricing" className="text-gray-400 hover:text-indigo-400">Pricing</RouterLink>
              <RouterLink to="/dashboard" className="text-gray-400 hover:text-indigo-400">Dashboard</RouterLink>
            </div>
          </div>

          {/* Features */}
          <div className="flex flex-col gap-4">
            <span className="font-bold text-white text-lg">Features</span>
            <div className="flex flex-col gap-2">
              <span className="text-gray-400 text-sm">Data Extraction</span>
              <span className="text-gray-400 text-sm">Export Formats</span>
              <span className="text-gray-400 text-sm">Real-time Updates</span>
              <span className="text-gray-400 text-sm">Advanced Search</span>
            </div>
          </div>

          {/* Contact Info */}
          <div className="flex flex-col gap-4">
            <span className="font-bold text-white text-lg">Contact</span>
            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-3">
                <FaMapMarkerAlt className="text-indigo-400" />
                <span className="text-gray-400 text-sm">Colombo, Sri Lanka</span>
              </div>
              <div className="flex items-center gap-3">
                <FaPhone className="text-indigo-400" />
                <span className="text-gray-400 text-sm">+94 11 123 4567</span>
              </div>
              <div className="flex items-center gap-3">
                <FaEnvelope className="text-indigo-400" />
                <span className="text-gray-400 text-sm">contact@leadtap.com</span>
              </div>
            </div>
          </div>
        </div>

        <div className="my-8 border-t border-white/10" />

        {/* Bottom Section */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <span className="text-gray-400 text-sm">© {currentYear} LeadTap. All rights reserved.</span>
          <div className="flex gap-6">
            <a href="#" className="text-gray-400 text-sm hover:text-indigo-400">Privacy Policy</a>
            <a href="#" className="text-gray-400 text-sm hover:text-indigo-400">Terms of Service</a>
            <a href="#" className="text-gray-400 text-sm hover:text-indigo-400">Cookie Policy</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 