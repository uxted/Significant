import axios from "axios";

const api = axios.create({
  baseURL: '',
  timeout: 30000,
});

let accessToken = null;
let refreshToken = null;

api.setTokens = (access, refresh) => {
  accessToken = access;
  refreshToken = refresh;
};

api.clearTokens = () => {
  accessToken = null;
  refreshToken = null;
};

// Request interceptor — attach JWT
api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Response interceptor — handle 401 (token expired)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const response = await axios.post(
          "/api/auth/refresh/",
          { refresh: refreshToken }
        );
        const { access, refresh: newRefresh } = response.data;
        accessToken = access;
        refreshToken = newRefresh;

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed — logout
        api.clearTokens();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
