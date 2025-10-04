import { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import Header from './components/Header';
import Home from './components/Home';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import MultiStepRegistration from './components/Registration/MultiStepRegistration';
import Menu from './components/Menu';
import { authService } from './services/authService';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [currentScreen, setCurrentScreen] = useState('home');

  useEffect(() => {
    // Check if user is already logged in
    checkIfLoggedIn();
  }, []);

  const checkIfLoggedIn = async () => {
    const isLoggedIn = await authService.isLoggedIn();
    setIsLoggedIn(isLoggedIn);
  };

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
    setShowLogin(false);
    setShowRegister(false);
  };

  const handleRegisterSuccess = () => {
    setIsLoggedIn(true);
    setShowLogin(false);
    setShowRegister(false);
  };

  const handleLogout = () => {
    authService.logout();
    setIsLoggedIn(false);
    setCurrentScreen('home');
  };

  const handleBackToHome = () => {
    setCurrentScreen('home');
    setShowLogin(false);
    setShowRegister(false);
  };

  const handleNavigate = (screen: string) => {
    setCurrentScreen(screen);
  };

  const handleBackToLogin = () => {
    setShowRegister(false);
    setShowLogin(true);
  };

  const handleBackToRegister = () => {
    setShowRegister(true);
    setShowLogin(false);
  };

  return (
    <Box>
      <Header 
        isLoggedIn={isLoggedIn}
        onLogin={handleBackToLogin}
        onRegister={handleBackToRegister}
        onMenuClick={() => setMenuOpen(true)}
        onBackToHome={handleBackToHome}
      />

      {isLoggedIn && (
        <Menu
          open={menuOpen}
          onClose={() => setMenuOpen(false)}
          onLogout={handleLogout}
          onNavigate={handleNavigate}
        />
      )}

      {showLogin ? (
        <LoginForm 
          onLoginSuccess={handleLoginSuccess}
          onBackToRegister={handleBackToRegister}
          onBackToHome={handleBackToHome} />
      ) : showRegister ? (
        <MultiStepRegistration 
          onRegisterSuccess={handleRegisterSuccess} 
          onBackToLogin={handleBackToLogin}
          onBackToHome={handleBackToHome}
        />
      ) : (
        <Home isLoggedIn={isLoggedIn} currentScreen={currentScreen} />
      )}
    </Box>
  );
}

export default App;
