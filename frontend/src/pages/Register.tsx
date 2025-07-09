import React, { useState } from 'react';
import { Box, Heading, Input, Button, VStack, Text, Link, Alert, AlertIcon } from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const Register = () => {
  const { register, loading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirm) return;
    setSubmitting(true);
    try {
      await register(email, password);
      navigate('/dashboard');
    } catch {}
    setSubmitting(false);
  };

  return (
    <Box maxW="sm" mx="auto" py={10} px={4}>
      <Heading as="h2" size="lg" mb={6}>Register</Heading>
      <VStack spacing={4} as="form" onSubmit={handleSubmit}>
        <Input placeholder="Email" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        <Input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        <Input placeholder="Confirm Password" type="password" value={confirm} onChange={e => setConfirm(e.target.value)} required />
        <Button colorScheme="teal" type="submit" width="100%" isLoading={submitting || loading}>Register</Button>
      </VStack>
      {error && <Alert status="error" mt={4}><AlertIcon />{error}</Alert>}
      <Text mt={4} textAlign="center">
        Already have an account?{' '}
        <Link as={RouterLink} to="/login" color="teal.500">Login</Link>
      </Text>
    </Box>
  );
};

export default Register; 