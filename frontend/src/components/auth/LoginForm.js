// File: frontend/src/components/auth/LoginForm.js
import React, { useState } from 'react';
import { TextField, Button, Typography, Paper, Box, Alert } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';

const LoginForm = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, error } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await login(email, password);
    if (success && onSuccess) {
      onSuccess();
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 400, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" component="h1" gutterBottom align="center">
        Login
      </Typography>
      
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      <Box component="form" onSubmit={handleSubmit}>
        <TextField
          label="Email"
          type="email"
          fullWidth
          margin="normal"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <TextField
          label="Password"
          type="password"
          fullWidth
          margin="normal"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <Button 
          type="submit" 
          variant="contained" 
          color="primary" 
          fullWidth 
          sx={{ mt: 3 }}
        >
          Login
        </Button>
      </Box>
    </Paper>
  );
};

export default LoginForm;