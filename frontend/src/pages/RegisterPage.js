// File: frontend/src/pages/RegisterPage.js
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Typography, Box } from '@mui/material';
import RegisterForm from '../components/auth/RegisterForm';

const RegisterPage = () => {
  const navigate = useNavigate();

  const handleRegisterSuccess = () => {
    navigate('/login');
  };

  return (
    <Box sx={{ p: 2, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        Invoice Analyzer
      </Typography>
      
      <RegisterForm onSuccess={handleRegisterSuccess} />
      
      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Typography variant="body2">
          Already have an account? <Link to="/login">Login</Link>
        </Typography>
      </Box>
    </Box>
  );
};

export default RegisterPage;