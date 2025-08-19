import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { BankingProvider } from './contexts/BankingContext';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ForgotUserIdPage from './pages/auth/ForgotUserIdPage';
import ChangePasswordPage from './pages/auth/ChangePasswordPage';
import MasterPage from './pages/banking/MasterPage';
import HomePage from './pages/banking/HomePage';
import AccountInfoPage from './pages/banking/AccountInfoPage';
import TransactionPage from './pages/banking/TransactionPage';
import AddMoneyPage from './pages/banking/AddMoneyPage';
import TransactionHistoryPage from './pages/banking/TransactionHistoryPage';
import ActivityLogPage from './pages/banking/ActivityLogPage';
import CustomerInfoPage from './pages/banking/CustomerInfoPage';
import ComplaintPage from './pages/banking/ComplaintPage';
import BranchLocationPage from './pages/common/BranchLocationPage';
import AddMoneyCallBackPage from './pages/common/AddMoneyCallBackPage';
import './App.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <BankingProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/forgot-userid" element={<ForgotUserIdPage />} />
            <Route path="/change-password" element={<ChangePasswordPage />} />
            <Route path="/branches" element={<BranchLocationPage />} />
            <Route path="/addmoneycallback" element={<AddMoneyCallBackPage />} />
            
            <Route path="/banking" element={<MasterPage />}>
              <Route index element={<Navigate to="home" replace />} />
              <Route path="home" element={<HomePage />} />
              <Route path="account/:accountNumber" element={<AccountInfoPage />} />
              <Route path="transfer" element={<TransactionPage />} />
              <Route path="addMoney" element={<AddMoneyPage />} />
              <Route path="history" element={<TransactionHistoryPage />} />
              <Route path="activity" element={<ActivityLogPage />} />
              <Route path="profile" element={<CustomerInfoPage />} />
              <Route path="complaints" element={<ComplaintPage />} />
            </Route>
            
            <Route path="/" element={<Navigate to="/login" />} />
            <Route path="*" element={<Navigate to="/login" />} />
          </Routes>
        </BankingProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;