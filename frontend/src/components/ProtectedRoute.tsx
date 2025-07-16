import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Box, Spinner, Center } from '@chakra-ui/react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPlan?: 'free' | 'pro' | 'business';
  adminOnly?: boolean;
  requiredRoles?: string[];
  requiredPermissions?: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredPlan = 'free',
  adminOnly = false,
  requiredRoles = [],
  requiredPermissions = []
}) => {
  const { user, loading, hasRole, hasPermission } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <Center minH="100vh">
        <Spinner size="xl" />
      </Center>
    );
  }

  if (!user) {
    // Redirect to login with return URL
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check plan requirements
  const planHierarchy = { free: 0, pro: 1, business: 2 };
  const userPlanLevel = planHierarchy[user.plan as keyof typeof planHierarchy] || 0;
  const requiredPlanLevel = planHierarchy[requiredPlan];

  if (userPlanLevel < requiredPlanLevel) {
    return <Navigate to="/pricing" replace />;
  }

  // Check admin requirements
  if (adminOnly && user.plan !== 'business') {
    return <Navigate to="/dashboard" replace />;
  }

  // Check required roles
  if (requiredRoles.length > 0 && !requiredRoles.some(r => hasRole(r))) {
    return <Box p={8} textAlign="center">You do not have the required role to access this page.</Box>;
  }

  // Check required permissions
  if (requiredPermissions.length > 0 && !requiredPermissions.some(p => hasPermission(p))) {
    return <Box p={8} textAlign="center">You do not have the required permission to access this page.</Box>;
  }

  return <>{children}</>;
};

export default ProtectedRoute; 