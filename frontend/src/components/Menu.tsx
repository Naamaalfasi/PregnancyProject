import { 
  Drawer, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText,
  Box,
  Typography
} from '@mui/material';
import { 
  ExitToApp, 
  Person, 
  Assignment, 
  Chat 
} from '@mui/icons-material';
import HomeIcon from '@mui/icons-material/Home';

interface MenuProps {
  open: boolean;
  onClose: () => void;
  onLogout: () => void;
  onNavigate: (screen: string) => void;
}

function Menu({ open, onClose, onLogout, onNavigate }: MenuProps) {
  const menuItems = [
    { text: 'Home', icon: <HomeIcon />, screen: 'home' },
    { text: 'Profile', icon: <Person />, screen: 'profile' },
    { text: 'Tasks', icon: <Assignment />, screen: 'tasks' },
    { text: 'Chatbot', icon: <Chat />, screen: 'chatbot' },
    { text: 'Logout', icon: <ExitToApp />, screen: 'logout' },
  ];

  const handleItemClick = async (screen: string) => {
    if (screen === 'logout') {
      await onLogout();
    } else {
      await onNavigate(screen);
    }
    onClose();
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: 280,
          background: 'linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%)',
          borderRight: '1px solid rgba(233, 30, 99, 0.1)',
        },
      }}
    >
      <Box sx={{ p: 3 }}>
        <Typography 
          variant="h6" 
          sx={{
            fontWeight: 600,
            background: 'linear-gradient(45deg, #e91e63, #9c27b0)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 2
          }}
        >
          Menu
        </Typography>
        
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                onClick={() => handleItemClick(item.screen)}
                sx={{
                  borderRadius: 2,
                  mb: 1,
                  '&:hover': {
                    backgroundColor: 'rgba(233, 30, 99, 0.1)',
                  },
                }}
              >
                <ListItemIcon sx={{ color: '#e91e63' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text}
                  sx={{ 
                    '& .MuiListItemText-primary': {
                      fontWeight: 500,
                      color: '#333'
                    }
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>
    </Drawer>
  );
}

export default Menu;
