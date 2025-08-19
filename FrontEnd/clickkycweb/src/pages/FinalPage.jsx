import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { generateReport } from '../services/kycService';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { FaCopy } from 'react-icons/fa';
import '../CSS/Final.css';

const Final = ({ showModal, setIsLoading, updateStepStatus }) => {
  const { authState } = useAuth();
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const navigate = useNavigate();
  useEffect(() => {
    if (authState?.status?.Status === "OK"){
      updateStepStatus(5, 'completed');
      setIsSuccess(true);
    }
    else{
      updateStepStatus(5, 'failed');
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authState?.status?.Status]);

  const handleDownloadReport = async () => {
    try {
      setIsGeneratingReport(true);
      const response = await generateReport(authState.accessToken);
      if (response.Status === 'OK') {
        const link = document.createElement('a');
        link.href = `data:application/pdf;base64,${response.Result}`;
        link.download = 'KYC_Report.pdf';
        link.click();
      } else {
        showModal('Error', response.Message);
      }
    } catch (err) {
      showModal('Error', 'Failed to generate report');
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    showModal('Info','Copied!');
  };

  return (
    <div className="selection-container">
      <div className="selection-header"> 
        <div className={`status-card ${isSuccess ? 'success' : 'error'}`}>
          <div className="status-icon">
            {isSuccess ? (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z"/>
              </svg>
            )}
          </div>
          
          <h2 className="status-title">
            {isSuccess ? 'Congratulations!!' : 'Failed!!'}
          </h2>
          
          <div className="status-message">
            {authState?.status?.Message && (
              <p className="api-message">{authState?.status?.Message}</p>
            )}
          </div>
          {isSuccess ? (
              <div className="customer-info">
                  {authState?.status?.Result.CUSTOMER_ID && authState?.status?.Result.ACCOUNT_NUMBER && (
                      <div className="account-section">
                        <h2 className="account-holder">{authState?.status?.Result.NAME}</h2>
                        
                        <div className="account-detail">
                          <span>Customer ID</span>
                          <div className="detail-row">
                            <strong>{authState?.status?.Result.CUSTOMER_ID}</strong>
                            <button onClick={() => copyToClipboard(authState?.status?.Result.CUSTOMER_ID)}>
                              <FaCopy className="copy-icon" />
                            </button>
                          </div>
                        </div>

                        <div className="account-detail">
                          <span>Account Number</span>
                          <div className="detail-row">
                            <strong>{authState?.status?.Result.ACCOUNT_NUMBER}</strong>
                            <button onClick={() => copyToClipboard(authState?.status?.Result.ACCOUNT_NUMBER)}>
                              <FaCopy className="copy-icon" />
                            </button>
                          </div>
                        </div>
                      </div>
                  )}
              </div>
          ) : (
              <div className="customer-error">
                  {authState?.status?.Result?.REJECT_REASON && (
                      <div className="error-row">
                      <span className="error-label">Reason:</span>
                      <span className="error-value">{authState?.status?.Result?.REJECT_REASON == null ? "Account Opening is Failed." : authState?.status?.Result?.REJECT_REASON}</span>
                      </div>
                  )}
              </div>
          )}
          

          {isSuccess ? (
            <button 
              onClick={handleDownloadReport} 
              className="button button-primary download-btn"
              disabled={isGeneratingReport}
            >
              {isGeneratingReport ? (
                <>
                  <LoadingSpinner small /> Generating Report...
                </>
              ) : (
                'Download KYC Report'
              )}
            </button>
          ) : (
            <div className="action-buttons">
              <button className="button button-primary"
                  onClick={() => navigate('/', { state: { currentStep: 1 } })}
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Final;