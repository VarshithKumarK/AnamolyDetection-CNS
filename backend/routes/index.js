const express = require("express");
const router = express.Router();

router.use("/upload", require("./upload.routes"));
router.use("/jobs", require("./jobs.routes"));

module.exports = router;
