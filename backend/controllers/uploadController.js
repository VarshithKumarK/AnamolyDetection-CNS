const Job = require("../models/Job");
const { sendFileToMlService } = require("../services/mlService");
const fs = require("fs");

// @desc    Upload CSV and run analysis
// @route   POST /api/upload
// @access  Private
const uploadFile = async (req, res) => {
  if (!req.file) {
    res.status(400);
    throw new Error("Please upload a file");
  }

  // Create Job (Pending)
  const job = await Job.create({
    user: req.user.id,
    filename: req.file.originalname,
    status: "pending",
  });

  try {
    // Send to ML Service
    const mlResponse = await sendFileToMlService(req.file.path);

    // Update Job (Done)
    job.status = "done";
    job.summary = mlResponse.summary;
    job.results = mlResponse; // Storing full result for now as per user request to reuse contract
    job.completedAt = Date.now();
    await job.save();

    // Clean up temp file
    fs.unlink(req.file.path, (err) => {
      if (err) console.error("Failed to delete temp file:", err);
    });

    res.status(200).json(job);
  } catch (error) {
    // Update Job (Failed)
    job.status = "failed";
    job.error = error.message;
    await job.save();

    // Clean up temp file
    fs.unlink(req.file.path, (err) => {
      if (err) console.error("Failed to delete temp file:", err);
    });

    res.status(500);
    throw new Error(`Analysis failed: ${error.message}`);
  }
};

module.exports = {
  uploadFile,
};
