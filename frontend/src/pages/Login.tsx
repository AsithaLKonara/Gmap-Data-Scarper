import React, { useState } from 'react';
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

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(email, password);
      toast({
        title: 'Login successful!',
        description: 'Welcome back to LeadTap',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      navigate('/dashboard');
    } catch (error) {
      toast({
        title: 'Login failed',
        description: error instanceof Error ? error.message : 'Invalid credentials',
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
              Welcome Back
            </Heading>
            <Text color="gray.400" fontSize="lg">
              Sign in to your LeadTap account
            </Text>
          </VStack>

          <Card className="card-modern" w="full">
            <CardBody>
              <form onSubmit={handleSubmit}>
                <VStack spacing={6}>
                  <FormControl isRequired>
                    <FormLabel color="white">Email</FormLabel>
                    <Input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email"
                      className="input-modern"
                    />
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel color="white">Password</FormLabel>
                    <Input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      className="input-modern"
                    />
                  </FormControl>

                  <Button
                    type="submit"
                    className="btn-modern"
                    w="full"
                    size="lg"
                    isLoading={isLoading}
                    loadingText="Signing in..."
                  >
                    Sign In
                  </Button>
      </VStack>
              </form>
            </CardBody>
          </Card>

          <Text color="gray.400" textAlign="center">
        Don't have an account?{' '}
            <Link as={RouterLink} to="/register" color="brand.400" fontWeight="semibold">
              Sign up here
            </Link>
      </Text>
        </VStack>
      </Container>
    </Box>
  );
};

export default Login; 