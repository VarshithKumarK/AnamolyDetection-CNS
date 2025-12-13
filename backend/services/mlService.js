const axios = require("axios");
const FormData = require("form-data");
const fs = require("fs");

const sendFileToMlService = async (filePath) => {
  const form = new FormData();
  form.append("file", fs.createReadStream(filePath));

  try {
    const response = await axios.post(process.env.ML_SERVICE_URL, form, {
      headers: {
        ...form.getHeaders(),
      },
      // Increase timeout for ML processing
      timeout: 120000,
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error("ML Service Error Data:", error.response.data);
      throw new Error(error.response.data.message || "ML Service Failed");
    } else if (error.request) {
      // The request was made but no response was received
      console.error("ML Service No Response:", error.request);
      throw new Error("ML Service did not respond");
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error("ML Service Request Error:", error.message);
      throw new Error(error.message);
    }
  }
};

module.exports = {
  sendFileToMlService,
};
