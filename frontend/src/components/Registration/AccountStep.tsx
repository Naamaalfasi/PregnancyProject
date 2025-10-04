import { Box, TextField, Typography, InputAdornment } from '@mui/material';
import { Person, Lock } from '@mui/icons-material';
import { type FormData } from './registration';


interface AccountStepProps {
  formData: FormData;
  setFormData: (data: FormData) => void;
}

function AccountStep({ formData, setFormData }: AccountStepProps) {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Let's start with your account
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        We'll use your email to send you important updates and reminders about your pregnancy journey.
      </Typography>
      
      <TextField
        fullWidth
        label="Email Address"
        type="email"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
        InputProps={{
          startAdornment: <InputAdornment position="start"><Person /></InputAdornment>
        }}
        sx={{ mb: 2 }}
        required
      />
      
      <TextField
        fullWidth
        label="Password"
        type="password"
        value={formData.password}
        onChange={(e) => setFormData({...formData, password: e.target.value})}
        InputProps={{
          startAdornment: <InputAdornment position="start"><Lock /></InputAdornment>
        }}
        sx={{ mb: 2 }}
        required
        helperText="Minimum 6 characters"
      />
      
      <TextField
        fullWidth
        label="Confirm Password"
        type="password"
        value={formData.confirmPassword}
        onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
        InputProps={{
          startAdornment: <InputAdornment position="start"><Lock /></InputAdornment>
        }}
        required
      />
    </Box>
  );
}

export default AccountStep;
