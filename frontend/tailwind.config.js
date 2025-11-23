/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#007AFF',
          dark: '#0051D5',
          light: '#5AC8FA',
        },
        secondary: {
          DEFAULT: '#5856D6',
          light: '#AF52DE',
        },
        success: '#34C759',
        warning: '#FF9500',
        error: '#FF3B30',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'gradient-secondary': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'gradient-success': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'gradient-warm': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
        'gradient-cool': 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
        'gradient-purple': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
      },
      backdropBlur: {
        xs: '2px',
        sm: '8px',
        md: '16px',
        lg: '24px',
        xl: '40px',
      },
      boxShadow: {
        'glass-sm': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'glass-md': '0 4px 16px rgba(0, 0, 0, 0.12)',
        'glass-lg': '0 8px 32px rgba(0, 0, 0, 0.16)',
        'glass-xl': '0 16px 64px rgba(0, 0, 0, 0.2)',
        'glass-glow': '0 0 20px rgba(102, 126, 234, 0.3)',
      },
      borderRadius: {
        'glass-sm': '8px',
        'glass-md': '12px',
        'glass-lg': '16px',
        'glass-xl': '24px',
      },
      animation: {
        'gradient': 'gradientShift 15s ease infinite',
        'shimmer': 'shimmer 2s infinite',
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'bounce-subtle': 'bounceSubtle 0.6s ease-out',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
      },
      keyframes: {
        gradientShift: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        fadeIn: {
          'from': { opacity: '0', transform: 'translateY(10px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          'from': { opacity: '0', transform: 'translateX(-20px)' },
          'to': { opacity: '1', transform: 'translateX(0)' },
        },
        slideUp: {
          'from': { opacity: '0', transform: 'translateY(20px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          'from': { opacity: '0', transform: 'scale(0.95)' },
          'to': { opacity: '1', transform: 'scale(1)' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(102, 126, 234, 0.3)' },
          '50%': { boxShadow: '0 0 30px rgba(102, 126, 234, 0.6)' },
        },
      },
      transitionProperty: {
        'height': 'height',
        'spacing': 'margin, padding',
      },
    },
  },
  plugins: [],
};

