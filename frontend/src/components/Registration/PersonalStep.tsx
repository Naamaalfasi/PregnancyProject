import { Box, TextField, Typography, InputAdornment, Grid } from '@mui/material';
import { Cake, Height, Favorite } from '@mui/icons-material';
import { type FormData } from './registration';

interface PersonalStepProps {
  formData: FormData;
  setFormData: (data: FormData) => void;
}

function PersonalStep({ formData, setFormData }: PersonalStepProps) {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Tell us about yourself
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        This information helps us provide personalized health recommendations and track your progress.
      </Typography>
      
      <TextField
        fullWidth
        label="Full Name"
        value={formData.name}
        onChange={(e) => setFormData({...formData, name: e.target.value})}
        sx={{ mb: 2 }}
        required
      />
      
      <TextField
        fullWidth
        label="Date of Birth (DDMMYYYY)"
        value={formData.date_of_birth}
        onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
        placeholder="01011990"
        InputProps={{
          startAdornment: <InputAdornment position="start"><Cake /></InputAdornment>
        }}
        sx={{ mb: 2 }}
        required
        helperText="Format: DDMMYYYY (e.g., 01011990)"
      />
      
      <Grid container spacing={2}>
        <Box>
          <TextField
            fullWidth
            label="Height (cm)"
            type="number"
            value={formData.height}
            onChange={(e) => setFormData({...formData, height: e.target.value})}
            InputProps={{
              startAdornment: <InputAdornment position="start"><Height /></InputAdornment>
            }}
            helperText="Optional"
          />
        </Box>
        <Box>
          <TextField
            fullWidth
            label="Weight (kg)"
            type="number"
            value={formData.weight}
            onChange={(e) => setFormData({...formData, weight: e.target.value})}
            InputProps={{
              startAdornment: <InputAdornment position="start"><Favorite /></InputAdornment>
            }}
            helperText="Optional"
          />
        </Box>
      </Grid>
      
      <TextField
        fullWidth
        label="Blood Type"
        value={formData.blood_type}
        onChange={(e) => setFormData({...formData, blood_type: e.target.value})}
        placeholder="A+, B-, O+, etc."
        sx={{ mt: 2 }}
        helperText="Optional - e.g., A+, B-, O+, AB-"
      />
    </Box>
  );
}

export default PersonalStep;
