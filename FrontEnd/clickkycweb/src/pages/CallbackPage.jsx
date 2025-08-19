import React, {  useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/common/LoadingSpinner';

const Callback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setAccessToken } = useAuth();
  useEffect(() => {
    const verifyResult = async () => {
      try {
        // Extract parameters from URL
        const data = searchParams.get('data');
        setAccessToken(data)
        setTimeout(() => {
          navigate('/', { state: { currentStep: 4 } });
        }, 5000);
      } catch (err) {
        setTimeout(() => {
          navigate('/', { state: { currentStep: 3 } });
        }, 5000);
      }
    };

    verifyResult();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <LoadingSpinner />;
};

export default Callback;