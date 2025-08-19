import React, { useState, useEffect } from 'react';
import { getCustomerRegistrationData, createCustomerAndAccount } from '../services/kycService';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/common/LoadingSpinner';
import '../CSS/CustomerInformation.css';
import {formatDate} from '../utils/helpers'

const CustomerInfo = ({ onNext, onPrev, showModal, setIsLoading, updateStepStatus }) => {
  const { authState, setStatus } = useAuth();
  const [customer, setCustomer] = useState(null);

  useEffect(() => {
    const fetchCustomerData = async () => {
      try {
        setIsLoading(true);
        const response = await getCustomerRegistrationData(authState.accessToken);
        if (response.Status === 'OK') {
          setCustomer(response.Result);
          if(!response.Result?.IS_TAX_ID_VERIFIED || response.Result?.STATUS === 'REJECTED'){
            updateStepStatus(3, 'failed');
            response.Status = "FAILED";
            response.Message = "Verification Failed."
            setStatus(response);
            onNext();
          }
        } else {
          showModal('Error', response.Message);
        }
      } catch (err) {
        console.log(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCustomerData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCreateAccount = async () => {
    try {
      setIsLoading(true);
      const response = await createCustomerAndAccount(authState.accessToken);
      const finalResponse = {
        Status: response.Status || 'FAILED',
        Message: response.Message || 'Failed to create account',
        Result: response.Result || {}
      };
      setStatus(finalResponse);
      onNext();
    } catch (err) {
      console.log(err);
      showModal('Error', 'Failed to create account');
    } finally {
      setIsLoading(false);
    }
  };

  if (!customer) {
    return <LoadingSpinner />;
  }

  return (
    <div className="selection-container">
      <div className="selection-header"> 
        <h2>Your Information</h2>
        <p>Please review your information before creating your account</p>
      </div>
      
      <div className="customer-details-grid">
        <div className="detail-section">
          <h3 className="section-title">Personal Information</h3>
          <div className="detail-row">
            <span className="detail-label">Full Name:</span>
            <span className="detail-value">{customer.NAME}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">First Name:</span>
            <span className="detail-value">{customer.FIRST_NAME}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Last Name:</span>
            <span className="detail-value">{customer.LAST_NAME}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Date of Birth:</span>
            <span className="detail-value">{formatDate(customer.BIRTH_DATE)}</span>
          </div>
        </div>

        <div className="detail-section">
          <h3 className="section-title">Identification</h3>
          <div className="detail-row">
            <span className="detail-label">ID Type:</span>
            <span className="detail-value">{customer.TAX_ID_TYPE}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">ID Number:</span>
            <span className="detail-value">{customer.TAX_ID}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">ID Verified:</span>
            <span className="detail-value">
              {customer.IS_TAX_ID_VERIFIED ? (
                <span className="verified-badge">Verified</span>
              ) : (
                <span className="unverified-badge">Not Verified</span>
              )}
            </span>
          </div>
        </div>

        <div className="detail-section">
          <h3 className="section-title">Address</h3>
          <div className="detail-row">
            <span className="detail-label">Address Type:</span>
            <span className="detail-value">{customer.ADDRESS_TYPE}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Address:</span>
            <span className="detail-value">
              {[
                customer.LINE_1,
                customer.LINE_2,
                customer.LINE_3,
                customer.LINE_4
              ]
              .filter(line => line != null && line.trim() !== '')
              .join(', ')}
            </span>
          </div>
          <div className="detail-row">
            <span className="detail-label">City:</span>
            <span className="detail-value">{customer.CITY}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">State:</span>
            <span className="detail-value">{customer.STATE_CODE}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Zip Code:</span>
            <span className="detail-value">{customer.ZIPCODE}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Country:</span>
            <span className="detail-value">{customer.COUNTRY_CODE}</span>
          </div>
        </div>
      </div>
      
      <div className="step-actions">
        <button onClick={onPrev} className="button button-secondary">Back</button>
        <button 
          onClick={handleCreateAccount} 
          className="button button-primary"
        >
          Open Account
        </button>
      </div>
    </div>
  );
};

export default CustomerInfo;