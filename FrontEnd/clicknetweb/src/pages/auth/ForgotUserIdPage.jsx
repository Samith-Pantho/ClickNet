import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ForgotUserIdForm from '../../components/auth/ForgotUserIdForm';
import Modal from '../../components/common/Modal';
import OTPModal from '../../components/common/OTPModal';
import { forgotUserId } from '../../services/authService';

const ForgotUserIdPage = () => {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showOTPModal, setShowOTPModal] = useState(false);
  const [recoveryData, setRecoveryData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [captchaToken, setCaptchaToken] = useState(null);
  const captchaRef = useRef(null);

  const handleRecoverUserId = async (data) => {
    setIsLoading(true);
    try {
      if (!captchaToken) {
        setError("Please complete the CAPTCHA");
        return;
      }
      data.captcha_token = captchaToken;
      const response = await forgotUserId(data);
      
      if (response.data.Status === 'OK') {
        setSuccess(response.data.Message || `Your User ID is: ${response.data.Result.user_id}`);
      } else if (response.data.Status === 'OTP') {
        setRecoveryData(data);
        setShowOTPModal(true);
      } else {
        captchaRef.current?.reset();
        setCaptchaToken(null);
        setError(response.data.Message || 'User ID recovery failed');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred during User ID recovery');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOTPSubmit = async (otp) => {
    setIsLoading(true);
    try {
      const updatedData = { ...recoveryData, otp };
      const response = await forgotUserId(updatedData);
      
      if (response.data.Status === 'OK') {
        setSuccess(response.data.Message || `Your User ID is: ${response.data.Result.user_id}`);
        setShowOTPModal(false);
        navigate('/login');
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
      <ForgotUserIdForm 
        onSubmit={handleRecoverUserId} 
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

export default ForgotUserIdPage;