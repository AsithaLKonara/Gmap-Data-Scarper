import React, { useEffect } from 'react';

const TAWK_TO_PROPERTY_ID = 'YOUR_TAWKTO_PROPERTY_ID'; // Replace with your real property ID
const TAWK_TO_WIDGET_ID = 'YOUR_TAWKTO_WIDGET_ID'; // Replace with your real widget ID

const LiveChatWidget: React.FC = () => {
  useEffect(() => {
    if (process.env.NODE_ENV !== 'production') return;
    if (window.Tawk_API) return;
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://embed.tawk.to/${TAWK_TO_PROPERTY_ID}/${TAWK_TO_WIDGET_ID}`;
    script.charset = 'UTF-8';
    script.setAttribute('crossorigin', '*');
    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    };
  }, []);
  return null;
};

export default LiveChatWidget; 