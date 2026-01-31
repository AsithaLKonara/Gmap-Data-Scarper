
import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  config: {
    initialColorMode: 'dark',
    useSystemColorMode: false,
  },
  colors: {
    brand: {
      50: '#F0F9FF',
      100: '#E0F2FE',
      200: '#BAE6FD',
      300: '#7DD3FC',
      400: '#38BDF8',
      500: '#0EA5E9', // Electric Blue
      600: '#0284C7',
      700: '#0369A1',
      800: '#075985',
      900: '#0C4A6E',
    },
    vibrant: {
      purple: '#8B5CF6',
      pink: '#EC4899',
      yellow: '#FACC15',
      cyan: '#06B6D4',
      gradient: 'linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%)',
    },
    dark: {
      50: '#F8FAFC',
      800: '#0F172A',
      900: '#020617', // Deeper dark for premium feel
    },
  },
  fonts: {
    heading: 'Outfit, Inter, sans-serif',
    body: 'Inter, sans-serif',
  },
  styles: {
    global: (props: any) => ({
      body: {
        bg: 'dark.900',
        color: 'white',
        minHeight: '100vh',
        overflowX: 'hidden',
        backgroundAttachment: 'fixed',
        backgroundImage: 'radial-gradient(circle at 20% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 25%), radial-gradient(circle at 80% 80%, rgba(236, 72, 153, 0.1) 0%, transparent 25%)',
      },
      '::-webkit-scrollbar': {
        width: '6px',
      },
      '::-webkit-scrollbar-track': {
        bg: 'dark.900',
      },
      '::-webkit-scrollbar-thumb': {
        bg: 'gray.700',
        borderRadius: '10px',
      },
    }),
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: '700',
        borderRadius: '14px',
        transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
        _hover: {
          transform: 'scale(1.05)',
        },
      },
      variants: {
        glow: {
          bg: 'vibrant.gradient',
          color: 'white',
          boxShadow: '0 0 20px rgba(139, 92, 246, 0.4)',
          _hover: {
            boxShadow: '0 0 35px rgba(139, 92, 246, 0.6)',
          },
        },
        glass: {
          bg: 'rgba(255, 255, 255, 0.08)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          color: 'white',
          _hover: {
            bg: 'rgba(255, 255, 255, 0.15)',
          },
        },
        solid: {
          bg: 'brand.500',
          _hover: {
            bg: 'brand.600',
          },
        },
      },
    },
    Card: {
      baseStyle: {
        container: {
          bg: 'rgba(15, 23, 42, 0.6)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '24px',
          boxShadow: '0 20px 50px rgba(0, 0, 0, 0.3)',
          overflow: 'hidden',
        },
      },
    },
    Input: {
      variants: {
        filled: {
          field: {
            bg: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            _focus: {
              bg: 'rgba(255, 255, 255, 0.08)',
              borderColor: 'brand.400',
            },
          },
        },
      },
      defaultProps: {
        variant: 'filled',
      },
    },
  },
});

export default theme;