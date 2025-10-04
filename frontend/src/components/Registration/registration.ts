export interface FormData {
    // Step 1: Account
    email: string;
    password: string;
    confirmPassword: string;
    
    // Step 2: Personal
    name: string;
    date_of_birth: string;
    height: string;
    weight: string;
    blood_type: string;
    
    // Step 3: Pregnancy
    lmp_date: string;
    due_date: string;
    
    // Step 4: Medical
    medical_conditions: string[];
    allergies: string[];
    medications: string[];
  }
  
  export interface FormDataProps {
    formData: FormData;
    setFormData: (data: FormData) => void;
  }