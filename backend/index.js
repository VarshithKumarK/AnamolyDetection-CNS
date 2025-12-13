require("dotenv").config();
const express = require("express");
const cors = require("cors");
const helmet = require("helmet");
const morgan = require("morgan");
const connectDB = require("./config/db");

const app = express();

// Middleware
app.use(helmet());
app.use(cors({ origin: process.env.FRONTEND_URL || "http://localhost:5173" }));
app.use(express.json());
app.use(morgan("dev"));

// Connect Database
connectDB();

// Routes
// We will mount these after creating them.
// For now, if files don't exist, this will crash.
// So let's create placeholders or comment them out until we create routes.
// But as an agent I will create them next, so I will leave them required.
// Note: If user runs this immediately it fails. But I am fast.
app.use("/api/auth", require("./routes/auth.routes"));
app.use("/api", require("./routes/index"));

// Error Handler
app.use(require("./middlewares/errorHandler"));

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => console.log(`Server listening on ${PORT}`));
