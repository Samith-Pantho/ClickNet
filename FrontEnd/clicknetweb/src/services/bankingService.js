import api from './api';
import { formatDate } from '../utils/helpers';

export const fetchAllAccounts = async (productCategory = null) => {
  const params = productCategory ? { product_category: productCategory } : {};
  return api.get('/Account/FetchAllAccounts', { params });
};

export const fetchAccountDetails = async (accountNumber) => {
  return api.get('/Account/FetchAccountDetailsByAccountNo', {
    params: { account_number: accountNumber }
  });
};

export const fetchAccountBalances = async (accountNumber) => {
  return api.get('/Account/FetchBalancesAndRateByAccountNo', {
    params: { account_number: accountNumber }
  });
};

export const fetchAvailableBalance = async (accountNumber) => {
  return api.get('/Account/FetchAvailableBalanceByAccountNo', {
    params: { account_number: accountNumber }
  });
};

export const fetchrasactionLimitInfo = async (accountNumber) => {
  return api.get('/Account/FetchTrasactionLimitInfoByAccountNo', {
    params: { account_number: accountNumber }
  });
};

export const fetchTransactionHistory = async (accountNumber, startDate, endDate) => {
  return api.get('/Account/FetchAccountWiseTransactionHistory', {
    params: {
      account_number: accountNumber,
      start_date: formatDate(startDate),
      end_date: formatDate(endDate)
    }
  });
};

export const generateStatement = async (accountNumber, startDate, endDate) => {
  return api.get('/Account/GenerateStatementOfAccount', {
    params: {
      account_number: accountNumber,
      start_date: formatDate(startDate),
      end_date: formatDate(endDate)
    }
  });
};

export const transferFunds = async (transferData) => {
  return api.post('/Transaction/Fundtransfer', transferData);
};

export const addMoneyRequest = async (addMoneyData) => {
  return api.post('/AddMoney/InitializeAddMoney', addMoneyData);
};

export const processAddMoneyCallback = async (secretKey) => {
  return api.get('/AddMoney/ProcessAddMoneyCallback', {
    params: { secret_key: secretKey }
  });
};

export const fetchCustomerInfo = async () => {
  return api.get('/Profile/FetchCustomerInfo');
};

export const fetchCustomerActivities = async (count, activityType = null) => {
  const params = activityType ? { count, activity_type: activityType } : {count};
  return api.get('/Profile/FetchCustomerActivityList/', {params});
};

export const uploadProfilePicture = async (file) => {
  const formData = new FormData();
  formData.append('photo', file);
  return api.post('/Profile/SaveCustomerProfilePicture', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

export const fetchProfilePicture = async () => {
  return api.get('/Profile/FetchCustomerProfilePicture');
};

export const fetchComplaints = async () => {
  return api.get('/Request/Complaints');
};

export const createComplaint = async (complaintData) => {
  return api.post('/Request/CreateComplaint', complaintData);
};

export const chatWithAI = async (message) => {
  console.log(message);
  if (message === null || message === '')
    return api.post('/Chat/ChatWithAI');
  else
    return api.post('/Chat/ChatWithAI?message='+ message);
};