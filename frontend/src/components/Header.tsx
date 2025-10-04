import { AppBar, Toolbar, Typography, Button, Box, IconButton } from '@mui/material';
import { Login, Menu as MenuIcon, PersonAdd } from '@mui/icons-material';

interface HeaderProps {
  isLoggedIn: boolean;
  onLogin: () => void;
  onRegister: () => void;
  onMenuClick: () => void;
  onBackToHome: () => void;
}

function Header({ isLoggedIn, onLogin, onRegister, onMenuClick, onBackToHome }: HeaderProps) {
  return (
    <AppBar 
      position="static"
      sx={{
        background: 'linear-gradient(45deg, #e91e63, #9c27b0)',
        boxShadow: '0 4px 20px rgba(233, 30, 99, 0.3)',
      }}
    >
      <Toolbar>
        {/* Logo on the left */}
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box 
            component="img" 
            src="/clearlogo.png" 
            alt="Logo" 
            sx={{ 
              height: '80px',
              width: 'auto',
              margin: '10px'
            }} 
          />
        </Box>
        
        {/* Title in the center */}
        <Typography 
          variant="h6" 
          component="div"
          onClick={onBackToHome}
          sx={{ 
            cursor: 'pointer',
            flexGrow: 1,
            textAlign: 'center',
            fontWeight: 550,
            fontSize: '1.5rem',
          }}
        >
          Pregnancy AI Assistant
        </Typography>
        
        {/* Buttons on the right */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {isLoggedIn ? (
            <IconButton 
              color="inherit" 
              onClick={onMenuClick}
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                },
              }}
            >
              <MenuIcon />
            </IconButton>
          ) : (
            <>
              <Button 
                color="inherit" 
                onClick={onRegister}
                startIcon={<PersonAdd />}
                sx={{
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  },
                  fontWeight: 500
                }}
              >
                Register
              </Button>
              <Button 
                color="inherit" 
                onClick={onLogin}
                startIcon={<Login />}
                sx={{
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  },
                  fontWeight: 500
                }}
              >
                Login
              </Button>
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
