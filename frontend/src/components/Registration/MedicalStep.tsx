import { Box, TextField, Typography } from '@mui/material';
import { LocalHospital } from '@mui/icons-material';
import { type FormData } from './registration';

interface MedicalStepProps {
  formData: FormData;
  setFormData: (data: FormData) => void;
}

function MedicalStep({ formData, setFormData }: MedicalStepProps) {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Medical Information
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        This information ensures we provide safe and relevant health guidance. All information is kept private and secure.
      </Typography>
      
      <TextField
        fullWidth
        label="Medical Conditions"
        value={formData.medical_conditions.join(', ')}
        onChange={(e) => setFormData({...formData, medical_conditions: e.target.value.split(',').map(s => s.trim()).filter(s => s)})}
        placeholder="Diabetes, High Blood Pressure, etc."
        helperText="Separate multiple conditions with commas - Optional"
        sx={{ mb: 2 }}
      />
      
      <TextField
        fullWidth
        label="Allergies"
        value={formData.allergies.join(', ')}
        onChange={(e) => setFormData({...formData, allergies: e.target.value.split(',').map(s => s.trim()).filter(s => s)})}
        placeholder="Peanuts, Penicillin, etc."
        helperText="Separate multiple allergies with commas - Optional"
        sx={{ mb: 2 }}
      />
      
      <TextField
        fullWidth
        label="Current Medications"
        value={formData.medications.join(', ')}
        onChange={(e) => setFormData({...formData, medications: e.target.value.split(',').map(s => s.trim()).filter(s => s)})}
        placeholder="Prenatal vitamins, Iron supplements, etc."
        helperText="Separate multiple medications with commas - Optional"
      />
    </Box>
  );
}

export default MedicalStep;
