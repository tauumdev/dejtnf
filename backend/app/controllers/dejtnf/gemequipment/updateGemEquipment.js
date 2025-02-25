const GemEquipment = require('../../../models/dejtnf/gemEquipment');
const { updateItem } = require('../../../middleware/db');
const { isIDGood, handleError } = require('../../../middleware/utils');
const { matchedData } = require('express-validator');
const { gemEquipmentExistsExcludingItself } = require('./helpers');

/**
 * Update item function called by route
 * @param {Object} req - request object
 * @param {Object} res - response object
 */
const updateGemEquipment = async (req, res) => {
    try {
        req = matchedData(req);
        const id = await isIDGood(req.id);
        const doesGemEquipmentExists = await gemEquipmentExistsExcludingItself(id, req.equipment_name);
        if (!doesGemEquipmentExists) {
            res.status(200).json(await updateItem(id, GemEquipment, req));
        }
    } catch (error) {
        handleError(res, error);
    }
}

module.exports = { updateGemEquipment };