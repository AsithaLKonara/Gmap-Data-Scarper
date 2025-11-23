import { useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { login, register } from '../utils/api';
import GlassCard from '../components/ui/GlassCard';
import GlassButton from '../components/ui/GlassButton';
import GlassInput from '../components/ui/GlassInput';
import ErrorDisplay from '../components/ErrorDisplay';

export default function LoginPage() {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let response;
      if (isLogin) {
        response = await login({ email, password });
      } else {
        response = await register({ email, password, name });
      }

      // Store tokens
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      localStorage.setItem('user_email', email);

      // Redirect to dashboard
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
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

      {/* Content */}
      <div className="relative min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" style={{ zIndex: 10 }}>
        <div className="max-w-md w-full">
          {/* Back Button */}
          <Link 
            href="/landing" 
            className="inline-flex items-center text-white/90 hover:text-white mb-6 transition-colors"
          >
            <svg 
              className="w-5 h-5 mr-2" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M10 19l-7-7m0 0l7-7m-7 7h18" 
              />
            </svg>
            Back to Home
          </Link>

          <GlassCard className="p-8 bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-white mb-2 drop-shadow-lg">
                {isLogin ? 'Sign in to your account' : 'Create a new account'}
              </h2>
              <p className="text-white/80 text-sm">
                {isLogin ? 'Welcome back!' : 'Get started with Lead Intelligence'}
              </p>
            </div>
            
            <form className="space-y-6" onSubmit={handleSubmit}>
              {error && (
                <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 text-white">
                  <div className="flex items-center justify-between">
                    <p className="text-sm">{error}</p>
                    <button
                      type="button"
                      onClick={() => setError('')}
                      className="text-white/80 hover:text-white transition-colors"
                    >
                      ×
                    </button>
                  </div>
                </div>
              )}
              
              <div className="space-y-4">
                {!isLogin && (
                  <GlassInput
                    id="name"
                    name="name"
                    type="text"
                    label="Name (optional)"
                    placeholder="Your name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    darkMode={true}
                  />
                )}
                <GlassInput
                  id="email"
                  name="email"
                  type="email"
                  label="Email address"
                  placeholder="you@example.com"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  darkMode={true}
                />
                <GlassInput
                  id="password"
                  name="password"
                  type="password"
                  label="Password"
                  placeholder="••••••••"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  darkMode={true}
                />
              </div>

              <GlassButton
                type="submit"
                disabled={loading}
                variant="primary"
                gradient
                className="w-full shadow-xl"
              >
                {loading ? 'Processing...' : isLogin ? 'Sign in' : 'Sign up'}
              </GlassButton>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => setIsLogin(!isLogin)}
                  className="text-sm text-white/90 hover:text-white transition-colors"
                >
                  {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
                </button>
              </div>
            </form>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}

