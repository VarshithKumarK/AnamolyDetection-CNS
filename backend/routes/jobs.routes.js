const express = require("express");
const router = express.Router();
const { getJobs, getJob, deleteJob } = require("../controllers/jobsController");
const { protect } = require("../middlewares/authMiddleware");

// Wrap async handlers
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

router.get("/", protect, asyncHandler(getJobs));
router.get("/:id", protect, asyncHandler(getJob));
router.delete("/:id", protect, asyncHandler(deleteJob));

module.exports = router;
