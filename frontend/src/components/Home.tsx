import HomeLoggedIn from './HomeLoggedIn';
import HomeLanding from './HomeLanding';
import ChatBot from './ChatBot';
import Profile from './Profile/Profile';

function Home({ isLoggedIn, currentScreen, onNavigate }: { isLoggedIn: boolean; currentScreen: string; onNavigate: (screen: string) => void }) {
  if (!isLoggedIn) {
    return <HomeLanding />;
  }

  // For now, show placeholder components for other screens
  switch (currentScreen) {
    case 'home':
      return <HomeLoggedIn />;
    case 'profile':
      return <Profile onNavigate={onNavigate}/>;
    case 'tasks':
      return <div>Tasks Screen - Coming Soon</div>;
    case 'documents':
      return <div>Documents Screen - Coming Soon</div>;
    case 'chatbot':
      return <ChatBot />;
    default:
      return <HomeLanding />;
  }
}

export default Home;
