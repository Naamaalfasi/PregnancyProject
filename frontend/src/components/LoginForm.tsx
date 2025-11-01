import { useState } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Paper, 
  InputAdornment,
  Alert
} from '@mui/material';
import { Person, Lock } from '@mui/icons-material';
import { authService } from '../services/authService';

import '../App.css';

interface LoginFormProps {
  onLoginSuccess: () => void;
  onBackToRegister: () => void;
  onBackToHome: () => void;
}

function LoginForm({ onLoginSuccess, onBackToRegister, onBackToHome }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const handleLogin = async () => {
    setError('');
    setIsLoading(true);

    try {
      const result = await authService.login(email, password);
      
      if (result.success) {
        console.log('Login successful for user:', result.user);
        onLoginSuccess();
      } else {
        setError('Invalid email or password');
      }
    } catch (error) {
      setError('Network error. Please check your connection.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Box className="auth-page-container">
      <Paper elevation={8} className="paper-design">
        <Box textAlign="center" mb={4}>
          <Box component="img" src="/logo.png" alt="Logo" sx={{ width: '75%', height: 'auto', mb: 2 }} />
          <Typography 
            variant="h4" 
            component="h1" 
            gutterBottom
            className="auth-title"
          >
            Welcome Back
          </Typography>
          <Typography 
            variant="body1" 
            color="text.secondary"
            sx={{ opacity: 0.8 }}
          >
            Sign in to your account
          </Typography>
        </Box>

        <Box component="form" sx={{ mt: 2 }}>
          <TextField
            fullWidth
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value.toLowerCase())}
            margin="normal"
            variant="outlined"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Person sx={{ color: '#e91e63', opacity: 0.7 }} />
                </InputAdornment>
              ),
            }}
            
          />
          
          <TextField
            fullWidth
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
            variant="outlined"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Lock sx={{ color: '#e91e63', opacity: 0.7 }} />
                </InputAdornment>
              ),
            }}
            
          />

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={handleLogin}
            disabled={isLoading || !email || !password}
            sx={{
              mt: 3,
              mb: 2,
              py: 1.5,
              fontSize: '1.1rem',
              borderRadius: 2
            }}
          >
            {isLoading ? 'Signing In...' : 'Sign In'}
          </Button>
          <Button
            fullWidth
            onClick={onBackToRegister}
            sx={{
              py: 1,
              fontSize: '1rem',
              color: 'text.secondary'
            }}
          >
            Don't have an account? Register here
          </Button>
          <Button
            fullWidth
            onClick={onBackToHome}
            sx={{
              py: 1,
              fontSize: '1rem',
              color: 'text.secondary'
            }}
          >
            Back to home
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}

export default LoginForm;