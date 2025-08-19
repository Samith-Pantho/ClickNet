import React, { createContext, useState, useContext } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [authState, setAuthState] = useState({
    accessToken: null,
    customerData: null,
    status:null
  });

  const setAccessToken= (newAccessToken) => {
    setAuthState(prev => ({
      ...prev,
      accessToken: newAccessToken
    }));
  };

  const setStatus= (newStatus) => {
    setAuthState(prev => ({
      ...prev,
      status: newStatus
    }));
  };
 return (
    <AuthContext.Provider value={{ authState, setAuthState, setAccessToken, setStatus }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);