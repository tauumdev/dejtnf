const GemEquipment = require('../../../models/dejtnf/gemEquipment');
const { createItem } = require('../../../middleware/db');
const { handleError } = require('../../../middleware/utils');
const { matchedData } = require('express-validator');
const { gemEquipmentExists } = require('./helpers');

/**
 * Create item function called by route
 * @param {Object} req - request object
 * @param {Object} res - response object
 */
const createGemEquipment = async (req, res) => {
    try {
        req = matchedData(req);
        const doesGemEquipmentExists = await gemEquipmentExists(req.equipment_name);
        if (!doesGemEquipmentExists) {
            res.status(201).json(await createItem(req, GemEquipment));
        }
    } catch (error) {
        handleError(res, error);
    }
};

module.exports = { createGemEquipment };