import { Box, TextField, Typography, InputAdornment } from '@mui/material';
import { PregnantWoman } from '@mui/icons-material';
import { type FormData } from './registration';

interface PregnancyStepProps {
  formData: FormData;
  setFormData: (data: FormData) => void;
}

function PregnancyStep({ formData, setFormData }: PregnancyStepProps) {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Pregnancy Information
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        This helps us provide week-specific advice, track important milestones, and remind you of upcoming appointments.
      </Typography>
      
      <TextField
        fullWidth
        label="Last Menstrual Period (DDMMYYYY)"
        value={formData.lmp_date}
        onChange={(e) => setFormData({...formData, lmp_date: e.target.value})}
        placeholder="01012024"
        InputProps={{
          startAdornment: <InputAdornment position="start"><PregnantWoman /></InputAdornment>
        }}
        sx={{ mb: 2 }}
        helperText="Format: DDMMYYYY (e.g., 01012024) - Optional"
      />
      
      <TextField
        fullWidth
        label="Due Date (DDMMYYYY)"
        value={formData.due_date}
        onChange={(e) => setFormData({...formData, due_date: e.target.value})}
        placeholder="08092024"
        helperText="Leave empty if you don't know yet - we can calculate it from your LMP"
      />
    </Box>
  );
}

export default PregnancyStep;
