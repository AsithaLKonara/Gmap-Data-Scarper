import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  config: {
    initialColorMode: 'dark',
    useSystemColorMode: false,
  },
  colors: {
    brand: {
      50: '#f0f0ff',
      100: '#e0e0ff',
      200: '#c7c7ff',
      300: '#a5a5ff',
      400: '#7c7cff',
      500: '#6366f1', // primary purple
      600: '#4f46e5', // primary purple dark
      700: '#4338ca',
      800: '#3730a3',
      900: '#312e81',
    },
    dark: {
      50: '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      300: '#cbd5e1',
      400: '#94a3b8',
      500: '#64748b',
      600: '#475569',
      700: '#334155', // dark blue light
      800: '#1e293b', // dark blue
      900: '#0f172a',
    },
    gray: {
      50: '#f9fafb',
      100: '#f3f4f6',
      200: '#e5e7eb',
      300: '#d1d5db',
      400: '#9ca3af',
      500: '#6b7280',
      600: '#4b5563',
      700: '#374151', // dark gray
      800: '#1f2937',
      900: '#111827',
    },
  },
  fonts: {
    heading: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    body: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  styles: {
    global: {
      body: {
        bg: 'linear-gradient(135deg, dark.800 0%, dark.700 100%)',
        color: 'white',
        minHeight: '100vh',
      },
    },
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: '600',
        borderRadius: '12px',
        _hover: {
          transform: 'translateY(-2px)',
          boxShadow: '0 8px 25px rgba(99, 102, 241, 0.4)',
        },
        transition: 'all 0.3s ease',
      },
      variants: {
        solid: {
          bg: 'linear-gradient(135deg, brand.500 0%, brand.600 100%)',
          color: 'white',
          boxShadow: '0 4px 15px rgba(99, 102, 241, 0.3)',
          _hover: {
            bg: 'linear-gradient(135deg, brand.600 0%, brand.700 100%)',
          },
        },
        outline: {
          border: '1px solid',
          borderColor: 'brand.500',
          color: 'brand.500',
          _hover: {
            bg: 'brand.500',
            color: 'white',
          },
        },
        ghost: {
          color: 'white',
          _hover: {
            bg: 'rgba(255, 255, 255, 0.1)',
          },
        },
      },
    },
    Input: {
      baseStyle: {
        field: {
          bg: 'rgba(255, 255, 255, 0.05)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '12px',
          color: 'white',
          _focus: {
            borderColor: 'brand.500',
            boxShadow: '0 0 0 3px rgba(99, 102, 241, 0.1)',
          },
          _placeholder: {
            color: 'gray.400',
          },
        },
      },
    },
    Card: {
      baseStyle: {
        container: {
          bg: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '16px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    Modal: {
      baseStyle: {
        dialog: {
          bg: 'dark.800',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '16px',
        },
      },
    },
  },
});

export default theme; 