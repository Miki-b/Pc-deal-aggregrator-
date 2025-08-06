const express = require("express");
const dotenv = require("dotenv");
const connectDB = require("./app/config/database"); // Adjust the path to your connectDB file

dotenv.config();

const app = express();
app.use(express.json());

const dealRouter = require("./app/routes/dealRoutes");

const path = require('path');

app.use('/images', express.static(path.join(__dirname, 'downloaded_images')));


app.use("/api/v1/deals", dealRouter);
// You can add productRouter and orderRouter similarly if needed

// ⏳ Connect to DB before starting the server
connectDB().then(() => {
  app.listen(3000, () => {
    console.log("✅ Server is running on port 3000");
  });
});

const errorHandler = require('./app/middleware/errorHandler');
app.use(errorHandler);

