import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ForgotPasswordForm from '../../components/auth/ForgotPasswordForm';
import Modal from '../../components/common/Modal';
import OTPModal from '../../components/common/OTPModal';
import { forgotPassword } from '../../services/authService';

const ForgotPasswordPage = () => {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showOTPModal, setShowOTPModal] = useState(false);
  const [resetData, setResetData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [captchaToken, setCaptchaToken] = useState(null);
  const captchaRef = useRef(null);

  const handleResetPassword = async (data) => {
    setIsLoading(true);
    try {
      if (data.newPassword !== data.confirmPassword) {
        setError('Passwords do not match');
        return;
      }
      if (!captchaToken) {
        setError("Please complete the CAPTCHA");
        return;
      }
      data.captcha_token = captchaToken;
      const response = await forgotPassword(data);
      
      if (response.data.Status === 'OK') {
        setSuccess(response.data.Message || 'Password reset successful');
        setTimeout(() => navigate('/login'), 3000);
      } else if (response.data.Status === 'OTP') {
        setResetData(data);
        setShowOTPModal(true);
      } else {
        captchaRef.current?.reset();
        setCaptchaToken(null);
        setError(response.data.Message || 'Password reset failed');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred during password reset');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOTPSubmit = async (otp) => {
    setIsLoading(true);
    try {
      const updatedData = { ...resetData, otp };
      const response = await forgotPassword(updatedData);
      
      if (response.data.Status === 'OK') {
        setSuccess(response.data.Message || 'Password reset successful');
        setShowOTPModal(false);
        setTimeout(() => navigate('/login'), 2000);
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
      <ForgotPasswordForm 
        onSubmit={handleResetPassword} 
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

export default ForgotPasswordPage;