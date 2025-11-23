import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import GlassButton from '../components/ui/GlassButton';
import GlassInput from '../components/ui/GlassInput';
import GlassCard from '../components/ui/GlassCard';
import { useUser } from '../contexts/UserContext';
import { showToast } from '../utils/toast';

export default function SignUpPage() {
  const router = useRouter();
  const { user, login } = useUser();
  const [mounted, setMounted] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    plan: 'free' as 'free' | 'monthly' | 'usage',
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    setMounted(true);
    // Get plan from query params
    const planParam = router.query.plan as string;
    if (planParam && ['free', 'monthly', 'usage'].includes(planParam)) {
      setFormData(prev => ({ ...prev, plan: planParam as 'free' | 'monthly' | 'usage' }));
    }
    // If user is already logged in, redirect to app
    if (user) {
      router.push('/');
    }
  }, [router, user]);

  if (!mounted) {
    return <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900" />;
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const planTypeMap: Record<string, string> = {
        'free': 'free',
        'monthly': 'paid_monthly',
        'usage': 'paid_usage',
      };
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          plan_type: planTypeMap[formData.plan] || 'free',
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Sign up failed');
      }

      const data = await response.json();
      
      // Auto-login after signup
      await login(formData.email, formData.password);
      
      showToast('Account created successfully!', 'success');
      
      // Redirect based on plan
      if (formData.plan !== 'free') {
        // Redirect to payment/upgrade flow
        router.push(`/upgrade?plan=${formData.plan}`);
      } else {
        // Redirect to app
        router.push('/');
      }
    } catch (error: any) {
      showToast(error.message || 'Sign up failed. Please try again.', 'error');
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
      <div className="relative min-h-screen flex items-center justify-center px-4 py-12" style={{ zIndex: 10 }}>
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

          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2 drop-shadow-lg">
              Create Your Account
            </h1>
            <p className="text-white/80">
              Start collecting leads in minutes
            </p>
          </div>

          <GlassCard className="p-8 bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Plan Selection */}
              <div>
                <label className="block text-sm font-medium text-white/90 mb-2">
                  Choose Your Plan
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['free', 'monthly', 'usage'] as const).map((plan) => (
                    <button
                      key={plan}
                      type="button"
                      onClick={() => setFormData(prev => ({ ...prev, plan }))}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                        formData.plan === plan
                          ? 'bg-blue-500 text-white shadow-lg'
                          : 'bg-white/10 backdrop-blur-sm border border-white/20 text-white/90 hover:bg-white/20'
                      }`}
                    >
                      {plan === 'free' ? 'Free' : plan === 'monthly' ? 'Monthly' : 'Pay/Lead'}
                    </button>
                  ))}
                </div>
                <p className="mt-2 text-xs text-white/80">
                  {formData.plan === 'free' && '10 leads/day • Free forever'}
                  {formData.plan === 'monthly' && '$29/month • Unlimited leads'}
                  {formData.plan === 'usage' && '$0.50/lead • Pay as you go'}
                </p>
              </div>

              {/* Email */}
              <div>
                <GlassInput
                  id="email"
                  type="email"
                  label="Email"
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="you@example.com"
                  className="w-full"
                  required
                  darkMode={true}
                  error={errors.email}
                />
              </div>

              {/* Password */}
              <div>
                <GlassInput
                  id="password"
                  type="password"
                  label="Password"
                  value={formData.password}
                  onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                  placeholder="At least 8 characters"
                  className="w-full"
                  required
                  darkMode={true}
                  error={errors.password}
                />
              </div>

              {/* Confirm Password */}
              <div>
                <GlassInput
                  id="confirmPassword"
                  type="password"
                  label="Confirm Password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                  placeholder="Re-enter your password"
                  className="w-full"
                  required
                  darkMode={true}
                  error={errors.confirmPassword}
                />
              </div>

              {/* Submit Button */}
              <GlassButton
                type="submit"
                variant="primary"
                gradient
                className="w-full shadow-xl"
                disabled={loading}
              >
                {loading ? 'Creating Account...' : 'Create Account'}
              </GlassButton>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-white/90">
                Already have an account?{' '}
                <Link href="/login" className="text-white hover:text-white/80 font-medium transition-colors">
                  Sign in
                </Link>
              </p>
            </div>
          </GlassCard>

        <div className="mt-6 text-center text-sm text-white/80">
          By signing up, you agree to our{' '}
          <Link href="/terms" className="text-white hover:text-white/80 underline transition-colors">
            Terms of Service
          </Link>{' '}
          and{' '}
          <Link href="/privacy" className="text-white hover:text-white/80 underline transition-colors">
            Privacy Policy
          </Link>
        </div>
      </div>
    </div>
  );
}

