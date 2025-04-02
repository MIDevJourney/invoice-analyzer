// File: frontend/src/pages/LoginPage.js
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Typography, Box } from '@mui/material';
import LoginForm from '../components/auth/LoginForm';

const LoginPage = () => {
  const navigate = useNavigate();

  const handleLoginSuccess = () => {
    navigate('/dashboard');
  };

  return (
    <Box sx={{ p: 2, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        Invoice Analyzer
      </Typography>
      
      <LoginForm onSuccess={handleLoginSuccess} />
      
      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Typography variant="body2">
          Don't have an account? <Link to="/register">Register</Link>
        </Typography>
      </Box>
    </Box>
  );
};

export default LoginPage;