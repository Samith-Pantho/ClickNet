import React, { useState, useContext, forwardRef  } from 'react';
import { useNavigate } from 'react-router-dom';
import { ConfigContext } from '../../contexts/ConfigContext';
import backgroundImage from '../../assets/images/Bg.png'; 
import logo from '../../assets/images/clicknet-logo.png';
import Captcha from '../common/Captcha'

const ForgotPasswordForm = forwardRef(({ onSubmit, isLoading, onChange }, ref) => {
  const config = useContext(ConfigContext);
  const [formData, setFormData] = useState({
    userId: '',
    customerId: '',
    taxId: '',
    birthDate: '',
    phone: '',
    email: '',
    newPassword: '',
    confirmPassword: '',
    otpChannel: config.DEFAULT_AUTHENTICATION_TYPE,
    captcha_token: null
  });

  const navigate = useNavigate();
  const captchaRef = ref;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="auth-container auth-overlay" style={{ 
      backgroundImage: `url(${backgroundImage})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }}>
      <div className="auth-form-wrapper">
        <div className="logo-title-container">
          <img src={logo} alt="ClickNet Logo" className="auth-logo" />
          <h3 className="auth-title">Reset Password</h3>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="userId">User ID</label>
            <input
              type="text"
              id="userId"
              name="userId"
              value={formData.userId}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="customerId">Customer ID</label>
              <input
                type="text"
                id="customerId"
                name="customerId"
                value={formData.customerId}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="taxId">Verification ID</label>
              <input
                type="text"
                id="taxId"
                name="taxId"
                value={formData.taxId}
                onChange={handleChange}
                required={config.TAXID_MENDATORY_AT_FORGET_PASSWORD?.toLowerCase() === 'true'}
              />
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="birthDate">Date of Birth</label>
              <input
                type="date"
                id="birthDate"
                name="birthDate"
                value={formData.birthDate}
                onChange={handleChange}
                required={config.DOB_VERIFICATION_MENDATORY_AT_FORGET_PASSWORD?.toLowerCase() === 'true'}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="phone">Phone Number</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                required={config.MOBILE_MENDATORY_AT_FORGET_PASSWORD?.toLowerCase() === 'true'}
              />
            </div>
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Email (Optional)</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
            />
          </div>
          
          {config.AUTO_GENARATED_PASSWORD?.toLowerCase() === 'false' && (
            <div className="form-row" hidden>
              <div className="form-group">
                <label htmlFor="newPassword">New Password</label>
                <input
                  type="password"
                  id="newPassword"
                  name="newPassword"
                  value={formData.newPassword}
                  onChange={handleChange}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
          )}

          <div className="checkbox-padding">
            <p className='otp-channel-title'>OTP Verification Channel</p>
            <div className="form-row">
              <div className="form-group">
                <label className="checkbox-container">
                  <input
                    type="radio"
                    name="otpChannel"
                    value="SMS"
                    checked={formData.otpChannel === 'SMS'}
                    onChange={handleChange}
                  />
                  <span className="checkmark"></span>
                  SMS
                </label>
              </div>
              <div className="form-group">
                <label className="checkbox-container">
                  <input
                    type="radio"
                    name="otpChannel"
                    value="EMAIL"
                    checked={formData.otpChannel === 'EMAIL'}
                    onChange={handleChange}
                  />
                  <span className="checkmark"></span>
                  Email
                </label>
              </div>
              <div className="form-group">
                <label className="checkbox-container">
                  <input
                    type="radio"
                    name="otpChannel"
                    value="BOTH"
                    checked={formData.otpChannel === 'BOTH'}
                    onChange={handleChange}
                  />
                  <span className="checkmark"></span>
                  Both
                </label>
              </div>
            </div>
          </div>
          
          <div className='align-center'>
            <Captcha
              ref={captchaRef}
              onChange={onChange}
            />
          </div>
          
          <div className="form-actions">
            <button type="submit" className="button button-primary" disabled={isLoading}>
              {isLoading ? 'Resetting...' : 'Reset Password'}
            </button>
            <button type="button" className="button button-secondary" onClick={() => navigate('/login')}>
              Back to Login
            </button>
          </div>
        </form>
      </div>
    </div>
  );
});

export default ForgotPasswordForm;