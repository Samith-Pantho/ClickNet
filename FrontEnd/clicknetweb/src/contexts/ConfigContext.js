import React, { useState, useEffect } from 'react';
import { fetchAllAppSettings } from '../services/configService';

export const ConfigContext = React.createContext();

export const ConfigProvider = ({ children }) => {
  const [config, setConfig] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Define all required configuration keys
  const configKeys = ['LOGIN_AFTER_OTP_VERIFICATION', 
    'OTP_LENGTH', 
    'OTP_TYPE', 
    'MOBILE_MENDATORY_AT_FORGET_PASSWORD',
    'TAXID_MENDATORY_AT_FORGET_PASSWORD', 
    'DOB_VERIFICATION_MENDATORY_AT_FORGET_PASSWORD',
    'MOBILE_MENDATORY_AT_FORGET_USERID',
    'TAXID_MENDATORY_AT_FORGET_USERID', 
    'DOB_VERIFICATION_MENDATORY_AT_FORGET_USERID',
    'AUTO_GENARATED_PASSWORD', 
    'AUTO_SET_USER_ID_AT_SIGNUP',
    'DEFAULT_AUTHENTICATION_TYPE',
    'GOOGLE_RECAPTCHA_SITE_KEY',
    'ORS_API_KEY',
    'STRIPE_PUBLISHABLE_KEY',
    'ENCRYPTION_SECRET_KEY_FOR_BOTH_BACKEND_FRONTEND'
    ];

  useEffect(() => {
    const fetchConfigs = async () => {
      try {
        const params = new URLSearchParams();
        configKeys.forEach(key => params.append('keys', key));
        const response = await fetchAllAppSettings(params);

        if (response.data && response.data.Status === 'OK') {
          const result = response.data.Result;

          if (Array.isArray(result)) {
            const configObj = {};
            result.forEach(item => {
              configObj[item.KEY] = item.VALUE;
            });
            setConfig(configObj);
            localStorage.setItem('appConfig', JSON.stringify(configObj));
          } else {
            throw new Error('Invalid config format');
          }
        } else {
          throw new Error('Failed to load configuration');
        }
      } catch (err) {
        console.error('Configuration error:', err);
        setError(err.message);
        
        // Load from localStorage fallback
        const cachedConfig = localStorage.getItem('appConfig');
        if (cachedConfig) {
          setConfig(JSON.parse(cachedConfig));
          console.log('Loaded config from localStorage');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchConfigs();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) return (
  <div className="loading-overlay">
    <img 
      src="/assets/images/loading.gif" 
      alt="Loading..." 
      className="loading-gif"
    />
  </div>
);

  if (error) return <div className="config-error">Configuration error: {error}</div>;

  return (
    <ConfigContext.Provider value={config}>
      {children}
    </ConfigContext.Provider>
  );
};
