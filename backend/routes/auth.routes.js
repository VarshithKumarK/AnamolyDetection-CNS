const express = require("express");
const router = express.Router();
const {
  registerUser,
  loginUser,
  getMe,
} = require("../controllers/authController");
const { protect } = require("../middlewares/authMiddleware");

// Wrap async handlers to catch errors
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

router.post("/signup", asyncHandler(registerUser));
router.post("/login", asyncHandler(loginUser));
router.get("/me", protect, asyncHandler(getMe));

module.exports = router;
