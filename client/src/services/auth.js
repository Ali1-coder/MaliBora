export const loginUser = async (email, password) => {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
      credentials: 'include'
    });
  
    if (!response.ok) throw new Error('Login failed');
    return await response.json();
  };
  
  export const registerUser = async (userData) => {
    const response = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
  
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Registration failed');
    }
    return await response.json();
  };
  
  export const logoutUser = async () => {
    await fetch('/api/logout', {
      method: 'GET',
      credentials: 'include'
    });
  };
  
  export const checkAuth = async () => {
    const response = await fetch('/api/dashboard', {
      credentials: 'include'
    });
    if (!response.ok) throw new Error('Not authenticated');
    return await response.json();
  };