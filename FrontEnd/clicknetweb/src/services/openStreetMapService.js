import api from './api';

export const fetchWaypoints = async (url) => {
  return api.get(url);
};