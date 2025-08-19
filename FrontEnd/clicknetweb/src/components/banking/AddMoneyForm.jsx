import React, { useState, useMemo, useEffect, useContext } from 'react';
//import { useNavigate } from 'react-router-dom';
import { loadStripe } from "@stripe/stripe-js";
import { useBanking } from '../../contexts/BankingContext';
import { useAuth } from '../../contexts/AuthContext';
import { addMoneyRequest } from '../../services/bankingService';
import { ConfigContext } from '../../contexts/ConfigContext';
import Modal from '../common/Modal';
import LoadingSpinner from '../common/LoadingSpinner';
import { FaStripeS, FaPaypal } from 'react-icons/fa';

const AddMoneyForm = () => {
  
  const { user } = useAuth();
  const { accounts } = useBanking();
  //const navigate = useNavigate();
  const config = useContext(ConfigContext);
  const defaultFormData = {
    toAccount: '',
    receiverName: '',
    amount: '',
    currency: 'USD',
    vendor: 'STRIPE'
  };
  const stripePromise = loadStripe(config.STRIPE_PUBLISHABLE_KEY);

  const [formData, setFormData] = useState(defaultFormData);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);

  const handleRefresh = () => {
    setFormData(defaultFormData);
    setSelectedAccount(null);
    setError(null);
    setSuccess(null);
  };

  // Filter only savings accounts for 'fromAccount'
  const savingsAccounts = useMemo(() => {
    return accounts['Deposit'] || [];
    }, [accounts]); 

  useEffect(() => {
    if (formData.toAccount) {
      const selecteAccount = savingsAccounts.find(
        acc => acc.account_number === formData.toAccount
      );
      if (selecteAccount) {
        setFormData(prev => ({
          ...prev,
          receiverName: selecteAccount.account_name || user?.fullName,
          currency: selecteAccount.currency || formData.currency
        }));
      }
    }
  }, [formData.toAccount,user?.fullName, formData.currency, savingsAccounts]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    if (!selectedAccount){
      setError("Select an account first.")
    }

    const payload = {
      ToAccountNo: formData.toAccount,
      ReceiverName: formData.receiverName,
      Amount: formData.amount,
      Currency: formData.currency,
      Vendor: formData.vendor
    };

    try {
      const response = await addMoneyRequest(payload);
      
      if (response.data.Status === 'OK') {
        localStorage.setItem('userInfo', JSON.stringify(user));
        const stripe = await stripePromise;
        await stripe.redirectToCheckout({ sessionId: response.data.Result});
      } else {
        setError(response.data.Message || 'Add Money request failed');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred during add money');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="addmoney-form-container">
      {isLoading && <LoadingSpinner />}
      
      <h2>Add Money</h2>

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="toAccount">Select Account</label>
            <select
              id="toAccount"
              name="toAccount"
              value={formData.toAccount}
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
            <label htmlFor="receiverName">Name</label>
            <input
              type="text"
              id="receiverName"
              name="receiverName"
              value={formData.receiverName}
              required
              readOnly
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
          <p className='otp-channel-title'>Choose Vendor</p>
          <div className="form-row">
            <div className="form-group">
              <label className="checkbox-container">
                <input
                  type="radio"
                  name="vendor"
                  value="STRIPE"
                  checked={formData.vendor === 'STRIPE'}
                  onChange={handleChange}
                />
                <span className="checkmark"></span>
                  <FaStripeS size={30} color="#635bff" />
                  Stripe
              </label>
            </div>
            <div className="form-group">
              <label className="checkbox-container">
                <input
                  type="radio"
                  name="vendor"
                  value="PAYPAL"
                  checked={formData.vendor === 'PAYPAL'}
                  //onChange={handleChange}
                />
                <span className="checkmark"></span>
                  <FaPaypal size={30} color="#003087" />
                  Paypal
              </label>
            </div>
          </div>
        </div>
        
        <div className="form-actions">
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Processing...' : 'Add Money'}
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
      
    </div>
  );
};

export default AddMoneyForm;