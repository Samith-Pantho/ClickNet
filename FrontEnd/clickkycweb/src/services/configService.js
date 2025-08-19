import api from './api';

export const fetchAllAppSettings = async (params) => {
  return api.get(`/AppConfig/GetAppSettingsByKeys?${params.toString()}`);
};