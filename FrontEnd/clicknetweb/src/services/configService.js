import api from './api';

export const fetchAllAppSettings = async (params) => {
  return api.get(`/AppConfig/GetAppSettingsByKeys?${params.toString()}`);
};

export const fetchbranches = async () => {
  return api.get(`/AppConfig/GetBranches`);
};