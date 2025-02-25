const ValidateLot = require('../../../models/dejtnf/validateLot');

exports.updateValidatelot = async (req, res) => {
    try {
        const { id } = req.params;
        const updatedLot = await ValidateLot.findByIdAndUpdate(id, req.body, { new: true });
        if (!updatedLot) {
            return res.status(404).json({ error: 'ValidateLot not found' });
        }
        res.status(200).json({ data: updatedLot });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};