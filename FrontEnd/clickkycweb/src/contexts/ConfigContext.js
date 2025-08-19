import React, { useState, useEffect } from 'react';
import { fetchAllAppSettings } from '../services/configService';
import LoadingSpinner from '../components/common/LoadingSpinner';

export const ConfigContext = React.createContext();

export const ConfigProvider = ({ children }) => {
  const [config, setConfig] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Define all required configuration keys
  const configKeys = ['OTP_LENGTH', 
    'OTP_TYPE', 
    'GOOGLE_RECAPTCHA_SITE_KEY'
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
  }, []);

  if (loading) return <div><LoadingSpinner /></div>;
  if (error) return <div className="config-error">Configuration error: {error}</div>;

  return (
    <ConfigContext.Provider value={config}>
      {children}
    </ConfigContext.Provider>
  );
};
