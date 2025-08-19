import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { formatDate } from '../../utils/helpers';
import { fetchCustomerActivities } from '../../services/bankingService';
import LoadingSpinner from '../common/LoadingSpinner';
import Modal from '../common/Modal';

const ActivityLog = () => {
  const { user } = useAuth();
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activityType, setActivityType] = useState(null);
  const [count, setCount] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const recordsPerPage = 10;

  const totalRecords = activities.length;
  const totalPages = Math.ceil(totalRecords / recordsPerPage);
  const indexOfLastRecord = currentPage * recordsPerPage;
  const indexOfFirstRecord = indexOfLastRecord - recordsPerPage;
  const currentRecords = activities.slice(indexOfFirstRecord, indexOfLastRecord);


  useEffect(() => {
    const loadActivities = async () => {
      setLoading(true);
      try {
        const response = await fetchCustomerActivities(count, activityType);
        
        if (response.data.Status === 'OK') {
          setActivities(response.data.Result);
        } else {
          setError(response.data.Message || 'Failed to load activities');
        }
      } catch (err) {
        setError(err.response?.data?.Message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };
    
    loadActivities();
  }, [count, activityType]);

  if (!user) return null;

  const getClassname = (activity) => {
    if (activity.ACTIVITY_TITLE?.toLowerCase().includes('fail')) return 'failed';
    if (activity.ACTIVITY_TITLE?.toLowerCase().includes('success')) return 'success';
    if (activity.ACTIVITY_TITLE?.toLowerCase().includes('try')) return 'info';
    return 'info'; // default
  };

  return (
    <div className="activity-log-container">
      {loading && <LoadingSpinner />}
      
      <h2>Activity Log</h2>
      
      <div className="filters">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="activityType">Activity Type</label>
            <select
              id="activityType"
              value={activityType || ''}
              onChange={(e) => setActivityType(e.target.value || null)}
            >
              <option value="">All Activities</option>
              <option value="LOGIN">Logins</option>
              <option value="LOGOUT">Logouts</option>
              <option value="FUNDTRANSFER">Fund Transfers</option>
              <option value="SECURITYUPDATE">Security Updates</option>
              <option value="REQUEST">Requests</option>
              <option value="ACCOUNT">Account related</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="count">Number of Activities</label>
            <select
              id="count"
              value={count}
              onChange={(e) => setCount(parseInt(e.target.value))}
            >
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="activities-list">
        {activities.length > 0 ? (
          <div>
            <table className="activity-table">
              <tbody>
                {currentRecords.map((activity, index) => (
                  <>
                  <tr key={index}>
                    <td className={`activity-status ${getClassname(activity)}`}>
                      <span className={`activity-type ${activity.ACTIVITY_TYPE?.toLowerCase()}`}>
                        {activity.ACTIVITY_TYPE}
                      </span>
                    </td>
                    <td>{formatDate(activity.ACTIVITY_DT)}</td>
                    <td>{activity.ACTIVITY_TITLE}</td>
                    <td>
                      <span className="activity-ip">{activity.REQUESTED_FROM}</span>
                    </td>
                  </tr>
                  <tr></tr>
                  </>
                ))}
              </tbody>
            </table>
          
            <div className="pagination-controls">
              <button 
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
              >
                Previous
              </button>
              
              <span>
                Page {currentPage} of {totalPages}
              </span>
              
              <button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
              >
                Next
              </button>
            </div>
          </div>
        ) : (
          <p>No activities found.</p>
        )}
      </div>
      
      <Modal
        isOpen={!!error}
        onClose={() => setError(null)}
        title="Error"
        message={error}
      />
    </div>
  );
};

export default ActivityLog;