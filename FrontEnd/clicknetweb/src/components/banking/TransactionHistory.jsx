import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useBanking } from '../../contexts/BankingContext';
import { formatCurrency, formatDate, formatDateTime } from '../../utils/helpers';
import { fetchTransactionHistory, generateStatement } from '../../services/bankingService';
import LoadingSpinner from '../common/LoadingSpinner';
import Modal from '../common/Modal';

const TransactionHistory = () => {
  const { accounts } = useBanking();
  const [transactions, setTransactions] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [generatingStatement, setGeneratingStatement] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const recordsPerPage = 10;
  const totalRecords = transactions.length;
  const totalPages = Math.ceil(totalRecords / recordsPerPage);
  const indexOfLastRecord = currentPage * recordsPerPage;
  const indexOfFirstRecord = indexOfLastRecord - recordsPerPage;
  const currentRecords = transactions.slice(indexOfFirstRecord, indexOfLastRecord);

  const savingsAccounts = useMemo(() => {
    return accounts['Deposit'] || [];
    }, [accounts]); 

  const loadTransactions = useCallback(async () => {
    if (!selectedAccount || !startDate || !endDate) return;
    
    setLoading(true);
    try {
      const response = await fetchTransactionHistory(
        selectedAccount,
        formatDate(startDate),  
        formatDate(endDate)
      );
      
      if (response.data.Status === 'OK') {
        setTransactions(response.data.Result);
      } else {
        setError(response.data.Message || 'Failed to load transactions');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred');
    } finally {
        setLoading(false);
    }
    }, [selectedAccount, startDate, endDate]);
    
  useEffect(() => {
    if (selectedAccount) {
        loadTransactions();
    }
    }, [selectedAccount, loadTransactions]);

  const handleGenerateStatement = async () => {
    if (!selectedAccount || !startDate || !endDate) return;
    
    setGeneratingStatement(true);
    try {
      const response = await generateStatement(
        selectedAccount,
        formatDate(startDate),  
        formatDate(endDate)
      );
      
      if (response.data.Status === 'OK') {
        // Create download link for the PDF
        const link = document.createElement('a');
        link.href = `data:application/pdf;base64,${response.data.Result}`;
        link.download = `statement_${selectedAccount}_${formatDate(startDate)}_to_${formatDate(endDate)}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        setSuccess('Statement generated successfully. Check your downloads.');
      } else {
        setError(response.data.Message || 'Failed to generate statement');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred');
    } finally {
      setGeneratingStatement(false);
    }
  };

  return (
    <div className="transaction-history-container">
      {loading && <LoadingSpinner />}
      
      <h2>Transaction History</h2>
      
      <div className="filters">
        <div className="form-group">
          <label htmlFor="account">Account</label>
          <select
            id="account"
            value={selectedAccount}
            onChange={(e) => {
                setSelectedAccount(e.target.value);
                setTransactions([]);
              }}
          >
            <option value="">Select Account</option>
            {savingsAccounts.map(account => (
              <option key={account.account_number} value={account.account_number}>
                {account.account_number} - {account.product_name}
              </option>
            ))}
          </select>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="startDate">Start Date</label>
            <input
              type="date"
              id="startDate"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="endDate">End Date</label>
            <input
              type="date"
              id="endDate"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              min={startDate}
            />
          </div>
        </div>
        
        <div className="form-actions">
          <button 
            type="button" 
            onClick={loadTransactions}
            className='button-primary'
            disabled={!selectedAccount || !startDate || !endDate}
          >
            Load Transactions
          </button>
          
          <button 
            type="button" 
            onClick={handleGenerateStatement}
            className='button-secondary'
            disabled={!selectedAccount || !startDate || !endDate || generatingStatement}
          >
            {generatingStatement ? 'Generating...' : 'Generate Statement'}
          </button>
        </div>
      </div>
      
      <div className="transactions-list">
        {transactions.length > 0 ? (
          <div>
            <table className="transaction-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Receiver Name</th>
                  <th>Amount</th>
                  <th>Narration</th>
                  <th>Transaction ID</th>
                </tr>
              </thead>
              <tbody>
                {currentRecords.map((txn, index) => (
                  <tr key={index} className="transaction-row">
                    <td>{formatDateTime(txn.trans_date)}</td>
                    <td>{txn.name}</td>
                    <td className={txn.dr_cr === 'D' ? 'debit' : 'credit'}>
                      {formatCurrency(txn.amount, txn.currency_nm)}
                    </td>
                    <td className="narration">{txn.narration}</td>
                    <td className="trans-id">{txn.trans_id}</td>
                  </tr>
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
          <p className="no-transactions">No transactions found for the selected period.</p>
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

export default TransactionHistory;