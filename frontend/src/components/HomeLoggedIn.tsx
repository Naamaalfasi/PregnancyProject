import { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Card, 
  CardContent
} from '@mui/material';
import { PregnantWoman, Description, Assignment } from '@mui/icons-material';
import { authService } from '../services/authService';
import Utils from '../services/utils';

function HomeLoggedIn() {
  // currentUser is a STATE VARIABLE that holds the full user object
  const [currentUser, setCurrentUser] = useState< any | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        // Get just the user ID from localStorage
        const userId = authService.getCurrentUserId(); 
        
        if (userId) {
          // Fetch the FULL user object from server
          const response = await fetch(`http://localhost:8000/users/${userId}`);
          const userData = await response.json(); // This is the full user object
          
          // Set the state variable with the full user data
          setCurrentUser(userData);
        }
      } catch (error) {
        console.error('Failed to fetch user data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchUserData();
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Welcome back, {currentUser?.name || 'User'}! 
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Your personalized AI assistant is here to support you through every step of your pregnancy.
      </Typography>

      {/* User Info Card */}
      {currentUser && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Your Profile
            </Typography>
            <Typography variant="body2" color="text.secondary">
              User ID: {currentUser.user_id}
            </Typography>
            {currentUser.pregnancy_week && (
              <Typography variant="body2" color="text.secondary">
                Pregnancy Week: {currentUser.pregnancy_week}
              </Typography>
            )}
            {currentUser.due_date && (
              <Typography variant="body2" color="text.secondary">
                Due Date: {Utils.convertToDate(currentUser.due_date).toLocaleDateString()}
              </Typography>
            )}
          </CardContent>
        </Card>
      )}

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
        <Box sx={{ flex: '1 1 100%', minWidth: '300px' }}>
          <Card>
            <CardContent>
              <Description sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Medical Documents
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Upload and analyze your medical documents with AI-powered insights.
              </Typography>
            </CardContent>
          </Card>
        </Box>
        
        <Box sx={{ flex: '1 1 100%', minWidth: '300px' }}>
          <Card>
            <CardContent>
              <Assignment sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Pregnancy Tasks
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Get personalized tasks and reminders for your pregnancy journey.
              </Typography>
            </CardContent>
          </Card>
        </Box>
        
        <Box sx={{ flex: '1 1 100%', minWidth: '300px' }}>
          <Card>
            <CardContent>
              <PregnantWoman sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                AI Support
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Chat with your AI assistant for personalized pregnancy guidance.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Container>
  );
}

export default HomeLoggedIn;
