import axios from "axios";

// Use your environment variable or default
const API_URL = process.env.REACT_APP_API_URL 

// Create an axios instance
const api = axios.create({
  baseURL: API_URL,
});

// Attach JWT token from localStorage to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
