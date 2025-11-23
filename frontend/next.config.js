/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Performance optimizations
  compress: true,
  poweredByHeader: false,
  // Experimental features disabled to avoid dependency issues
  // experimental: {
  //   optimizeCss: true, // Requires 'critters' package
  // },
  async rewrites() {
    // In production, API calls go to the backend URL
    // In development, proxy to localhost
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Only proxy in development
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: `${apiUrl}/api/:path*`,
        },
      ];
    }
    
    return [];
  },
  images: {
    domains: ['localhost'],
    unoptimized: true, // For Vercel deployment
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
  // Experimental features for better performance
  // optimizeCss requires 'critters' package - disabled for now
  // experimental: {
  //   optimizeCss: true,
  // },
};

module.exports = nextConfig;

