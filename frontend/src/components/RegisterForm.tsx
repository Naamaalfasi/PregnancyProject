import { useState } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Paper, 
  Container,
  InputAdornment,
  Alert
} from '@mui/material';
import { Person, Lock } from '@mui/icons-material';
import { authService } from '../services/authService';

interface RegisterFormProps {
  onRegisterSuccess: () => void;
  onBackToLogin: () => void;
  onBackToHome: () => void;
}

function RegisterForm({ onRegisterSuccess, onBackToLogin, onBackToHome }: RegisterFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const handleInputChange = (setter: (value: string) => void) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setter(e.target.value);
    setError(''); // Clear error when user starts typing
  };

  const validateForm = () => {
    if (!email || !password) {
      setError('Please fill in all fields');
      return false;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return false;
    }

    return true;
  };

  const handleRegister = async () => {
    if (!validateForm()) return;

    setError('');
    setIsLoading(true);

    try {
      const result = await authService.register(email, password);
      
      if (result.success) {
        console.log('Registration successful for user:', result.user);
        onRegisterSuccess();
      } else {
        setError(result.error || 'Registration failed. Please try again.');
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
              Create Account
            </Typography>
            <Typography 
              variant="body1" 
              color="text.secondary"
              sx={{ opacity: 0.8 }}
            >
              Join your pregnancy journey with AI assistance
            </Typography>
          </Box>

          <Box component="form" sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Email"
              value={email}
              onChange={handleInputChange(setEmail)}
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
              onChange={handleInputChange(setPassword)}
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

            <TextField
              fullWidth
              label="Confirm Password"
              type="password"
              value={confirmPassword}
              onChange={handleInputChange(setConfirmPassword)}
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
              onClick={handleRegister}
              disabled={isLoading || !email || !password || !confirmPassword}
              sx={{
                mt: 3,
                mb: 2,
                py: 1.5,
                fontSize: '1.1rem',
                borderRadius: 2
              }}
            >
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </Button>

            <Button
              fullWidth
              onClick={onBackToLogin}
              sx={{
                py: 1,
                fontSize: '1rem',
                color: 'text.secondary'
              }}
            >
              Already have an account? Sign In
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

export default RegisterForm;
