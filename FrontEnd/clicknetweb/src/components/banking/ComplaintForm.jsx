import React, { useState, useEffect } from 'react';
import { createComplaint, fetchComplaints } from '../../services/bankingService';
import LoadingSpinner from '../common/LoadingSpinner';
import Modal from '../common/Modal';
import { formatDateTime, capitalizeName } from '../../utils/helpers';

const ComplaintForm = () => {
  const [complaints, setComplaints] = useState([]);

  const defaultFormData ={
    category: '',
    description: ''
  };
  const [formData, setFormData] = useState(defaultFormData);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeTab, setActiveTab] = useState('history');

  useEffect(() => {
    const loadComplaints = async () => {
      setFetching(true);
      try {
        const response = await fetchComplaints();
        
        if (response.data.Status === 'OK') {
          // Map the response to match our expected format
          const formattedComplaints = response.data.Result.map(complaint => ({
            id: complaint.COMPLAINT_ID,
            userId: complaint.USER_ID,
            category: complaint.CATEGORY,
            description: complaint.DESCRIPTION,
            status: complaint.STATUS,
            response: complaint.RESPONSE,
            created_date: complaint.CREATED_AT,
            updated_date: complaint.UPDATED_AT
          }));
          setComplaints(formattedComplaints);
        } else {
          setError(response.data.Message || 'Failed to load complaints');
        }
      } catch (err) {
        setError(err.response?.data?.Message || 'An error occurred');
      } finally {
        setFetching(false);
      }
    };
    
    loadComplaints();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleRefresh = () => {
    setFormData(defaultFormData);
    setError(null);
    setSuccess(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Prepare request body according to API spec
      const requestBody = {
        category: formData.category,
        description: formData.description
      };
      
      const response = await createComplaint(requestBody);
      
      if (response.data.Status === 'OK') {
        setSuccess(response.data.Message || 'Complaint submitted successfully');
        setFormData({ category: '', description: '' });
        
        // Refresh complaints list
        const refreshResponse = await fetchComplaints();
        if (refreshResponse.data.Status === 'OK') {
          const formattedComplaints = refreshResponse.data.Result.map(complaint => ({
            id: complaint.COMPLAINT_ID,
            userId: complaint.USER_ID,
            category: complaint.CATEGORY,
            description: complaint.DESCRIPTION,
            status: complaint.STATUS,
            response: complaint.RESPONSE,
            created_date: complaint.CREATED_AT,
            updated_date: complaint.UPDATED_AT
          }));
          setComplaints(formattedComplaints);
        }
        setActiveTab('history');
      } else {
        setError(response.data.Message || 'Failed to submit complaint');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="complaint-container">
      {loading && <LoadingSpinner />}
      
      <h2>Customer Complaints</h2>
      
      <div className="complaint-tabs">
        <button 
          className={activeTab === 'history' ? 'active' : ''}
          onClick={() => setActiveTab('history')}
        >
          Complaint History
        </button>
        <button 
          className={activeTab === 'new' ? 'active' : ''}
          onClick={() => setActiveTab('new')}
        >
          New Complaint
        </button>
      </div>
      
      <div className="complaint-content">
        {activeTab === 'history' ? (
          <div className="complaint-history">
            {fetching ? (
              <LoadingSpinner />
            ) : complaints.length > 0 ? (
                complaints.map((complaint, index) => (
                  <div className="complaint-item modern-complaint">
                    <div className="complaint-header">
                      <div className="category-badge">{complaint.category}</div>
                      <div className="complaint-meta">
                        <span className="complaint-date">
                          <svg className="icon" viewBox="0 0 24 24">
                            <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zM9 14H7v-2h2v2zm4 0h-2v-2h2v2zm4 0h-2v-2h2v2zm-8 4H7v-2h2v2zm4 0h-2v-2h2v2zm4 0h-2v-2h2v2z"/>
                          </svg>
                          {formatDateTime(complaint.created_date)}
                        </span>
                        <span className={`status-badge ${complaint.status.toLowerCase().replace('_', '-')}`}>
                          {complaint.status.replace('_', ' ').split(' ').map(part => capitalizeName(part)).join(' ')}
                        </span>
                      </div>
                    </div>
                    
                    <div className="complaint-content">
                      <div className="description-card">
                        <h4>Description</h4>
                        <div className="description-text">
                          {complaint.description}
                        </div>
                      </div>
                      
                      {complaint.response && (
                        <div className="response-card">
                          <h4>
                            <svg className="icon" viewBox="0 0 24 24">
                              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15h2v2h-2zm2.07-7.75l-.9.92C13.45 11.9 13 12.5 13 14h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
                            </svg>
                            Official Response
                          </h4>
                          <div className="response-text">
                            {complaint.response}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))
            ) : (
              <p>No complaints found.</p>
            )}
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="new-complaint-form">
            <div className="form-group">
              <label htmlFor="category">Category</label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                required
              >
                <option value="">Select Category</option>
                <option value="Account">Account Issue</option>
                <option value="Transaction">Transaction Problem</option>
                <option value="Service">Service Complaint</option>
                <option value="Security">Security Concern</option>
                <option value="Other">Other</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows="5"
                required
                placeholder="Please describe your complaint in detail..."
              />
            </div>
            
            <div className="form-actions">
              <button type="submit" disabled={loading}>
                {loading ? 'Submitting...' : 'Submit Complaint'}
              </button>
              <button ype="button" disabled={loading} className="refresh-button"
                onClick={handleRefresh}>
                Refresh
            </button>
            </div>
          </form>
        )}
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

export default ComplaintForm;