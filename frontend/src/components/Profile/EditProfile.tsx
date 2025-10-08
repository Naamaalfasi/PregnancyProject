import { useState  } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper,
  Button,
  Alert,
  TextField,
  InputAdornment
} from '@mui/material';
import Grid from '@mui/material/GridLegacy';
import { 
  Person, 
  Height, 
  PregnantWoman, 
  LocalHospital,
  Save,
  Cancel
} from '@mui/icons-material';
import type { 
  UserProfile, 
  EditFormData, 
  CalculatedFields,
} from './Utils';

import { 
  initializeEditFormData,
  prepareUpdatedProfile,
  calculateAge,
  calculatePregnancyWeek,
  calculateDueDate,
  formatDate
} from './Utils';

interface ProfileEditProps {
  currentUser: UserProfile;
  onSuccess: (updatedUser: UserProfile) => void;
  onCancel: () => void;
}

function ProfileEdit({ currentUser, onSuccess, onCancel }: ProfileEditProps) {
  const [editFormData, setEditFormData] = useState<EditFormData>(initializeEditFormData(currentUser));
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string>('');
  const [calculatedFields, setCalculatedFields] = useState<CalculatedFields>({
    age: null,
    pregnancy_week: null,
    due_date: null
  });

  const handleDateOfBirthChange = (value: string) => {
    setEditFormData({...editFormData, date_of_birth: value});
    
    // Recalculate age when date of birth changes
    const newAge = calculateAge(value);
    setCalculatedFields(prev => ({
      ...prev,
      age: newAge
    }));
  };

  const handleLmpDateChange = (value: string) => {
    setEditFormData({...editFormData, lmp_date: value});
    
    // Recalculate pregnancy week and due date when LMP changes
    const newPregnancyWeek = calculatePregnancyWeek(value);
    const newDueDate = calculateDueDate(value);
    
    setCalculatedFields(prev => ({
      ...prev,
      pregnancy_week: newPregnancyWeek,
      due_date: newDueDate
    }));
    
    // Also update the due_date in form data if calculated
    if (newDueDate) {
      setEditFormData(prev => ({
        ...prev,
        due_date: newDueDate
      }));
    }
  };

  const handleSaveProfile = async () => {
    setIsSaving(true);
    setError('');

    try {
      const updatedProfile = prepareUpdatedProfile(currentUser, editFormData, calculatedFields);

      // Call the update API
      const response = await fetch(`http://localhost:8000/users/${currentUser.user_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedProfile)
      });

      if (response.ok) {
        const updatedUserData = await response.json();
        onSuccess(updatedUserData);
      } else {
        setError('Failed to update profile. Please try again.');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      setError('Network error. Please check your connection and try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Edit Profile
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            variant="outlined" 
            startIcon={<Cancel />}
            onClick={onCancel}
            color="error"
          >
            Cancel
          </Button>
          <Button 
            variant="contained" 
            startIcon={<Save />}
            onClick={handleSaveProfile}
            disabled={isSaving}
            sx={{ 
              background: 'linear-gradient(45deg, #e91e63, #9c27b0)',
              '&:hover': {
                background: 'linear-gradient(45deg, #c2185b, #7b1fa2)',
              }
            }}
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>
      )}

      {/* Personal Information Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Person sx={{ fontSize: 30, color: '#e91e63', mr: 2 }} />
          <Typography variant="h6">Personal Information</Typography>
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">Full Name</Typography>
            <TextField
              fullWidth
              value={editFormData.name}
              onChange={(e) => setEditFormData({...editFormData, name: e.target.value})}
              placeholder="Enter your full name"
              size="small"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">Email</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {currentUser.email || "Not provided"}
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">Date of Birth</Typography>
            <TextField
              fullWidth
              value={editFormData.date_of_birth}
              onChange={(e) => handleDateOfBirthChange(e.target.value)}
              placeholder="DDMMYYYY"
              size="small"
              helperText="Format: DDMMYYYY (e.g., 01011990)"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">Age</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {calculatedFields.age !== null 
                ? `${calculatedFields.age} years old (calculated)`
                : currentUser.age 
                  ? `${currentUser.age} years old` 
                  : "Not calculated"}
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
            <TextField
              fullWidth
              type="number"
              value={editFormData.height}
              onChange={(e) => setEditFormData({...editFormData, height: e.target.value})}
              placeholder="Height in cm"
              size="small"
              InputProps={{
                endAdornment: <InputAdornment position="end">cm</InputAdornment>
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">Weight</Typography>
            <TextField
              fullWidth
              type="number"
              value={editFormData.weight}
              onChange={(e) => setEditFormData({...editFormData, weight: e.target.value})}
              placeholder="Weight in kg"
              size="small"
              InputProps={{
                endAdornment: <InputAdornment position="end">kg</InputAdornment>
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">Blood Type</Typography>
            <TextField
              fullWidth
              value={editFormData.blood_type}
              onChange={(e) => setEditFormData({...editFormData, blood_type: e.target.value})}
              placeholder="A+, B-, O+, etc."
              size="small"
              helperText="e.g., A+, B-, O+, AB-"
            />
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
              {calculatedFields.pregnancy_week !== null
                ? `Week ${calculatedFields.pregnancy_week} (calculated)`
                : currentUser.pregnancy_week 
                  ? `Week ${currentUser.pregnancy_week}` 
                  : "Not calculated"}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">Last Menstrual Period</Typography>
            <TextField
              fullWidth
              value={editFormData.lmp_date}
              onChange={(e) => handleLmpDateChange(e.target.value)}
              placeholder="DDMMYYYY"
              size="small"
              helperText="Format: DDMMYYYY"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">Due Date</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {calculatedFields.due_date 
                ? `${formatDate(calculatedFields.due_date)} (calculated)`
                : formatDate(currentUser.due_date)}
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
            <TextField
              fullWidth
              value={editFormData.medical_conditions.join(',')}
              onChange={(e) => setEditFormData({
                ...editFormData, 
                medical_conditions: e.target.value.split(',')
              })}
              placeholder="Diabetes, High Blood Pressure, etc."
              size="small"
              helperText="Separate multiple conditions with commas"
            />
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" gutterBottom>Allergies</Typography>
            <TextField
              fullWidth
              value={editFormData.allergies.join(', ')}
              onChange={(e) => setEditFormData({
                ...editFormData, 
                allergies: e.target.value.split(',').map(s => s.trim()).filter(s => s)
              })}
              placeholder="Peanuts, Penicillin, etc."
              size="small"
              helperText="Separate multiple allergies with commas"
            />
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" gutterBottom>Current Medications</Typography>
            <TextField
              fullWidth
              value={editFormData.medications.join(', ')}
              onChange={(e) => setEditFormData({
                ...editFormData, 
                medications: e.target.value.split(',').map(s => s.trim()).filter(s => s)
              })}
              placeholder="Prenatal vitamins, Iron supplements, etc."
              size="small"
              helperText="Separate multiple medications with commas"
            />
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
}

export default ProfileEdit;
