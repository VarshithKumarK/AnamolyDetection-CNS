import { createContext, useContext, useState, useEffect } from 'react';
import authService from '../api/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  // Persistence Logic
  // NOTE: For production, it is recommended to use httpOnly cookies for token storage to prevent XSS attacks.
  // The current implementation uses localStorage for simplicity in this demo environment.
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');

      if (storedToken && storedToken !== 'null' && storedToken !== 'undefined') {
        setToken(storedToken);
        let parsedUser = null;
        if (storedUser && storedUser !== 'null' && storedUser !== 'undefined') {
          try {
            parsedUser = JSON.parse(storedUser);
            setUser(parsedUser);
          } catch (e) {
            console.error("Failed to parse stored user data:", e);
            localStorage.removeItem('user');
          }
        }
        
        // If we still don't have a user but have a token, try to fetch it
        if (!parsedUser) {
             try {
                 const userProfile = await authService.getProfile();
                 setUser(userProfile);
                 localStorage.setItem('user', JSON.stringify(userProfile));
             } catch (error) {
                 console.error("Failed to fetch profile with stored token:", error);
                 logout();
             }
        }
      } else {
        // Invalid token string found
        if (storedToken) logout();
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (credentials) => {
    try {
      const data = await authService.login(credentials);
      // Backend returns: { _id, name, email, token }
      const receivedToken = data.token;
      // Extract user fields (exclude token)
      const { token, ...receivedUser } = data;

      localStorage.setItem('token', receivedToken);
      localStorage.setItem('user', JSON.stringify(receivedUser));
      
      setToken(receivedToken);
      setUser(receivedUser);
      return data;
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  const signup = async (userData) => {
    try {
      const data = await authService.signup(userData);
      const receivedToken = data.token;
      // Extract user fields
      const { token, ...receivedUser } = data;

      localStorage.setItem('token', receivedToken);
      localStorage.setItem('user', JSON.stringify(receivedUser));

      setToken(receivedToken);
      setUser(receivedUser);
      return data;
    } catch (error) {
      console.error("Signup failed:", error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('lastAnalysis'); // Clean up analysis data on logout
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      login, 
      signup, 
      logout, 
      loading, 
      isAuthenticated: !!token 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
