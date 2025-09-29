import { useState, useEffect } from 'react'; 
import LoginForm from './components/LoginForm';
import Home from './components/Home';
import './App.css';

function App() {

  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);
  
  return (
    <>
      {isLoggedIn ? <Home setIsLoggedIn={setIsLoggedIn} /> : <LoginForm setIsLoggedIn={setIsLoggedIn} />}
    </>
  );
}

export default App;
