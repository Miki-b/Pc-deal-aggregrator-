const GlobalError = require("../utils/GlobalErrorHandler");

const errorHandler = (err, req, res, next) => {
  console.error(err);

  if (!err.statusCode) {
    err = new GlobalError('Internal Server Error', 500);
  }

  res.status(err.statusCode).json({
    status: err.status || 'error',
    message: err.message || 'Something went wrong',
  });
};

module.exports = errorHandler;
