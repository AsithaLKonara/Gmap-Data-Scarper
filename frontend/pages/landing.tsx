import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import GlassButton from '../components/ui/GlassButton';
import PricingSection from '../components/PricingSection';
import { useUser } from '../contexts/UserContext';

export default function LandingPage() {
  const router = useRouter();
  const { user, loading } = useUser();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // If user is already logged in, redirect to app
    if (user && !loading) {
      router.push('/');
    }
  }, [user, loading, router]);

  if (!mounted || loading) {
    return <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900" />;
  }

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Video Background */}
      <div className="fixed inset-0 w-full h-full pointer-events-none overflow-hidden" style={{ zIndex: 0 }}>
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover"
          style={{ 
            zIndex: 0,
            minWidth: '100%',
            minHeight: '100%',
            width: 'auto',
            height: 'auto'
          }}
        >
          <source src="/Background.mp4" type="video/mp4" />
        </video>
        {/* Dark overlay for better text readability */}
        <div 
          className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-black/60" 
          style={{ zIndex: 1 }} 
        />
      </div>
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/10 dark:bg-black/20 backdrop-blur-xl border-b border-white/20 shadow-lg" style={{ zIndex: 50 }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-white drop-shadow-lg">
                Lead Intelligence
              </h1>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <button
                onClick={() => scrollToSection('features')}
                className="text-white/90 hover:text-white transition-colors font-medium"
              >
                Features
              </button>
              <button
                onClick={() => scrollToSection('how-it-works')}
                className="text-white/90 hover:text-white transition-colors font-medium"
              >
                How It Works
              </button>
              <button
                onClick={() => scrollToSection('pricing')}
                className="text-white/90 hover:text-white transition-colors font-medium"
              >
                Pricing
              </button>
              <Link
                href="/login"
                className="text-white/90 hover:text-white transition-colors font-medium"
              >
                Sign In
              </Link>
              <Link href="/signup">
                <GlassButton variant="primary" gradient className="shadow-xl">
                  Get Started
                </GlassButton>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8" style={{ zIndex: 10 }}>
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 drop-shadow-2xl animate-fade-in">
            Extract Leads with
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 animate-gradient">
              {' '}Intelligence
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-3xl mx-auto drop-shadow-lg">
            Automatically collect and enrich lead data from Google Maps and other platforms.
            Get phone numbers, emails, and business insights in minutes.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup">
              <GlassButton variant="primary" gradient className="px-8 py-4 text-lg shadow-2xl hover:scale-105 transition-transform">
                Start Free Trial
              </GlassButton>
            </Link>
            <button
              onClick={() => scrollToSection('how-it-works')}
              className="px-8 py-4 text-lg bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl font-medium text-white hover:bg-white/20 transition-all shadow-lg hover:scale-105"
            >
              See How It Works
            </button>
          </div>
          <p className="mt-6 text-sm text-white/80">
            No credit card required • 10 leads/day free forever
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative py-20 px-4 sm:px-6 lg:px-8 bg-black/30 backdrop-blur-sm" style={{ zIndex: 10 }}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4 drop-shadow-lg">
              Everything you need to collect leads
            </h2>
            <p className="text-xl text-white/90">
              Powerful features built for modern lead generation
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl hover:bg-white/15 hover:scale-105 transition-all duration-300 hover:shadow-glow">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mb-4 shadow-lg">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Smart Scraping
              </h3>
              <p className="text-white/80">
                Automatically extract leads from Google Maps, LinkedIn, and more with intelligent queries.
              </p>
            </div>
            <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl hover:bg-white/15 hover:scale-105 transition-all duration-300 hover:shadow-glow">
              <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mb-4 shadow-lg">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Phone Extraction
              </h3>
              <p className="text-white/80">
                Automatically find and verify phone numbers from business profiles and websites.
              </p>
            </div>
            <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl hover:bg-white/15 hover:scale-105 transition-all duration-300 hover:shadow-glow">
              <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mb-4 shadow-lg">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Data Enrichment
              </h3>
              <p className="text-white/80">
                Enrich leads with additional data including emails, social profiles, and business insights.
              </p>
            </div>
            <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl hover:bg-white/15 hover:scale-105 transition-all duration-300 hover:shadow-glow">
              <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center mb-4 shadow-lg">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Export & Integrate
              </h3>
              <p className="text-white/80">
                Export leads to CSV, JSON, or Excel. Integrate with your CRM and tools.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="relative py-20 px-4 sm:px-6 lg:px-8" style={{ zIndex: 10 }}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4 drop-shadow-lg">
              How It Works
            </h2>
            <p className="text-xl text-white/90">
              Get started in minutes, not hours
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="text-center bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-8 shadow-2xl hover:bg-white/15 hover:scale-105 transition-all duration-300">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl font-bold text-white shadow-lg">
                1
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Sign Up Free
              </h3>
              <p className="text-white/80">
                Create your account in seconds. No credit card required.
              </p>
            </div>
            <div className="text-center bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-8 shadow-2xl hover:bg-white/15 hover:scale-105 transition-all duration-300">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl font-bold text-white shadow-lg">
                2
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Enter Your Query
              </h3>
              <p className="text-white/80">
                Tell us what you're looking for. We'll optimize your search queries.
              </p>
            </div>
            <div className="text-center bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-8 shadow-2xl hover:bg-white/15 hover:scale-105 transition-all duration-300">
              <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl font-bold text-white shadow-lg">
                3
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Watch It Work
              </h3>
              <p className="text-white/80">
                See leads being extracted in real-time with live browser view.
              </p>
            </div>
            <div className="text-center bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-8 shadow-2xl hover:bg-white/15 hover:scale-105 transition-all duration-300">
              <div className="w-20 h-20 bg-gradient-to-br from-orange-500 to-orange-600 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl font-bold text-white shadow-lg">
                4
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Export & Use
              </h3>
              <p className="text-white/80">
                Download your leads in your preferred format and start reaching out.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="relative py-20 px-4 sm:px-6 lg:px-8 bg-black/30 backdrop-blur-sm" style={{ zIndex: 10 }}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4 drop-shadow-lg">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-white/90">
              Choose the plan that works for you
            </p>
          </div>
          <PricingSection />
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8" style={{ zIndex: 10 }}>
        <div className="max-w-4xl mx-auto text-center bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl p-12 shadow-2xl">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4 drop-shadow-lg">
            Ready to start collecting leads?
          </h2>
          <p className="text-xl text-white/90 mb-8">
            Join thousands of users who are already extracting leads with intelligence.
          </p>
          <Link href="/signup">
            <GlassButton variant="primary" gradient className="px-8 py-4 text-lg shadow-2xl hover:scale-105 transition-transform">
              Get Started Free
            </GlassButton>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative bg-black/40 backdrop-blur-xl border-t border-white/20 text-white/80 py-12 px-4 sm:px-6 lg:px-8" style={{ zIndex: 10 }}>
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-white font-semibold mb-4">Product</h3>
              <ul className="space-y-2">
                <li><Link href="#features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Company</h3>
              <ul className="space-y-2">
                <li><Link href="/about" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="/careers" className="hover:text-white transition-colors">Careers</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Legal</h3>
              <ul className="space-y-2">
                <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-white transition-colors">Terms</Link></li>
                <li><Link href="/policy" className="hover:text-white transition-colors">Policy</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Support</h3>
              <ul className="space-y-2">
                <li><Link href="/docs" className="hover:text-white transition-colors">Documentation</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-white/20 text-center">
            <p>&copy; 2025 Lead Intelligence Platform. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

