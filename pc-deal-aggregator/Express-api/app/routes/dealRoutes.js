const express = require("express");
const dealController = require("../controllers/dealController");
const router = express.Router();

//get all products
router.get("/", dealController.getAllDeals);

module.exports = router;