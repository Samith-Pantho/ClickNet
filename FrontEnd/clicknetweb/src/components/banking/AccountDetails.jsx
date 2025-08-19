import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { fetchAccountDetails, fetchAccountBalances, fetchrasactionLimitInfo } from '../../services/bankingService';
import { formatDateTime, capitalizeName, formatCurrency } from '../../utils/helpers';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../common/LoadingSpinner';
import Modal from '../common/Modal';

const AccountDetails = () => {
  const { accountNumber } = useParams();
  const [account, setAccount] = useState(null);
  const [balances, setBalances] = useState(null);
  const [translimit, setTranslimit] = useState(null);
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('details');

  useEffect(() => {
    const loadAccountData = async () => {
      try {
        setLoading(true);
        const [detailsResponse, balancesResponse, transactionLimitresponse] = await Promise.all([
          fetchAccountDetails(accountNumber),
          fetchAccountBalances(accountNumber),
          fetchrasactionLimitInfo(accountNumber)
        ]);
        
        if (detailsResponse.data.Status === 'OK') {
          setAccount(detailsResponse.data.Result);
        } else {
          setError(detailsResponse.data.Message || 'Failed to load account details');
        }
        
        if (balancesResponse.data.Status === 'OK') {
          setBalances(balancesResponse.data.Result);
        } else {
          setError(balancesResponse.data.Message || 'Failed to load account balances');
        }

        if (transactionLimitresponse.data.Status === 'OK') {
          setTranslimit(transactionLimitresponse.data.Result);
        } else {
          setError(balancesResponse.data.Message || 'Failed to load account transaction limit');
        }
      } catch (err) {
        setError(err.response?.data?.Message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };
    
    loadAccountData();
  }, [accountNumber]);

  if (loading) return <LoadingSpinner />;
  if (error) return <Modal isOpen={true} onClose={() => setError(null)} title="Error" message={error} />;
  if (!account) return <div>No account data available</div>;

  return (
    <div className="account-details-container">
      <div className="account-header">
        <h2>{user.fullName.split(' ').map(part => capitalizeName(part)).join(' ')}</h2>
        <p className="account-number">{account.account_number}</p>
      </div>
      
      <div className="account-tabs">
        <button 
          className={activeTab === 'details' ? 'active' : ''}
          onClick={() => setActiveTab('details')}
        >
          Account Details
        </button>
        <button 
          className={activeTab === 'balances' ? 'active' : ''}
          onClick={() => setActiveTab('balances')}
        >
          Balances & Rates
        </button>
        <button 
          className={activeTab === 'translimit' ? 'active' : ''}
          onClick={() => setActiveTab('translimit')}
        >
          Transaction Limit
        </button>
      </div>
      
      <div className="account-content">
        {activeTab === 'details' && (
          <div className="account-details-section">
            <div className="account-details-row">
              <span>Account Category:</span>
              <span>{account.product_category}</span>
            </div>
            <div className="account-details-row">
              <span>Account Type:</span>
              <span>{account.product_type}-{account.product_name}</span>
            </div>
            <div className="account-details-row">
              <span>Account Status:</span>
              <span>{account.status}</span>
            </div>
            <div className="account-details-row">
              <span>Branch Code:</span>
              <span>{account.branch_code}</span>
            </div>
            <div className="account-details-row">
              <span>Open Date:</span>
              <span>{formatDateTime(account.opened_date)}</span>
            </div>
            <div className="account-details-row">
              <span>Maturity Date:</span>
              <span>{formatDateTime(account.maturity_date)}</span>
            </div>
          </div>
        )}
        
        {activeTab === 'balances' && balances && (
          <div className="account-details-section">
            <div className="account-details-row highlight">
              <span>Available Balance:</span>
              <span>{formatCurrency(balances.available_balance, account.currency)}</span>
            </div>
            <div className="account-details-row">
              <span>Original Balance:</span>
              <span>{formatCurrency(balances.original_balance, account.currency)}</span>
            </div>
            <div className="account-details-row">
              <span>Current Balance:</span>
              <span>{formatCurrency(balances.current_balance, account.currency)}</span>
            </div>
            {balances.interest_rate && (
              <div className="account-details-row">
                <span>Interest Rate:</span>
                <span>{balances.interest_rate}%</span>
              </div>
            )}
          </div>
        )}

        {activeTab === 'translimit' && translimit && (
          <div className="account-details-section">
            <div className="account-details-row highlight">
              <span>Payment Frequency:</span>
              <span>
                {translimit.payment_frequency === 'D' ? 'Daily' : 
                translimit.payment_frequency === 'M' ? 'Monthly' : 
                translimit.payment_frequency}
              </span>
            </div>
            <div className="account-details-row">
              <span>Minimum Amount per Payment:</span>
              <span>{formatCurrency(translimit.payment_min_amount, account.currency)}</span>
            </div>
            <div className="account-details-row">
              <span>Maximum Amount per Payment:</span>
              <span>{formatCurrency(translimit.payment_max_amount, account.currency)}</span>
            </div>
            <div className="account-details-row">
              <span>Daily Payment Limit:</span>
              <span>{translimit.daily_no_of_payments} transactions</span>
            </div>
            <div className="account-details-row highlight">
              <span>Today's Total Transfered Amount:</span>
              <span>{formatCurrency(translimit.today_total_amount, account.currency)}</span>
            </div>
            <div className="account-details-row highlight">
              <span>Today's Transactions Count:</span>
              <span>{translimit.today_total_transactions}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AccountDetails;