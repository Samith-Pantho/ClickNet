import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { fetchAllAccounts } from '../services/bankingService';
import { useAuth } from './AuthContext';

const BankingContext = createContext();

export const BankingProvider = ({ children }) => {
  const [accounts, setAccounts] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { user } = useAuth();

  const loadAccounts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchAllAccounts();
      if (response.data.Status === 'OK') {
        // Group accounts by product category
        const groupedAccounts = response.data.Result.reduce((acc, account) => {
          const category = account.product_category || 'Other';
          if (!acc[category]) {
            acc[category] = [];
          }
          acc[category].push(account);
          return acc;
        }, {});
        setAccounts(groupedAccounts);
      } else {
        setError(response.data.Message || 'Failed to load accounts');
      }
    } catch (err) {
      setError(err.response?.data?.Message || err.message || 'Failed to load accounts');
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-load accounts when user is authenticated
  useEffect(() => {
    if (user) {
      loadAccounts();
    } else {
      // Clear data when user logs out
      setAccounts({});
      setError(null);
    }
  }, [user, loadAccounts]);

  const value = {
    accounts,
    loading,
    error,
    loadAccounts
  };

  return (
    <BankingContext.Provider value={value}>
      {children}
    </BankingContext.Provider>
  );
};

export const useBanking = () => useContext(BankingContext);