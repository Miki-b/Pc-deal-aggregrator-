const mongoose = require('mongoose');

const dealSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true
  },
  model: String,
  processor: String,
  generation: String,
  ram: String,
  storage: String,
  screen_size: String,
  resolution: String,
  graphics_card: String,
  graphics_memory: String,
  battery_life: String,
  condition: String,
  price: {
    type: Number,
    required: true
  },
  currency: {
    type: String,
    default: 'Birr'
  },
  url: String,
  urls: [String],
  contact_numbers: [String],
  image_path: String,
  raw_message: String,
  timestamp: {
    type: Date,
    default: Date.now
  }
}, {
  collection: 'deals' // Explicitly set the collection name in MongoDB
});

module.exports = mongoose.model('Deal', dealSchema);
