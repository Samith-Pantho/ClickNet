import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {processAddMoneyCallback} from '../../services/bankingService';
import Modal from '../../components/common/Modal';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import backgroundImage from '../../assets/images/Bg.png'; 
import logo from '../../assets/images/clicknet-logo.png';

const AddMoneyCallBack = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { setUser, loadProfilePicture } = useAuth();
  const [ status, setStatus] = useState(null);
  const [ transactionData, setTransactionData] = useState({});
  const [ loginData, setLoginData] = useState({});
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const processData = async () => {
      setIsLoading(true);
      const queryParams = new URLSearchParams(location.search);
      const secret_key = queryParams.get('data');
      
      if (secret_key) {
        try {
          const response = await processAddMoneyCallback(secret_key);
          
          if (response.data.Status === 'OK') {
            setStatus(response.data.Result?.PaymentStatus);
            setLoginData(response.data.Result?.LoginData);
            setTransactionData(response.data.Result?.TransactionData);

          } else {
            setError(response.data.Message || 'Add Money request failed');
          }
        } catch (err) {
          setError(err.response?.data?.Message || 'An error occurred during add money');
        } finally {
          setIsLoading(false);
        }
      }
    };

    processData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location]); 

  const handleOkClick = async () => {
    const { access_token, fullName, customerId, userName, ForcePasswordChangedFlag} = loginData;
    setUser({
      token: access_token,
      fullName,
      customerId,
      userId: userName,
      forcePasswordChangedFlag: ForcePasswordChangedFlag,
      profile_picture: await loadProfilePicture() || '/assets/images/default-profile.png'
    });

    if(ForcePasswordChangedFlag)
      navigate('/change-password');
    else
      navigate('/banking');
  };

  return (
    <div className="auth-container auth-overlay" style={{ 
      backgroundImage: `url(${backgroundImage})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }}>
      <div className="callback-form-wrapper">
        {isLoading && <LoadingSpinner />}

        <div className="logo-title-container">
          <img src={logo} alt="ClickNet Logo" className="auth-logo" />
          <h3 className={`auth-title ${status?.toLowerCase()}`}>
            {status?.toLowerCase() === 'success' ? 'Payment Successful' : 'Payment Failed'}
          </h3>
        </div>
        <div className="callback-container">
          <div className={`callback-card ${status?.toLowerCase()}`}>
            <div className={`callback-icon ${status?.toLowerCase()}`}>
              <svg viewBox="0 0 24 24">
                {status?.toLowerCase() === 'success' ? (
                  <path fill="currentColor" d="M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2M10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z" />
                ) : (
                  <path fill="currentColor" d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z" />
                )}
              </svg>
            </div>

            {status?.toLowerCase() === 'success' ? (
              <>
                <h2>Payment Successful</h2>
                <div className="transaction-details">
                  <div className="detail-row">
                    <span className="detail-label">Amount:</span>
                    <span className="detail-value">
                      {transactionData?.Amount} {transactionData?.Currency}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Account:</span>
                    <span className="detail-value">
                      {transactionData?.ToAccountNo}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Receiver:</span>
                    <span className="detail-value">
                      {transactionData?.ReceiverName}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Vendor:</span>
                    <span className="detail-value">
                      {transactionData?.Vendor}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Reference id:</span>
                    <span className="detail-value">
                      {transactionData?.ReferenceId}
                    </span>
                  </div>
                </div>
              </>
            ) : (
              <>
                <h2>Payment Failed</h2>
                <div className="transaction-details">
                  <div className="detail-row">
                    <span className="detail-label">Amount:</span>
                    <span className="detail-value">
                      {transactionData?.Amount} {transactionData?.Currency}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Account:</span>
                    <span className="detail-value">
                      {transactionData?.ToAccountNo}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Receiver:</span>
                    <span className="detail-value">
                      {transactionData?.ReceiverName}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Vendor:</span>
                    <span className="detail-value">
                      {transactionData?.Vendor}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Reference id:</span>
                    <span className="detail-value">
                      {transactionData?.ReferenceId}
                    </span>
                  </div>
                </div>
              </>
            )}

            <div className="form-actions">
              <button type="submit" className="button button-primary" onClick={handleOkClick}>
                OK
              </button>
              <button type="button" className="button button-secondary" onClick={handleOkClick}>
                Cancel
              </button>
            </div>
          </div>
        </div>
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
  );
};

export default AddMoneyCallBack;