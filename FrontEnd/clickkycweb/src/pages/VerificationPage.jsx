import React from 'react';
import { initializeVerification } from '../services/kycService';
import '../CSS/Verification.css';

const Verification = ({ onNext, onPrev, showModal, setIsLoading, accessToken, updateStepStatus }) => {

  const handleVerification = async () => {
    try {
      setIsLoading(true);
      const response = await initializeVerification(accessToken);
      console.log(response)
      if (response.Status === 'OK') {
        window.location.href = response.Result; 
      } else {
        showModal('Error', response.Message);
      }
    } catch (err) {
      showModal('Error', 'Failed to initialize verification');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="selection-container">
      <div className="selection-header">    
        <h2>Identity Verification</h2>
        <p>Verify your identity to proceed with your application</p>
      </div>
      
      <div className="verification-content">
        <div className="verification-instructions">
          <p>To complete your application, we need to verify your identity. This process typically takes 2-3 minutes.</p>
          <ul className="instruction-list">
            <li>Have your government-issued ID ready</li>
            <li>Ensure good lighting for facial recognition</li>
            <li>Use a supported browser (Chrome, Firefox, or Safari)</li>
          </ul>
        </div>
        <div className='button-centerized'>
          <button 
            onClick={handleVerification} 
            className="button button-primary .start-verify-button"
          >
            Start Verification
          </button>
      </div>
    </div>
      
      <div className="step-actions">
        <button onClick={onPrev} className="button button-secondary">Back</button>
      </div>
    </div>
  );
};

export default Verification;