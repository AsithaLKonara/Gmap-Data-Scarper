import type { AppProps } from 'next/app';
import { useState, useEffect } from 'react';
import Head from 'next/head';
import '../styles/globals.css';
import { UserProvider } from '../contexts/UserContext';
import PWAInstallPrompt from '../components/PWAInstallPrompt';

export default function App({ Component, pageProps }: AppProps) {
  const [mounted, setMounted] = useState(false);
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    setMounted(true);

    // Set initial online status
    setIsOnline(navigator.onLine);

    // Listen for online/offline events
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Register service worker for PWA
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((registration) => {
          console.log('[PWA] Service Worker registered:', registration);
          
          // Check for updates
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  // New service worker available
                  console.log('[PWA] New service worker available');
                }
              });
            }
          });
        })
        .catch((error) => {
          console.error('[PWA] Service Worker registration failed:', error);
        });
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!mounted) {
    return null; // Prevent hydration mismatch
  }

  return (
    <>
      <Head>
        <meta name="application-name" content="Lead Intelligence Platform" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="Lead Intel" />
        <meta name="description" content="Advanced lead scraping and intelligence platform" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="theme-color" content="#667eea" />
        <link rel="apple-touch-icon" href="/icon-192.png" />
        <link rel="manifest" href="/manifest.json" />
        <link rel="shortcut icon" href="/favicon.ico" />
      </Head>
      <UserProvider>
        <Component {...pageProps} />
        <PWAInstallPrompt />
        {!isOnline && (
          <div className="fixed top-0 left-0 right-0 bg-orange-500 text-white text-center py-2 z-50">
            <p className="text-sm">You are currently offline. Some features may be limited.</p>
          </div>
        )}
      </UserProvider>
    </>
  );
}

