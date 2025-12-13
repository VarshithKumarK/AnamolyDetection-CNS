const express = require("express");
const router = express.Router();
const multer = require("multer");
const { uploadFile } = require("../controllers/uploadController");
const { protect } = require("../middlewares/authMiddleware");
const rateLimit = require("../middlewares/rateLimiter");

// Configure Multer
const upload = multer({
  dest: "uploads/",
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
  fileFilter: (req, file, cb) => {
    if (!file.originalname.match(/\.(csv)$/)) {
      return cb(new Error("Please upload a CSV file"));
    }
    cb(null, true);
  },
});

// Wrap async handlers
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

router.post(
  "/",
  protect,
  rateLimit,
  upload.single("file"),
  asyncHandler(uploadFile)
);

module.exports = router;
