import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get('/api/dashboard', { withCredentials: true ,headers: { 'Cache-Control': 'no-cache' }});
      setCurrentUser(response.data);
    } catch (error) {
      setCurrentUser(null);
    }
    setLoading(false);
  };

  const login = async (email, password) => {
    const response = await axios.post('/api/login', { email, password }, { withCredentials: true });
    await checkAuthStatus();
    return response;
  };

  const logout = async () => {
    await axios.get('/api/logout', { withCredentials: true });
    setCurrentUser(null);
  };

  return (
    <AuthContext.Provider value={{ currentUser, loading, login, logout }}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);