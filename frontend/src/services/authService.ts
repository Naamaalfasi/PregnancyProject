class AuthService {
  private baseURL = 'http://localhost:8000';

  async login(email: string, password: string): Promise<{ success: boolean; user?: any }> {
    try {
      // Step 1: Verify password
      const verifyResponse = await fetch(`${this.baseURL}/users/verify-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (!verifyResponse.ok) {
        return { success: false };
      }

      const isValid = await verifyResponse.json();
      if (!isValid) {
        return { success: false };
      }

      // Step 2: Get user profile
      const userResponse = await fetch(`${this.baseURL}/users/email/${email}`);
      if (!userResponse.ok) {
        return { success: false };
      }

      const userId = await userResponse.json();
      
      // Step 3: Store user data
      localStorage.setItem('currentUser', JSON.stringify(userId));
      
      return { success: true, user: userId };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false };
    }
  }

  async newRegister(userProfile: any): Promise<{ success: boolean; user?: any; error?: string }> {
    try {
      const response = await fetch(`${this.baseURL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userProfile)
      });
      
      if (!response.ok) {
        return { success: false, error: 'Registration failed. User ID might already exist.' };
      }
      
      // Auto-login after successful registration
      const response2 = await fetch(`${this.baseURL}/users/email/${userProfile.email}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response2.ok) {
        return { success: false, error: 'Couldnt give you a user id by email.' };
      }
      const userID = await response2.json();
      localStorage.setItem('currentUser', userID);
      
      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Network error. Please check your connection.' };
    }
  }

  async register(email: string, password: string): Promise<{ success: boolean; user?: any; error?: string }> {
    try {
      // Create minimal user profile object with only required fields
      const userProfile = {
        user_id: "1",
        password: password,
        name: "None-String",           // Default value
        email: email,          // Default value
        date_of_birth: "None-String",  // Default value
        lmp_date: "None-String",       // Default value
        due_date: "None-String",       // Default value
        pregnancy_week: null,          // Will be calculated later
        age: 0,                        // Will be calculated later
        height: 0,                     // Default value
        weight: 0,                     // Default value
        blood_type: "None-String",     // Default value
        medical_conditions: [],        // Empty array
        allergies: [],                 // Empty array
        medications: [],               // Empty array
        medical_documents: [],         // Empty array
        tasks: [],                     // Empty array
        conversations: [],             // Empty array
        current_conversation: "None-String", // Default value
        created_at: new Date().toISOString(), // Current timestamp
        updated_at: new Date().toISOString()  // Current timestamp
      };

      // Send POST request to /users endpoint
      const response = await fetch(`${this.baseURL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userProfile)
      });

      // Check if request was successful
      if (!response.ok) {
        // Try to get error message from response
        const errorData = await response.json().catch(() => ({}));
        return { 
          success: false, 
          error: errorData.detail || 'Registration failed. User ID might already exist.' 
        };
      }
      
      // Store user data in localStorage and auto-login
      const response2 = await fetch(`${this.baseURL}/users/email/${email}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response2.ok) {
        return { success: false, error: 'Couldnt give you a user id by email.' };
      }
      const userID = await response2.json();
      localStorage.setItem('currentUser', JSON.stringify(userID));
      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Network error. Please check your connection.' };
    }
  }

  async verifyUserId(userId: string) {
    return await fetch(`${this.baseURL}/users/${userId}/validate`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
  }

  getCurrentUserId() {
    const saved = localStorage.getItem('currentUser');
    return saved ? JSON.parse(saved) : null;
  }

  logout() {
    localStorage.removeItem('currentUser');
  }

  async isLoggedIn() {
    const user = this.getCurrentUserId();
    if (!user) return false;
    
    // Verify with server by attempting login
    try {
      const response = await this.verifyUserId(user);
      return response.ok;
    } catch (error) {
      return false;
    }
  }
}

export const authService = new AuthService();


