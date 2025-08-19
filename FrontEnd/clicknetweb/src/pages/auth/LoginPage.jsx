import React, { useState, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import LoginForm from '../../components/auth/LoginForm';
import Modal from '../../components/common/Modal';
import OTPModal from '../../components/common/OTPModal';

const LoginPage = () => {
  const { login } = useAuth();
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showOTPModal, setShowOTPModal] = useState(false);
  const [loginData, setLoginData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [captchaToken, setCaptchaToken] = useState(null);
  const captchaRef = useRef(null);

  const handleLogin = async (data) => {
    setIsLoading(true);
    try {
      if (!captchaToken) {
        setError("Please complete the CAPTCHA");
        return;
      }
      data.captcha_token = captchaToken;
      const response = await login(data);
      
      if (response.data.Status === 'OK') {
        //setSuccess(response.data.Message || 'Login successful');
      } else if (response.data.Status === 'OTP') {
        setLoginData(data);
        setShowOTPModal(true);
      } else {
        captchaRef.current?.reset();
        setCaptchaToken(null);
        setError(response.data.Message || 'Login failed');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred during login');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOTPSubmit = async (otp) => {
    setIsLoading(true);
    try {
      const updatedData = { ...loginData, otp };
      const response = await login(updatedData);
      
      if (response.data.Status === 'OK') {
        //setSuccess(response.data.Message || 'Login successful');
        setShowOTPModal(false);
      } else {
        setError(response.data.Message || 'OTP verification failed');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred during OTP verification');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <LoginForm
        onSubmit={handleLogin}
        isLoading={isLoading}
        onChange={setCaptchaToken}
        ref={captchaRef}
      />
      
      <Modal
        isOpen={!!error}
        onClose={() => setError(null)}
        title="Error"
        message={error}
      />
      
      <Modal
        isOpen={!!success}
        onClose={() => setSuccess(null)}
        title="Success"
        message={success}
      />
      
      <OTPModal
        isOpen={showOTPModal}
        onClose={() => setShowOTPModal(false)}
        onSubmit={handleOTPSubmit}
        isLoading={isLoading}
      />
    </div>
  );
};

export default LoginPage;