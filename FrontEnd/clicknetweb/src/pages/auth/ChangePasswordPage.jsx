import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiLock, FiEye, FiEyeOff, FiCheckCircle } from 'react-icons/fi';
import { useAuth } from '../../contexts/AuthContext';
import { changePassword } from '../../services/authService';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import backgroundImage from '../../assets/images/Bg.png'; 
import logo from '../../assets/images/clicknet-logo.png';

const ChangePasswordPage = () => {
  const defaultFormData = {
    oldPassword: '',
    newPassword: '',
    confirmNewPassword: ''
  };
  const [formData, setFormData] = useState(defaultFormData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const { user, logout } = useAuth();
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [requirements, setRequirements] = useState({
    length: false,
    upper: false,
    lower: false,
    number: false,
    special: false
  });
  const navigate = useNavigate();
  
  useEffect(() => {
    if (user === undefined) return; 

    if (user === null)
      navigate('/login', { replace: true });
  }, [user, navigate]);

  if (user === undefined) return null;

  const checkRequirements = (password) => {
    setRequirements({
      length: password.length >= 8,
      upper: /[A-Z]/.test(password),
      lower: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[!@%^&*]/.test(password)
    });
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (name === 'newPassword') {
      checkRequirements(value);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.newPassword !== formData.confirmNewPassword) {
      setError("New passwords don't match");
      return;
    }
    
    setLoading(true);
    try {
      const request = {
        UserID: user?.userId,
        OldPassword: formData.oldPassword,
        NewPassword: formData.newPassword,
        ConfirmNewPassword: formData.confirmNewPassword
      };

      const response = await changePassword(request);
      
      if (response.data.Status === 'OK') {
        setSuccess('Password changed successfully. You will be logged out shortly...');
        
        // Logout after 3 seconds
        setTimeout(() => {
          logout();
          navigate('/login');
        }, 3000);
        setFormData(defaultFormData);
      } else {
        setError(response.data.Message || 'Password change failed');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="auth-container auth-overlay" style={{ 
      backgroundImage: `url(${backgroundImage})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }}>
      <div className="auth-form-wrapper">
        <div className="logo-title-container">
          <img src={logo} alt="ClickNet Logo" className="auth-logo" />
          <h3 className="auth-title" >Change Password <FiLock size={24} /></h3>
        </div>
        <div className="password-change-container">

          <div className="password-instructions">
            <h3>Password Requirements:</h3>
            <ul>
              <li className={requirements.length ? 'valid' : ''}>
                <FiCheckCircle /> Minimum 8 characters
              </li>
              <li className={requirements.upper ? 'valid' : ''}>
                <FiCheckCircle /> At least one uppercase letter
              </li>
              <li className={requirements.lower ? 'valid' : ''}>
                <FiCheckCircle /> At least one lowercase letter
              </li>
              <li className={requirements.number ? 'valid' : ''}>
                <FiCheckCircle /> At least one number
              </li>
              <li className={requirements.special ? 'valid' : ''}>
                <FiCheckCircle /> At least one special character (!@#$%^&*)
              </li>
            </ul>
          </div>

          <form className="password-form" onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Current Password</label>
                <div className="input-with-icon">
                  <input
                    type={showCurrent ? "text" : "password"}
                    placeholder="Enter your current password"
                    name="oldPassword"
                    value={formData.oldPassword}
                    onChange={handleChange}
                    required
                  />
                  <button 
                    type="button" 
                    className="toggle-visibility"
                    onClick={() => setShowCurrent(!showCurrent)}
                  >
                    {showCurrent ? <FiEyeOff /> : <FiEye />}
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label>New Password</label>
                <div className="input-with-icon">
                  <input
                    type={showNew ? "text" : "password"}
                    placeholder="Create new password"
                    name="newPassword"
                    value={formData.newPassword}
                    onChange={handleChange}
                    required
                  />
                  <button 
                    type="button" 
                    className="toggle-visibility"
                    onClick={() => setShowNew(!showNew)}
                  >
                    {showNew ? <FiEyeOff /> : <FiEye />}
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label>Confirm New Password</label>
                <div className="input-with-icon">
                  <input
                    type={showConfirm ? "text" : "password"}
                    placeholder="Re-enter new password"
                    name="confirmNewPassword"
                    value={formData.confirmNewPassword}
                    onChange={handleChange}
                    required
                  />
                  <button 
                    type="button" 
                    className="toggle-visibility"
                    onClick={() => setShowConfirm(!showConfirm)}
                  >
                    {showConfirm ? <FiEyeOff /> : <FiEye />}
                  </button>
                </div>
              </div>
            </div>
            <div className="form-actions">
              <button type="submit" className="primary-btn" disabled={loading}>
                {loading ? 'Processing...' : 'Change Password'}
              </button>
              <button type="button" className="secondary-btn"  onClick={() => navigate('/login')}>
                Cancel
              </button>
            </div>
          </form>
        </div>

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
    </div>
  </div>

  );
};

export default ChangePasswordPage;