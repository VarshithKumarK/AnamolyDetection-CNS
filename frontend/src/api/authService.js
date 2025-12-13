import apiClient from "./apiClient";

const authService = {
  signup: async (userData) => {
    const response = await apiClient.post("/api/auth/signup", userData);
    return response.data;
  },
  login: async (credentials) => {
    const response = await apiClient.post("/api/auth/login", credentials);
    return response.data;
  },
  // Optional: Get user profile if needed, or rely on stored user object
  getProfile: async () => {
    const response = await apiClient.get("/api/auth/me");
    return response.data;
  },
};

export default authService;
