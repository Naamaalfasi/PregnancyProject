import { useState } from 'react';
import { 
  Box, Button, Typography, Paper, Container,
  Stepper, Step, StepLabel, Alert
} from '@mui/material';
import { authService } from '../../services/authService';

// Step components
import AccountStep from './AccountStep';
import PersonalStep from './PersonalStep';
import PregnancyStep from './PregnancyStep';
import MedicalStep from './MedicalStep';
import { type FormData } from './registration';

const steps = [
  'Account Setup',
  'Personal Info', 
  'Pregnancy Details',
  'Medical Info'
];

interface MultiStepRegistrationProps {
  onRegisterSuccess: () => void;
  onBackToLogin: () => void;
  onBackToHome: () => void;
}

function MultiStepRegistration({ onRegisterSuccess, onBackToLogin, onBackToHome }: MultiStepRegistrationProps) {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<FormData>({
    email: '', password: '', confirmPassword: '',
    name: '', date_of_birth: '', height: '', weight: '', blood_type: '',
    lmp_date: '', due_date: '',
    medical_conditions: [], allergies: [], medications: []
  });
  
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const validateCurrentStep = () => {
    setError('');
    switch (activeStep) {
      case 0:
        if (!formData.email || !formData.password || !formData.confirmPassword) {
          setError('Please fill in all fields');
          return false;
        }
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          return false;
        }
        if (formData.password.length < 6) {
          setError('Password must be at least 6 characters');
          return false;
        }
        return true;
      case 1:
        if (!formData.name || !formData.date_of_birth) {
          setError('Please fill in at least your name and date of birth');
          return false;
        }
        return true;
      case 2:
        // Pregnancy info is optional
        return true;
      case 3:
        // Medical info is optional
        return true;
      default:
        return true;
    }
  };
  
  const handleNext = () => {
    if (validateCurrentStep()) {
      setActiveStep((prev) => prev + 1);
    }
  };
  
  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };
  
  const handleRegister = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      // Create user profile with all collected data
      const userProfile = {
        user_id: "", // Let backend generate
        email: formData.email,
        password: formData.password,
        name: formData.name || "None-String",
        date_of_birth: formData.date_of_birth || "None-String",
        height: parseFloat(formData.height) || 0,
        weight: parseFloat(formData.weight) || 0,
        blood_type: formData.blood_type || "None-String",
        lmp_date: formData.lmp_date || "None-String",
        due_date: formData.due_date || "None-String",
        pregnancy_week: null, // Will be calculated by backend
        age: 0, // Will be calculated by backend
        medical_conditions: formData.medical_conditions,
        allergies: formData.allergies,
        medications: formData.medications,
        medical_documents: [],
        tasks: [],
        conversations: [],
        current_conversation: "None-String",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const result = await authService.newRegister(userProfile);
      
      if (result.success) {
        onRegisterSuccess();
      } else {
        setError(result.error || 'Registration failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const renderStepContent = (step: number) => {
    switch (step) {
      case 0: return <AccountStep formData={formData} setFormData={setFormData} />;
      case 1: return <PersonalStep formData={formData} setFormData={setFormData} />;
      case 2: return <PregnancyStep formData={formData} setFormData={setFormData} />;
      case 3: return <MedicalStep formData={formData} setFormData={setFormData} />;
      default: return null;
    }
  };
  
  return (
    <Container maxWidth="sm">
      <Paper elevation={8} sx={{ p: 4, mt: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Button onClick={onBackToHome} color="inherit">
            ← Back to Home
          </Button>
          <Button onClick={onBackToLogin} color="inherit">
            Already have an account? Login
          </Button>
        </Box>
        <Box component="img" src="/logo.png" alt="Logo" sx={{ width: '60%', height: 'auto', mb: 2 }} />
        <Typography className="auth-title" variant="h4" align="center" gutterBottom>
          Create Your Account
        </Typography>
        
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        
        <Box sx={{ mb: 3 }}>
          {renderStepContent(activeStep)}
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button onClick={handleBack} disabled={activeStep === 0}>
            Back
          </Button>
          
          {activeStep === steps.length - 1 ? (
            <Button variant="contained" onClick={handleRegister} disabled={isLoading}>
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </Button>
          ) : (
            <Button variant="contained" onClick={handleNext}>
              Next
            </Button>
          )}
        </Box>
      </Paper>
    </Container>
  );
}

export default MultiStepRegistration;
