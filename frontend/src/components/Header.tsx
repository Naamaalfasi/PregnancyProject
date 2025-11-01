import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
} from "@mui/material";
import { Login, Menu as MenuIcon, PersonAdd } from "@mui/icons-material";

interface HeaderProps {
  isLoggedIn: boolean;
  onLogin: () => void;
  onRegister: () => void;
  onMenuClick: () => void;
  onBackToHome: () => void;
}

function Header({
  isLoggedIn,
  onLogin,
  onRegister,
  onMenuClick,
  onBackToHome,
}: HeaderProps) {
  return (
    <AppBar
      position="static"
      sx={{
        background: "linear-gradient(45deg, #e91e63, #9c27b0)",
        boxShadow: "0 4px 20px rgba(233, 30, 99, 0.3)",
        position: "relative", // מאפשר absolute positioning יחסי ל-AppBar
      }}
    >
      <Toolbar sx={{ minHeight: "100px !important" }}>
        {" "}
        {/* גובה מותאם ללוגו */}
        {/* Title on the left */}
        <Typography
          variant="body1"
          component="div"
          onClick={onBackToHome}
          sx={{
            cursor: "pointer",
            fontWeight: 550,
            fontSize: "1.1rem",
            mr: 2,
            lineHeight: 1.5,
          }}
        >
          Pregnancy AI Assistant
        </Typography>
        {/* Logo in the center - ממורכז ביחס לעמוד כולו */}
        <Box
          sx={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: "translate(-50%, -50%)",
            display: "flex",
            alignItems: "center",
            zIndex: 1,
          }}
        >
          <Box
            component="img"
            src="/clearlogo.png"
            alt="Logo"
            onClick={onBackToHome}
            sx={{
              height: "80px",
              width: "auto",
              cursor: "pointer",
            }}
          />
        </Box>
        {/* Buttons on the right */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 2, ml: "auto" }}>
          {isLoggedIn ? (
            <IconButton
              color="inherit"
              onClick={onMenuClick}
              sx={{
                "&:hover": {
                  backgroundColor: "rgba(255, 255, 255, 0.1)",
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
                  "&:hover": {
                    backgroundColor: "rgba(255, 255, 255, 0.1)",
                  },
                  fontWeight: 500,
                }}
              >
                Register
              </Button>
              <Button
                color="inherit"
                onClick={onLogin}
                startIcon={<Login />}
                sx={{
                  "&:hover": {
                    backgroundColor: "rgba(255, 255, 255, 0.1)",
                  },
                  fontWeight: 500,
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
