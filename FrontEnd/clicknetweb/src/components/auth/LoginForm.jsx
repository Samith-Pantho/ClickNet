import React, { useState, useContext, forwardRef  } from 'react';
import { useNavigate } from 'react-router-dom';
import { ConfigContext } from '../../contexts/ConfigContext';
import backgroundImage from '../../assets/images/Bg.png'; 
import logo from '../../assets/images/clicknet-logo.png';
import Captcha from '../common/Captcha'
import { FaUser, FaLock, FaSearch, FaUniversity } from 'react-icons/fa'; 

const LoginForm = forwardRef(({ onSubmit, isLoading, onChange }, ref) => {
  const config = useContext(ConfigContext);
  const [formData, setFormData] = useState({
    userId: '',
    password: '',
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
          <h1 className="auth-title">ClickNet</h1>
        </div>

        <div className="three-column-layout">
          
          <div className="dos-column">
            <div className="dos-section">
              <h3>Security Do's</h3>
              <div className="dos">
                <p><span className="check">✓</span> ALWAYS ensure the website starts with https:// and has a valid certificate</p>
                <p><span className="check">✓</span> ALWAYS properly log out after completing online banking activities</p>
                <p><span className="check">✓</span> ALWAYS keep your computer's antivirus and firewall up-to-date</p>
                <p><span className="check">✓</span> ALWAYS use secure, private networks for financial transactions</p>
                <p><span className="check">✓</span> ALWAYS keep your banking app and devices updated</p>
              </div>
            </div>
          </div>

          
          <div className="login-column">
            <div className="login-section">
              <h2>Login</h2>
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <input
                  type="text"
                  id="userId"
                  name="userId"
                  placeholder="User ID"
                  value={formData.userId}
                  onChange={handleChange}
                  required
                  />
                </div>
                
                <div className="form-group">
                  <input
                  type="password"
                  id="password"
                  name="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  />
                </div>

                {config.LOGIN_AFTER_OTP_VERIFICATION?.toLowerCase() === 'true' && (
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
                )}
                
                <div className='align-center'>
                  <Captcha
                    ref={captchaRef}
                    onChange={onChange}
                  />
                </div>

                <div className="form-actions">
                  <button type="submit" disabled={isLoading}>
                  {isLoading ? 'Logging in...' : 'Log in'}
                  </button>
                  <button type="button" className="refresh-btn">
                  Refresh
                  </button>
                </div>
              </form>
              
            <div className="divider"></div>

            <div className="recovery-section">
              <div className="recovery-links">
                <button type="button" onClick={() => navigate('/forgot-password')}>
                  <FaLock /> Forgot Password? 
                </button>
                <button type="button" onClick={() => navigate('/forgot-userid')}>
                  <FaUser /> Forgotten your User ID? 
                </button>
              </div>
              <div className="recovery-links">
                <button type="button" onClick={() => navigate('/register')}>
                  <FaUniversity /> Don't have an account? Please Sign Up 
                </button>
              </div>
              
              <div className="recovery-links">
                <button type="button" onClick={() => navigate('/branches')}>
                  <FaSearch /> Find Branches 
                </button>
              </div>
            </div>
          </div>
        </div>

          {/* Right Column - Don'ts */}
          <div className="donts-column">
            <div className="donts-section">
              <h3>Security Don'ts</h3>
              <div className="donts">
                <p><span className="cross">✗</span> NEVER disclose your Login ID, Password, or OTP to anyone</p>
                <p><span className="cross">✗</span> NEVER store your banking credentials in notes or unsecured apps</p>
                <p><span className="cross">✗</span> NEVER access your account from public/shared computers</p>
                <p><span className="cross">✗</span> NEVER click suspicious links in emails/SMS claiming to be from your bank</p>
                <p><span className="cross">✗</span> NEVER install banking apps from third-party stores</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

export default LoginForm;