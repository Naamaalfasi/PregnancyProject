import HomeLoggedIn from "./HomeLoggedIn";
import HomeLanding from "./HomeLanding";
import Tasks from "./Tasks";
import ChatBot from "./ChatBot";
import Profile from "./Profile/Profile";
import Documents from "./Documents";

function Home({
  isLoggedIn,
  currentScreen,
  onNavigate,
}: {
  isLoggedIn: boolean;
  currentScreen: string;
  onNavigate: (screen: string) => void;
}) {
  if (!isLoggedIn) {
    return <HomeLanding />;
  }

  // For now, show placeholder components for other screens
  switch (currentScreen) {
    case "home":
      return <HomeLoggedIn onNavigate={onNavigate} />;
    case "profile":
      return <Profile onNavigate={onNavigate} />;
    case "tasks":
      return <Tasks />;
    case "documents":
      return <Documents />;
    case "chatbot":
      return <ChatBot />;
    default:
      return <HomeLanding />;
  }
}

export default Home;
