import HomeLoggedIn from './HomeLoggedIn';
import HomeLanding from './HomeLanding';

function Home({ isLoggedIn, currentScreen }: { isLoggedIn: boolean; currentScreen: string }) {
  if (!isLoggedIn) {
    return <HomeLanding />;
  }

  // For now, show placeholder components for other screens
  switch (currentScreen) {
    case 'home':
      return <HomeLoggedIn />;
    case 'profile':
      return <div>Profile Screen - Coming Soon</div>;
    case 'tasks':
      return <div>Tasks Screen - Coming Soon</div>;
    case 'chatbot':
      return <div>Chatbot Screen - Coming Soon</div>;
    default:
      return <HomeLanding />;
  }
}

export default Home;
