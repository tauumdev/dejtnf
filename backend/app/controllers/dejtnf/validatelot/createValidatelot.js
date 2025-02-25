const ValidateLot = require('../../../models/dejtnf/validateLot');

exports.createValidatelot = async (req, res) => {
    try {
        const newLot = new ValidateLot(req.body);
        const savedLot = await newLot.save();
        res.status(201).json({ data: savedLot });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};