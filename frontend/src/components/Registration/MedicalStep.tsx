import {
  TextField,
  Button,
  Box,
  Typography,
  IconButton
} from '@mui/material';
import { Add, Delete } from '@mui/icons-material';

interface MedicalStepProps {
  formData: any;
  setFormData: (data: any) => void;
}

const MedicalStep: React.FC<MedicalStepProps> = ({ formData, setFormData }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {/* Medical Conditions */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
          Medical Conditions - Optional
        </Typography>
        {formData.medical_conditions.map((condition: string, index: number) => (
          <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Enter medical condition (e.g., Diabetes, Hypertension)"
              value={condition}
              onChange={(e) => {
                const newConditions = [...formData.medical_conditions];
                newConditions[index] = e.target.value;
                setFormData({...formData, medical_conditions: newConditions});
              }}
              sx={{ mr: 1 }}
            />
            <IconButton
              size="small"
              onClick={() => {
                const newConditions = formData.medical_conditions.filter((_: any, i: number) => i !== index);
                setFormData({...formData, medical_conditions: newConditions});
              }}
              sx={{ color: 'error.main' }}
            >
              <Delete />
            </IconButton>
          </Box>
        ))}
        <Button
          variant="outlined"
          size="small"
          startIcon={<Add />}
          onClick={() => {
            setFormData({...formData, medical_conditions: [...formData.medical_conditions, '']});
          }}
          sx={{ mt: 1 }}
        >
          Add Medical Condition
        </Button>
      </Box>

      {/* Allergies */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
          Allergies - Optional
        </Typography>
        {formData.allergies.map((allergy: string, index: number) => (
          <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Enter allergy (e.g., Peanuts, Shellfish)"
              value={allergy}
              onChange={(e) => {
                const newAllergies = [...formData.allergies];
                newAllergies[index] = e.target.value;
                setFormData({...formData, allergies: newAllergies});
              }}
              sx={{ mr: 1 }}
            />
            <IconButton
              size="small"
              onClick={() => {
                const newAllergies = formData.allergies.filter((_: any, i: number) => i !== index);
                setFormData({...formData, allergies: newAllergies});
              }}
              sx={{ color: 'error.main' }}
            >
              <Delete />
            </IconButton>
          </Box>
        ))}
        <Button
          variant="outlined"
          size="small"
          startIcon={<Add />}
          onClick={() => {
            setFormData({...formData, allergies: [...formData.allergies, '']});
          }}
          sx={{ mt: 1 }}
        >
          Add Allergy
        </Button>
      </Box>

      {/* Current Medications */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
          Current Medications - Optional
        </Typography>
        {formData.medications.map((medication: string, index: number) => (
          <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Enter medication (e.g., Prenatal vitamins, Iron supplements)"
              value={medication}
              onChange={(e) => {
                const newMedications = [...formData.medications];
                newMedications[index] = e.target.value;
                setFormData({...formData, medications: newMedications});
              }}
              sx={{ mr: 1 }}
            />
            <IconButton
              size="small"
              onClick={() => {
                const newMedications = formData.medications.filter((_: any, i: number) => i !== index);
                setFormData({...formData, medications: newMedications});
              }}
              sx={{ color: 'error.main' }}
            >
              <Delete />
            </IconButton>
          </Box>
        ))}
        <Button
          variant="outlined"
          size="small"
          startIcon={<Add />}
          onClick={() => {
            setFormData({...formData, medications: [...formData.medications, '']});
          }}
          sx={{ mt: 1 }}
        >
          Add Medication
        </Button>
      </Box>
    </Box>
  );
};

export default MedicalStep;
