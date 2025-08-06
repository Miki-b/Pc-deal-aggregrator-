const Deal = require("../models/dealModel");
class DealRepository{
    async getAllDeals() {
        try{
            const deals = await Deal.find();
            return deals;
        } catch (error) {
            throw error;
        }
    }
}


module.exports = new DealRepository();