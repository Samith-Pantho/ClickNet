import api from './api';
import { OTP_CHANNELS } from '../utils/constants';

export const login = async (credentials) => {
  const payload = {
    UserID: credentials.userId,
    Password: credentials.password,
    IPAddress: '127.0.0.1',
    OTP: credentials.otp || "",
    OTP_verify_channel: credentials.otpChannel || OTP_CHANNELS.SMS,
    captcha_token: credentials.captcha_token
  };
  return api.post('/Login/Login', payload);
};

export const register = async (userData) => {
  const payload = {
    user_id: userData.userId,
    customer_title: userData.customerTitle,
    customer_id: userData.customerId,
    tax_id: userData.taxId,
    phone_number: userData.phone,
    birth_date: userData.birthDate,
    email: userData.email,
    remark: userData.remark || "",
    OTP: userData.otp || "",
    OTP_verify_channel:  userData.otpChannel || OTP_CHANNELS.SMS,
    captcha_token: userData.captcha_token
  };
  return api.post('/Registration/SignUp', payload);
};

export const checkUserIdAvailability = async (userId) => {
  return api.get('/Registration/IsUserIDAvailable', {
    params: { user_id: userId }
  });
};

export const forgotPassword = async (data) => {
  const payload = {
    UserID: data.userId,
    Newpassword: data.newPassword,
    ConfirmNewPassword: data.confirmPassword,
    CustomerID: data.customerId,
    TaxID: data.taxId,
    BirthDate: data.birthDate,
    Phone: data.phone,
    Email: data.email,
    OTP: data.otp || "",
    OTP_verify_channel: data.otpChannel || OTP_CHANNELS.SMS,
    captcha_token: data.captcha_token
  };
  return api.post('/UserIdPassword/ForgetPassword', payload);
};

export const changePassword = async (data) => {
  const payload = {
    UserID: data.UserID,
    OldPassword: data.OldPassword,
    NewPassword: data.NewPassword,
    ConfirmNewPassword: data.ConfirmNewPassword
  };
  return api.post('/UserIdPassword/ChangePassword', payload);
};

export const forgotUserId = async (data) => {
  const payload = {
    CustomerID: data.customerId,
    TaxID: data.taxId,
    BirthDate: data.birthDate,
    Phone: data.phone,
    Email: data.email,
    OTP: data.otp || "",
    OTP_verify_channel: data.otpChannel || OTP_CHANNELS.SMS,
    captcha_token: data.captcha_token
  };
  return api.post('/UserIdPassword/ForgetUserId', payload);
};

export const logout = async () => {
  return api.get('/Logout/Logout');
};