export const API_BASE_URL = '/api';
export const WS_BASE_URL = `${window.location.host}/api`;
export const APP_NAME = 'ClickNet';

console.log(process.env.REACT_APP_API_URL);

export const ACCOUNT_TYPES = {
  SAVINGS: 'Deposit',
  LOAN: 'Loan'
};

export const ACTIVITY_TYPES = {
  LOGIN: 'LOGIN',
  LOGOUT: 'LOGOUT',
  FUNDTRANSFER: 'FUNDTRANSFER',
  SECURITYUPDATE: 'SECURITYUPDATE',
  REGISTER: 'REGISTER',
  SIGNUP: 'SIGNUP',
  REQUEST: 'REQUEST',
  PROFILE: 'PROFILE',
  ACCOUNT: 'ACCOUNT'
};

export const OTP_CHANNELS = {
  SMS: 'SMS',
  EMAIL: 'EMAIL',
  BOTH: 'BOTH'
};