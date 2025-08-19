import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { formatDate } from '../../utils/helpers';
import { fetchCustomerInfo } from '../../services/bankingService';
import LoadingSpinner from '../common/LoadingSpinner';
import Modal from '../common/Modal';

const CustomerInfo = ({ onEditPicture }) => {
  const { user } = useAuth();
  const [customerInfo, setCustomerInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('personal');

  useEffect(() => {
    const loadCustomerInfo = async () => {
      setLoading(true);
      try {
        const response = await fetchCustomerInfo();
        
        if (response.data.Status === 'OK') {
          setCustomerInfo(response.data.Result);
        } else {
          setError(response.data.Message || 'Failed to load customer info');
        }
      } catch (err) {
        setError(err.response?.data?.Message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };
    
    if (user) {
      loadCustomerInfo();
    }
  }, [user]);

  if (loading) return <LoadingSpinner />;
  if (!customerInfo) return <div>No customer information available</div>;

  return (
    <div className="customer-info-container">
      {error && (
        <Modal
          isOpen={!!error}
          onClose={() => setError(null)}
          title="Error"
          message={error}
        />
      )}
            
      {/* Profile Picture */}
      <div className="profile-picture-wrapper">
        <div className="profile-picture-container">
          <img 
            src={user?.profile_picture || '/assets/images/default-profile.png'} 
            alt="Profile" 
            className="profile-picture profile-picture-large"
            onClick={onEditPicture}
          />
          <div className="profile-edit-overlay" onClick={onEditPicture}>
            <svg 
              className="profile-edit-icon" 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
          </div>
        </div>
      </div>
      
      {/* Basic Info */}
      <div className="profile-basic-info profile-basic-info-centered">
        <h3>{customerInfo.customer.name}</h3>
        <p>Customer ID: {customerInfo.customer.customer_id}</p>
        <p>User ID: {user.userId}</p>
      </div>
      
      {/* Tabs */}
      <div className="profile-tabs">
        <div className="profile-tabs-header">
          <button
            className={`profile-tab-btn ${activeTab === 'personal' ? 'profile-tab-active' : ''}`}
            onClick={() => setActiveTab('personal')}
          >
            Personal Information
          </button>
          <button
            className={`profile-tab-btn ${activeTab === 'address' ? 'profile-tab-active' : ''}`}
            onClick={() => setActiveTab('address')}
          >
            Address
          </button>
          <button
            className={`profile-tab-btn ${activeTab === 'contact' ? 'profile-tab-active' : ''}`}
            onClick={() => setActiveTab('contact')}
          >
            Contact Information
          </button>
        </div>
        
        {/* Tab Content */}
        <div className="profile-tab-content">
          {activeTab === 'personal' && (
            <div className="personal-info-grid">
              <div className="detail-row">
                <span>Title:</span>
                <span>{customerInfo.customer.title}</span>
              </div>
              <div className="detail-row">
                <span>Full Name:</span>
                <span>{customerInfo.customer.name}</span>
              </div>
              <div className="detail-row">
                <span>Date of Birth:</span>
                <span>{formatDate(customerInfo.customer.birth_date)}</span>
              </div>
              <div className="detail-row">
                <span>Tax ID:</span>
                <span>{customerInfo.customer.tax_id}</span>
              </div>
            </div>
          )}
          
          {activeTab === 'address' && (
            <div className="addresses-container">
              {customerInfo.addresses.map((address) => (
                <div key={address.id} className="address-card">
                  <h4 className="address-type">{address.type} Address</h4>
                  <div className="address-details">
                    <p>{address.line_1}</p>
                    {address.line_2 && <p>{address.line_2}</p>}
                    <p>{address.city}, {address.state_code}</p>
                    <p>{address.zip_code}, {address.country_code}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {activeTab === 'contact' && (
            <div className="contact-info-grid">
              <div className="contact-section">
                <h4>Phone Numbers</h4>
                {customerInfo.phones.map(phone => (
                  <div key={phone.id} className="contact-item">
                    <span className="contact-type">{phone.type}: </span>
                    <span>{phone.number}</span>
                  </div>
                ))}
              </div>
              <div className="contact-section">
                <h4>Email Addresses</h4>
                {customerInfo.emails.map(email => (
                  <div key={email.id} className="contact-item">
                    <span className="contact-type">{email.type}: </span>
                    <span>{email.address}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CustomerInfo;