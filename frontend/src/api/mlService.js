import apiClient from "./apiClient";

const mlService = {
  uploadFile: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post("/api/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    });
    return response.data;
  },

  // Future: get results by ID if async
  getResults: async (id) => {
    const response = await apiClient.get(`/api/results/${id}`);
    return response.data;
  },
};

export default mlService;
