import { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper,
  Chip,
  Button,
  Alert,
  CircularProgress
} from '@mui/material';
import Grid from '@mui/material/GridLegacy';
import { 
  Person, 
  Height, 
  PregnantWoman, 
  LocalHospital,
  Edit,
  Description,
  Assignment
} from '@mui/icons-material';
import { authService } from '../../services/authService';
import type { 
  UserProfile
} from './Utils';
import { 
  formatDate
} from './Utils';
import ProfileEdit from './EditProfile';

function Profile({ onNavigate }: { onNavigate: (screen: string) => void }) {
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [isEditMode, setIsEditMode] = useState(false);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        setIsLoading(true);
        setError('');
        
        const userData = await authService.getCurrentUser();
        
        if (userData) {
          setCurrentUser(userData);
        } else {
          setError('Failed to load profile data');
        }
      } catch (error) {
        console.error('Failed to fetch user data:', error);
        setError('Failed to load profile data');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchUserData();
  }, []);

  const handleEditClick = () => {
    setIsEditMode(true);
  };

  const handleEditSuccess = (updatedUser: UserProfile) => {
    setCurrentUser(updatedUser);
    setIsEditMode(false);
  };

  const handleEditCancel = () => {
    setIsEditMode(false);
  };

  if (isLoading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error && !isEditMode) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!currentUser) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="warning">No profile data found</Alert>
      </Container>
    );
  }

  if (isEditMode) {
    return (
      <ProfileEdit
        currentUser={currentUser}
        onSuccess={handleEditSuccess}
        onCancel={handleEditCancel}
      />
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          My Profile
        </Typography>
        <Button 
          variant="outlined" 
          startIcon={<Edit />}
          onClick={handleEditClick}
          sx={{ 
            background: 'linear-gradient(45deg, #e91e63, #9c27b0)',
            color: 'white',
            '&:hover': {
              background: 'linear-gradient(45deg, #c2185b, #7b1fa2)',
            }
          }}
        >
          Edit Profile
        </Button>
      </Box>

      {/* Personal Information Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Person sx={{ fontSize: 30, color: '#e91e63', mr: 2 }} />
          <Typography variant="h6">Personal Information</Typography>
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">Full Name</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {currentUser.name || "Not provided"}
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">Email</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {currentUser.email || "Not provided"}
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">Date of Birth</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {formatDate(currentUser.date_of_birth)}
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">Age</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {currentUser.age ? `${currentUser.age} years old` : "Not calculated"}
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Physical Information Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Height sx={{ fontSize: 30, color: '#e91e63', mr: 2 }} />
          <Typography variant="h6">Physical Information</Typography>
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">Height</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {currentUser.height ? `${currentUser.height} cm` : "Not provided"}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">Weight</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {currentUser.weight ? `${currentUser.weight} kg` : "Not provided"}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">Blood Type</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {currentUser.blood_type && currentUser.blood_type !== "None-String" 
                ? currentUser.blood_type 
                : "Not provided"}
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Pregnancy Information Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <PregnantWoman sx={{ fontSize: 30, color: '#e91e63', mr: 2 }} />
          <Typography variant="h6">Pregnancy Information</Typography>
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">Pregnancy Week</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {currentUser.pregnancy_week ? `Week ${currentUser.pregnancy_week}` : "Not calculated"}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">Last Menstrual Period</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {formatDate(currentUser.lmp_date)}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">Due Date</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {formatDate(currentUser.due_date)}
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Medical Information Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <LocalHospital sx={{ fontSize: 30, color: '#e91e63', mr: 2 }} />
          <Typography variant="h6">Medical Information</Typography>
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" gutterBottom>Medical Conditions</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {currentUser.medical_conditions && currentUser.medical_conditions.length > 0 ? (
                currentUser.medical_conditions.map((condition, index) => (
                  <Chip 
                    key={index} 
                    label={condition} 
                    size="small" 
                    sx={{ 
                      background: 'linear-gradient(45deg, #e91e63, #9c27b0)',
                      color: 'white'
                    }}
                  />
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">None</Typography>
              )}
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" gutterBottom>Allergies</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {currentUser.allergies && currentUser.allergies.length > 0 ? (
                currentUser.allergies.map((allergy, index) => (
                  <Chip 
                    key={index} 
                    label={allergy} 
                    size="small" 
                    color="warning"
                  />
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">None</Typography>
              )}
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" gutterBottom>Current Medications</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {currentUser.medications && currentUser.medications.length > 0 ? (
                currentUser.medications.map((medication, index) => (
                  <Chip 
                    key={index} 
                    label={medication} 
                    size="small" 
                    color="info"
                  />
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">None</Typography>
              )}
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Quick Actions Section */}
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Quick Actions</Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Access your documents and tasks from your profile
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button 
            variant="outlined" 
            startIcon={<Description />}
            onClick={() => onNavigate('documents')}
            sx={{ 
              borderColor: '#e91e63',
              color: '#e91e63',
              '&:hover': {
                borderColor: '#c2185b',
                backgroundColor: 'rgba(233, 30, 99, 0.1)'
              }
            }}
          >
            View Medical Documents
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<Assignment />}
            onClick={() => onNavigate('tasks')}
            sx={{ 
              borderColor: '#e91e63',
              color: '#e91e63',
              '&:hover': {
                borderColor: '#c2185b',
                backgroundColor: 'rgba(233, 30, 99, 0.1)'
              }
            }}
          >
            View Tasks
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}

export default Profile;
