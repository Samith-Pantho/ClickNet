import React, { createContext, useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login as authLogin, logout as authLogout } from '../services/authService';
import { fetchProfilePicture } from '../services/bankingService';

const AuthContext = createContext();
export const authState = { user: null };

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadProfilePicture = async () => {
    try {
      setLoading(true);
      const response = await fetchProfilePicture();
      console.log(response);
      if (response.data.Status === 'OK') {
        setLoading(false);
        return response.data.Result?.startsWith('data:image') 
          ? response.data.Result 
          : `data:image/jpeg;base64,${response.data.Result}`;
      }
    } catch (error) {
      setLoading(false);
    }
  };

  const updateProfilePicture = (newPicture) => {
    setUser(prev => ({
      ...prev,
      profile_picture: newPicture || '/assets/images/default-profile.png'
    }));
  };

  const login = async (credentials) => {
    try {
      setLoading(true);
      const response = await authLogin(credentials);
      if (response.data.Status === 'OK') {
        const { access_token, fullName, customerId, userName, ForcePasswordChangedFlag, Advertisements} = response.data.Result;
        
        setUser({
          token: access_token,
          fullName,
          customerId,
          userId: userName,
          forcePasswordChangedFlag: ForcePasswordChangedFlag,
          advertisements: Advertisements,
          profile_picture: await loadProfilePicture() || '/assets/images/default-profile.png'
        });
        if(ForcePasswordChangedFlag)
          navigate('/change-password');
        else
          navigate('/banking');
      }
      setLoading(false);
      return response;
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const updateAdvertisements = () => {
    setUser(prev => ({
      ...prev,
      advertisements: null
    }));
  };

  const logout = async () => {
    try {
      setLoading(true);
      await authLogout();
    } catch (error) {
      setLoading(false);
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setLoading(false);
      navigate('/login');
    }
  };

  authState.user = user;

  return (
    <AuthContext.Provider value={{ user, loading, setUser, login, logout, loadProfilePicture, updateProfilePicture, updateAdvertisements }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);