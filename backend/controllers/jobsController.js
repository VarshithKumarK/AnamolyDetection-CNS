const Job = require("../models/Job");

// @desc    Get user jobs
// @route   GET /api/jobs
// @access  Private
const getJobs = async (req, res) => {
  const jobs = await Job.find({ user: req.user.id })
    .select("-results") // Exclude heavy results for list view
    .sort({ createdAt: -1 });
  res.status(200).json(jobs);
};

// @desc    Get single job
// @route   GET /api/jobs/:id
// @access  Private
const getJob = async (req, res) => {
  const job = await Job.findById(req.params.id);

  if (!job) {
    res.status(404);
    throw new Error("Job not found");
  }

  // Check for user
  if (!req.user) {
    res.status(401);
    throw new Error("User not found");
  }

  // Make sure the logged in user matches the job user
  if (job.user.toString() !== req.user.id) {
    res.status(401);
    throw new Error("User not authorized");
  }

  res.status(200).json(job);
};

// @desc    Delete job
// @route   DELETE /api/jobs/:id
// @access  Private
const deleteJob = async (req, res) => {
  const job = await Job.findById(req.params.id);

  if (!job) {
    res.status(404);
    throw new Error("Job not found");
  }

  // Check for user
  if (!req.user) {
    res.status(401);
    throw new Error("User not found");
  }

  // Make sure the logged in user matches the job user
  if (job.user.toString() !== req.user.id) {
    res.status(401);
    throw new Error("User not authorized");
  }

  // Use deleteOne() instead of remove()
  await job.deleteOne();

  res.status(200).json({ id: req.params.id });
};

module.exports = {
  getJobs,
  getJob,
  deleteJob,
};
