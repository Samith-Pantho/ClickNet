import api from './api';

export const getProductList = async (productCategory) => {
  const response = await api.get(`/Internal/GetProductList/${productCategory}`);
  return response.data;
};

export const getBranches = async () => {
  const response = await api.get('/Internal/GetBranches');
  return response.data;
};

export const sendMobileOTP = async (phoneNumber) => {
  const response = await api.get(`/Internal/SendOTPforMobile/${phoneNumber}`);
  return response.data;
};

export const verifyMobileOTP = async (phoneNumber, otp) => {
  const response = await api.post(`/Internal/CheckMobileOTP`, {
    phone_number: phoneNumber, 
    code: otp               
  });
  return response.data;
};

export const sendEmailOTP = async (email) => {
  const response = await api.get(`/Internal/SendOTPforEmail/${email}`);
  return response.data;
};

export const verifyEmailOTP = async (email, otp) => {
  const response = await api.post(`/Internal/CheckEmailOTP`,{
    email_address: email, 
    code: otp               
  });
  return response.data;
};

export const initialize = async (initializeData) => {
  const response = await api.post(
    `/Internal/Initialize`,{
    product_code: initializeData.product_code,
    branch_code: initializeData.branch_code,
    phone_number: initializeData.phone_number,
    email_address: initializeData.email_address,
  });
  return response.data;
};

export const initializeVerification = async (accessToken) => {
  const response = await api.get('/Internal/Initializeverification', {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  return response.data;
};

export const getCustomerRegistrationData = async (accessToken) => {
  const response = await api.get('/Internal/GetCustomerRegistrationData', {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  return response.data;
};

export const createCustomerAndAccount = async (accessToken) => {
  const response = await api.get('/Internal/CreateCustomerAndAccount', {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  return response.data;
};

export const generateReport = async (accessToken) => {
  const response = await api.get('/Internal/GenerateReport', {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  return response.data;
};