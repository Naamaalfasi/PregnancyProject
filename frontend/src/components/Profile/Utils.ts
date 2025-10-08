import Utils from '../../services/utils';

export interface UserProfile {
  user_id: string;
  name: string;
  email: string;
  date_of_birth: string;
  age: number;
  height: number;
  weight: number;
  blood_type: string;
  pregnancy_week: number;
  lmp_date: string;
  due_date: string;
  medical_conditions: string[];
  allergies: string[];
  medications: string[];
}

export interface EditFormData {
  name: string;
  date_of_birth: string;
  height: string;
  weight: string;
  blood_type: string;
  lmp_date: string;
  due_date: string;
  medical_conditions: string[];
  allergies: string[];
  medications: string[];
}

export interface CalculatedFields {
  age: number | null;
  pregnancy_week: number | null;
  due_date: string | null;
}

// Utility functions for date calculations (matching backend logic)
export const parseDDMMYYYY = (dateStr: string): Date | null => {
  if (!dateStr || dateStr === "None-String" || dateStr === "0" || dateStr.length !== 8) {
    return null;
  }
  
  try {
    const day = parseInt(dateStr.substring(0, 2));
    const month = parseInt(dateStr.substring(2, 4));
    const year = parseInt(dateStr.substring(4, 8));
    
    if (day < 1 || day > 31 || month < 1 || month > 12 || year < 1900 || year > 2100) {
      return null;
    }
    
    return new Date(year, month - 1, day); // month is 0-indexed in Date constructor
  } catch {
    return null;
  }
};

export const calculateAge = (dateOfBirth: string): number | null => {
  const birthDate = parseDDMMYYYY(dateOfBirth);
  if (!birthDate) return null;
  
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  
  // Adjust if birthday hasn't occurred this year
  if (today.getMonth() < birthDate.getMonth() || 
      (today.getMonth() === birthDate.getMonth() && today.getDate() < birthDate.getDate())) {
    age -= 1;
  }
  
  return Math.max(0, age);
};

export const calculatePregnancyWeek = (lmpDate: string): number | null => {
  const lmpDateTime = parseDDMMYYYY(lmpDate);
  if (!lmpDateTime) return null;
  
  const today = new Date();
  const diffTime = today.getTime() - lmpDateTime.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  const weeksPregnant = Math.floor(diffDays / 7);
  
  return Math.max(1, Math.min(weeksPregnant, 42)); // Clamp between 1-42 weeks
};

export const calculateDueDate = (lmpDate: string): string | null => {
  const lmpDateTime = parseDDMMYYYY(lmpDate);
  if (!lmpDateTime) return null;
  
  const dueDate = new Date(lmpDateTime);
  dueDate.setDate(dueDate.getDate() + (40 * 7)); // Add 40 weeks
  
  // Convert back to DDMMYYYY format
  const day = dueDate.getDate().toString().padStart(2, '0');
  const month = (dueDate.getMonth() + 1).toString().padStart(2, '0');
  const year = dueDate.getFullYear().toString();
  
  return `${day}${month}${year}`;
};

export const formatDate = (dateString: string) => {
  if (!dateString || dateString === "None-String") return "Not provided";
  try {
    return Utils.convertToDate(dateString).toLocaleDateString();
  } catch {
    return dateString;
  }
};

export const formatList = (items: string[]) => {
  if (!items || items.length === 0) return "None";
  return items.join(", ");
};

export const initializeEditFormData = (userData: UserProfile): EditFormData => {
  return {
    name: userData.name || '',
    date_of_birth: userData.date_of_birth || '',
    height: userData.height?.toString() || '',
    weight: userData.weight?.toString() || '',
    blood_type: userData.blood_type || '',
    lmp_date: userData.lmp_date || '',
    due_date: userData.due_date || '',
    medical_conditions: userData.medical_conditions || [],
    allergies: userData.allergies || [],
    medications: userData.medications || []
  };
};

export const prepareUpdatedProfile = (
  currentUser: UserProfile,
  editFormData: EditFormData,
  calculatedFields: CalculatedFields
) => {
  return {
    ...currentUser,
    name: editFormData.name || "None-String",
    date_of_birth: editFormData.date_of_birth || "None-String",
    height: parseFloat(editFormData.height) || 0,
    weight: parseFloat(editFormData.weight) || 0,
    blood_type: editFormData.blood_type || "None-String",
    lmp_date: editFormData.lmp_date || "None-String",
    due_date: editFormData.due_date || "None-String",
    medical_conditions: editFormData.medical_conditions,
    allergies: editFormData.allergies,
    medications: editFormData.medications,
    // Include calculated fields
    age: calculatedFields.age || currentUser.age,
    pregnancy_week: calculatedFields.pregnancy_week || currentUser.pregnancy_week,
    updated_at: new Date().toISOString()
  };
};
