import { useState } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Paper, 
  Container,
  InputAdornment 
} from '@mui/material';
import { Person, Lock } from '@mui/icons-material';

function LoginForm({ setIsLoggedIn }: { setIsLoggedIn: (isLoggedIn: boolean) => void }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    
    return (
        <Container maxWidth="sm">
            <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                justifyContent="center"
                minHeight="100vh"
                sx={{
                    background: 'linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%)',
                    padding: 2
                }}
            >
                <Paper
                    elevation={8}
                    sx={{
                        p: 4,
                        width: '100%',
                        maxWidth: 400,
                        borderRadius: 3,
                        background: 'rgba(255, 255, 255, 0.95)',
                        backdropFilter: 'blur(10px)',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        userSelect: 'none'
                    }}
                >
                    <Box textAlign="center" mb={4}>
                        <img src="/logo.png" alt="Logo" style={{ width: '75%', height: '75%' }} />
                        <Typography 
                            variant="h4" 
                            component="h1" 
                            gutterBottom
                            sx={{
                                fontWeight: 600,
                                background: 'linear-gradient(45deg, #e91e63, #9c27b0)',
                                backgroundClip: 'text',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                mb: 1
                            }}
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
                            label="Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            margin="normal"
                            variant="outlined"
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <Person sx={{ color: '#e91e63', opacity: 0.7 }} />
                                    </InputAdornment>
                                ),
                            }}
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    '&:hover fieldset': {
                                        borderColor: '#e91e63',
                                    },
                                    '&.Mui-focused fieldset': {
                                        borderColor: '#9c27b0',
                                    },
                                },
                                '& .MuiInputLabel-root.Mui-focused': {
                                    color: '#9c27b0',
                                },
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
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    '&:hover fieldset': {
                                        borderColor: '#e91e63',
                                    },
                                    '&.Mui-focused fieldset': {
                                        borderColor: '#9c27b0',
                                    },
                                },
                                '& .MuiInputLabel-root.Mui-focused': {
                                    color: '#9c27b0',
                                },
                            }}
                        />

                        <Button
                            fullWidth
                            variant="contained"
                            size="large"
                            onClick={() => {
                                if (username === 'admin' && password === 'admin') {
                                    console.log('Login successful');
                                    setIsLoggedIn(true);
                                    localStorage.setItem('token', 'admin');
                                } else {
                                    console.log('Login failed');
                                    localStorage.removeItem('token');
                                }
                            }}
                            sx={{
                                mt: 3,
                                mb: 2,
                                py: 1.5,
                                background: 'linear-gradient(45deg, #e91e63, #9c27b0)',
                                '&:hover': {
                                    background: 'linear-gradient(45deg, #c2185b, #7b1fa2)',
                                    transform: 'translateY(-2px)',
                                    boxShadow: '0 8px 25px rgba(233, 30, 99, 0.3)',
                                },
                                transition: 'all 0.3s ease',
                                borderRadius: 2,
                                fontWeight: 600,
                                textTransform: 'none',
                                fontSize: '1.1rem'
                            }}
                        >
                            Sign In
                        </Button>
                    </Box>
                </Paper>
            </Box>
        </Container>
    );
}

export default LoginForm;