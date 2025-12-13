const mongoose = require("mongoose");

const jobSchema = mongoose.Schema(
  {
    user: {
      type: mongoose.Schema.Types.ObjectId,
      required: true,
      ref: "User",
    },
    filename: {
      type: String,
      required: true,
    },
    status: {
      type: String,
      enum: ["pending", "done", "failed"],
      default: "pending",
    },
    summary: {
      type: mongoose.Schema.Types.Mixed,
    },
    results: {
      type: mongoose.Schema.Types.Mixed, // Storing full results, or preview
    },
    error: {
      type: String,
    },
    completedAt: {
      type: Date,
    },
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model("Job", jobSchema);
