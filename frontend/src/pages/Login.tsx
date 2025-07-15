import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  VStack,
  Heading,
  FormControl,
  FormLabel,
  Input,
  Button,
  Text,
  Link,
  useToast,
  Card,
  CardBody
} from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { EmailIcon, LockIcon } from '@chakra-ui/icons';
import { getTenantSsoConfig } from '../api';
import { useTranslation } from 'react-i18next';

const Login = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [tenant, setTenant] = useState('');
  const [ssoEnabled, setSsoEnabled] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const { login } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => {
    if (tenant) {
      getTenantSsoConfig(tenant)
        .then(cfg => setSsoEnabled(!!cfg && !!cfg.entity_id && !!cfg.sso_url && !!cfg.cert))
        .catch(() => setSsoEnabled(false));
    } else {
      setSsoEnabled(false);
    }
  }, [tenant]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setFormError(null);

    try {
      if (!tenant) throw new Error(t('login.error.tenantRequired', 'Tenant/Organization is required'));
      localStorage.setItem('tenantSlug', tenant);
      await login(email, password);
      toast({
        title: t('login.success', 'Login successful!'),
        description: t('login.welcome', 'Welcome back to LeadTap'),
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      navigate('/dashboard');
    } catch (error) {
      let message = t('login.error.invalidCredentials', 'Invalid credentials');
      if (error instanceof Error) message = error.message;
      setFormError(message);
      toast({
        title: t('login.failed', 'Login failed'),
        description: message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box minH="calc(100vh - 64px)" py={20}>
      <Container maxW="md">
        <VStack spacing={8}>
          <VStack spacing={4} textAlign="center">
            <Heading size="2xl" className="gradient-text">
              {t('login.heading', 'Welcome Back')}
            </Heading>
            <Text color="gray.400" fontSize="lg">
              {t('login.subtitle', 'Sign in to your LeadTap account')}
            </Text>
          </VStack>

          <Card className="card-modern" w="full">
            <CardBody>
              <form onSubmit={handleSubmit}>
                {/* Show form error if present */}
                {formError && (
                  <Text color="red.400" fontSize="sm" textAlign="center">{formError}</Text>
                )}
                <VStack spacing={6}>
                  <FormControl isRequired>
                    <FormLabel color="white">{t('login.email', 'Email')}</FormLabel>
                    <Input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder={t('login.emailPlaceholder', 'Enter your email')}
                      className="input-modern"
                    />
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel color="white">{t('login.password', 'Password')}</FormLabel>
                    <Input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder={t('login.passwordPlaceholder', 'Enter your password')}
                      className="input-modern"
                    />
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel color="white">{t('login.tenant', 'Organization/Tenant')}</FormLabel>
                    <Input
                      value={tenant}
                      onChange={(e) => setTenant(e.target.value)}
                      placeholder={t('login.tenantPlaceholder', 'Enter your organization/tenant slug')}
                      className="input-modern"
                    />
                  </FormControl>

                  {ssoEnabled && (
                    <Button
                      w="full"
                      colorScheme="purple"
                      onClick={() => window.location.href = `/api/auth/sso/login?tenant=${tenant}`}
                    >
                      {t('login.sso', 'Sign in with SSO')}
                    </Button>
                  )}

                  <Button
                    type="submit"
                    className="btn-modern"
                    w="full"
                    size="lg"
                    isLoading={isLoading}
                    loadingText={t('login.signingIn', 'Signing in...')}
                  >
                    {t('login.signIn', 'Sign In')}
                  </Button>
      </VStack>
              </form>
            </CardBody>
          </Card>

          <Text color="gray.400" textAlign="center">
            {t('login.noAccount', "Don't have an account?")}{' '}
            <Link as={RouterLink} to="/register" color="brand.400" fontWeight="semibold">
              {t('login.signUpHere', 'Sign up here')}
            </Link>
          </Text>
        </VStack>
      </Container>
    </Box>
  );
};

export default Login; 