import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import RegisterForm from '../../components/auth/RegisterForm';
import Modal from '../../components/common/Modal';
import OTPModal from '../../components/common/OTPModal';
import { register, checkUserIdAvailability } from '../../services/authService';

const RegisterPage = () => {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showOTPModal, setShowOTPModal] = useState(false);
  const [registrationData, setRegistrationData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [userIdAvailable, setUserIdAvailable] = useState(null);
  const [checkingUserId, setCheckingUserId] = useState(false);
  const [captchaToken, setCaptchaToken] = useState(null);
  const captchaRef = useRef(null);

  const handleUserIdCheck = async (userId) => {
    if (!userId) {
      setUserIdAvailable(null);
      return;
    }

    setCheckingUserId(true);
    try {
      const response = await checkUserIdAvailability(userId);
      setUserIdAvailable(response.data.Status === 'OK' && response.data.Result);
    } catch (err) {
      setError(err.response?.data?.Message || 'Error checking user ID availability');
      setUserIdAvailable(false);
    } finally {
      setCheckingUserId(false);
    }
  };

  const handleRegister = async (data) => {
    setIsLoading(true);
    try {
      
      if (!captchaToken) {
        setError("Please complete the CAPTCHA");
        return;
      }
      data.captcha_token = captchaToken;

      const response = await register(data);
      
      if (response.data.Status === 'OK') {
        setSuccess(response.data.Message || 'Registration successful');
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } else if (response.data.Status === 'OTP') {
        setRegistrationData(data);
        setShowOTPModal(true);
      } else {
        captchaRef.current?.reset();
        setCaptchaToken(null);
        setError(response.data.Message || 'Registration failed');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred during registration');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOTPSubmit = async (otp) => {
    setIsLoading(true);
    try {
      const updatedData = { ...registrationData, otp };
      const response = await register(updatedData);
      
      if (response.data.Status === 'OK') {
        setSuccess(response.data.Message || 'Registration successful');
        setShowOTPModal(false);
        setTimeout(() => {
          navigate('/login');
        }, 3000);
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
      <RegisterForm 
        onSubmit={handleRegister} 
        isLoading={isLoading} 
        onUserIdChange={handleUserIdCheck}
        userIdAvailable={userIdAvailable}
        checkingUserId={checkingUserId}
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

export default RegisterPage;