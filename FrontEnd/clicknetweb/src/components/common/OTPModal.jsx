import React, { useState, useRef, useContext, useEffect  } from 'react';
import { ConfigContext } from '../../contexts/ConfigContext';

const OTPModal = ({ isOpen, onClose, onSubmit, isLoading }) => {
  const config = useContext(ConfigContext);
  const [otp, setOtp] = useState(
    config.OTP_LENGTH ? Array(parseInt(config.OTP_LENGTH, 10)).fill('') : []
  );
   
  const inputRefs = useRef([]);
  useEffect(() => {
    if (isOpen) {
      setOtp(config.OTP_LENGTH ? Array(parseInt(config.OTP_LENGTH, 10)).fill('') : []);
      if (inputRefs.current[0]) {
        inputRefs.current[0].focus();
      }
    }
  }, [isOpen, config.OTP_LENGTH]);

  if (!isOpen) return null;

  const handleChange = (index, value) => {
    let filteredValue = value;
    
    switch(config.OTP_TYPE) {
      case 'NUMERIC':
        filteredValue = value.replace(/\D/g, '');
        break;
      case 'ALPHA_NUMERIC':
        filteredValue = value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
        break;
      case 'NON_ALPHA_NUMERIC':
        // Allow any character except whitespace
        filteredValue = value.replace(/\s/g, '');
        break;
      default:
        filteredValue = value.replace(/\D/g, '');
    }

    if (filteredValue.length <= 1) {
      const newOtp = [...otp];
      newOtp[index] = filteredValue;
      setOtp(newOtp);

      // Auto focus to next input
      if (filteredValue && index < parseInt(config.OTP_LENGTH,10) - 1) {
        inputRefs.current[index + 1].focus();
      }
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1].focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    let pasteData = e.clipboardData.getData('text/plain');
    
    switch(config.OTP_TYPE) {
      case 'NUMERIC':
        pasteData = pasteData.replace(/\D/g, '');
        break;
      case 'ALPHA_NUMERIC':
        pasteData = pasteData.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
        break;
      case 'NON_ALPHA_NUMERIC':
        pasteData = pasteData.replace(/\s/g, '');
        break;
      default:
        pasteData = pasteData.replace(/\D/g, '');
    }
    
    pasteData = pasteData.slice(0, parseInt(config.OTP_LENGTH,10));
    
    if (pasteData.length === parseInt(config.OTP_LENGTH,10)) {
      const newOtp = pasteData.split('');
      setOtp(newOtp);
      inputRefs.current[parseInt(config.OTP_LENGTH,10) - 1].focus();
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const fullOtp = otp.join('');
    if (fullOtp.length === parseInt(config.OTP_LENGTH,10)) {
      onSubmit(fullOtp);
    }
  };

  const getInputPattern = () => {
    switch(config.OTP_TYPE) {
      case 'NUMERIC':
        return '[0-9]*';
      case 'ALPHA_NUMERIC':
        return '[a-zA-Z0-9]*';
      case 'NON_ALPHA_NUMERIC':
        return '[^\\s]*';
      default:
        return '[0-9]*';
    }
  };

  const getInputType = () => {
    return config.OTP_TYPE === 'NUMERIC' ? 'number' : 'text';
  };

  const getInputMode = () => {
    switch(config.OTP_TYPE) {
      case 'NUMERIC':
        return 'numeric';
      case 'ALPHA_NUMERIC':
        return 'text';
      case 'NON_ALPHA_NUMERIC':
        return 'text';
      default:
        return 'numeric';
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-container otp-model-bg">
        <div className={`modal-content`}>
          <div className="modal-close-btn">
              <button 
                onClick={onClose} 
                className="close-btn"
              >
                &times;
              </button>
            </div>
          <div className="modal-header">
            <h3 className="modal-title">OTP Verification</h3>
          </div>
          <div className="modal-body">
            <p>Please enter the OTP sent to your registered mobile/email</p>
            <form onSubmit={handleSubmit} className="otp-form">
              <div className="otp-input-container">
                {otp.map((digit, index) => (
                  <input
                    key={index}
                    type={getInputType()}
                    inputMode={getInputMode()}
                    value={otp[index]}
                    onChange={(e) => handleChange(index, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(index, e)}
                    onPaste={handlePaste}
                    ref={(el) => (inputRefs.current[index] = el)}
                    className={`otp-input ${config.OTP_TYPE === 'ALPHA_NUMERIC' ? 'uppercase' : ''}`}
                    maxLength={1}
                    pattern={getInputPattern()}
                    required
                  />
                ))}
              </div>
              
              <button
                type="submit"
                className="submit-button"
                disabled={isLoading || otp.some(digit => !digit)}
              >
                {isLoading ? (
                  <svg className="spinner-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="spinner-circle" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="spinner-path" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : 'Verify OTP'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OTPModal;