import { Button } from "@mui/material";

function Home({ setIsLoggedIn }: { setIsLoggedIn: (isLoggedIn: boolean) => void }) {
    
    return (
        <>
            <h1>Home</h1>
            <Button onClick={() => {
                localStorage.removeItem('token');
                setIsLoggedIn(false);
            }}>Logout</Button>
        </>
    );
  }
  
  export default Home;
