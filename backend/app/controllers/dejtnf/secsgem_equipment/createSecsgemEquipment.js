const SecsgemEquipment = require('../../../models/dejtnf/secsgemEquipment')
const { createItem } = require('../../../middleware/db')
const { handleError } = require('../../../middleware/utils')
const { matchedData } = require('express-validator')
const { secsgemEquipmentExists } = require('./helpers')
/**
 * Create item function called by route
 * @param {Object} req - request object
 * @param {Object} res - response object
 */
const createSecsgemEquipment = async (req, res) => {
    try {
        req = matchedData(req)
        const doesSecsgemEquipmentExists = await secsgemEquipmentExists(req.equipment_name, req.address)
        if (!doesSecsgemEquipmentExists) {
            res.status(201).json(await createItem(req, SecsgemEquipment))
        }
    } catch (error) {
        handleError(res, error)
    }
}

module.exports = { createSecsgemEquipment }