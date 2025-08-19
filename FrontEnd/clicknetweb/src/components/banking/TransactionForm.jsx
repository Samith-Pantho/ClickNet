import React, { useState, useMemo, useEffect, useCallback, useContext } from 'react';
//import { useNavigate } from 'react-router-dom';
import { useBanking } from '../../contexts/BankingContext';
import { useAuth } from '../../contexts/AuthContext';
import { formatCurrency } from '../../utils/helpers';
import { transferFunds, fetchAvailableBalance } from '../../services/bankingService';
import { ConfigContext } from '../../contexts/ConfigContext';
import Modal from '../common/Modal';
import OTPModal from '../common/OTPModal';
import LoadingSpinner from '../common/LoadingSpinner';

const TransactionForm = () => {
  
  const { user } = useAuth();
  const { accounts } = useBanking();
  //const navigate = useNavigate();
  const config = useContext(ConfigContext);
  const defaultFormData = {
    fromAccount: '',
    toAccount: '',
    amount: '',
    purpose: '',
    senderName: '',
    receiverName: '',
    currency: 'USD',
    otpChannel: config.DEFAULT_AUTHENTICATION_TYPE
  };

  const [formData, setFormData] = useState(defaultFormData);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showOTPModal, setShowOTPModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [transferRequest, setTransferRequest] = useState(null);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [selectedAccountBalance, setSelectedAccountBalance] = useState('0.0');

  const handleRefresh = () => {
    setFormData(defaultFormData);
    setSelectedAccount(null);
    setSelectedAccountBalance('0.0');
    setError(null);
    setSuccess(null);
  };

  // Filter only savings accounts for 'fromAccount'
  const savingsAccounts = useMemo(() => {
    return accounts['Deposit'] || [];
    }, [accounts]); 

  useEffect(() => {
    if (formData.fromAccount) {
      const selectedAccount = savingsAccounts.find(
        acc => acc.account_number === formData.fromAccount
      );
      if (selectedAccount) {
        setFormData(prev => ({
          ...prev,
          senderName: selectedAccount.account_name || user?.fullName,
          currency: selectedAccount.currency || formData.currency
        }));
      }
    }
  }, [formData.fromAccount,user?.fullName, formData.currency, savingsAccounts]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleBalanceCheck = useCallback(async (e) => {
    if (selectedAccount === null) return;

    try {
      setIsLoading(true);
      const response = await fetchAvailableBalance(selectedAccount);
      
      if (response.data.Status === 'OK') {
        setSelectedAccountBalance(response.data.Result);
      } else {
        setError(response.data.Message || 'Failed to fetch balance');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, [selectedAccount]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    const payload = {
      FromAccount: formData.fromAccount,
      SenderName: formData.senderName,
      ToAccount: formData.toAccount,
      ReceiverName: formData.receiverName,
      Pourpose: formData.purpose,
      Amount: formData.amount,
      Currency: formData.currency,
      OTP: "",
      OTP_verify_channel: formData.otpChannel
    };

    try {
      const response = await transferFunds(payload);
      
      if (response.data.Status === 'OK') {
        setSuccess(response.data.Message || 'Transfer successful');
      } else if (response.data.Status === 'OTP') {
        setTransferRequest(payload);
        setShowOTPModal(true);
      } else {
        setError(response.data.Message || 'Transfer failed');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred during transfer');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOTPSubmit = async (otp) => {
    setIsLoading(true);
    try {
      const payload = {
        ...transferRequest,
        OTP: otp
      };
      
      const response = await transferFunds(payload);
      
      if (response.data.Status === 'OK') {
        setShowOTPModal(false);
        handleRefresh();
        setSuccess(response.data.Message || 'Transfer successful');
      } else {
        setError(response.data.Message || 'OTP verification failed');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred during OTP verification');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (selectedAccount != null){
      handleBalanceCheck();
    }
  }, [selectedAccount, handleBalanceCheck]);

  return (
    <div className="transaction-form-container">
      {isLoading && <LoadingSpinner />}
      
      <h2>Fund Transfer</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="fromAccount">From Account</label>
            <select
              id="fromAccount"
              name="fromAccount"
              value={formData.fromAccount}
              onChange={(e) => {
                setSelectedAccount(e.target.value);
                handleChange(e);
              }}
              required
            >
              <option value="">Select Account</option>
              {savingsAccounts.map(account => (
                <option key={account.account_number} value={account.account_number}>
                  {account.account_number} - {account.product_name}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="availableBalance">Available Balance</label>
            <input
                  type="text"
                  id="availableBalance"
                  name="availableBalance"
                  value={formatCurrency(selectedAccountBalance, formData.currency)}
                  required
                  readOnly
                />
          </div>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="senderName">Sender Name</label>
            <input
              type="text"
              id="senderName"
              name="senderName"
              value={formData.senderName}
              required
              readOnly
            />
          </div>

          <div className="form-group">
            <label htmlFor="purpose">Purpose</label>
            <input
              type="text"
              id="purpose"
              name="purpose"
              value={formData.purpose}
              onChange={handleChange}
            />
          </div>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="toAccount">To Account Number</label>
            <input
              type="text"
              id="toAccount"
              name="toAccount"
              value={formData.toAccount}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="receiverName">Receiver Name</label>
            <input
              type="text"
              id="receiverName"
              name="receiverName"
              value={formData.receiverName}
              onChange={handleChange}
              required
            />
          </div>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="amount">Amount</label>
            <input
              type="number"
              id="amount"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              min="0.01"
              step="0.01"
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="currency">Currency</label>
            <select
              id="currency"
              name="currency"
              value={formData.currency}
              onChange={handleChange}
              required
            >
              <option value="USD">USD</option>
            </select>
          </div>
        </div>

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
        
        <div className="form-actions">
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Processing...' : 'Transfer Funds'}
          </button>
          <button ype="button" disabled={isLoading} className="refresh-button"
            onClick={handleRefresh}>
            Refresh
        </button>
        </div>
      </form>
      
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
      
      <OTPModal
        isOpen={showOTPModal}
        onClose={() => setShowOTPModal(false)}
        onSubmit={handleOTPSubmit}
        isLoading={isLoading}
      />
    </div>
  );
};

export default TransactionForm;