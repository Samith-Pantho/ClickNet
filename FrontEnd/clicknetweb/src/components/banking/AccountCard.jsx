import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { formatCurrency } from '../../utils/helpers';
import { fetchAccountBalances } from '../../services/bankingService';
import LoadingSpinner from '../common/LoadingSpinner';
import Modal from '../common/Modal';

const AccountCard = ({ account }) => {
  const navigate = useNavigate();
  const [showBalance, setShowBalance] = useState(false);
  const [detailedBalance, setDetailedBalance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (showBalance) {
      const timer = setTimeout(() => {
        setShowBalance(false);
        setDetailedBalance(null);
      }, 10000);
      return () => clearTimeout(timer);
    }
  }, [showBalance]);

  const handleBalanceClick = async (e) => {
    e.stopPropagation();
    if (showBalance) return;
    
    try {
      setLoading(true);
      const response = await fetchAccountBalances(account.account_number);
      
      if (response.data.Status === 'OK') {
        setDetailedBalance(response.data.Result);
        setShowBalance(true);
      } else {
        setError(response.data.Message || 'Failed to fetch balance');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCardClick = () => {
    navigate(`/banking/account/${account.account_number}`);
  };

  return (
    <div 
      className="account-card glass-card"
      onClick={handleCardClick}
    >
      <div className="account-header">
        <span className={`account-type ${account.product_category.toLowerCase()}`}>
          {account.product_category}
        </span>
        <h3>{account.account_name}</h3>
      </div>
      
      <div className="account-details">
        <p className="account-number">{account.account_number}</p>
        <p className="product-name">{account.product_name}</p>
        
        {showBalance && detailedBalance ? (
          <div className="balance-details">
            <div className="balance-row">
              <span>Available:</span>
              <strong>{formatCurrency(detailedBalance.available_balance, account.currency)}</strong>
            </div>
            <div className="balance-row">
              <span>Current:</span>
              <strong>{formatCurrency(detailedBalance.current_balance, account.currency)}</strong>
            </div>
            {detailedBalance.interest_rate && (
              <div className="balance-row">
                <span>Interest:</span>
                <strong>{detailedBalance.interest_rate}%</strong>
              </div>
            )}
          </div>
        ) : (
          <div 
            className="balance-placeholder"
            onClick={handleBalanceClick}
          >
            {loading ? (
              <LoadingSpinner mini />
            ) : (
              formatCurrency(0, account.currency).replace(/[0-9]/g, '•')
            )}
          </div>
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

export default AccountCard;