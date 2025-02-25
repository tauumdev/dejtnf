const ValidateLot = require('../../../models/dejtnf/validateLot');

exports.getValidatelots = async (req, res) => {
    try {
        let { page = 1, limit = 10 } = req.query;
        page = parseInt(page);
        limit = parseInt(limit);
        const options = {
            page,
            limit,
            sort: { createdAt: -1 },
        };
        const results = await ValidateLot.paginate({}, options);
        res.status(200).json(results);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};