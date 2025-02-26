const SecsgemEquipment = require('../../../models/dejtnf/secsgemEquipment');
const { updateItem } = require('../../../middleware/db');
const { isIDGood, handleError } = require('../../../middleware/utils');
const { matchedData } = require('express-validator');
const { secsgemEquipmentExistsExcludingItself } = require('./helpers');

/**
 * Update item function called by route
 * @param {Object} req - request object
 * @param {Object} res - response object
 */
const updateSecsgemEquipment = async (req, res) => {
    try {
        req = matchedData(req);
        const id = await isIDGood(req.id);
        const doesSecsgemEquipmentExists = await secsgemEquipmentExistsExcludingItself(id, req.equipment_name, req.address);
        if (!doesSecsgemEquipmentExists) {
            res.status(200).json(await updateItem(id, SecsgemEquipment, req));
        }
    } catch (error) {
        handleError(res, error);
    }
}

module.exports = { updateSecsgemEquipment }