import apiClient from "./apiClient";

const jobsService = {
  // Get all jobs (without full results)
  getJobs: async () => {
    const response = await apiClient.get("/api/jobs");
    return response.data;
  },

  // Get single job with full results
  getJob: async (id) => {
    const response = await apiClient.get(`/api/jobs/${id}`);
    return response.data;
  },

  deleteJob: async (id) => {
    const response = await apiClient.delete(`/api/jobs/${id}`);
    return response.data;
  },
};

export default jobsService;
