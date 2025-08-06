const DealRepository = require("../repository/dealRepository");
const GlobalError = require("../utils/GlobalErrorHandler");


//Get all products
exports.getAllDeals = async (req, res,next) => {
    try {
        const deals = await DealRepository.getAllDeals();
        res.status(200).json(deals);
    } catch (error) {
        next(error);
    }
};
